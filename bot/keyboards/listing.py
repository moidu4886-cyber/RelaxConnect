from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models import ListingCategory


def category_pick_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💆 Spa", callback_data=f"listing:cat:{ListingCategory.SPA.value}"
                ),
                InlineKeyboardButton(
                    text="🧘 Massage Center",
                    callback_data=f"listing:cat:{ListingCategory.MASSAGE.value}",
                ),
            ],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="menu:main")],
        ]
    )
