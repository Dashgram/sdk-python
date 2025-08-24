import pytest
import httpx
from unittest.mock import Mock, AsyncMock
from dashgram.client import Dashgram
from datetime import datetime

import aiogram
import telegram
import telebot.types


@pytest.fixture
def sample_api_success_response():
    """Sample successful API response"""
    return httpx.Response(status_code=200, json={"status": "success", "details": "Event tracked successfully"})


@pytest.fixture
def sample_api_error_response_400():
    """Sample error API response"""
    return httpx.Response(status_code=400, json={"status": "error", "details": "Invalid request"})


@pytest.fixture
def sample_api_error_response_403():
    """Sample error API response"""
    return httpx.Response(status_code=403, json={"status": "error", "details": "Invalid credentials"})


@pytest.fixture
def mock_httpx_client(sample_api_success_response, sample_api_error_response_400, sample_api_error_response_403):
    """Mock httpx.AsyncClient for testing API calls"""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(side_effect=[sample_api_success_response, sample_api_error_response_400, sample_api_error_response_403])
    return mock_client


@pytest.fixture
def dashgram_client(mock_httpx_client):
    """Basic Dashgram client instance for testing"""
    sdk = Dashgram(project_id="test_project", access_key="test_key", origin="Python + Dashgram SDK")
    sdk._client = mock_httpx_client
    return sdk


@pytest.fixture
def sample_message_dict():
    return {
        "message_id": 1,
        "from": {"id": 123, "first_name": "Test", "is_bot": False},
        "chat": {"id": 456, "type": "private"},
        "date": 1640995200,
        "text": "Hello, world!"
    }

@pytest.fixture
def sample_event_dict(sample_message_dict):
    """Sample event dictionary for testing"""
    return {
        "update_id": 123456,
        "message": sample_message_dict
    }
    
@pytest.fixture
def sample_aiogram_message(sample_message_dict):
    """Sample aiogram.types.Message for testing"""
    return aiogram.types.Message.model_validate(sample_message_dict)


@pytest.fixture
def sample_telegram_message(sample_message_dict):
    """Sample python-telegram-bot.Message for testing"""
    return telegram.Message.de_json(sample_message_dict)


@pytest.fixture
def sample_telebot_message(sample_message_dict):
    """Sample pyTelegramBotAPI.Message for testing"""
    return telebot.types.Message.de_json(sample_message_dict)