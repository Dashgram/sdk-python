import typing
import httpx

from dashgram.integrations.base import object_to_dict
from dashgram.integrations import aiogram, telegram, telebot
from dashgram.enums import HandlerType
from dashgram.exceptions import InvalidCredentials, DashgramApiError
from dashgram.utils import auto_async, wrap_event


class Dashgram:
    def __init__(self, project_id: typing.Union[int, str], access_key: str, *,
                 api_url: typing.Optional[str] = None,
                 origin: typing.Optional[str] = None) -> None:
        self.project_id = project_id
        self.access_key = access_key

        if api_url is None:
            api_url = "https://api.dashgram.io/v1"
        self.api_url = f"{api_url}/{project_id}"

        if origin is None:
            origin = "Python + Dashgram SDK"
        self.origin = origin

        self._client = httpx.AsyncClient(base_url=self.api_url, headers={"Authorization": f"Bearer {access_key}"})

    @auto_async
    async def track_event(self, event, handler_type: typing.Optional[HandlerType] = None):
        if not isinstance(event, dict):
            event = object_to_dict(event, handler_type)
        else:
            event = wrap_event(event, handler_type)

        req_data = {"origin": self.origin, "updates": [event]}

        resp = await self._client.post("track", json=req_data)

        if resp.status_code == 403:
            raise InvalidCredentials

        resp_data = resp.json()

        if resp_data.get("status") != "success":
            raise DashgramApiError(resp.status_code, resp_data.get("details"))

    def bind_aiogram(self, dp: aiogram.Dispatcher):
        aiogram.bind(self, dp)

    def bind_telegram(self, app: telegram.Application, group: int = 1):
        telegram.bind(self, app, group)

    def bind_telebot(self, bot: telebot.TeleBot):
        telebot.bind(self, bot)
