from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from bot.config import config


class IsAdmin(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        user = event.from_user
        if not user:
            return False
        return user.id in config.admin_ids
