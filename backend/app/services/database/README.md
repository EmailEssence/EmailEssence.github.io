# Database Services

This directory contains the database access layer for the application, following the Repository pattern with clear separation of concerns.

## Structure

```
database/
├── connection.py         # Database connection management
├── base_repository.py    # Generic repository implementation
├── interfaces.py         # Repository interfaces
├── email_repository.py   # Email-specific operations
├── user_repository.py    # User-specific operations
├── summary_repository.py # Summary-specific operations
└── factories.py          # Repository factory functions
```

## Key Components

### Connection Management
- `DatabaseConnection`: Manages MongoDB connections
- `get_database_connection`: Context manager for connection lifecycle
- Thread-safe connection handling
- Automatic connection cleanup

### Repository Pattern
- `BaseRepository`: Generic implementation with model conversion
- Entity-specific repositories for business logic
- Interface-based design for testability
- Factory functions for dependency injection

## Usage Examples

### Basic Connection
```python
from app.services.database import get_database_connection

async def some_function():
    async with get_database_connection() as db:
        # Use database collections
        emails = await db.emails.find_one({...})
```

### Using Repositories
```python
from app.services.database import EmailRepository, get_database_connection

async def process_emails():
    async with get_database_connection() as db:
        email_repo = EmailRepository(db.emails)
        unread = await email_repo.find_unread()
        # Process emails...
```

### Dependency Injection
```python
from fastapi import Depends
from app.services.database import get_email_repository

class EmailService:
    def __init__(self, email_repo = Depends(get_email_repository())):
        self.email_repo = email_repo
```

## Best Practices

1. **Connection Management**
   - Always use `get_database_connection` context manager
   - Never store connection instances globally
   - Handle connection errors appropriately

2. **Repository Usage**
   - Use repository interfaces for type hints
   - Inject repositories through dependency injection
   - Keep business logic in repositories

3. **Testing**
   - Mock repositories using interfaces
   - Use factory functions for test data
   - Test connection error handling

## Error Handling

The database layer provides several error handling mechanisms:
- Connection state validation
- Model conversion error handling
- MongoDB operation error propagation

## Contributing

When adding new repositories:
1. Define interface in `interfaces.py`
2. Implement in entity-specific repository
3. Add factory function in `factories.py`
4. Update `__init__.py` exports 