from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="1️⃣ Find Spa", callback_data="spa:menu"),
            InlineKeyboardButton(text="2️⃣ Add Spa", callback_data="listing:start"),
        ],
        [
            InlineKeyboardButton(text="3️⃣ Anonymous Feed", callback_data="feed:enter"),
            InlineKeyboardButton(text="4️⃣ My Profile", callback_data="profile:view"),
        ],
        [
            InlineKeyboardButton(text="5️⃣ Settings", callback_data="settings:menu"),
            InlineKeyboardButton(text="6️⃣ Support", callback_data="support:view"),
        ],
    ]
    if is_admin:
        rows.append(
            [InlineKeyboardButton(text="🛡 Admin Panel", callback_data="admin:panel")]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def disclaimer_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ I Agree", callback_data="feed:agree")],
            [InlineKeyboardButton(text="◀️ Back", callback_data="menu:main")],
        ]
    )
