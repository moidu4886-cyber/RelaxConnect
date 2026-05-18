from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.models import oid_str
from bot.database.repositories import (
    AnalyticsRepository,
    BanRepository,
    FeedRepository,
    ListingRepository,
    ReportRepository,
    SettingsRepository,
    UserRepository,
)
from bot.filters.admin import IsAdmin
from bot.keyboards.admin import admin_panel_kb, listing_review_kb, report_action_kb
from bot.keyboards.main import main_menu_kb
from bot.loader import bot
from bot.states.admin import (
    AdminBanStates,
    AdminBroadcastStates,
    AdminDeletePostStates,
    AdminUnbanStates,
)
from bot.utils.formatters import format_analytics, format_listing_detail

router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(Command("admin"))
@router.callback_query(F.data == "admin:panel")
async def admin_panel(event: Message | CallbackQuery) -> None:
    maintenance = await SettingsRepository.is_maintenance()
    text = "<b>🛡 RelaxConnect Admin Panel</b>\n\nSelect an action:"
    kb = admin_panel_kb(maintenance)
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb)


async def _show_pending_listing(callback: CallbackQuery, page: int) -> None:
    pending = await ListingRepository.pending(skip=page, limit=1)
    if not pending:
        await callback.message.edit_text(
            "✅ No pending listings.",
            reply_markup=admin_panel_kb(await SettingsRepository.is_maintenance()),
        )
        return
    listing = pending[0]
    lid = oid_str(listing["_id"])
    await callback.message.edit_text(
        format_listing_detail(listing) + "\n\n<b>⏳ PENDING REVIEW</b>",
        reply_markup=listing_review_kb(lid, page),
    )


@router.callback_query(F.data.startswith("admin:listings:"))
async def admin_listings(callback: CallbackQuery) -> None:
    page = int(callback.data.split(":")[-1])
    await _show_pending_listing(callback, page)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:approve:"))
async def admin_approve(callback: CallbackQuery) -> None:
    lid = callback.data.split(":")[-1]
    await ListingRepository.approve(lid, callback.from_user.id)
    await callback.answer("Approved!", show_alert=True)
    await _show_pending_listing(callback, 0)


@router.callback_query(F.data.startswith("admin:reject:"))
async def admin_reject(callback: CallbackQuery) -> None:
    lid = callback.data.split(":")[-1]
    await ListingRepository.reject(lid, callback.from_user.id, "Does not meet guidelines")
    await callback.answer("Rejected.", show_alert=True)
    await _show_pending_listing(callback, 0)


@router.callback_query(F.data == "admin:analytics")
async def admin_analytics(callback: CallbackQuery) -> None:
    data = await AnalyticsRepository.dashboard()
    await callback.message.edit_text(
        format_analytics(data),
        reply_markup=admin_panel_kb(await SettingsRepository.is_maintenance()),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:reports:"))
async def admin_reports(callback: CallbackQuery) -> None:
    reports = await ReportRepository.open_reports(skip=0, limit=1)
    if not reports:
        await callback.message.edit_text(
            "✅ No open reports.",
            reply_markup=admin_panel_kb(await SettingsRepository.is_maintenance()),
        )
        await callback.answer()
        return
    report = reports[0]
    rid = oid_str(report["_id"])
    post = await FeedRepository.get_post(report["target_id"])
    post_preview = post.get("text", "N/A")[:200] if post else "Deleted / missing"
    await callback.message.edit_text(
        f"<b>🚨 Report</b>\n\n"
        f"<b>Target:</b> {report['target_type']}\n"
        f"<b>ID:</b> <code>{report['target_id']}</code>\n"
        f"<b>Reason:</b> {report['reason']}\n\n"
        f"<b>Post preview:</b>\n{post_preview}",
        reply_markup=report_action_kb(rid, report["target_id"]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:resolve:"))
async def admin_resolve_report(callback: CallbackQuery) -> None:
    rid = callback.data.split(":")[-1]
    await ReportRepository.resolve(rid, callback.from_user.id)
    await callback.answer("Resolved.")
    await admin_reports(callback)


@router.callback_query(F.data.startswith("admin:delpost:"))
async def admin_delete_post_cb(callback: CallbackQuery) -> None:
    post_id = callback.data.split(":")[-1]
    await FeedRepository.delete_post(post_id)
    await callback.answer("Post deleted.", show_alert=True)
    await admin_reports(callback)


@router.callback_query(F.data == "admin:delete_post")
async def admin_delete_post_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminDeletePostStates.post_id)
    await callback.message.edit_text("Send the <b>post ID</b> to delete:")
    await callback.answer()


@router.message(AdminDeletePostStates.post_id)
async def admin_delete_post_id(message: Message, state: FSMContext) -> None:
    await FeedRepository.delete_post(message.text.strip())
    await state.clear()
    await message.answer("✅ Post deleted.")


@router.callback_query(F.data == "admin:ban")
async def admin_ban_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminBanStates.user_id)
    await callback.message.edit_text("Enter <b>Telegram user ID</b> to ban:")
    await callback.answer()


@router.message(AdminBanStates.user_id)
async def admin_ban_user_id(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("Invalid user ID.")
        return
    await state.update_data(ban_user_id=int(message.text.strip()))
    await state.set_state(AdminBanStates.reason)
    await message.answer("Enter ban <b>reason</b>:")


@router.message(AdminBanStates.reason)
async def admin_ban_reason(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    uid = data["ban_user_id"]
    await BanRepository.ban(uid, message.text.strip()[:200], message.from_user.id)
    await state.clear()
    await message.answer(f"🚫 User {uid} banned.")


@router.callback_query(F.data == "admin:unban")
async def admin_unban_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminUnbanStates.user_id)
    await callback.message.edit_text("Enter <b>Telegram user ID</b> to unban:")
    await callback.answer()


@router.message(AdminUnbanStates.user_id)
async def admin_unban_user(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("Invalid user ID.")
        return
    uid = int(message.text.strip())
    await BanRepository.unban(uid)
    await state.clear()
    await message.answer(f"✅ User {uid} unbanned.")


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminBroadcastStates.message)
    await callback.message.edit_text("Send the <b>broadcast message</b> (HTML supported):")
    await callback.answer()


@router.message(AdminBroadcastStates.message)
async def admin_broadcast_msg(message: Message, state: FSMContext) -> None:
    await state.update_data(broadcast_text=message.html_text or message.text)
    await state.set_state(AdminBroadcastStates.confirm)
    await message.answer(
        f"Broadcast to all users?\n\n{message.html_text or message.text}",
        reply_markup=__import__(
            "bot.keyboards.common", fromlist=["confirm_cancel_kb"]
        ).confirm_cancel_kb("admin:broadcast:send", "admin:panel"),
    )


@router.callback_query(F.data == "admin:broadcast:send", AdminBroadcastStates.confirm)
async def admin_broadcast_send(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    text = data.get("broadcast_text", "")
    from bot.database.connection import get_db

    cursor = get_db().users.find({"is_banned": False}, {"telegram_id": 1})
    users = await cursor.to_list(length=100000)
    sent = 0
    for u in users:
        try:
            await bot.send_message(u["telegram_id"], text)
            sent += 1
        except Exception:
            pass
    await state.clear()
    await callback.message.edit_text(
        f"📢 Broadcast sent to {sent} users.",
        reply_markup=admin_panel_kb(await SettingsRepository.is_maintenance()),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:words")
async def admin_words(callback: CallbackQuery) -> None:
    words = await SettingsRepository.get_blocked_words()
    word_list = ", ".join(words[:30]) or "None"
    await callback.message.edit_text(
        f"<b>📝 Blocked Words</b>\n\n{word_list}\n\n"
        "Send /addword &lt;word&gt; or /removeword &lt;word&gt;",
        reply_markup=admin_panel_kb(await SettingsRepository.is_maintenance()),
    )
    await callback.answer()


@router.message(Command("addword"))
async def admin_add_word(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /addword &lt;word&gt;")
        return
    await SettingsRepository.add_blocked_word(parts[1])
    await message.answer(f"Added: {parts[1]}")


@router.message(Command("removeword"))
async def admin_remove_word(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /removeword &lt;word&gt;")
        return
    await SettingsRepository.remove_blocked_word(parts[1])
    await message.answer(f"Removed: {parts[1]}")


@router.callback_query(F.data == "admin:maint:on")
async def admin_maint_on(callback: CallbackQuery) -> None:
    await SettingsRepository.set_maintenance(True)
    await callback.answer("Maintenance ON", show_alert=True)
    await admin_panel(callback)


@router.callback_query(F.data == "admin:maint:off")
async def admin_maint_off(callback: CallbackQuery) -> None:
    await SettingsRepository.set_maintenance(False)
    await callback.answer("Maintenance OFF", show_alert=True)
    await admin_panel(callback)

