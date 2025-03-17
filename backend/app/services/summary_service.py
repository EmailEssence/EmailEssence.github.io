import logging
from typing import List, Optional, Dict, Any
import pymongo
from bson import ObjectId
from datetime import datetime, timezone, timedelta

from app.models import SummarySchema
from database import db

# Create module-specific logger
logger = logging.getLogger(__name__)

class SummaryService:
    """
    Service for managing email summaries in the database.
    
    This class provides methods for storing, retrieving, searching,
    and managing email summaries in MongoDB.
    """
    
    async def initialize(self):
        """
        Initialize database indexes for summaries.
        
        Creates necessary indexes for efficient querying of summaries.
        """
        # Create indexes for efficient querying
        await db.summaries.create_index("email_id", unique=True)
        await db.summaries.create_index("keywords")  # For keyword searching
        await db.summaries.create_index("generated_at")  # For time-based queries
        
        logger.info("Summary collection indexes initialized")
    
    async def save_summary(self, summary: SummarySchema) -> str:
        """
        Store or update a summary in the database.
        
        Args:
            summary: Summary to save
            
        Returns:
            str: ID of the saved summary
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Convert to dict using the to_dict method
            summary_dict = summary.to_dict()
            
            # Use upsert to either update existing or insert new
            result = await db.summaries.update_one(
                {"email_id": summary.email_id},
                {"$set": summary_dict},
                upsert=True
            )
            
            logger.debug(f"Summary saved for email {summary.email_id}")
            return summary.email_id
            
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")
            raise
    
    async def get_summary(self, email_id: str) -> Optional[SummarySchema]:
        """
        Retrieve a summary by email ID.
        
        Args:
            email_id: ID of the email
            
        Returns:
            Optional[SummarySchema]: Summary if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            result = await db.summaries.find_one({"email_id": email_id})
            if not result:
                return None
            return SummarySchema.from_dict(result)
        except Exception as e:
            logger.error(f"Failed to retrieve summary for email {email_id}: {e}")
            raise
    
    async def get_summaries(
        self, 
        skip: int = 0, 
        limit: int = 20,
        sort_by: str = "generated_at",
        sort_order: str = "desc"
    ) -> List[SummarySchema]:
        """
        Retrieve a paginated list of summaries.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_by: Field to sort by
            sort_order: Sort direction ("asc" or "desc")
            
        Returns:
            List[SummarySchema]: List of summary objects
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Determine sort direction
            sort_direction = -1 if sort_order == "desc" else 1
            
            # Fetch summaries with pagination and sorting
            results = await db.summaries.find() \
                .sort([(sort_by, sort_direction)]) \
                .skip(skip) \
                .limit(limit) \
                .to_list(length=limit)
            
            # Convert results to SummarySchema objects
            return [SummarySchema.from_dict(doc) for doc in results]
        except Exception as e:
            logger.error(f"Failed to retrieve summaries: {e}")
            raise
    
    async def search_by_keywords(
        self, 
        keywords: List[str], 
        limit: int = 10
    ) -> List[SummarySchema]:
        """
        Find summaries containing specific keywords.
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum results to return
            
        Returns:
            List[SummarySchema]: Matching summaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            query = {"keywords": {"$in": keywords}}
            results = await db.summaries.find(query).limit(limit).to_list(length=limit)
            return [SummarySchema.from_dict(result) for result in results]
        except Exception as e:
            logger.error(f"Failed to search summaries by keywords: {e}")
            raise
    
    async def get_recent_summaries(
        self, 
        days: int = 7, 
        limit: int = 20
    ) -> List[SummarySchema]:
        """
        Get summaries generated within recent days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of summaries to return
            
        Returns:
            List[SummarySchema]: Recent summaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            query = {"generated_at": {"$gte": cutoff_date}}
            
            results = await db.summaries.find(query) \
                .sort([("generated_at", -1)]) \
                .limit(limit) \
                .to_list(length=limit)
                
            return [SummarySchema.from_dict(doc) for doc in results]
        except Exception as e:
            logger.error(f"Failed to retrieve recent summaries: {e}")
            raise
    
    async def delete_summary(self, email_id: str) -> bool:
        """
        Delete a summary.
        
        Args:
            email_id: ID of the email whose summary to delete
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            result = await db.summaries.delete_one({"email_id": email_id})
            deleted = result.deleted_count > 0
            
            if deleted:
                logger.info(f"Summary for email {email_id} deleted")
            else:
                logger.info(f"No summary found for email {email_id} to delete")
                
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete summary for email {email_id}: {e}")
            raise
    
    async def save_summaries_batch(self, summaries: List[SummarySchema]) -> Dict[str, int]:
        """
        Store multiple summaries in a single operation.
        
        Args:
            summaries: List of summaries to store
            
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
                operations.append(
                    pymongo.UpdateOne(
                        {"email_id": summary.email_id},
                        {"$set": summary_dict},
                        upsert=True
                    )
                )
            
            # Execute bulk operation
            if operations:
                result = await db.summaries.bulk_write(operations)
                stats = {
                    "inserted": result.upserted_count,
                    "modified": result.modified_count
                }
                logger.info(f"Batch summary save: {result.upserted_count} inserted, "
                            f"{result.modified_count} modified")
                return stats
            return {"inserted": 0, "modified": 0}
            
        except Exception as e:
            logger.error(f"Error in batch saving summaries: {e}")
            raise
    
    async def count_summaries(self, query: Dict = None) -> int:
        """
        Count summaries matching the given query.
        
        Args:
            query: MongoDB query to filter summaries
            
        Returns:
            int: Number of matching summaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            return await db.summaries.count_documents(query or {})
        except Exception as e:
            logger.error(f"Failed to count summaries: {e}")
            raise
    
    async def get_summaries_by_ids(self, email_ids: List[str]) -> List[SummarySchema]:
        """
        Retrieve multiple summaries by their email IDs.
        
        Args:
            email_ids: List of email IDs to fetch summaries for
            
        Returns:
            List[SummarySchema]: List of found summaries (may be fewer than requested if some don't exist)
            
        Raises:
            Exception: If database operation fails
        """
        if not email_ids:
            return []
        
        try:
            # Query for all summaries matching the provided email IDs
            query = {"email_id": {"$in": email_ids}}
            results = await db.summaries.find(query).to_list(length=len(email_ids))
            
            # Convert to SummarySchema objects
            summaries = [SummarySchema.from_dict(doc) for doc in results]
            
            # Log how many were found
            logger.debug(f"Found {len(summaries)} summaries out of {len(email_ids)} requested")
            
            return summaries
        except Exception as e:
            logger.error(f"Failed to retrieve summaries by IDs: {e}")
            raise 