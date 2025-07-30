import typing

from dashgram.integrations import aiogram, telegram, telebot
from dashgram.enums import HandlerType

_MAPPING = {
    "aiogram": aiogram.object_to_dict,
    "telegram": telegram.object_to_dict,
    "telebot": telebot.object_to_dict,
    "telethon": None,
}

def get_package(obj) -> typing.Optional[str]:
    package = obj.__module__.split(".")[0]
    if package not in _MAPPING:
        return None
    return package

def determine_object_source(obj):
    package = get_package(obj)
    return _MAPPING.get(package)


def object_to_dict(obj, handler_type: typing.Optional[HandlerType] = None):
    conv = determine_object_source(obj)
    if conv is None:
        return {}

    return conv(obj, handler_type)

