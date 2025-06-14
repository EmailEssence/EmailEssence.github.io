"""
Service for handling email summarization operations.
"""

# Standard library imports
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta

# Third-party imports
from fastapi import HTTPException, status, Depends
from bson import ObjectId

# Internal imports
from app.utils.helpers import get_logger, log_operation, standardize_error_response
from app.models import EmailSchema, SummarySchema
from app.services.database.repositories.summary_repository import SummaryRepository
from app.services.database.factories import get_summary_repository, get_email_service
from app.services.summarization.base import AdaptiveSummarizer
from app.services.summarization import (
    ProcessingStrategy, 
    OpenAIEmailSummarizer,
    GeminiEmailSummarizer
)

# -------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------

logger = get_logger(__name__, 'service')

class SummaryService:
    """
    Service for handling email summarization operations.
    
    This class provides methods for managing email summaries, including:
    - Creating and retrieving summaries
    - Updating summary status and content
    - Managing summary metadata
    """
    
    def __init__(self, summary_repository: SummaryRepository = None):
        """
        Initialize the summary service.
        
        Args:
            summary_repository: Summary repository instance
        """
        self.summary_repository = summary_repository or get_summary_repository()
        self.email_service = get_email_service()
    
    async def initialize(self):
        """
        Initialize database indexes for summaries.
        
        Creates necessary indexes for efficient querying of summaries.
        """
        try:
            await self.summary_repository.create_index("email_id", unique=True)
            await self.summary_repository.create_index("keywords")  # For keyword searching
            await self.summary_repository.create_index("generated_at")  # For time-based queries
            await self.summary_repository.create_index("google_id")  # For user-specific summaries
            
            log_operation(logger, 'info', "Summary collection indexes initialized")
        except Exception as e:
            raise standardize_error_response(e, "initialize summary indexes")
    
    async def save_summary(self, summary: SummarySchema, google_id: str) -> str:
        """
        Store or update a summary in the database.
        
        Args:
            summary: Summary to save
            google_id: Google ID of the user who owns the summary
            
        Returns:
            str: ID of the saved summary
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # If summary is already a SummarySchema instance, use it directly
            if isinstance(summary, SummarySchema):
                summary_dict = summary.model_dump()
            else:
                # Otherwise create a new SummarySchema instance
                summary_dict = SummarySchema(**summary).model_dump()
            
            # Add google_id to the summary
            summary_dict["google_id"] = google_id
            
            # Use upsert to either update existing or insert new
            result = await self.summary_repository.update_one(
                {"email_id": summary.email_id, "google_id": google_id},
                summary_dict,
                upsert=True
            )
            
            if not result:
                raise Exception("Failed to save summary")
                
            log_operation(logger, 'debug', f"Summary saved for email {summary.email_id} for user {google_id}")
            return summary.email_id
            
        except Exception as e:
            raise standardize_error_response(e, "save summary", summary.email_id)
    
    async def get_summary(self, email_id: str, google_id: str) -> Optional[SummarySchema]:
        """
        Retrieve a summary by email ID.
        
        Args:
            email_id: ID of the email
            google_id: Google ID of the user who owns the summary
            
        Returns:
            Optional[SummarySchema]: Summary if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.summary_repository.find_one({"email_id": email_id, "google_id": google_id})
            if not result:
                return None
            # If result is already a SummarySchema instance, return it directly
            if isinstance(result, SummarySchema):
                return result
            # Otherwise create a new SummarySchema instance
            return SummarySchema(**result)
        except Exception as e:
            raise standardize_error_response(e, "get summary", email_id)
    
    async def get_summaries(
        self, 
        skip: int = 0, 
        limit: int = 20,
        sort_by: str = "generated_at",
        sort_order: str = "desc",
        google_id: str = None
    ) -> List[SummarySchema]:
        """
        Retrieve a paginated list of summaries.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_by: Field to sort by
            sort_order: Sort direction ("asc" or "desc")
            google_id: Google ID of the user whose summaries to retrieve
            
        Returns:
            List[SummarySchema]: List of summary objects
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Determine sort direction
            sort_direction = -1 if sort_order == "desc" else 1
            
            # Create query with google_id filter if provided
            query = {"google_id": google_id} if google_id else {}
            
            # Fetch summaries with pagination and sorting
            results = await self.summary_repository.find_many(
                query,
                limit=limit,
                skip=skip,
                sort=[(sort_by, sort_direction)]
            )
            
            # Convert results to SummarySchema objects if needed
            return [result if isinstance(result, SummarySchema) else SummarySchema(**result) for result in results]
        except Exception as e:
            raise standardize_error_response(e, "get summaries")
    
    async def search_by_keywords(
        self, 
        keywords: List[str], 
        limit: int = 10,
        google_id: str = None
    ) -> List[SummarySchema]:
        """
        Find summaries containing specific keywords.
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum results to return
            google_id: Google ID of the user whose summaries to search
            
        Returns:
            List[SummarySchema]: Matching summaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            query = {"keywords": {"$in": keywords}}
            if google_id:
                query["google_id"] = google_id
                
            results = await self.summary_repository.find_many(query, limit=limit)
            return [result if isinstance(result, SummarySchema) else SummarySchema(**result) for result in results]
        except Exception as e:
            raise standardize_error_response(e, "search summaries by keywords")
    
    async def get_recent_summaries(
        self, 
        days: int = 7, 
        limit: int = 20,
        google_id: str = None
    ) -> List[SummarySchema]:
        """
        Get summaries generated within recent days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of summaries to return
            google_id: Google ID of the user whose summaries to retrieve
            
        Returns:
            List[SummarySchema]: Recent summaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Create timezone-aware cutoff date
            now = datetime.now(timezone.utc)
            cutoff_date = now - timedelta(days=days)
            
            # Build query with proper datetime comparison for MongoDB
            query = {
                "generated_at": {
                    "$gte": cutoff_date,
                    "$lte": now
                }
            }
            if google_id:
                query["google_id"] = google_id
                
            log_operation(logger, 'debug', f"Querying summaries between {cutoff_date.isoformat()} and {now.isoformat()}")
            
            results = await self.summary_repository.find_many(
                query,
                limit=limit,
                sort=[("generated_at", -1)]
            )
            
            log_operation(logger, 'debug', f"Found {len(results)} summaries matching query")
            return [result if isinstance(result, SummarySchema) else SummarySchema(**result) for result in results]
        except Exception as e:
            raise standardize_error_response(e, "get recent summaries")
    
    async def delete_summary(self, email_id: str, google_id: str) -> bool:
        """
        Delete a summary.
        
        Args:
            email_id: ID of the email whose summary to delete
            google_id: Google ID of the user who owns the summary
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.summary_repository.delete_one({"email_id": email_id, "google_id": google_id})
            deleted = result.deleted_count > 0
            
            if deleted:
                log_operation(logger, 'info', f"Summary for email {email_id} deleted for user {google_id}")
            else:
                log_operation(logger, 'info', f"No summary found for email {email_id} for user {google_id} to delete")
                
            return deleted
        except Exception as e:
            raise standardize_error_response(e, "delete summary", email_id)
    
    async def delete_summaries_by_google_id(self, google_id: str) -> bool:
        """
        Delete all summaries for a specific Google user ID.
        
        Args:
            google_id: Google ID of the user whose summaries to delete
            
        Returns:
            bool: True if any summaries were deleted, False otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            result = await self.summary_repository.delete_by_google_id({"google_id": google_id})
            deleted = result.deleted_count > 0
            
            if deleted:
                log_operation(logger, 'info', f"All summaries deleted for user {google_id}")
            else:
                log_operation(logger, 'info', f"No summaries found for user {google_id} to delete")
                
            return deleted
        except Exception as e:
            raise standardize_error_response(e, "delete summaries by google id", google_id)
    
    async def save_summaries_batch(self, summaries: List[SummarySchema], google_id: str) -> Dict[str, int]:
        """
        Store multiple summaries in a single operation.
        
        Args:
            summaries: List of summaries to store
            google_id: Google ID of the user who owns the summaries
            
        Returns:
            Dict: Statistics about the operation (inserted, modified counts)
            
        Raises:
            Exception: If database operation fails
        """
        if not summaries:
            return {"inserted": 0, "modified": 0}
            
        try:
            # Create operations for bulk write
            operations = []
            for summary in summaries:
                summary_dict = summary.to_dict()
                summary_dict["google_id"] = google_id
                operations.append(
                    {
                        "filter": {"email_id": summary.email_id, "google_id": google_id},
                        "update": summary_dict,
                        "upsert": True
                    }
                )
            
            # Execute bulk operation
            if operations:
                result = await self.summary_repository.bulk_write(operations)
                stats = {
                    "inserted": result.upserted_count,
                    "modified": result.modified_count
                }
                log_operation(logger, 'info', f"Batch summary save: {result.upserted_count} inserted, "
                            f"{result.modified_count} modified for user {google_id}")
                return stats
            return {"inserted": 0, "modified": 0}
            
        except Exception as e:
            raise standardize_error_response(e, "save summaries batch")
    
    async def count_summaries(self, query: Dict = None, google_id: str = None) -> int:
        """
        Count summaries matching the given query.
        
        Args:
            query: MongoDB query to filter summaries
            google_id: Google ID of the user whose summaries to count
            
        Returns:
            int: Number of matching summaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            query = query or {}
            if google_id:
                query["google_id"] = google_id
            return await self.summary_repository.count_documents(query)
        except Exception as e:
            raise standardize_error_response(e, "count summaries")
    
    async def get_summaries_by_ids(self, email_ids: List[str], google_id: str) -> List[SummarySchema]:
        """
        Retrieve multiple summaries by their email IDs.
        
        Args:
            email_ids: List of email IDs to fetch summaries for
            google_id: Google ID of the user who owns the summaries
            
        Returns:
            List[SummarySchema]: List of found summaries (may be fewer than requested if some don't exist)
            
        Raises:
            Exception: If database operation fails
        """
        if not email_ids:
            return []
        
        try:
            # Query for all summaries matching the provided email IDs
            query = {"email_id": {"$in": email_ids}, "google_id": google_id}
            results = await self.summary_repository.find_many(query, limit=len(email_ids))
            
            # Convert to SummarySchema objects
            summaries = []
            for doc in results:
                if isinstance(doc, SummarySchema):
                    summaries.append(doc)
                else:
                    summaries.append(SummarySchema(**doc))
            
            # Log how many were found
            log_operation(logger, 'debug', f"Found {len(summaries)} summaries out of {len(email_ids)} requested for user {google_id}")
            
            return summaries
        except Exception as e:
            raise standardize_error_response(e, "get summaries by ids")
    
    async def get_or_create_summary(
        self,
        email_id: str,
        summarizer: AdaptiveSummarizer[EmailSchema],
        google_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get an existing summary or create a new one if it doesn't exist.
        
        Args:
            email_id: ID of the email to summarize
            summarizer: The summarizer implementation to use
            google_id: Google ID of the user requesting the summary
            
        Returns:
            Optional[Dict[str, Any]]: Summary if found or created, None otherwise
        """
        try:
            # Try to get existing summary
            summary = await self.get_summary(email_id, google_id)
            if summary:
                return summary.model_dump()
                
            # Get email data
            email = await self.email_service.get_email(email_id, google_id)
            if not email:
                log_operation(logger, 'warning', f"Email {email_id} not found for user {google_id}")
                return None
                
            # Generate summary using EmailSchema directly
            summaries = await summarizer.summarize(
                [email],
                strategy=ProcessingStrategy.SINGLE
            )
            
            if not summaries:
                log_operation(logger, 'warning', f"Failed to generate summary for email {email_id}")
                return None
                
            # Create a new SummarySchema with the google_id
            summary_data = summaries[0].model_dump()
            summary_data["google_id"] = google_id
            summary = SummarySchema(**summary_data)
            
            # Store summary
            await self.save_summary(summary, google_id)
            log_operation(logger, 'info', f"Created new summary for email {email_id}")
            
            return summary.model_dump()
            
        except Exception as e:
            raise standardize_error_response(e, "get or create summary", email_id)
    
    async def get_or_create_summaries_batch(
        self,
        email_ids: List[str],
        summarizer: AdaptiveSummarizer[EmailSchema],
        google_id: str,
        batch_size: int = 50  # Process in smaller batches to avoid timeouts
    ) -> Dict[str, List[SummarySchema]]:
        """
        Get or create summaries for multiple email IDs in batch.
        
        Args:
            email_ids: List of email IDs to process
            summarizer: The summarizer implementation to use
            google_id: Google ID of the user requesting the summaries
            batch_size: Maximum number of emails to process in a single batch
            
        Returns:
            Dict[str, List[SummarySchema]]: Dictionary containing:
                - 'summaries': List of successfully processed summaries
                - 'missing_emails': List of email IDs that couldn't be found
                - 'failed_summaries': List of email IDs that failed to generate summaries
        """
        if not email_ids:
            return {
                'summaries': [],
                'missing_emails': [],
                'failed_summaries': []
            }
            
        try:
            # Process in smaller batches to avoid timeouts
            all_summaries = []
            all_missing_emails = []
            all_failed_summaries = []
            
            # Split email_ids into batches
            for i in range(0, len(email_ids), batch_size):
                batch_ids = email_ids[i:i + batch_size]
                
                try:
                    # First get all existing summaries for this batch
                    existing_summaries = await self.get_summaries_by_ids(batch_ids, google_id)
                    existing_email_ids = {summary.email_id for summary in existing_summaries}
                    
                    # Find which emails need new summaries
                    missing_email_ids = set(batch_ids) - existing_email_ids
                    
                    if missing_email_ids:
                        # Get email data for missing summaries
                        missing_emails = []
                        failed_emails = []
                        
                        for email_id in missing_email_ids:
                            try:
                                email = await self.email_service.get_email(email_id, google_id)
                                if email:
                                    missing_emails.append(email)
                                else:
                                    failed_emails.append(email_id)
                                    log_operation(logger, 'warning', f"Email {email_id} not found for user {google_id}")
                            except Exception as e:
                                failed_emails.append(email_id)
                                log_operation(logger, 'warning', f"Error fetching email {email_id}: {e}")
                        
                        if missing_emails:
                            # Generate summaries for missing emails
                            try:
                                new_summaries = await summarizer.summarize(
                                    missing_emails,
                                    strategy=ProcessingStrategy.ADAPTIVE
                                )
                                
                                # Save new summaries
                                if new_summaries:
                                    await self.save_summaries_batch(new_summaries, google_id)
                                    all_summaries.extend(new_summaries)
                            except Exception as e:
                                log_operation(logger, 'error', f"Failed to generate summaries for batch: {e}")
                                all_failed_summaries.extend([email.email_id for email in missing_emails])
                                continue
                        
                        all_missing_emails.extend(failed_emails)
                    
                    # Add existing summaries to results
                    all_summaries.extend(existing_summaries)
                    
                except Exception as e:
                    log_operation(logger, 'error', f"Error processing batch {i//batch_size + 1}: {e}")
                    # Mark all emails in this batch as failed
                    all_failed_summaries.extend(batch_ids)
                    continue
            
            # Log final results
            log_operation(logger, 'info',
                f"Batch summary results for user {google_id}: "
                f"{len(all_summaries)} successful, {len(all_missing_emails)} missing emails, "
                f"{len(all_failed_summaries)} failed summaries"
            )
            
            return {
                'summaries': all_summaries,
                'missing_emails': all_missing_emails,
                'failed_summaries': all_failed_summaries
            }
            
        except Exception as e:
            raise standardize_error_response(e, "process batch summaries")