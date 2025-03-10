from datetime import datetime
import pytest

from app.services.email_service import clean_body, parse_email_message

"""
Tests for clean_body(str) : Pure function
"""

# Test clean_body
def test_clean_body():
    """Test email body cleaning functionality"""
    test_cases = [
        ( # image tags 
            "[image:logo.png]\nHello\n\nWorld\n[image:another.png]",
            "Hello\nWorld"
        ),
        ( # no clean
            "Simple text",
            "Simple text"
        ),
        ( # newLines
            "\r\n\r\nMultiple\r\nNewlines\r\n\r\n",
            "Multiple\nNewlines"
        ),
        ( # white space
            "   Leading and trailing whitespace   ",
            "Leading and trailing whitespace"
        ),
        ( # empty
            "",
            ""
        ),
        ( # broad
            "[image:test.gif]  Line1\r\n\nLine2   [image:x] ",
            "Line1\nLine2"
        )
    ]
    
    for input_text, expected in test_cases:
        assert clean_body(input_text) == expected

# Test parse_email_message
def test_parse_email_message(mock_email_message):
    """Test email message parsing"""
    uid = 12345
    raw_body = "Test email body"
    received_date = datetime.now()
    
    result = parse_email_message(uid, mock_email_message, raw_body, received_date)
    
    assert result["email_id"] == str(uid)
    assert result["subject"] == "Test Subject"
    assert result["sender"] == "sender@example.com"
    assert len(result["recipients"]) == 2
    assert "recipient1@example.com" in result["recipients"]
    assert result["body"] == "Test email body"
    assert isinstance(result["received_at"], datetime)
    assert result["category"] == "uncategorized"
    assert result["is_read"] is False

# TODO consider more edge cases / weird formatting