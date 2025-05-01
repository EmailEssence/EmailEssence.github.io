# """
# Tests for IMAP client interactions in the EmailService class.

# This module tests the functionality related to IMAP operations in the EmailService class,
# including email fetching, searching, and filtering.
# """
# import pytest
# from unittest.mock import patch, MagicMock, AsyncMock
# import os
# from datetime import datetime, timezone, timedelta
# from fastapi import HTTPException

# from app.services.email_service import EmailService

# # =============================================================================
# # IMAP Connection Tests
# # =============================================================================

# @pytest.mark.asyncio
# async def test_connect_to_imap_success(email_service, test_env):
#     """Test successfully connecting to IMAP server."""
#     # Create mock with autospec
#     with patch('imapclient.IMAPClient', autospec=True) as MockIMAPClient:
#         # Configure the mock instance
#         mock_imap = MockIMAPClient.return_value
        
#         with patch.dict(os.environ, test_env):
#             with patch.object(email_service, 'get_auth_token', return_value="test_token"):
#                 # Mock _fetch_from_imap_sync to access IMAPClient 
#                 with patch.object(email_service, '_fetch_from_imap_sync') as mock_fetch_sync:
#                     # Call fetch_from_imap to test the IMAP connection flow
#                     await email_service.fetch_from_imap(
#                         token="test_token",
#                         email_account="test@example.com"
#                     )
                    
#                     # Verify _fetch_from_imap_sync was called with correct parameters
#                     mock_fetch_sync.assert_called_once_with(
#                         "test_token", 
#                         "test@example.com", 
#                         'default', 
#                         None, 
#                         None, 
#                         'INBOX', 
#                         'ALL'
#                     )

# @pytest.mark.asyncio
# async def test_connect_to_imap_no_email_account(email_service):
#     """Test error when no email account is set."""
#     # Create mock with autospec
#     with patch('imapclient.IMAPClient', autospec=True) as MockIMAPClient:
#         # Empty environment to simulate missing EMAIL_ACCOUNT
#         with patch.dict(os.environ, {}, clear=True):
#             with patch.object(email_service, 'get_auth_token', return_value="test_token"):
#                 # Set default_email_account to None to simulate the missing environment variable
#                 email_service.default_email_account = None
                
#                 # Test the _refresh_emails_from_imap method which checks for EMAIL_ACCOUNT
#                 debug_info = {"timing": {}}
                
#                 # Call the method (the exception is caught internally)
#                 await email_service._refresh_emails_from_imap(debug_info)
                
#                 # Verify error was recorded in debug_info
#                 assert "imap_error" in debug_info
#                 assert "EMAIL_ACCOUNT environment variable not set" in debug_info["imap_error"]

# @pytest.mark.asyncio
# async def test_connect_to_imap_auth_failure(email_service, test_env):
#     """Test handling IMAP authentication failure."""
#     # Mock the entire IMAPClient module to avoid any real connections
#     with patch('app.services.email_service.IMAPClient') as MockIMAPClient:
#         # Configure the mock instance that will be created inside the method
#         mock_instance = MagicMock()
#         MockIMAPClient.return_value.__enter__.return_value = mock_instance
        
#         # Set up the oauth2_login method to raise an exception with the correct format
#         mock_instance.oauth2_login.side_effect = Exception("[AUTHENTICATIONFAILED] Invalid credentials (Failure)")
        
#         with patch.dict(os.environ, test_env):
#             with patch.object(email_service, 'get_auth_token', return_value="test_token"):
#                 # Test directly with _fetch_from_imap_sync
#                 with pytest.raises(Exception) as exc_info:
#                     email_service._fetch_from_imap_sync(
#                         token="test_token",
#                         email_account="test@example.com"
#                     )
                
#                 # Check for the actual error format that IMAPClient produces
#                 assert "Invalid credentials" in str(exc_info.value)

# # =============================================================================
# # IMAP Search Tests
# # =============================================================================

# @pytest.mark.asyncio
# async def test_search_mailbox(email_service, test_env):
#     """Test searching the mailbox using fetch_from_imap."""
#     # Create mock with autospec to get proper method signatures
#     with patch('imapclient.IMAPClient', autospec=True) as MockIMAPClient:
#         # Configure the mock instance
#         mock_imap = MockIMAPClient.return_value
#         mock_imap.search.return_value = [1, 2, 3]
        
#         with patch.dict(os.environ, test_env):
#             with patch.object(email_service, 'get_auth_token', return_value="test_token"):
#                 # Mock the low-level _fetch_from_imap_sync method to avoid IMAP calls
#                 with patch.object(email_service, '_fetch_from_imap_sync') as mock_fetch_sync:
#                     # Mock return value for the fetch method
#                     mock_fetch_sync.return_value = [
#                         {"email_id": "1", "subject": "Test Message 1"},
#                         {"email_id": "2", "subject": "Test Message 2"},
#                         {"email_id": "3", "subject": "Test Message 3"}
#                     ]
                    
#                     # Call fetch_from_imap
#                     emails = await email_service.fetch_from_imap(
#                         token="test_token",
#                         email_account="test@example.com",
#                         criteria="ALL"
#                     )
                    
#                     # Verify the method was called with correct parameters
#                     mock_fetch_sync.assert_called_once_with(
#                         "test_token", 
#                         "test@example.com", 
#                         'default', 
#                         None, 
#                         None, 
#                         'INBOX', 
#                         'ALL'
#                     )
                    
#                     # Verify the returned results
#                     assert len(emails) == 3
#                     assert emails[0]["email_id"] == "1"
#                     assert emails[2]["subject"] == "Test Message 3"

# @pytest.mark.asyncio
# async def test_search_mailbox_with_date_range(email_service, test_env):
#     """Test searching the mailbox with date range."""
#     # Create mock with autospec
#     with patch('imapclient.IMAPClient', autospec=True) as MockIMAPClient:
#         # Configure the mock instance
#         mock_imap = MockIMAPClient.return_value
#         mock_imap.search.return_value = [1, 2]
        
#         with patch.dict(os.environ, test_env):
#             with patch.object(email_service, 'get_auth_token', return_value="test_token"):
#                 # Set up date range for the test
#                 since_date = datetime.now(timezone.utc) - timedelta(days=7)
                
#                 # Expected results
#                 expected_emails = [
#                     {"email_id": "1", "subject": "Test Message 1", "received_at": datetime.now(timezone.utc)},
#                     {"email_id": "2", "subject": "Test Message 2", "received_at": datetime.now(timezone.utc)}
#                 ]
                
#                 # Mock the method to avoid real IMAP calls
#                 with patch.object(email_service, '_fetch_from_imap_sync', return_value=expected_emails) as mock_fetch:
#                     # Call fetch_from_imap - this will use our mocked _fetch_from_imap_sync
#                     emails = await email_service.fetch_from_imap(
#                         token="test_token",
#                         email_account="test@example.com",
#                         since_date=since_date
#                     )
                    
#                     # Verify the method was called with correct parameters
#                     mock_fetch.assert_called_once_with(
#                         "test_token",
#                         "test@example.com",
#                         'default',  # default user_id
#                         None,      # default limit
#                         since_date,
#                         'INBOX',   # default folder
#                         'ALL'      # default criteria
#                     )
                    
#                     # Verify results
#                     assert len(emails) == 2
#                     assert emails[0]["email_id"] == "1"
#                     assert emails[1]["subject"] == "Test Message 2"

# # =============================================================================
# # IMAP Fetch Tests
# # =============================================================================

# @pytest.mark.asyncio
# async def test_fetch_from_imap(email_service, test_env):
#     """Test fetching emails from IMAP."""
#     # Create mock with autospec to get proper method signatures
#     with patch('imapclient.IMAPClient', autospec=True) as MockIMAPClient:
#         # Configure the mock instance
#         mock_imap = MockIMAPClient.return_value
        
#         with patch.dict(os.environ, test_env):
#             with patch.object(email_service, 'get_auth_token', return_value="test_token"):
#                 # Setup test data
#                 parsed_emails = [
#                     {"email_id": "12345", "subject": "Test Subject", "sender": "test@example.com"}
#                 ]
                
#                 # Only patch run_in_threadpool, not _fetch_from_imap_sync
#                 with patch('app.services.email_service.run_in_threadpool', new_callable=AsyncMock) as mock_run:
#                     # Configure the mock to return our test data
#                     mock_run.return_value = parsed_emails
                    
#                     # Call the method
#                     emails = await email_service.fetch_from_imap(
#                         token="test_token",
#                         email_account="test@example.com",
#                         limit=1
#                     )
                    
#                     # Verify results
#                     assert len(emails) == 1
#                     assert emails[0]["email_id"] == "12345"
#                     assert emails[0]["subject"] == "Test Subject"
                    
#                     # Verify run_in_threadpool was called with a lambda function
#                     mock_run.assert_called_once()
#                     # Extract the lambda function that was passed
#                     assert callable(mock_run.call_args[0][0])

# def test_fetch_from_imap_sync(email_service, test_env):
#     """Test the synchronous implementation of IMAP fetching."""
#     # Mock the entire IMAPClient module to avoid any real connections
#     with patch('app.services.email_service.IMAPClient') as MockIMAPClient:
#         # Configure the mock instance that will be created inside the method
#         mock_instance = MagicMock()
#         MockIMAPClient.return_value.__enter__.return_value = mock_instance
        
#         # Configure the mocked instance behavior
#         mock_instance.search.return_value = [12345]
#         mock_instance.oauth2_login = MagicMock()
#         mock_instance.select_folder = MagicMock()
        
#         # Setup mock fetch data
#         fetch_data = {
#             12345: {
#                 b'RFC822': b'test email content',
#                 b'INTERNALDATE': datetime.now(timezone.utc)
#             }
#         }
#         mock_instance.fetch.return_value = fetch_data
        
#         with patch.dict(os.environ, test_env):
#             # Mock email parsing
#             with patch.object(email_service, '_parse_email_message') as mock_parse:
#                 with patch.object(email_service, '_extract_email_body') as mock_extract:
#                     with patch('email.message_from_bytes') as mock_message_from_bytes:
#                         # Configure mocks
#                         mock_message = MagicMock()
#                         mock_message_from_bytes.return_value = mock_message
#                         mock_extract.return_value = "Test Body"
#                         mock_parse.return_value = {"email_id": "12345", "subject": "Test Subject"}
                        
#                         # Call the sync method directly
#                         emails = email_service._fetch_from_imap_sync(
#                             token="test_token",
#                             email_account="test@example.com",
#                             limit=1
#                         )
                        
#                         # Verify results
#                         assert len(emails) == 1
#                         assert emails[0]["email_id"] == "12345"
                        
#                         # Verify IMAP methods were called
#                         mock_instance.oauth2_login.assert_called_once_with("test@example.com", "test_token")
#                         mock_instance.select_folder.assert_called_once_with("INBOX")
#                         mock_instance.search.assert_called_once()
#                         mock_instance.fetch.assert_called_once()

# def test_fetch_from_imap_sync_no_emails(email_service, test_env):
#     """Test fetching when no emails are found."""
#     # Mock the entire IMAPClient module to avoid any real connections
#     with patch('app.services.email_service.IMAPClient') as MockIMAPClient:
#         # Configure the mock instance that will be created inside the method
#         mock_instance = MagicMock()
#         MockIMAPClient.return_value.__enter__.return_value = mock_instance
        
#         # No emails found in search
#         mock_instance.search.return_value = []
#         mock_instance.oauth2_login = MagicMock()
#         mock_instance.select_folder = MagicMock()
#         mock_instance.fetch = MagicMock()
        
#         with patch.dict(os.environ, test_env):
#             # Call the sync method
#             emails = email_service._fetch_from_imap_sync(
#                 token="test_token",
#                 email_account="test@example.com",
#                 limit=10
#             )
            
#             # Verify results
#             assert len(emails) == 0
#             # Fetch should not be called if no emails found
#             mock_instance.fetch.assert_not_called()

# def test_fetch_from_imap_sync_with_criteria(email_service, test_env):
#     """Test fetching emails with specific search criteria."""
#     # Mock the entire IMAPClient module to avoid any real connections
#     with patch('app.services.email_service.IMAPClient') as MockIMAPClient:
#         # Configure the mock instance that will be created inside the method
#         mock_instance = MagicMock()
#         MockIMAPClient.return_value.__enter__.return_value = mock_instance
        
#         # Setup search to return one message ID
#         mock_instance.search.return_value = [12345]
#         mock_instance.oauth2_login = MagicMock()
#         mock_instance.select_folder = MagicMock()
        
#         # Setup mock fetch data
#         fetch_data = {
#             12345: {
#                 b'RFC822': b'test email content',
#                 b'INTERNALDATE': datetime.now(timezone.utc)
#             }
#         }
#         mock_instance.fetch.return_value = fetch_data
        
#         with patch.dict(os.environ, test_env):
#             # Mock email parsing
#             with patch.object(email_service, '_parse_email_message') as mock_parse:
#                 with patch.object(email_service, '_extract_email_body') as mock_extract:
#                     with patch('email.message_from_bytes') as mock_message_from_bytes:
#                         # Configure mocks
#                         mock_message = MagicMock()
#                         mock_message_from_bytes.return_value = mock_message
#                         mock_extract.return_value = "Test Body"
#                         mock_parse.return_value = {"email_id": "12345", "subject": "Test Subject"}
                        
#                         # Call with specific search criteria
#                         emails = email_service._fetch_from_imap_sync(
#                             token="test_token",
#                             email_account="test@example.com",
#                             criteria="FROM"
#                         )
                        
#                         # Verify results
#                         assert len(emails) == 1
#                         # Verify search was called with the right criteria
#                         mock_instance.search.assert_called_once()
#                         search_args = mock_instance.search.call_args[0][0]
#                         assert "FROM" in search_args 