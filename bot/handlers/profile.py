from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.repositories import UserRepository
from bot.keyboards.common import cancel_kb
from bot.keyboards.profile import profile_kb
from bot.states.profile import ProfileStates
from bot.utils.content_validator import validate_display_name
from bot.utils.formatters import format_profile

router = Router(name="profile")


@router.callback_query(F.data == "profile:view")
async def profile_view(callback: CallbackQuery, db_user: dict) -> None:
    await callback.message.edit_text(
        format_profile(db_user),
        reply_markup=profile_kb(has_name=bool(db_user.get("display_name"))),
    )
    await callback.answer()


@router.callback_query(F.data == "profile:edit")
async def profile_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ProfileStates.set_display_name)
    await callback.message.edit_text(
        "<b>🎭 Custom Display Name</b>\n\n"
        "Choose a unique public name (3-20 chars, letters/numbers/_).\n"
        "Your Telegram username is <b>never</b> shown.",
        reply_markup=cancel_kb("profile:view"),
    )
    await callback.answer()


@router.message(ProfileStates.set_display_name)
async def profile_set_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    ok, err = validate_display_name(name)
    if not ok:
        await message.answer(f"🚫 {err}")
        return
    success = await UserRepository.set_display_name(message.from_user.id, name)
    if not success:
        await message.answer("That name is taken. Try another.")
        return
    await state.clear()
    user = await UserRepository.get(message.from_user.id)
    await message.answer(
        format_profile(user),
        reply_markup=profile_kb(has_name=True),
    )
