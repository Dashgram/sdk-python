import typing
import httpx
import warnings

from dashgram.integrations.base import object_to_dict, resolve_framework
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
            framework = resolve_framework()
            if framework is None:
                origin = "Python + Dashgram SDK"
            else:
                origin = f"Python + Dashgram SDK + {framework}"

        self.origin = origin

        self._client = httpx.AsyncClient(base_url=self.api_url, headers={"Authorization": f"Bearer {access_key}"})

    async def _request(self, url: str, json: typing.Optional[typing.Dict[str, typing.Any]] = None, suppress_exceptions: bool = True) -> bool:
        try:
            resp = await self._client.post(url, json=json)
            
            if resp.status_code == 403:
                raise InvalidCredentials
            
            resp_data = resp.json()
            
            if resp.status_code != 200 or resp_data.get("status") != "success":
                raise DashgramApiError(resp.status_code, resp_data.get("details"))
            
            return True
        except Exception as e:
            if not suppress_exceptions:
                raise e
            warnings.warn(f"{type(e).__name__}: {e}")
            return False

    @auto_async
    async def track_event(self, event, handler_type: typing.Optional[HandlerType] = None, suppress_exceptions: bool = True) -> bool:
        if not isinstance(event, dict):
            event = object_to_dict(event, handler_type)
        else:
            event = wrap_event(event, handler_type)

        req_data = {"origin": self.origin, "updates": [event]}

        return await self._request("track", json=req_data, suppress_exceptions=suppress_exceptions)
            
        
    @auto_async
    async def invited_by(self, user_id: int, invited_by: int, suppress_exceptions: bool = True) -> bool:
        req_data = {"user_id": user_id, "invited_by": invited_by, "origin": self.origin}
            
        return await self._request("invited_by", json=req_data, suppress_exceptions=suppress_exceptions)

    def bind_aiogram(self, dp):
        aiogram.bind(self, dp)

    def bind_telegram(self, app, group: int = -1, block: bool = False):
        telegram.bind(self, app, group, block)

    def bind_telebot(self, bot):
        telebot.bind(self, bot)
