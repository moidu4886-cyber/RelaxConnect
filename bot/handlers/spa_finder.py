import math

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import config
from bot.database.repositories import ListingRepository
from bot.keyboards.spa import listing_detail_kb, spa_list_kb, spa_menu_kb
from bot.states.spa import SpaSearchStates
from bot.utils.formatters import format_listing_card, format_listing_detail

router = Router(name="spa_finder")


@router.callback_query(F.data == "spa:menu")
async def spa_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "<b>🏪 Spa & Massage Finder</b>\n\n"
        "Browse verified wellness listings or search by city.",
        reply_markup=spa_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("spa:cat:"))
async def spa_by_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = callback.data.split(":")[-1]
    await state.update_data(category=category, city=None)
    await _show_listings(callback, page=0, category=category, city=None)


@router.callback_query(F.data == "spa:city")
async def spa_city_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SpaSearchStates.city_input)
    await callback.message.edit_text(
        "<b>🌆 Enter city name</b>\n\nExample: <code>kochi</code>, <code>mumbai</code>",
    )
    await callback.answer()


@router.message(SpaSearchStates.city_input)
async def spa_city_search(message: Message, state: FSMContext) -> None:
    city = message.text.strip().lower()
    data = await state.get_data()
    category = data.get("category")
    await state.update_data(city=city)
    await state.set_state(None)
    total = await ListingRepository.count_search(city=city, category=category)
    if total == 0:
        await message.answer(
            f"No listings found in <b>{city.title()}</b>.",
            reply_markup=spa_menu_kb(),
        )
        return
    listings = await ListingRepository.search(
        city=city,
        category=category,
        skip=0,
        limit=config.listings_page_size,
    )
    page_size = config.listings_page_size
    total_pages = max(1, math.ceil(total / page_size))
    text = f"<b>Results in {city.title()}</b> (Page 1/{total_pages})\n\n"
    for i, item in enumerate(listings, 1):
        text += format_listing_card(item, i) + "\n\n"
    await message.answer(
        text,
        reply_markup=spa_list_kb(listings, 0, total_pages),
    )


@router.callback_query(F.data.startswith("spa:browse:"))
async def spa_browse(callback: CallbackQuery, state: FSMContext) -> None:
    page = int(callback.data.split(":")[-1])
    data = await state.get_data()
    await _show_listings(
        callback,
        page=page,
        category=data.get("category"),
        city=data.get("city"),
    )


async def _show_listings(
    callback: CallbackQuery,
    page: int,
    category: str | None,
    city: str | None,
) -> None:
    page = max(0, page)
    page_size = config.listings_page_size
    total = await ListingRepository.count_search(city=city, category=category)
    if total == 0:
        await callback.message.edit_text(
            "No approved listings yet. Be the first to add one!",
            reply_markup=spa_menu_kb(),
        )
        await callback.answer()
        return
    total_pages = max(1, math.ceil(total / page_size))
    page = min(page, total_pages - 1)
    listings = await ListingRepository.search(
        city=city,
        category=category,
        skip=page * page_size,
        limit=page_size,
    )
    title = "<b>🏪 Spa & Massage Listings</b>"
    if city:
        title += f" — {city.title()}"
    text = f"{title} (Page {page + 1}/{total_pages})\n\n"
    for i, item in enumerate(listings, 1):
        text += format_listing_card(item, i + page * page_size) + "\n\n"
    await callback.message.edit_text(
        text,
        reply_markup=spa_list_kb(listings, page, total_pages),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("spa:view:"))
async def spa_view_detail(callback: CallbackQuery) -> None:
    listing_id = callback.data.split(":")[-1]
    listing = await ListingRepository.get(listing_id)
    if not listing or listing.get("status") != "approved":
        await callback.answer("Listing not found.", show_alert=True)
        return
    await callback.message.edit_text(
        format_listing_detail(listing),
        reply_markup=listing_detail_kb(
            listing_id,
            listing.get("whatsapp", ""),
            listing.get("maps_link", ""),
        ),
    )
    await callback.answer()
