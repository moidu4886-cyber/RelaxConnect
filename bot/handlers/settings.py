from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.profile import settings_kb

router = Router(name="settings")


@router.callback_query(F.data == "settings:menu")
async def settings_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "<b>⚙️ Settings</b>\n\nManage your profile and community preferences.",
        reply_markup=settings_kb(),
    )
    await callback.answer()
