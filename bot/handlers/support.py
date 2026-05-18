from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.config import config
from bot.keyboards.common import back_main_kb

router = Router(name="support")


@router.callback_query(F.data == "support:view")
async def support_view(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "<b>💬 Support</b>\n\n"
        f"Contact: @{config.support_username}\n\n"
        "For listing issues, reports, or account help.",
        reply_markup=back_main_kb(),
    )
    await callback.answer()
