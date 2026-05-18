from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from bot.config import config


class IsAdmin(BaseFilter):
    async def __call__(self, event) -> bool:
        user = None

        if isinstance(event, Message):
            user = event.from_user

        elif isinstance(event, CallbackQuery):
            user = event.from_user

        elif getattr(event, "message", None):
            user = event.message.from_user

        elif getattr(event, "callback_query", None):
            user = event.callback_query.from_user

        if not user:
            return False

        return user.id in config.admin_ids
