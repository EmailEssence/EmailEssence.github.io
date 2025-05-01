# Testing Plan

This document outlines a comprehensive testing strategy for the Email Essence backend application. It organizes testing tasks by component, focusing on both unit tests and integration tests to ensure code quality and reliability.

## Services

### Database Repositories

#### Base Repository
- [x] Test base repository CRUD operations
- [ ] Test error handling and edge cases
- [ ] Test pagination and filtering

#### Email Repository (`backend/app/services/database/email_repository.py`)
- [x] Test `find_by_email_id()`
- [x] Test `find_by_google_id()`
- [x] Test `update_by_email_and_google_id()`
- [x] Test `delete_by_email_and_google_id()`
- [x] Test `mark_as_read()`
- [ ] Test batch operations with emails
- [ ] Test search functionality

#### Summary Repository (`backend/app/services/database/summary_repository.py`)
- [ ] Test `find_by_email_id()`
- [ ] Test `find_by_google_id()`
- [ ] Test `update_by_email_id()`
- [ ] Test `delete_by_email_and_google_id()`
- [ ] Test search by keywords
- [ ] Test filtering by dates

#### User Repository (`backend/app/services/database/user_repository.py`)
- [ ] Test `find_by_email()`
- [ ] Test `find_by_google_id()`
- [ ] Test `insert_one()`
- [ ] Test `update_by_google_id()`
- [ ] Test `delete_by_email()`
- [ ] Test `find_by_id()` with both ObjectId and Google ID

#### Token Repository (`backend/app/services/database/token_repository.py`)
- [ ] Test `find_by_token()`
- [ ] Test `find_by_google_id()`
- [ ] Test `insert_one()`
- [ ] Test `upsert_token()`
- [ ] Test `update_by_google_id()`
- [ ] Test `delete_by_google_id()`

### Auth Service (`backend/app/services/auth_service.py`)
- [ ] Test `verify_user_access()`
- [ ] Test `create_authorization_url()`
- [ ] Test `get_tokens_from_code()`
- [ ] Test `get_current_user()`
- [ ] Test `refresh_access_token()`
- [ ] Test `validate_token()`
- [ ] Test `get_token_data()`
- [ ] Test `get_token_record()`
- [ ] Test error handling for expired/invalid tokens
- [ ] Test OAuth2 flow integration

### Email Service (`backend/app/services/email_service.py`)
- [ ] Test email fetching methods
- [ ] Test email parsing logic
- [ ] Test search functionality
- [ ] Test filtering by categories
- [ ] Test database operations (save, retrieve, update)
- [ ] Test `mark_email_as_read()`
- [ ] Test `delete_email()`
- [ ] Test handling of different email formats
- [ ] Test email content cleaning

### User Service (`backend/app/services/user_service.py`)
- [ ] Test `get_user_by_email()`
- [ ] Test `create_user()`
- [ ] Test `update_user()`
- [ ] Test `delete_user()`
- [ ] Test `get_preferences()`
- [ ] Test `update_preferences()`
- [ ] Test validation logic
- [ ] Test error handling

### Summarization

#### Summary Service (`backend/app/services/summarization/summary_service.py`)
- [ ] Test `save_summary()`
- [ ] Test `get_summary()`
- [ ] Test `get_summaries()`
- [ ] Test `search_by_keywords()`
- [ ] Test `save_summaries_batch()`
- [ ] Test `count_summaries()`
- [ ] Test error handling

#### Email Summarizers
- [ ] Test OpenAI Summarizer (`backend/app/services/summarization/providers/openai/openai.py`)
  - [ ] Test content preparation
  - [ ] Test API integration
  - [ ] Test response parsing
  - [ ] Test error handling
  - [ ] Test batch processing

- [ ] Test Gemini Summarizer (`backend/app/services/summarization/providers/google/google.py`)
  - [ ] Test content preparation
  - [ ] Test API integration
  - [ ] Test response parsing
  - [ ] Test error handling
  - [ ] Test batch processing

- [ ] Test Adaptive Summarizer Base Class
  - [ ] Test strategy selection
  - [ ] Test batch size optimization
  - [ ] Test metrics collection

## Routers

### Auth Router (`backend/app/routers/auth_router.py`)
- [ ] Test `/login` endpoint
- [ ] Test `/callback` endpoint
- [ ] Test `/exchange` endpoint
- [ ] Test `/token` endpoint
- [ ] Test `/refresh` endpoint
- [ ] Test `/verify` endpoint
- [ ] Test `/logout` endpoint
- [ ] Test protected route access
- [ ] Test OAuth flow

### Emails Router (`backend/app/routers/emails_router.py`)
- [ ] Test GET `/` endpoint for listing emails
- [ ] Test GET `/{email_id}` endpoint for single email
- [ ] Test PUT `/{email_id}/read` endpoint
- [ ] Test DELETE `/{email_id}` endpoint
- [ ] Test query parameters (skip, limit, sort)
- [ ] Test filtering (unread, category)
- [ ] Test search functionality
- [ ] Test error handling

### Summaries Router (`backend/app/routers/summaries_router.py`)
- [ ] Test GET `/` endpoint for listing summaries
- [ ] Test POST `/summarize` endpoint
- [ ] Test GET `/all` endpoint
- [ ] Test GET `/batch` endpoint
- [ ] Test DELETE `/{email_id}` endpoint
- [ ] Test GET `/keyword/{keyword}` endpoint
- [ ] Test GET `/recent/{days}` endpoint
- [ ] Test pagination
- [ ] Test filtering
- [ ] Test error handling

### User Router (`backend/app/routers/user_router.py`)
- [ ] Test GET `/me` endpoint
- [ ] Test GET `/preferences` endpoint
- [ ] Test PUT `/preferences` endpoint
- [ ] Test GET `/{user_id}` endpoint
- [ ] Test GET `/email/{email}` endpoint
- [ ] Test POST `/` endpoint for creating users
- [ ] Test PUT `/{user_id}` endpoint
- [ ] Test DELETE `/{user_id}` endpoint
- [ ] Test authentication requirements
- [ ] Test error handling

## Models

### Email Models (`backend/app/models/email_models.py`)
- [ ] Test validation
- [ ] Test serialization/deserialization
- [ ] Test default values
- [ ] Test helper methods

### Auth Models (`backend/app/models/auth_models.py`)
- [ ] Test TokenData validation
- [ ] Test TokenResponse validation
- [ ] Test ExchangeCodeRequest validation
- [ ] Test RefreshTokenRequest validation

### Summary Models (`backend/app/models/summary_models.py`)
- [ ] Test SummarySchema validation
- [ ] Test to_dict() method
- [ ] Test date handling

### User Models (`backend/app/models/user_models.py`)
- [ ] Test UserSchema validation
- [ ] Test PreferencesSchema validation
- [ ] Test default values

## Integration Tests

### Database Integration
- [ ] Test repository implementations with real MongoDB (marked with `@pytest.mark.mongodb`)
- [ ] Test complete CRUD cycles for each repository
- [ ] Test index creation and uniqueness constraints
- [ ] Test query performance with larger datasets
- [ ] Test error handling with network interruptions
- [ ] Test concurrent operations

### API Integration
- [ ] Test complete OAuth flow
- [ ] Test email fetching and summarization flow
- [ ] Test user creation and management flow
- [ ] Test error scenarios and recovery

### External Service Integration
- [ ] Test Google API integration
- [ ] Test OpenAI API integration
- [ ] Test Gemini API integration
- [ ] Test error handling with external services

## Configuration and Utilities

### Settings and Configuration
- [ ] Test environment variable loading
- [ ] Test default configurations
- [ ] Test dynamic configuration updates

### Prompt Management
- [ ] Test prompt templates
- [ ] Test version handling
- [ ] Test prompt formatting

## Performance Tests
- [ ] Test database query performance
- [ ] Test email batch processing
- [ ] Test summary generation performance
- [ ] Test API response times

## Security Tests
- [ ] Test authentication mechanisms
- [ ] Test authorization rules
- [ ] Test token expiration and refresh
- [ ] Test input validation and sanitization
- [ ] Test error responses (no information leakage)
