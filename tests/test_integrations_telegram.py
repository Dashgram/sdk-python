import pytest
from unittest.mock import Mock, AsyncMock

from dashgram.integrations.telegram import object_to_dict, bind
from dashgram.enums import HandlerType

from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ExtBot
import telegram


from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.strings import TextEncoding
from telegram._utils.types import ODVInput
from telegram.error import BadRequest, RetryAfter, TimedOut
from telegram.request import BaseRequest, HTTPXRequest, RequestData

from typing import Optional


class OfflineRequest(BaseRequest):
    """This Request class disallows making requests to Telegram's servers.
    Use this in tests that should not depend on the network.
    """

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    @property
    def read_timeout(self):
        return 1

    def __init__(self, *args, **kwargs):
        pass

    async def do_request(
        self,
        url: str,
        method: str,
        request_data: Optional[RequestData] = None,
        read_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        write_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        connect_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        pool_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
    ) -> tuple[int, bytes]:
        pytest.fail("OfflineRequest: Network access disallowed in this test")

def _get_bot_user():
    """Used to return a mock user in bot.get_me(). This saves API calls on every init."""
    user_id = 123
    first_name = "Test"
    username = "test"
    return telegram.User(
        user_id,
        first_name,
        is_bot=True,
        username=username,
        can_join_groups=True,
        can_read_all_group_messages=False,
        supports_inline_queries=True,
    )


async def _mocked_get_me(bot):
    if bot._bot_user is None:
        bot._bot_user = _get_bot_user()
    return bot._bot_user


class PytestExtBot(ExtBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Makes it easier to work with the bot in tests
        self._unfreeze()

    # Here we override get_me for caching because we don't want to call the API repeatedly in tests
    async def get_me(self, *args, **kwargs):
        return await _mocked_get_me(self)
    
    
def make_bot(bot_info=None, offline: bool = True, **kwargs):
    """
    Tests are executed on tg.ext.ExtBot, as that class only extends the functionality of tg.bot
    """
    token = "1234567:tgsgges"

    request_class = OfflineRequest

    return PytestExtBot(
        token=token,
        private_key=None,
        request=request_class(8),
        get_updates_request=request_class(1),
        **kwargs,
    )


def test_object_to_dict_with_update_object(sample_telegram_message):
    """Test object_to_dict with telegram Update object"""
    update = telegram.Update(update_id=1, message=sample_telegram_message)
    result = object_to_dict(update)
    assert result == {'update_id': 1, 'message': {'channel_chat_created': False, 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'text': 'Hello, world!', 'chat': {'id': 456, 'type': "private"}, 'date': 1640995200, 'message_id': 1, 'from': {'first_name': 'Test', 'id': 123, 'is_bot': False}}}


def test_object_to_dict_with_message_object(sample_telegram_message):
    """Test object_to_dict with telegram Message object"""
    result = object_to_dict(sample_telegram_message)
    assert result == sample_telegram_message.to_dict()


def test_object_to_dict_import_error(mocker, sample_telegram_message):
    """Test object_to_dict when telegram is not installed"""
    mocker.patch("dashgram.integrations.telegram.telegram", False)
    with pytest.raises(ImportError):
        object_to_dict(sample_telegram_message)


def test_bind_function(dashgram_client):
    """Test bind function with telegram available"""
    mock_app = Mock()
    
    bind(dashgram_client, mock_app)
    
    # Verify handler was added
    mock_app.add_handler.assert_called_once()
    
    # Get the handler that was added
    handler_call = mock_app.add_handler.call_args
    handler = handler_call[0][0]
    
    # Verify it's the correct handler type
    assert handler.callback is not None
    assert handler.block is False


def test_bind_function_import_error(mocker):
    """Test bind function when telegram is not installed"""
    mocker.patch("dashgram.integrations.telegram.telegram", False)
    with pytest.raises(ImportError):
        bind(Mock(), Mock())


@pytest.mark.asyncio
async def test_full_telegram_integration_workflow(dashgram_client, sample_telegram_message):
    """Test complete telegram integration workflow"""
    dashgram_client.track_event = AsyncMock()
    mock_handler = AsyncMock()
    
    update = telegram.Update(update_id=1, message=sample_telegram_message)
    
    app = Application.builder().bot(make_bot(offline=True)).build()
    
    bind(dashgram_client, app, block=True)
    
    # Create a test handler
    async def message_handler(update, context):
        await mock_handler(update.message)
    
    # Add our test handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    async with app:
        await app.process_update(update)
    
    # Verify tracking was called
    dashgram_client.track_event.assert_awaited_once_with(update)
    mock_handler.assert_awaited_once_with(update.message)


@pytest.mark.asyncio
async def test_telegram_track_update(dashgram_client, sample_telegram_message, sample_message_dict, mock_httpx_client):
    """Test telegram track_event"""
    update = telegram.Update(update_id=1, message=sample_telegram_message)
    
    res = await dashgram_client.track_event(update)
    assert res is True
    
    mock_httpx_client.post.assert_awaited_once_with(
        "track",
        json={
            "origin": "Python + Dashgram SDK",
            "updates": [
                {'update_id': 1, 'message': {'channel_chat_created': False, 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'text': 'Hello, world!', 'chat': {'id': 456, 'type': "private"}, 'date': 1640995200, 'message_id': 1, 'from': {'first_name': 'Test', 'id': 123, 'is_bot': False}}}
            ],
        },
    )
