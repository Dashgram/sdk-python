# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-24

### Added
- **Core SDK functionality**
  - `Dashgram` class with project initialization
  - Event tracking with `track_event()` method
  - User invitation tracking with `invited_by()` method
  - Automatic async/sync conversion with `@auto_async` decorator
  - Configurable error handling with exception suppression

- **Framework integrations**
  - **aiogram** (v3.x) integration with automatic event tracking
  - **python-telegram-bot** (v21.x) integration with middleware support
  - **pyTelegramBotAPI** (v4.x) integration with sync/async middleware
  - Framework auto-detection and origin string generation

- **Event type support**
  - Complete `HandlerType` enum with all Telegram update types:
    - Message events: `MESSAGE`, `EDITED_MESSAGE`, `CHANNEL_POST`, `EDITED_CHANNEL_POST`
    - Business events: `BUSINESS_CONNECTION`, `BUSINESS_MESSAGE`, `EDITED_BUSINESS_MESSAGE`, `DELETED_BUSINESS_MESSAGES`
    - Interactive events: `CALLBACK_QUERY`, `INLINE_QUERY`, `CHOSEN_INLINE_RESULT`
    - Payment events: `SHIPPING_QUERY`, `PRE_CHECKOUT_QUERY`, `PURCHASED_PAID_MEDIA`
    - Poll events: `POLL`, `POLL_ANSWER`
    - Member events: `MY_CHAT_MEMBER`, `CHAT_MEMBER`, `CHAT_JOIN_REQUEST`
    - Boost events: `CHAT_BOOST`, `REMOVED_CHAT_BOOST`
    - Reaction events: `MESSAGE_REACTION`, `MESSAGE_REACTION_COUNT`

- **Error handling**
  - `InvalidCredentials` exception for authentication errors
  - `DashgramApiError` exception for API errors with status codes
  - Configurable exception suppression with warning fallback
  - Graceful handling of network errors

- **Configuration options**
  - Custom API URL support
  - Custom origin string configuration
  - Environment variable support for credentials
  - Framework-specific middleware configuration

- **Utility functions**
  - `object_to_dict()` for converting framework objects to dictionaries
  - `wrap_event()` for proper event structure formatting
  - `resolve_framework()` for automatic framework detection
  - `auto_async()` decorator for seamless async/sync compatibility

- **Examples and documentation**
  - Complete working examples for all supported frameworks
  - Basic usage examples with manual and automatic tracking
  - Environment variable configuration examples
  - Error handling examples

### Technical details
- **Dependencies**: httpx>=0.28.1 for HTTP client
- **Python support**: >=3.8
- **Async support**: Full async/await with automatic sync wrapper
- **Type hints**: Comprehensive type annotations throughout
- **Testing**: Complete test suite with pytest and pytest-asyncio

### Framework-specific features

#### aiogram integration
- Automatic event tracking via dispatcher binding
- Support for all aiogram update types
- Manual tracking with `HandlerType` specification
- Middleware-based automatic tracking

#### python-telegram-bot integration
- Application-level middleware integration
- Support for all update types via `Update.ALL_TYPES`
- Configurable handler group and blocking options
- Automatic event serialization

#### pyTelegramBotAPI integration
- Sync and async middleware support
- Automatic event type detection
- Middleware-based tracking for all update types
- Support for both `TeleBot` and `AsyncTeleBot`

---

## Version History

### Version 0.1.0 (Initial Release)
- **Release Date**: August 24, 2025
- **Status**: Beta
- **Features**: Core SDK with three framework integrations
- **Compatibility**: Python 3.8+, all major Telegram bot frameworks

---

## Contributing

When contributing to this project, please update the changelog by adding a new entry under the `[Unreleased]` section. Follow the existing format and include:

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for security vulnerability fixes

## Links

- [GitHub Repository](https://github.com/Dashgram/sdk-python)
- [Documentation](https://docs.dashgram.io)
- [Issue Tracker](https://github.com/Dashgram/sdk-python/issues)
- [PyPI Package](https://pypi.org/project/dashgram/)
