import time
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, List

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.config import config
from bot.database.repositories import BanRepository, UserRepository
from bot.filters.admin import IsAdmin


class FloodMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self._timestamps: Dict[int, List[float]] = defaultdict(list)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        if await IsAdmin()(event):
            return await handler(event, data)

        now = time.time()
        window = config.flood_window_seconds
        limit = config.flood_limit
        stamps = self._timestamps[user.id]
        stamps[:] = [t for t in stamps if now - t < window]
        stamps.append(now)

        if len(stamps) > limit:
            warnings = await UserRepository.add_warning(user.id)
            msg = f"⚠️ Slow down! Warning {warnings}/{config.spam_warn_threshold}."
            if warnings >= config.spam_warn_threshold:
                await BanRepository.ban(user.id, "Spam / flood violations", 0)
                msg = "🚫 Permanent ban: repeated spam detected."
            if isinstance(event, Message):
                await event.answer(msg)
            elif isinstance(event, CallbackQuery):
                await event.answer(msg, show_alert=True)
            return None

        return await handler(event, data)
