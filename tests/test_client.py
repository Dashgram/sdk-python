import pytest

from unittest.mock import Mock

from dashgram import Dashgram, __version__
from dashgram.enums import HandlerType
from dashgram.exceptions import InvalidCredentials, DashgramApiError


def test_client_initialization_with_required_params(mocker):
    """Test client initialization with required parameters"""
    mocker.patch("dashgram.client.resolve_framework", return_value=None)
    
    sdk = Dashgram(project_id=123, access_key="test")
    assert sdk.project_id == 123
    assert sdk.access_key == "test"
    assert sdk.api_url == "https://api.dashgram.io/v1/123"
    assert sdk.origin == f"Python + Dashgram SDK v{__version__}"


def test_client_initialization_with_custom_api_url():
    """Test client initialization with custom API URL"""
    sdk = Dashgram(project_id=123, access_key="test", api_url="https://test-server.com/v2")
    assert sdk.api_url == "https://test-server.com/v2/123"


def test_client_initialization_with_custom_origin():
    """Test client initialization with custom origin"""
    sdk = Dashgram(project_id=123, access_key="test", origin="test")
    assert sdk.origin == "test"


def test_client_initialization_with_framework_detection(mocker):
    """Test client initialization with framework auto-detection"""
    mocker.patch("dashgram.client.resolve_framework", return_value="test")
    sdk = Dashgram(project_id=123, access_key="test")
    assert sdk.origin == f"Python + Dashgram SDK v{__version__} + test"


def test_client_httpx_client_initialization():
    """Test that httpx.AsyncClient is properly initialized"""
    sdk = Dashgram(project_id=123, access_key="test")
    assert str(sdk._client.base_url) == "https://api.dashgram.io/v1/123/"
    assert sdk._client.headers["Authorization"] == "Bearer test"


@pytest.mark.asyncio
async def test_client_request_without_suppress_exceptions(dashgram_client, sample_event_dict):
    res = await dashgram_client.track_event(sample_event_dict, suppress_exceptions=False)
    
    assert res is True
    
    with pytest.raises(DashgramApiError) as exc_info:
        await dashgram_client.track_event(sample_event_dict, suppress_exceptions=False)
    assert exc_info.value.status_code == 400
    assert exc_info.value.details == "Invalid request"
    
    with pytest.raises(InvalidCredentials) as exc_info:
        await dashgram_client.track_event(sample_event_dict, suppress_exceptions=False)


@pytest.mark.asyncio
async def test_track_event_with_suppress_exceptions(dashgram_client, sample_event_dict, mocker):
    """Test track_event with 400 API error (DashgramApiError)"""
    mock_warn = mocker.patch("dashgram.client.warnings.warn", return_value=None)
    
    res1 = await dashgram_client.track_event(sample_event_dict, suppress_exceptions=True)
    
    res2 = await dashgram_client.track_event(sample_event_dict, suppress_exceptions=True)
    mock_warn.assert_called_with("DashgramApiError: Invalid request - Status Code: 400")
    
    res3 = await dashgram_client.track_event(sample_event_dict, suppress_exceptions=True)
    
    mock_warn.assert_called_with("InvalidCredentials: Invalid project_id or access_key")
    
    assert [res1, res2, res3] == [True, False, False]


@pytest.mark.asyncio
async def test_track_event_with_dict_input(dashgram_client, sample_event_dict, mocker):
    """Test track_event with dictionary input"""
    mock_wrap_event = mocker.patch("dashgram.client.wrap_event", return_value=sample_event_dict)
    
    await dashgram_client.track_event({"test": "test"}, HandlerType.MESSAGE)
    
    mock_wrap_event.assert_called_once_with({"test": "test"}, HandlerType.MESSAGE)


@pytest.mark.asyncio
async def test_track_event_with_object_input(dashgram_client, sample_aiogram_message, sample_event_dict, mocker):
    """Test track_event with object input"""
    mock_object_to_dict = mocker.patch("dashgram.client.object_to_dict", return_value=sample_event_dict)
    
    await dashgram_client.track_event(sample_aiogram_message, HandlerType.MESSAGE)
    
    mock_object_to_dict.assert_called_once_with(sample_aiogram_message, HandlerType.MESSAGE)


@pytest.mark.asyncio
async def test_track_event(mock_httpx_client, dashgram_client, sample_event_dict):
    """Test track_event with successful API response"""
    res = await dashgram_client.track_event(sample_event_dict, suppress_exceptions=False)
    
    assert res is True
    
    mock_httpx_client.post.assert_awaited_once_with(
        "track",
        json={
            "origin": "Python + Dashgram SDK",
            "updates": [sample_event_dict],
        },
    )
        
        
@pytest.mark.asyncio
async def test_invited_by(mock_httpx_client, dashgram_client):
    """Test invited_by with successful API response"""
    res = await dashgram_client.invited_by(user_id=123, invited_by=456)
    assert res is True
    
    mock_httpx_client.post.assert_awaited_once_with(
        "invited_by",
        json={"user_id": 123, "invited_by": 456, "origin": "Python + Dashgram SDK"},
    )


def test_client_bind_aiogram(dashgram_client, mocker):
    """Test client bind_aiogram function"""
    mock_bind = mocker.patch("dashgram.client.aiogram.bind")
    mock_dp = Mock()
    
    dashgram_client.bind_aiogram(mock_dp)
    
    mock_bind.assert_called_once_with(dashgram_client, mock_dp)


def test_client_bind_telegram(dashgram_client, mocker):
    """Test client bind_telegram function"""
    mock_bind = mocker.patch("dashgram.client.telegram.bind")
    mock_app = Mock()
    
    dashgram_client.bind_telegram(mock_app, group=2)
    
    mock_bind.assert_called_once_with(dashgram_client, mock_app, 2, False)


def test_client_bind_telebot(dashgram_client, mocker):
    """Test client bind_telebot function"""
    mock_bind = mocker.patch("dashgram.client.telebot.bind")
    mock_bot = Mock()
    
    dashgram_client.bind_telebot(mock_bot)
    
    mock_bind.assert_called_once_with(dashgram_client, mock_bot)
