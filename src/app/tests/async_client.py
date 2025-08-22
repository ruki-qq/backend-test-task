import asyncio
import functools
from typing import Callable, Any
from httpx import AsyncClient, ASGITransport
from core.database import initialize_database
from app.app import app


def with_async_client(func: Callable) -> Callable:
    """
    Decorator that creates an async client and manages the event loop for tests.
    
    This decorator:
    1. Initializes the database
    2. Creates an AsyncClient with the test app
    3. Manages the event loop properly
    4. Passes the client to the test function
    
    Usage:
        @with_async_client
        def test_something():
            async def _test(client: AsyncClient):
                # Your test logic here
                response = await client.get("/api/endpoint")
                assert response.status_code == 200
            
            return _test
    """
    
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get the inner async function
        inner_func = func(*args, **kwargs)
        
        # Create a new event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the async test
            return loop.run_until_complete(inner_func)
        finally:
            loop.close()
    
    return wrapper


def create_test_client() -> AsyncClient:
    """
    Helper function to create a test client.
    Use this inside your async test functions.
    """
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        timeout=30.0,
    )


def with_database_and_client(func: Callable) -> Callable:
    """
    Decorator that handles database initialization and async client creation.
    
    This decorator:
    1. Initializes the database
    2. Creates an AsyncClient with the test app
    3. Manages the event loop properly
    4. Passes the client to the test function
    5. Automatically cleans up the database after each test
    
    Usage:
        @with_database_and_client
        def test_something():
            async def _test(client: AsyncClient):
                # Your test logic here
                response = await client.get("/api/endpoint")
                assert response.status_code == 200
            
            return _test
    """
    
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get the inner async function
        inner_func = func(*args, **kwargs)
        
        # Create a new event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def setup_and_run():
            # Initialize database
            await initialize_database()
            
            # Create test client and run the test
            async with create_test_client() as client:
                return await inner_func(client)
        
        try:
            # Run the async test
            return loop.run_until_complete(setup_and_run())
        finally:
            loop.close()
    
    return wrapper


def with_database_setup(func: Callable) -> Callable:
    """
    Decorator that only handles database initialization.
    Use this when you need to create your own client or don't need a client.
    
    Usage:
        @with_database_setup
        def test_something():
            async def _test():
                # Your test logic here
            
            return _test
    """
    
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get the inner async function
        inner_func = func(*args, **kwargs)
        
        # Create a new event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def setup_and_run():
            # Initialize database
            await initialize_database()
            
            # Run the test
            return await inner_func()
        
        try:
            # Run the async test
            return loop.run_until_complete(setup_and_run())
        finally:
            loop.close()
    
    return wrapper