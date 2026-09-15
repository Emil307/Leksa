# Telegram Handler Implementation Template — python-aiogram

## Rules

- Implement the smallest handler change that passes the failing test; tests stay read-only.
- Place handlers under `bot/src/bot_app/handlers/{feature}.py` and register them in
  the dispatcher wiring.
- Parse the update, call one bot operation or typed API-client method, and render through
  a keyboard builder/reply helper.
- Never import API application code, access its database, or call another handler.
- Multi-step flows update/clear `FSMContext`; callback payloads use typed `CallbackData`.
- Map typed API failures to explicit user-visible replies without leaking raw responses.

## Shape

```python
async def process_item_callback(
    callback: CallbackQuery,
    callback_data: ItemCallback,
    state: FSMContext,
    api_client: ItemApiClient,
) -> None:
    item = await api_client.get_item(callback_data.item_id)
    await state.clear()
    await callback.message.answer(
        text=ItemView.text(item),
        reply_markup=ItemView.keyboard(item),
    )
```

## Verify

- Run the focused handler test command from the Bot conventions in `technology.md`.
- Every edited file is at most 200 lines.
