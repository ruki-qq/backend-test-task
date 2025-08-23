import asyncio
import functools
from typing import Any, Callable

from httpx import ASGITransport, AsyncClient

from app.app import app
from core.database import initialize_database
from core.database.models.chat_bot import ChatBot


def create_test_client() -> AsyncClient:
    """
    Функция для создания клиентов для тестов.
    """
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        timeout=30.0,
    )


def with_database_and_client(func: Callable) -> Callable:
    """
    Декоратор, который инициализирует БД и создает асинхронного клиента.

    Использование:
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
        inner_func = func(*args, **kwargs)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def setup_and_run():
            await initialize_database()
            chat_bot = ChatBot(name="TestBot", secret_token="test_token_123")
            await chat_bot.insert()
            kwargs["chat_bot_id"] = str(chat_bot.id)
            async with create_test_client() as client:
                return await inner_func(client, **kwargs)

        try:
            return loop.run_until_complete(setup_and_run())
        finally:
            loop.close()

    return wrapper


def with_database_setup(func: Callable) -> Callable:
    """
    Декоратор, инициализирующий БД.
    Используется, если необходимо создать своего клиента или клиент не нужен.

    Использование:
        @with_database_setup
        def test_something():
            async def _test():
                # Your test logic here

            return _test
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        inner_func = func(*args, **kwargs)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def setup_and_run():
            await initialize_database()
            chat_bot = ChatBot(name="SimpleTestBot", secret_token="simple_token_123")
            await chat_bot.insert()
            return await inner_func(chat_bot=chat_bot)

        try:
            return loop.run_until_complete(setup_and_run())
        finally:
            loop.close()

    return wrapper
