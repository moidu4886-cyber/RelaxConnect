import math

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import config
from bot.database.repositories import (
    FeedRepository,
    ReportRepository,
    SettingsRepository,
    UserRepository,
)
from bot.keyboards.common import cancel_kb
from bot.keyboards.feed import feed_menu_kb, feed_post_kb
from bot.keyboards.main import disclaimer_kb, main_menu_kb
from bot.states.feed import FeedStates
from bot.utils.content_validator import validate_feed_text
from bot.utils.formatters import format_disclaimer, format_feed_post

router = Router(name="feed")


async def _author_display(author_id: int) -> str:
    user = await UserRepository.get(author_id)
    if user and user.get("display_name"):
        return user["display_name"]
    return "Anonymous"


@router.callback_query(F.data == "feed:enter")
async def feed_enter(callback: CallbackQuery, db_user: dict) -> None:
    has_profile = bool(db_user.get("display_name"))
    agreed = bool(db_user.get("agreed_terms"))
    if not has_profile:
        await callback.message.edit_text(
            "<b>🎭 Profile Required</b>\n\n"
            "Create a display name in <b>My Profile</b> before using the feed.",
            reply_markup=main_menu_kb(is_admin=callback.from_user.id in config.admin_ids),
        )
        await callback.answer()
        return
    if not agreed:
        await callback.message.edit_text(
            format_disclaimer(),
            reply_markup=disclaimer_kb(),
        )
        await callback.answer()
        return
    await callback.message.edit_text(
        "<b>📜 Anonymous Community Feed</b>\n\n"
        "Text-only • No links • No personal info • Moderated",
        reply_markup=feed_menu_kb(has_profile=True, agreed=True),
    )
    await callback.answer()


@router.callback_query(F.data == "feed:disclaimer")
async def feed_disclaimer(callback: CallbackQuery) -> None:
    await callback.message.edit_text(format_disclaimer(), reply_markup=disclaimer_kb())
    await callback.answer()


@router.callback_query(F.data == "feed:agree")
async def feed_agree(callback: CallbackQuery, db_user: dict) -> None:
    if not db_user.get("display_name"):
        await callback.answer("Set a display name first.", show_alert=True)
        return
    await UserRepository.agree_terms(callback.from_user.id)
    await callback.message.edit_text(
        "✅ You agreed to community rules.\n\nWelcome to the Anonymous Feed!",
        reply_markup=feed_menu_kb(has_profile=True, agreed=True),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("feed:browse:"))
async def feed_browse(callback: CallbackQuery) -> None:
    page = max(0, int(callback.data.split(":")[-1]))
    page_size = config.feed_page_size
    total = await FeedRepository.feed_count()
    if total == 0:
        await callback.message.edit_text(
            "No posts yet. Be the first to share!",
            reply_markup=feed_menu_kb(has_profile=True, agreed=True),
        )
        await callback.answer()
        return
    total_pages = max(1, math.ceil(total / page_size))
    page = min(page, total_pages - 1)
    posts = await FeedRepository.feed(skip=page * page_size, limit=1)
    if not posts:
        page = 0
        posts = await FeedRepository.feed(skip=0, limit=1)
    post = posts[0]
    post_id = str(post["_id"])
    name = await _author_display(post["author_id"])
    text = format_feed_post(post, name)
    text += f"\n\n<i>Post {page + 1} of {total}</i>"
    await callback.message.edit_text(
        text,
        reply_markup=feed_post_kb(post_id, page),
    )
    await callback.answer()


@router.callback_query(F.data == "feed:new")
async def feed_new(callback: CallbackQuery, state: FSMContext, db_user: dict) -> None:
    if not db_user.get("agreed_terms"):
        await callback.answer("Accept disclaimer first.", show_alert=True)
        return
    await state.set_state(FeedStates.composing)
    await callback.message.edit_text(
        "<b>✍️ New Anonymous Post</b>\n\nSend your text message (max 500 chars, no links/phones):",
        reply_markup=cancel_kb("feed:enter"),
    )
    await callback.answer()


@router.message(FeedStates.composing)
async def feed_compose(message: Message, state: FSMContext, db_user: dict) -> None:
    blocked = await SettingsRepository.get_blocked_words()
    result = await validate_feed_text(message.text or "", blocked)
    if not result.valid:
        warnings = await UserRepository.add_warning(message.from_user.id)
        await message.answer(
            f"🚫 {result.reason}\nWarning {warnings}/3"
        )
        return
    post_id = await FeedRepository.create_post(message.from_user.id, message.text.strip())
    await state.clear()
    await message.answer(
        "✅ Your post is live in the feed!",
        reply_markup=feed_menu_kb(
            has_profile=bool(db_user.get("display_name")),
            agreed=True,
        ),
    )


@router.callback_query(F.data.startswith("feed:reply:"))
async def feed_reply_start(callback: CallbackQuery, state: FSMContext) -> None:
    post_id = callback.data.split(":")[-1]
    post = await FeedRepository.get_post(post_id)
    if not post:
        await callback.answer("Post not found.", show_alert=True)
        return
    await state.set_state(FeedStates.replying)
    await state.update_data(reply_to=post_id)
    await callback.message.edit_text(
        "<b>↩️ Anonymous Reply</b>\n\nType your reply (text only):",
        reply_markup=cancel_kb("feed:enter"),
    )
    await callback.answer()


@router.message(FeedStates.replying)
async def feed_reply_send(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    blocked = await SettingsRepository.get_blocked_words()
    result = await validate_feed_text(message.text or "", blocked)
    if not result.valid:
        await message.answer(f"🚫 {result.reason}")
        return
    await FeedRepository.create_post(
        message.from_user.id,
        message.text.strip(),
        reply_to=data.get("reply_to"),
    )
    await state.clear()
    await message.answer("✅ Reply posted!", reply_markup=feed_menu_kb(True, True))


@router.callback_query(F.data.startswith("feed:react:"))
async def feed_react(callback: CallbackQuery) -> None:
    parts = callback.data.split(":")
    post_id, reaction = parts[2], parts[3]
    changed = await FeedRepository.add_reaction(post_id, callback.from_user.id, reaction)
    await callback.answer("Reaction updated!" if changed else "Already reacted")


@router.callback_query(F.data.startswith("feed:report:"))
async def feed_report_start(callback: CallbackQuery, state: FSMContext) -> None:
    post_id = callback.data.split(":")[-1]
    await state.set_state(FeedStates.report_reason)
    await state.update_data(report_post_id=post_id)
    await callback.message.edit_text(
        "<b>🚨 Report Post</b>\n\nBriefly describe the issue:",
        reply_markup=cancel_kb("feed:enter"),
    )
    await callback.answer()


@router.message(FeedStates.report_reason)
async def feed_report_submit(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    post_id = data.get("report_post_id")
    if not post_id:
        await state.clear()
        return
    reason = (message.text or "No reason provided")[:200]
    await ReportRepository.create(
        message.from_user.id,
        "feed_post",
        post_id,
        reason,
    )
    await FeedRepository.increment_report(post_id)
    await state.clear()
    await message.answer(
        "✅ Report submitted. Moderators will review it.",
        reply_markup=feed_menu_kb(True, True),
    )
