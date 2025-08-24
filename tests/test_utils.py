import pytest

import inspect

from dashgram.utils import auto_async, wrap_event
from dashgram.enums import HandlerType


@pytest.fixture
def auto_async_function():
    @auto_async
    async def func(a: int, b: int, c: bool = False):
        if c:
            raise ValueError("test")
        return a + b
    return func


def test_auto_async_with_sync_function(auto_async_function):
    """Test auto_async with a synchronous function"""
    assert auto_async_function(1, 2) == 3
    assert auto_async_function(1, 2, c=False) == 3
    with pytest.raises(ValueError):
        auto_async_function(1, 2, c=True)


@pytest.mark.asyncio
async def test_auto_async_with_async_function(auto_async_function):
    """Test auto_async with an asynchronous function"""
    
    coro = auto_async_function(1, 2)
    assert inspect.iscoroutine(coro)

    assert await coro == 3
    assert await auto_async_function(1, 2, c=False) == 3
    with pytest.raises(ValueError):
        await auto_async_function(1, 2, c=True)


def test_wrap_event_with_update_id():
    """Test wrap_event with event that already has update_id"""
    event = {
        "update_id": 123456,
        "message": {
            "message_id": 1,
            "from": {"id": 123, "first_name": "Test", "is_bot": False},
            "chat": {"id": 456, "type": "private"},
            "date": 1640995200,
            "text": "Hello, world!"
        }
    }
    assert wrap_event(event) == event


def test_wrap_event_without_update_id():
    """Test wrap_event with event that doesn't have update_id"""
    event = {
        "message": {
            "message_id": 1,
            "from": {"id": 123, "first_name": "Test", "is_bot": False},
            "chat": {"id": 456, "type": "private"},
            "date": 1640995200,
            "text": "Hello, world!"
        }
    }
    assert wrap_event(event) == event


def test_wrap_event_with_handler_type():
    """Test wrap_event with explicit handler_type"""
    event = {
        "message_id": 1,
        "from": {"id": 123, "first_name": "Test", "is_bot": False},
        "chat": {"id": 456, "type": "private"},
        "date": 1640995200,
        "text": "Hello, world!"
    }
    assert wrap_event(event, HandlerType.MESSAGE) == {
        "update_id": -1,
        "message": event
    }