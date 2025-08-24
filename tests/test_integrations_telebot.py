import pytest
from unittest.mock import Mock, AsyncMock

from dashgram.integrations.telebot import object_to_dict, bind, TrackMiddleware, AsyncTrackMiddleware
from dashgram.enums import HandlerType

import telebot.types
import telebot.async_telebot


@pytest.fixture
def sample_telebot_update(sample_telebot_message):
    return telebot.types.Update(update_id=1, message=sample_telebot_message, edited_message=None, channel_post=None, edited_channel_post=None, inline_query=None, chosen_inline_result=None, callback_query=None, shipping_query=None, pre_checkout_query=None, poll=None, poll_answer=None, my_chat_member=None, chat_member=None, chat_join_request=None, message_reaction=None, message_reaction_count=None, removed_chat_boost=None, chat_boost=None, business_connection=None, business_message=None, edited_business_message=None, deleted_business_messages=None, purchased_paid_media=None)


def test_object_to_dict_with_update_object(sample_message_dict, sample_telebot_update):
    """Test object_to_dict with telebot Update object"""
    update = sample_telebot_update
    result = object_to_dict(update)
    assert result == {
        "update_id": 1,
        "message": sample_message_dict
    }


def test_object_to_dict_with_message_object(sample_telebot_message):
    """Test object_to_dict with telebot Message object"""
    result = object_to_dict(sample_telebot_message, HandlerType.MESSAGE)
    assert result == {
        "update_id": -1,
        "message": sample_telebot_message.json
    }


def test_object_to_dict_without_handler_type(sample_telebot_message):
    """Test object_to_dict without handler_type"""
    with pytest.raises(TypeError):
        object_to_dict(sample_telebot_message)


def test_object_to_dict_import_error(mocker, sample_telebot_message):
    """Test object_to_dict when telebot is not installed"""
    mocker.patch("dashgram.integrations.telebot.telebot", False)
    with pytest.raises(ImportError):
        object_to_dict(sample_telebot_message)


def test_bind_function_sync(dashgram_client):
    """Test bind function with sync telebot"""
    mock_bot = Mock()
    mock_bot.__class__ = telebot.TeleBot # type: ignore
    
    bind(dashgram_client, mock_bot)
    
    # Verify middleware was set up
    mock_bot.setup_middleware.assert_called_once()
    
    # Get the middleware that was added
    middleware = mock_bot.setup_middleware.call_args[0][0]
    assert isinstance(middleware, TrackMiddleware)
    assert middleware.sdk == dashgram_client


def test_bind_function_async(dashgram_client):
    """Test bind function with async telebot"""
    mock_bot = Mock()
    mock_bot.__class__ = telebot.async_telebot.AsyncTeleBot # type: ignore
    
    bind(dashgram_client, mock_bot)
    
    # Verify middleware was set up
    mock_bot.setup_middleware.assert_called_once()
    
    # Get the middleware that was added
    middleware = mock_bot.setup_middleware.call_args[0][0]
    assert isinstance(middleware, AsyncTrackMiddleware)
    assert middleware.sdk == dashgram_client


def test_bind_function_import_error(mocker):
    """Test bind function when telebot is not installed"""
    mocker.patch("dashgram.integrations.telebot.telebot", False)
    with pytest.raises(ImportError):
        bind(Mock(), Mock())


def test_track_middleware_sync(dashgram_client, sample_telebot_message):
    """Test sync TrackMiddleware"""
    dashgram_client.track_event = Mock()
    
    middleware = TrackMiddleware(dashgram_client)
    
    # Test post_process_message
    middleware.post_process_message(sample_telebot_message, {}, None)
    
    # Verify track_event was called with correct parameters
    dashgram_client.track_event.assert_called_once_with(sample_telebot_message, HandlerType.MESSAGE)


@pytest.mark.asyncio
async def test_track_middleware_async(dashgram_client, sample_telebot_message):
    """Test async TrackMiddleware"""
    dashgram_client.track_event = AsyncMock()
    
    middleware = AsyncTrackMiddleware(dashgram_client)
    
    # Test post_process_message
    await middleware.post_process_message(sample_telebot_message, {}, None)
    
    dashgram_client.track_event.assert_awaited_once_with(sample_telebot_message, HandlerType.MESSAGE)


def test_full_telebot_sync_integration_workflow(dashgram_client, sample_telebot_update, sample_telebot_message):
    """Test complete telebot integration workflow"""
    dashgram_client.track_event = Mock()
    print(dashgram_client.track_event)
    mock_handler = Mock()
    
    # Create sync bot
    bot = telebot.TeleBot("test_token", use_class_middlewares=True, validate_token=False, threaded=False)
    
    # Bind the middleware
    bind(dashgram_client, bot)
    
    # Create a test handler
    @bot.message_handler()
    def message_handler(message):
        mock_handler(message)
    
    bot.process_new_updates([sample_telebot_update])
    
    dashgram_client.track_event.assert_called_once_with(sample_telebot_message, HandlerType.MESSAGE)
    
    mock_handler.assert_called_once_with(sample_telebot_message)
    

@pytest.mark.asyncio
async def test_full_telebot_async_integration_workflow(dashgram_client, sample_telebot_update, sample_telebot_message):
    """Test complete telebot integration workflow"""
    dashgram_client.track_event = AsyncMock()
    mock_handler = AsyncMock()
    
    # Create async bot
    bot = telebot.async_telebot.AsyncTeleBot("test_token", validate_token=False)
    
    # Bind the middleware
    bind(dashgram_client, bot)
    
    # Create a test handler
    @bot.message_handler()
    async def message_handler(message):
        await mock_handler(message)
    
    await bot.process_new_updates([sample_telebot_update])
    
    dashgram_client.track_event.assert_awaited_once_with(sample_telebot_message, HandlerType.MESSAGE)
    
    mock_handler.assert_awaited_once()
    assert mock_handler.call_args[0][0] == sample_telebot_update.message
    


@pytest.mark.asyncio
async def test_telebot_track_update(dashgram_client, sample_telebot_message, sample_message_dict, mock_httpx_client, sample_telebot_update):
    """Test telebot track_event with update"""
    
    res = await dashgram_client.track_event(sample_telebot_update)
    assert res is True
    
    mock_httpx_client.post.assert_awaited_once_with(
        "track",
        json={
            "origin": "Python + Dashgram SDK",
            "updates": [
                {
                    "update_id": 1,
                    "message": sample_message_dict
                }
            ],
        },
    )


@pytest.mark.asyncio
async def test_telebot_track_message(dashgram_client, sample_telebot_message, sample_message_dict, mock_httpx_client):
    """Test telebot track_event with message and handler type"""
    res = await dashgram_client.track_event(sample_telebot_message, HandlerType.MESSAGE)
    assert res is True
    
    mock_httpx_client.post.assert_awaited_once_with(
        "track",
        json={
            "origin": "Python + Dashgram SDK",
            "updates": [
                {
                    "update_id": -1,
                    "message": sample_message_dict
                }
            ],
        },
    )
