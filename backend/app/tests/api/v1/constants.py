# tests/api/v1/constants.py
"""
Test constants for API v1 testing
"""

EMAIL_ENDPOINT = "/emails"
SUMMARY_ENDPOINT = "/summaries"
AUTH_ENDPOINT = "/auth"

TEST_EMAIL_DATA = {
    "from_": "test@example.com",
    "subject": "Test Subject",
    "body": "Test Body"
}

TEST_SUMMARY_DATA = {
    "email_id": 1,
    "summary": "This is a test summary"
}