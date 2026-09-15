import os
from typing import Any

from httpx import AsyncClient, Response

DEFAULT_BACKEND_PORT = "8000"
DEFAULT_BACKEND_HOST = "localhost"


def resolve_base_url() -> str:
    host = os.environ.get("BACKEND_EXTERNAL_HOST", DEFAULT_BACKEND_HOST)
    port = os.environ.get("BACKEND_PORT", DEFAULT_BACKEND_PORT)
    return f"http://{host}:{port}"


class ApplicationClient:
    def __init__(self, http: AsyncClient):
        self.http = http

    async def get(self, path: str, **kwargs) -> Response:
        return await self.http.get(path, **kwargs)

    async def post(self, path: str, **kwargs) -> Response:
        return await self.http.post(path, **kwargs)

    @staticmethod
    def _json_body(response: Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return None

    @classmethod
    def _json_object(cls, response: Response) -> dict[str, Any]:
        body = cls._json_body(response)
        return body if isinstance(body, dict) else {}

    @staticmethod
    def _nested_object(body: dict[str, Any], key: str) -> dict[str, Any]:
        value = body.get(key)
        return value if isinstance(value, dict) else {}
