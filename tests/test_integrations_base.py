import pytest
from unittest.mock import Mock, patch
from dashgram.integrations.base import (
    get_package, determine_object_source, object_to_dict, resolve_framework
)
from dashgram.integrations import aiogram, telebot, telegram
from dashgram.enums import HandlerType


def test_get_package_with_aiogram_object(sample_aiogram_message):
    """Test get_package with aiogram object"""
    assert get_package(sample_aiogram_message) == "aiogram"


def test_get_package_with_telegram_object(sample_telegram_message):
    """Test get_package with python-telegram-bot object"""
    assert get_package(sample_telegram_message) == "telegram"


def test_get_package_with_telebot_object(sample_telebot_message):
    """Test get_package with pyTelegramBotAPI object"""
    assert get_package(sample_telebot_message) == "telebot"


def test_get_package_with_unknown_object():
    """Test get_package with unknown object"""
    assert get_package(Mock()) is None


def test_determine_object_source_with_aiogram(sample_aiogram_message):
    """Test determine_object_source with aiogram object"""
    assert determine_object_source(sample_aiogram_message) == aiogram.object_to_dict


def test_determine_object_source_with_telegram(sample_telegram_message):
    """Test determine_object_source with python-telegram-bot object"""
    assert determine_object_source(sample_telegram_message) == telegram.object_to_dict


def test_determine_object_source_with_telebot(sample_telebot_message):
    """Test determine_object_source with pyTelegramBotAPI object"""
    assert determine_object_source(sample_telebot_message) == telebot.object_to_dict


def test_determine_object_source_with_unknown():
    """Test determine_object_source with unknown object"""
    assert determine_object_source(Mock()) is None


def test_object_to_dict_with_aiogram(sample_aiogram_message, mocker):
    """Test object_to_dict with aiogram object"""
    mock_object_to_dict = Mock()
    mocker.patch("dashgram.integrations.base.determine_object_source", return_value=mock_object_to_dict)
    
    object_to_dict(sample_aiogram_message, HandlerType.MESSAGE)
    mock_object_to_dict.assert_called_once_with(sample_aiogram_message, HandlerType.MESSAGE)

def test_object_to_dict_with_telegram(sample_telegram_message, mocker):
    """Test object_to_dict with python-telegram-bot object"""
    mock_object_to_dict = Mock()
    mocker.patch("dashgram.integrations.base.determine_object_source", return_value=mock_object_to_dict)
    
    object_to_dict(sample_telegram_message, HandlerType.MESSAGE)
    mock_object_to_dict.assert_called_once_with(sample_telegram_message, HandlerType.MESSAGE)

def test_object_to_dict_with_telebot(sample_telebot_message, mocker):
    """Test object_to_dict with pyTelegramBotAPI object"""
    mock_object_to_dict = Mock()
    mocker.patch("dashgram.integrations.base.determine_object_source", return_value=mock_object_to_dict)
    
    object_to_dict(sample_telebot_message, HandlerType.MESSAGE)
    mock_object_to_dict.assert_called_once_with(sample_telebot_message, HandlerType.MESSAGE)

def test_object_to_dict_with_unknown():
    """Test object_to_dict with unknown object"""
    
    assert object_to_dict(Mock(), HandlerType.MESSAGE) == {}
    
    
@patch('dashgram.integrations.aiogram.aiogram', True)
@patch('dashgram.integrations.telegram.telegram', False)
@patch('dashgram.integrations.telebot.telebot', False)
def test_resolve_framework_with_aiogram():
    """Test resolve_framework when aiogram is available"""
    assert resolve_framework() == "Aiogram"


@patch('dashgram.integrations.aiogram.aiogram', False)
@patch('dashgram.integrations.telegram.telegram', True)
@patch('dashgram.integrations.telebot.telebot', False)
def test_resolve_framework_with_telegram():
    """Test resolve_framework when python-telegram-bot is available"""
    assert resolve_framework() == "python-telegram-bot"


@patch('dashgram.integrations.aiogram.aiogram', False)
@patch('dashgram.integrations.telegram.telegram', False)
@patch('dashgram.integrations.telebot.telebot', True)
def test_resolve_framework_with_telebot():
    """Test resolve_framework when pyTelegramBotAPI is available"""
    assert resolve_framework() == "pyTelegramBotAPI"


@patch('dashgram.integrations.aiogram.aiogram', False)
@patch('dashgram.integrations.telegram.telegram', False)
@patch('dashgram.integrations.telebot.telebot', False)
def test_resolve_framework_with_none():
    """Test resolve_framework when no framework is available"""
    assert resolve_framework() is None
