# python-telegram-bot integration
import typing
import warnings

try:
    from telegram.ext import BaseHandler, Application
    from telegram import Update
    telegram = True
except ImportError:
    telegram = False
    Application = typing.Any
    Update = typing.Any
    BaseHandler = object


def object_to_dict(obj, *args, **kwargs) -> dict:
    return obj.to_dict()


def bind(sdk, app: Application, group: int = 1):
    if not telegram:
        raise ImportError("python-telegram-bot is not installed")

    class UpdateHandler(BaseHandler):
        def check_update(self, update: Update):
            return True

    async def track_update(update: Update, context) -> None:
        try:
            await sdk.track_event(update)
        except Exception as exc:
            warnings.warn(f"{type(exc).__name__}: {exc}")

    app.add_handler(UpdateHandler(track_update, block=False), group=group)