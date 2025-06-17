import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.models import EmailSchema
from app.services.summarization.providers.openrouter.openrouter import OpenRouterEmailSummarizer, OpenRouterBackend
from app.services.summarization.providers.openrouter.prompts import OpenRouterPromptManager
from app.utils.config import PromptVersion

@pytest.fixture
def email_schema_fixture():
    """Fixture for a sample EmailSchema."""
    return EmailSchema(
        email_id="test_email_id",
        google_id="test_google_id",
        sender="sender@example.com",
        recipients=["recipient@example.com"],
        subject="Test Subject",
        body="This is a test email body.",
        received_at="2023-01-01T00:00:00Z"
    )

@pytest.fixture
def summarizer():
    """Fixture for OpenRouterEmailSummarizer."""
    return OpenRouterEmailSummarizer(api_key="test_api_key")

@pytest.mark.asyncio
async def test_summarizer_prepare_content(summarizer: OpenRouterEmailSummarizer, email_schema_fixture: EmailSchema):
    """Test that prepare_content formats the email correctly."""
    content = await summarizer.prepare_content(email_schema_fixture)
    assert "From: sender@example.com" in content
    assert "Subject: Test Subject" in content
    assert "Body:\nThis is a test email body." in content

@pytest.mark.asyncio
@patch('app.services.summarization.providers.openrouter.openrouter.AsyncOpenAI')
async def test_backend_generate_summary_success(mock_async_openai, email_schema_fixture: EmailSchema):
    """Test successful summary generation with valid JSON response."""
    # Mock the OpenAI client
    mock_client = MagicMock()
    mock_async_openai.return_value = mock_client

    # Mock the response from chat.completions.create
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = '{"summary": "This is a test summary.", "keywords": ["test", "email"]}'
    
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

    # Setup backend
    prompt_manager = OpenRouterPromptManager(prompt_version=PromptVersion.V1)
    backend = OpenRouterBackend(api_key="test_key", prompt_manager=prompt_manager)
    
    # Run the method
    summary, keywords = await backend.generate_summary("test content")

    # Assertions
    assert summary == "This is a test summary."
    assert keywords == ["test", "email"]
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs['model'] is not None
    assert call_args.kwargs['messages'] is not None


@pytest.mark.asyncio
@patch('app.services.summarization.providers.openrouter.openrouter.AsyncOpenAI')
async def test_backend_generate_summary_json_error(mock_async_openai):
    """Test summary generation with a non-JSON response."""
    # Mock the OpenAI client
    mock_client = MagicMock()
    mock_async_openai.return_value = mock_client

    # Mock a non-JSON response
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = 'This is just a plain text summary.'
    
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

    # Setup backend
    prompt_manager = OpenRouterPromptManager(prompt_version=PromptVersion.V1)
    backend = OpenRouterBackend(api_key="test_key", prompt_manager=prompt_manager)
    
    # Run the method
    summary, keywords = await backend.generate_summary("test content")

    # Assertions for fallback behavior
    assert summary == "This is just a plain text summary."
    assert keywords == []
    mock_client.chat.completions.create.assert_called_once() 