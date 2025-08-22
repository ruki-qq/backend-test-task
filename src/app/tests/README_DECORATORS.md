# Async Test Decorators

This document explains how to use the decorators in `async_client.py` to simplify async testing and avoid code repetition.

## Overview

The decorators handle:
- Database initialization
- Event loop management
- AsyncClient creation
- Proper cleanup

## Available Decorators

### 1. `@with_database_and_client`

Use this when you need both database access and an HTTP client for testing API endpoints.

**Usage:**
```python
from .async_client import with_database_and_client

@with_database_and_client
def test_something():
    async def _test(client: AsyncClient):
        # Your test logic here
        response = await client.get("/api/endpoint")
        assert response.status_code == 200
    
    return _test
```

**What it provides:**
- Database initialized and ready
- `client` parameter of type `AsyncClient`
- Automatic event loop management
- Database cleanup after test

### 2. `@with_database_setup`

Use this when you only need database access (no HTTP client needed).

**Usage:**
```python
from .async_client import with_database_setup

@with_database_setup
def test_database_operations():
    async def _test():
        # Your test logic here
    
    return _test
```

**What it provides:**
- Database initialized and ready
- Automatic event loop management
- Database cleanup after test

### 3. `@with_async_client`

Use this when you need an HTTP client but don't need database access.

**Usage:**
```python
from .async_client import with_async_client

@with_async_client
def test_api_without_db():
    async def _test(client: AsyncClient):
        # Your test logic here
        response = await client.get("/api/endpoint")
        assert response.status_code == 200
    
    return _test
```

**What it provides:**
- `client` parameter of type `AsyncClient`
- Automatic event loop management

## Helper Functions

### `create_test_client()`

Creates a test client manually if needed:

```python
from .async_client import create_test_client

async def custom_test():
    async with create_test_client() as client:
        response = await client.get("/api/endpoint")
        # ... rest of test
```

## Migration from Old Tests

### Before (with manual event loop management):
```python
def test_something():
    async def _test():
        await initialize_database()
        # ... test logic
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_test())
    finally:
        loop.close()
```

### After (with decorator):
```python
@with_database_setup
def test_something():
    async def _test():
        # ... test logic
    
    return _test
```

## Benefits

1. **Cleaner Tests**: No more boilerplate event loop code
2. **Consistent Setup**: All tests use the same database and client setup
3. **Automatic Cleanup**: Database is properly cleaned up after each test
4. **Event Loop Safety**: No more conflicts between Beanie and pytest-asyncio
5. **Maintainable**: Changes to setup logic only need to be made in one place

## Example Test Files

- `test_channels.py` - Uses `@with_database_and_client`
- `test_webhook.py` - Uses `@with_database_and_client`
- `test_simple_db.py` - Uses `@with_database_setup`

## Notes

- Always return the inner async function from your test
- The decorator will handle running it in the correct event loop
- Database is automatically dropped and recreated for each test
- All tests run in isolation with their own event loop
