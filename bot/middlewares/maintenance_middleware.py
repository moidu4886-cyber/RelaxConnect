from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.database.repositories import SettingsRepository
from bot.filters.admin import IsAdmin


class MaintenanceMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not await SettingsRepository.is_maintenance():
            return await handler(event, data)

        if await IsAdmin()(event):
            return await handler(event, data)

        text = "🔧 RelaxConnect is under maintenance. Please try again later."
        if isinstance(event, Message):
            await event.answer(text)
        elif isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)
        return None
