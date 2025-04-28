# """
# Tests for email parsing methods in the EmailService class.

# This module tests the email parsing functionality of the EmailService class,
# focusing on methods that extract and process email content.
# """
# import pytest
# from unittest.mock import patch, MagicMock
# import email
# from datetime import datetime, timezone

# from app.services.email_service import EmailService

# # =============================================================================
# # Email Field Parsing Tests
# # =============================================================================

# def test_clean_body_plain_text(email_service):
#     """Test cleaning a plain text email body."""
#     body = "Hello\r\n\r\n[image:logo.png]\r\nTest\r\n\r\n"
#     cleaned = email_service._clean_body(body)
    
#     assert cleaned == "Hello\nTest"
#     assert "[image:" not in cleaned
#     assert "\r\n\r\n" not in cleaned

# def test_clean_body_html(email_service):
#     """Test cleaning an HTML email body."""
#     body = "<div>Hello</div>\r\n\r\n[image:logo.png]\r\n<div>Test</div>\r\n\r\n"
#     cleaned = email_service._clean_body(body, is_html=True)
    
#     assert cleaned == "<div>Hello</div>\n<div>Test</div>"
#     assert "[image:" not in cleaned
#     assert "\r\n\r\n" not in cleaned

# def test_decode_email_field(email_service):
#     """Test decoding an email field."""
#     # Test with plain ASCII
#     result = email_service._decode_email_field("Hello")
#     assert result == "Hello"
    
#     # Test with None value
#     result = email_service._decode_email_field(None, default="Default")
#     assert result == "Default"
    
#     # Test with empty string
#     result = email_service._decode_email_field("", default="Default")
#     assert result == "Default"

# # =============================================================================
# # Email Body Extraction Tests
# # =============================================================================

# def test_extract_email_body_plain(email_service, mock_email_message):
#     """Test extracting the body from a plain text email."""
#     with patch.object(email_service, '_clean_body', return_value="Cleaned body"):
#         body = email_service._extract_email_body(mock_email_message)
        
#         assert body == "Cleaned body"
#         email_service._clean_body.assert_called_once()

# def test_extract_email_body_multipart(email_service, multipart_message):
#     """Test extracting the body from a multipart email with text and HTML."""
#     def mock_clean(content, is_html=False):
#         return f"Cleaned {'HTML' if is_html else 'text'}: {content}"
    
#     with patch.object(email_service, '_clean_body', side_effect=mock_clean):
#         body = email_service._extract_email_body(multipart_message)
        
#         # Should prefer HTML over plain text
#         assert "Cleaned HTML" in body or "Cleaned text" in body

# def test_extract_email_body_text_only_multipart(email_service, multipart_message):
#     """Test extracting body from multipart with only text (no HTML)."""
#     # Remove HTML part from the payload
#     html_part = multipart_message.get_payload.return_value[1]
#     html_part.get_content_type.return_value = "something/else"
    
#     def mock_clean(content, is_html=False):
#         return f"Cleaned {'HTML' if is_html else 'text'}: {content}"
    
#     with patch.object(email_service, '_clean_body', side_effect=mock_clean):
#         body = email_service._extract_email_body(multipart_message)
        
#         # Should use plain text since no HTML is available
#         assert "Cleaned text" in body

# # =============================================================================
# # Email Message Parsing Tests
# # =============================================================================

# def test_parse_email_message(email_service, mock_email_message):
#     """Test parsing an email message into schema-compliant format."""
#     uid = 12345
#     body = "This is the email body"
#     received_date = datetime(2023, 3, 17, 12, 0, 0, tzinfo=timezone.utc)
    
#     with patch.object(email_service, '_decode_email_field', side_effect=lambda x, default="": x or default):
#         result = email_service._parse_email_message(uid, mock_email_message, body, received_date)
        
#         # Check basic fields
#         assert result["email_id"] == "12345"
#         assert result["sender"] == "Test Sender <test@example.com>"
#         assert "recipient@example.com" in result["recipients"]
#         assert result["subject"] == "Test Subject"
#         assert result["body"] == body
#         assert result["received_at"] == received_date 