"""
User router for Email Essence.

This module handles user profile management, preferences, and user-related operations.
It provides endpoints for retrieving and updating user information and preferences.
"""

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status

# Internal imports
from app.dependencies import get_current_user, get_current_user_info
from app.utils.helpers import get_logger, log_operation, standardize_error_response
from app.models import PreferencesSchema, UserSchema
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.email_service import EmailService
from app.services.summarization.summary_service import SummaryService
from app.services.database.factories import get_auth_service, get_user_service, get_email_service, get_summary_service

# -------------------------------------------------------------------------
# Router Configuration
# -------------------------------------------------------------------------

router = APIRouter()
logger = get_logger(__name__, 'router')

# -------------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------------

@router.get(
    "/me", 
    response_model=UserSchema,
    summary="Get current user profile",
    description="Retrieves the authenticated user's profile information or creates a new user record if one doesn't exist"
)
async def get_current_user_profile(
    user: UserSchema = Depends(get_current_user)
):
    """
    Retrieve current user profile.
    
    Args:
        user: Current authenticated user from dependency
        
    Returns:
        UserSchema: User profile information
    """
    logger.debug(f"User profile retrieved: {user.email}")
    return user

@router.get(
    "/preferences",
    summary="Get user preferences",
    description="Retrieves the authenticated user's preference settings"
)
async def get_user_preferences(
    user_data: dict = Depends(get_current_user_info),
    user_service: UserService = Depends(get_user_service)
):
    """
    Retrieves the user's preferences from their profile.
    
    Args:
        user_data: User information from token validation
        user_service: User service instance
        
    Returns:
        dict: User preference settings
        
    Raises:
        HTTPException: If preferences cannot be retrieved
    """
    logger.debug("Retrieving user preferences...")
    
    try:
        user_info = user_data['user_info']
        user_email = user_info.get('email')
        
        logger.debug(f"Fetching preferences for user: {user_email}")
        
        # Get user first to ensure they exist
        user = await user_service.get_user_by_email(user_email)
        if not user:
            logger.debug(f"User not found: {user_email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        preferences = user.preferences.model_dump()
        logger.debug(f"Preferences retrieved successfully for user: {user_email}")
        return {"preferences": preferences}
    except Exception as e:
        raise standardize_error_response(e, "retrieve user preferences")

@router.put(
    "/preferences",
    summary="Update user preferences",
    description="Updates the authenticated user's preference settings"
)
async def update_preferences(
    preferences: PreferencesSchema,
    user_data: dict = Depends(get_current_user_info),
    user_service: UserService = Depends(get_user_service)
):
    """
    Updates the user's preference settings.
    
    Args:
        preferences: Preference settings to update
        user_data: User information from token validation
        user_service: User service instance
        
    Returns:
        dict: Updated user preferences
        
    Raises:
        HTTPException: If preference update fails
    """
    logger.debug("Updating user preferences...")
    
    try:
        user_info = user_data['user_info']
        user_email = user_info.get('email')
        
        logger.debug(f"Updating preferences for user: {user_email}")
        
        # Get user first to ensure they exist
        user = await user_service.get_user_by_email(user_email)
        if not user:
            logger.debug(f"User not found: {user_email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        logger.debug(f"Found user with ID: {user.google_id}")
        logger.debug(f"Current user data: {user.model_dump()}")
            
        # Create update data with existing user fields and new preferences
        update_data = {
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "oauth": user.oauth.model_dump() if hasattr(user, 'oauth') and user.oauth else {},
            "preferences": preferences.model_dump()
        }
        
        logger.debug(f"Update data: {update_data}")
        
        # Update user with new preferences
        try:
            updated_user = await user_service.update_user(
                user.google_id,
                update_data
            )
        except Exception as e:
            raise standardize_error_response(e, "update preferences")
        
        if not updated_user:
            logger.debug("Update returned None")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences"
            )
        
        logger.debug(f"Updated user data: {updated_user.model_dump()}")
        logger.debug(f"Preferences updated successfully for user: {user_email}")
        return {"preferences": updated_user.preferences.model_dump()}
    except Exception as e:
        raise standardize_error_response(e, "update preferences")

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserSchema:
    """
    Get a user by ID.
    
    Args:
        user_id: The ID of the user to retrieve
        user_service: Injected UserService instance
        auth_service: Injected AuthService instance
        
    Returns:
        UserSchema: The requested user
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = await user_service.get_user(user_id)
    if not user:
        raise standardize_error_response(
            Exception("User not found"), 
            "get user", 
            user_id
        )
    return user

@router.get("/email/{email}", response_model=UserSchema)
async def get_user_by_email(
    email: str,
    user_service: UserService = Depends(get_user_service)
) -> UserSchema:
    """
    Get a user by email.
    
    Args:
        email: The email of the user to retrieve
        user_service: Injected UserService instance
        
    Returns:
        UserSchema: The requested user
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = await user_service.get_user_by_email(email)
    if not user:
        raise standardize_error_response(
            Exception("User not found"), 
            "get user by email", 
            email
        )
    return user

@router.post("/", response_model=UserSchema)
async def create_user(
    user_data: UserSchema,
    user_service: UserService = Depends(get_user_service)
) -> UserSchema:
    """
    Create a new user.
    
    Args:
        user_data: The user data to create
        user_service: Injected UserService instance
        
    Returns:
        UserSchema: The created user
    """
    return await user_service.create_user(user_data)

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    user_data: UserSchema,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserSchema:
    """
    Update a user.
    
    Args:
        user_id: The ID of the user to update
        user_data: The updated user data
        user_service: Injected UserService instance
        auth_service: Injected AuthService instance
        
    Returns:
        UserSchema: The updated user
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = await user_service.update_user(user_id, user_data)
    if not user:
        raise standardize_error_response(
            Exception("User not found"), 
            "update user", 
            user_id
        )
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service),
    summary_service: SummaryService = Depends(get_summary_service)
) -> dict:
    """
    Delete a user.
    
    Args:
        user_id: The ID of the user to delete
        user_service: Injected UserService instance
        auth_service: Injected AuthService instance
        email_service: Injected EmailService instance
        summary_service: Injected SummaryService instance
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if user not found
    """
    successDeleteUser = await user_service.delete_user(user_id)
    if not successDeleteUser:
        raise standardize_error_response(
            HTTPException(status_code=404, detail="User not found"),
            action="delete user",
            context=user_id
        )
    
    successDeleteEmails = await email_service.delete_emails(user_id)
    if not successDeleteEmails:
        raise standardize_error_response(
            HTTPException(status_code=500, detail="Failed to delete user emails"),
            action="delete emails by user ID",
            context=user_id
        )
    
    # Note: This is commented out to avoid having to inccur the cost of deleting and resummarizing
    
    #successDeleteSummaries = await summary_service.delete_summaries_by_google_id(user_id)
    #if not successDeleteSummaries:
    #    raise standardize_error_response(
    #        HTTPException(status_code=404, detail="Summaries not found"),
    #        action="delete summaries by user ID",
    #        context=user_id
    #)
    
    return {"message": "User deleted successfully"}
    