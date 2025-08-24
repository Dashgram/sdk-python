import pytest
from unittest.mock import Mock, AsyncMock

from dashgram.integrations.aiogram import object_to_dict, rename_key, bind
from dashgram.enums import HandlerType

import aiogram


def test_object_to_dict_with_update_object(sample_aiogram_message):
    """Test object_to_dict with aiogram Update object"""
    update = aiogram.types.Update(update_id=1, message=sample_aiogram_message)
    result = object_to_dict(update)
    assert result == {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": 123, "first_name": "Test", "is_bot": False},
            "chat": {"id": 456, "type": "private"},
            "date": 1640995200,
            "text": "Hello, world!"
        }
    }


def test_object_to_dict_with_message_object(sample_aiogram_message):
    """Test object_to_dict with aiogram Message object"""
    with pytest.raises(TypeError):
        object_to_dict(sample_aiogram_message)


def test_object_to_dic_with_message_object_and_handler_type(sample_aiogram_message):
    """Test object_to_dict with explicit handler_type"""
    result = object_to_dict(sample_aiogram_message, HandlerType.MESSAGE)
    assert result == {
        "update_id": -1,
        "message": {
            "message_id": 1,
            "from": {"id": 123, "first_name": "Test", "is_bot": False},
            "chat": {"id": 456, "type": "private"},
            "date": 1640995200,
            "text": "Hello, world!"
        }
    }


def test_object_to_dict_import_error(mocker, sample_aiogram_message):
    """Test object_to_dict when aiogram is not installed"""
    mocker.patch("dashgram.integrations.aiogram.aiogram", False)
    with pytest.raises(ImportError):
        object_to_dict(sample_aiogram_message)


def test_rename_key_basic_functionality():
    """Test basic rename_key functionality"""
    test_dict = {"old_key": "value1", "other_key": "value2"}
    result = rename_key(test_dict, "old_key", "new_key")
    assert result == {"new_key": "value1", "other_key": "value2"}
    assert "old_key" not in result
    assert "new_key" in result


def test_rename_key_with_nested_dict():
    """Test rename_key with nested dictionary"""
    test_dict = {"old_key": "value1", "other_key": "value2", "nested": {"old_key": "nested_value", "other_key": "value3"}}
    result = rename_key(test_dict, "old_key", "new_key")
    assert result == {"new_key": "value1", "other_key": "value2", "nested": {"new_key": "nested_value", "other_key": "value3"}}
    assert "old_key" not in result
    assert "new_key" in result
    assert "old_key" not in result["nested"]
    assert "new_key" in result["nested"]


def test_bind_function(dashgram_client, mocker):
    """Test bind function with aiogram available"""
    mock_dp = Mock()
    
    mock_register = Mock()
    mock_dp.update.outer_middleware.return_value = mock_register
    
    bind(dashgram_client, mock_dp)
    mock_register.assert_called_once()


def test_bind_function_import_error(mocker):
    """Test bind function when aiogram is not installed"""
    mocker.patch("dashgram.integrations.aiogram.aiogram", False)
    with pytest.raises(ImportError):
        bind(Mock(), Mock())


@pytest.mark.asyncio
async def test_full_aiogram_integration_workflow(dashgram_client, sample_aiogram_message):
    """Test complete aiogram integration workflow"""
    dashgram_client.track_event = AsyncMock()
    mock_handler = AsyncMock()
    
    dp = aiogram.Dispatcher()
    
    @dp.message()
    async def message_handler(message: aiogram.types.Message):
        await mock_handler(message)
    
    bind(dashgram_client, dp)
    
    update = aiogram.types.Update(update_id=1, message=sample_aiogram_message)
    
    await dp.feed_update(Mock(), update)
    
    dashgram_client.track_event.assert_awaited_once()
    assert dashgram_client.track_event.call_args[0][0].model_dump() == update.model_dump()
    
    mock_handler.assert_awaited_once()
    assert mock_handler.call_args[0][0].model_dump() == sample_aiogram_message.model_dump()
    
    
@pytest.mark.asyncio
async def test_aiogram_track_update(dashgram_client, sample_aiogram_message, sample_message_dict, mock_httpx_client):
    """Test aiogram track_event"""
    update = aiogram.types.Update(update_id=1, message=sample_aiogram_message)
    
    res = await dashgram_client.track_event(update)
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
async def test_aiogram_track_handler(dashgram_client, sample_aiogram_message, sample_message_dict, mock_httpx_client):
    """Test aiogram track_event"""
    res = await dashgram_client.track_event(sample_aiogram_message, HandlerType.MESSAGE)
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
