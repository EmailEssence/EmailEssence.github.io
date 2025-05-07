# Database Services

Database access layer implementing the Repository pattern with MongoDB.

## Structure

```
database/
├── connection.py         # MongoDB connection management
├── base_repository.py    # Generic repository implementation
├── interfaces.py         # Repository interfaces
├── email_repository.py   # Email operations
├── user_repository.py    # User operations
├── summary_repository.py # Summary operations
├── token_repository.py   # OAuth token operations
└── factories.py          # Repository factories
```

## Key Components

### Connection Management
- Thread-safe MongoDB connection handling
- Automatic connection cleanup via context manager
- Connection state validation

### Repository Pattern
- Generic `BaseRepository` with model conversion
- Entity-specific repositories
- Interface-based design
- Factory-based dependency injection

### Token Management
- OAuth token storage and retrieval
- Email-based token operations
- Token validation and updates
- Secure token deletion

## Usage

### Basic Connection
```python
from app.services.database import get_database_connection

async def some_function():
    async with get_database_connection() as db:
        emails = await db.emails.find_one({...})
```

### Using Repositories
```python
from app.services.database import EmailRepository, TokenRepository, get_database_connection

async def process_emails():
    async with get_database_connection() as db:
        email_repo = EmailRepository(db.emails)
        token_repo = TokenRepository(db.tokens)
        unread = await email_repo.find_unread()
        token = await token_repo.find_by_email("user@example.com")
```

### Dependency Injection
```python
from fastapi import Depends
from app.services.database import get_email_repository, get_token_repository

class EmailService:
    def __init__(
        self, 
        email_repo = Depends(get_email_repository()),
        token_repo = Depends(get_token_repository())
    ):
        self.email_repo = email_repo
        self.token_repo = token_repo
```

## Best Practices

1. **Connection Management**
   - Use `get_database_connection` context manager
   - Avoid global connection instances
   - Handle connection errors

2. **Repository Usage**
   - Use repository interfaces
   - Inject repositories via DI
   - Keep business logic in repositories

3. **Token Management**
   - Use email-based token operations
   - Implement proper token validation
   - Secure token storage and deletion

4. **Testing**
   - Mock repositories using interfaces
   - Use factory functions for test data

## Contributing

When adding new repositories:
1. Define interface in `interfaces.py`
2. Implement in entity-specific repository
3. Add factory function in `factories.py`
4. Update `__init__.py` exports 