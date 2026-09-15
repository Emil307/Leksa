# Bot API Client Implementation Template — python-aiogram

## Rules

- Place the client under `bot/src/bot_app/api/{resource}.py`.
- Read the base URL from required `API_BASE_URL`; never assemble it from API port values.
- Use typed request/response models and finite timeouts.
- Map HTTP and transport failures into typed bot-client errors at this boundary.
- Do not retry non-idempotent operations unless the API contract supplies an idempotency
  mechanism and the scenario requires it.

## Shape

```python
class ItemApiClient:
    def __init__(self, transport: AsyncClient, base_url: str) -> None:
        self._transport = transport
        self._base_url = base_url.rstrip("/")

    async def get_item(self, item_id: str) -> ItemResponse:
        response = await self._transport.get(f"{self._base_url}/items/{item_id}")
        response.raise_for_status()
        return ItemResponse.model_validate(response.json())
```

## Verify

- Run the focused bot API-client test command from `technology.md`.
