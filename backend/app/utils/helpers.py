"""
Helper functions for Email Essence FastAPI application.

This module contains shared utilities for logging and error handling that can be 
used across the application without creating circular dependencies.
"""

# Standard library imports
import logging
import os
from typing import Optional

# Third-party imports
from fastapi import HTTPException, status


def _get_logging_level_config() -> dict:
    """
    Get logging level configuration based on environment.
    
    Returns:
        dict: Mapping of module types to logging levels
    """
    environment = os.getenv('ENVIRONMENT', 'production').lower()
    
    # Logging level configuration by environment
    config = {
        'development': {
            'router': logging.DEBUG,
            'service': logging.DEBUG,
            'default': logging.DEBUG
        },
        'production': {
            'router': logging.INFO,
            'service': logging.INFO,
            'default': logging.INFO
        },
        'testing': {
            'router': logging.WARNING,
            'service': logging.WARNING,
            'default': logging.WARNING
        }
    }
    
    return config.get(environment, config['production'])


def get_logger(name: str, module_type: str = 'default') -> logging.Logger:
    """
    Get a configured logger instance with appropriate level based on environment.
    
    Args:
        name: Logger name (typically __name__)
        module_type: Type of module ('router', 'service', or 'default')
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Get appropriate logging level based on environment and module type
    level_config = _get_logging_level_config()
    logging_level = level_config.get(module_type, level_config['default'])
    
    logger.setLevel(logging_level)
    
    # Ensure the logger has a handler to output messages to the console
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # Prevent logs from being passed to the root logger to avoid duplicate output
        logger.propagate = False
        
    return logger


def configure_module_logging(module_name: str, module_type: str = 'default') -> logging.Logger:
    """
    Configure logging for a specific module with environment-based levels.
    
    Args:
        module_name: Name of the module
        module_type: Type of module ('router', 'service', or 'default')
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return get_logger(module_name, module_type)


def standardize_error_response(
    error: Exception, 
    operation: str, 
    resource_id: str = None,
    user_id: str = None
) -> HTTPException:
    """
    Standardize error responses across the application.
    
    Args:
        error: The original exception
        operation: Description of the operation that failed
        resource_id: Optional resource identifier
        user_id: Optional user identifier
        
    Returns:
        HTTPException: Standardized HTTP exception
    """
    error_msg = f"Failed to {operation}"
    if resource_id:
        error_msg += f" resource {resource_id}"
    if user_id:
        error_msg += f" for user {user_id}"
    
    # Log the original error for debugging
    logger = get_logger(__name__, 'default')
    logger.exception(f"{error_msg}: {str(error)}")
    
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=error_msg
    )


def log_operation(
    logger: logging.Logger, 
    level: str, 
    message: str, 
    **kwargs
) -> None:
    """
    Standardize logging across services.
    
    Args:
        logger: Logger instance to use
        level: Log level (debug, info, warning, error, exception)
        message: Log message
        **kwargs: Additional context for logging
    """
    log_method = getattr(logger, level.lower())
    if kwargs:
        log_method(message, extra=kwargs)
    else:
        log_method(message) 