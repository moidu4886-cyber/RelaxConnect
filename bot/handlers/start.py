from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.config import config
from bot.database.repositories import AnalyticsRepository, UserRepository
from bot.keyboards.main import main_menu_kb
from bot.utils.formatters import format_main_menu

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, db_user: dict) -> None:
    await UserRepository.get_or_create(message.from_user.id)
    await AnalyticsRepository.increment("bot_starts")
    is_admin = message.from_user.id in config.admin_ids
    await message.answer(
        format_main_menu(),
        reply_markup=main_menu_kb(is_admin=is_admin),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    is_admin = message.from_user.id in config.admin_ids
    await message.answer(
        format_main_menu(),
        reply_markup=main_menu_kb(is_admin=is_admin),
    )
