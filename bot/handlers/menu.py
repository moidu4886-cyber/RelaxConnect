from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.config import config
from bot.keyboards.main import main_menu_kb
from bot.utils.formatters import format_main_menu

router = Router(name="menu")


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery) -> None:
    is_admin = callback.from_user.id in config.admin_ids
    await callback.message.edit_text(
        format_main_menu(),
        reply_markup=main_menu_kb(is_admin=is_admin),
    )
    await callback.answer()
