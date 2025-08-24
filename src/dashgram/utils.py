import functools
import asyncio
import typing

from dashgram.enums import HandlerType


def auto_async(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        coro = func(*args, **kwargs)
        try:
            loop = asyncio.get_running_loop()
            return coro
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
    return wrapper


def wrap_event(event: dict, handler_type: typing.Optional[HandlerType] = None) -> dict:
    if event.get("update_id") is not None or handler_type is None:
        return event
    return {"update_id": -1, **{str(handler_type): event}}
