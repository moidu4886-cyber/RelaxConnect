from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot.database.repositories import UserRepository
from bot.filters.admin import IsAdmin


class MediaBlockMiddleware(BaseMiddleware):
    """Block non-text content globally (feed safety)."""

    BLOCKED_CONTENT = (
        "photo",
        "video",
        "voice",
        "video_note",
        "audio",
        "document",
        "sticker",
        "animation",
        "contact",
        "location",
        "venue",
        "poll",
        "dice",
    )

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        if await IsAdmin()(event):
            return await handler(event, data)

        state = data.get("state")
        state_str = await state.get_state() if state else None

        # Allow text during FSM flows; block media always in feed context
        for attr in self.BLOCKED_CONTENT:
            if getattr(event, attr, None):
                # Listing submission allows only text except whatsapp/maps in specific states
                if state_str and "ListingStates" in str(state_str):
                    if attr in ("photo", "video", "voice", "document", "sticker", "animation"):
                        await event.answer(
                            "🚫 Only text is allowed during listing submission."
                        )
                        return None
                else:
                    await event.answer(
                        "🚫 Only plain text is allowed in RelaxConnect.\n"
                        "Photos, videos, files, stickers, and GIFs are blocked."
                    )
                    warnings = await UserRepository.add_warning(event.from_user.id)
                    if warnings >= 3:
                        from bot.database.repositories import BanRepository

                        await BanRepository.ban(
                            event.from_user.id,
                            "Repeated media violations",
                            0,
                        )
                    return None

        return await handler(event, data)
