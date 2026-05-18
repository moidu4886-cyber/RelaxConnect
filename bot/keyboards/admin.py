from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_panel_kb(maintenance: bool) -> InlineKeyboardMarkup:
    maint_label = "🔴 Disable Maintenance" if maintenance else "🟢 Enable Maintenance"
    maint_data = "admin:maint:off" if maintenance else "admin:maint:on"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Pending Listings", callback_data="admin:listings:0"),
                InlineKeyboardButton(text="🚨 Reports", callback_data="admin:reports:0"),
            ],
            [
                InlineKeyboardButton(text="📊 Analytics", callback_data="admin:analytics"),
                InlineKeyboardButton(text="📢 Broadcast", callback_data="admin:broadcast"),
            ],
            [
                InlineKeyboardButton(text="🚫 Ban User", callback_data="admin:ban"),
                InlineKeyboardButton(text="✅ Unban User", callback_data="admin:unban"),
            ],
            [
                InlineKeyboardButton(text="📝 Blocked Words", callback_data="admin:words"),
                InlineKeyboardButton(text="🗑 Delete Post", callback_data="admin:delete_post"),
            ],
            [InlineKeyboardButton(text=maint_label, callback_data=maint_data)],
            [InlineKeyboardButton(text="◀️ Main Menu", callback_data="menu:main")],
        ]
    )


def listing_review_kb(listing_id: str, page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve", callback_data=f"admin:approve:{listing_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Reject", callback_data=f"admin:reject:{listing_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="➡️ Next Pending", callback_data=f"admin:listings:{page + 1}"
                )
            ],
            [InlineKeyboardButton(text="◀️ Admin Panel", callback_data="admin:panel")],
        ]
    )


def report_action_kb(report_id: str, post_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Delete Post", callback_data=f"admin:delpost:{post_id}"
                ),
                InlineKeyboardButton(
                    text="✅ Resolve", callback_data=f"admin:resolve:{report_id}"
                ),
            ],
            [InlineKeyboardButton(text="◀️ Admin Panel", callback_data="admin:panel")],
        ]
    )
