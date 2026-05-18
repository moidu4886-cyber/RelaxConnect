from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def feed_menu_kb(has_profile: bool, agreed: bool) -> InlineKeyboardMarkup:
    rows = []
    if agreed and has_profile:
        rows.extend(
            [
                [InlineKeyboardButton(text="📜 Browse Feed", callback_data="feed:browse:0")],
                [InlineKeyboardButton(text="✍️ New Post", callback_data="feed:new")],
            ]
        )
    rows.append([InlineKeyboardButton(text="◀️ Main Menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def feed_post_kb(post_id: str, page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍", callback_data=f"feed:react:{post_id}:like"),
                InlineKeyboardButton(text="❤️", callback_data=f"feed:react:{post_id}:love"),
                InlineKeyboardButton(text="🔥", callback_data=f"feed:react:{post_id}:fire"),
            ],
            [
                InlineKeyboardButton(text="↩️ Reply", callback_data=f"feed:reply:{post_id}"),
                InlineKeyboardButton(text="🚨 Report", callback_data=f"feed:report:{post_id}"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Prev", callback_data=f"feed:browse:{page - 1}"),
                InlineKeyboardButton(text="➡️ Next", callback_data=f"feed:browse:{page + 1}"),
            ],
            [InlineKeyboardButton(text="◀️ Feed Menu", callback_data="feed:enter")],
        ]
    )


def feed_nav_only_kb(page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Prev", callback_data=f"feed:browse:{max(0, page - 1)}"),
                InlineKeyboardButton(text="➡️ Next", callback_data=f"feed:browse:{page + 1}"),
            ],
            [InlineKeyboardButton(text="◀️ Feed Menu", callback_data="feed:enter")],
        ]
    )
