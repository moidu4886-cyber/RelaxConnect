from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def profile_kb(has_name: bool) -> InlineKeyboardMarkup:
    rows = []
    if has_name:
        rows.append(
            [InlineKeyboardButton(text="✏️ Change Display Name", callback_data="profile:edit")]
        )
    else:
        rows.append(
            [InlineKeyboardButton(text="➕ Create Display Name", callback_data="profile:edit")]
        )
    rows.append([InlineKeyboardButton(text="◀️ Main Menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎭 Edit Profile Name", callback_data="profile:edit")],
            [
                InlineKeyboardButton(
                    text="📜 Re-read Community Rules",
                    callback_data="feed:disclaimer",
                )
            ],
            [InlineKeyboardButton(text="◀️ Main Menu", callback_data="menu:main")],
        ]
    )
