from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.models import ListingCategory


def spa_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💆 Spa", callback_data="spa:cat:spa"),
                InlineKeyboardButton(
                    text="🧘 Massage Center",
                    callback_data=f"spa:cat:{ListingCategory.MASSAGE.value}",
                ),
            ],
            [InlineKeyboardButton(text="🌆 Search by City", callback_data="spa:city")],
            [InlineKeyboardButton(text="📋 Browse All", callback_data="spa:browse:0")],
            [InlineKeyboardButton(text="◀️ Main Menu", callback_data="menu:main")],
        ]
    )


def spa_list_kb(
    listings: list,
    page: int,
    total_pages: int,
    prefix: str = "spa:view",
) -> InlineKeyboardMarkup:
    rows = []
    for item in listings:
        lid = str(item["_id"])
        name = item["business_name"][:30]
        rows.append(
            [InlineKeyboardButton(text=f"✨ {name}", callback_data=f"{prefix}:{lid}")]
        )
    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(text="⬅️ Prev", callback_data=f"spa:browse:{page - 1}")
        )
    if page < total_pages - 1:
        nav.append(
            InlineKeyboardButton(text="➡️ Next", callback_data=f"spa:browse:{page + 1}")
        )
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="◀️ Spa Menu", callback_data="spa:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def listing_detail_kb(listing_id: str, whatsapp: str, maps_link: str) -> InlineKeyboardMarkup:
    wa = whatsapp if whatsapp.startswith("+") else f"+{whatsapp}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 WhatsApp",
                    url=f"https://wa.me/{wa.replace('+', '')}",
                ),
                InlineKeyboardButton(text="📍 Google Maps", url=maps_link),
            ],
            [InlineKeyboardButton(text="◀️ Back to Results", callback_data="spa:menu")],
        ]
    )
