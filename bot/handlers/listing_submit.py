from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import config
from bot.database.repositories import ListingRepository
from bot.keyboards.common import confirm_cancel_kb
from bot.keyboards.listing import category_pick_kb
from bot.keyboards.main import main_menu_kb
from bot.states.listing import ListingStates
from bot.utils.content_validator import validate_maps_link, validate_whatsapp
from bot.utils.formatters import category_label

router = Router(name="listing_submit")


@router.callback_query(F.data == "listing:start")
async def listing_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ListingStates.business_name)
    await callback.message.edit_text(
        "<b>➕ Submit Spa Listing</b>\n\n"
        "All submissions require <b>admin approval</b> before going public.\n\n"
        "Enter <b>business name</b>:",
    )
    await callback.answer()


@router.message(ListingStates.business_name)
async def listing_business_name(message: Message, state: FSMContext) -> None:
    await state.update_data(business_name=message.text.strip()[:100])
    await state.set_state(ListingStates.city)
    await message.answer("Enter <b>city</b>:")


@router.message(ListingStates.city)
async def listing_city(message: Message, state: FSMContext) -> None:
    await state.update_data(city=message.text.strip().lower()[:50])
    await state.set_state(ListingStates.area)
    await message.answer("Enter <b>area / locality</b>:")


@router.message(ListingStates.area)
async def listing_area(message: Message, state: FSMContext) -> None:
    await state.update_data(area=message.text.strip()[:80])
    await state.set_state(ListingStates.category)
    await message.answer("Select <b>category</b>:", reply_markup=category_pick_kb())


@router.callback_query(F.data.startswith("listing:cat:"), ListingStates.category)
async def listing_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = callback.data.split(":")[-1]
    await state.update_data(category=category)
    await state.set_state(ListingStates.price_range)
    await callback.message.edit_text("Enter <b>price range</b> (e.g. ₹500-1500):")
    await callback.answer()


@router.message(ListingStates.price_range)
async def listing_price(message: Message, state: FSMContext) -> None:
    await state.update_data(price_range=message.text.strip()[:50])
    await state.set_state(ListingStates.whatsapp)
    await message.answer(
        "Enter <b>WhatsApp number</b> (digits only, with country code):\n"
        "Example: <code>919876543210</code>"
    )


@router.message(ListingStates.whatsapp)
async def listing_whatsapp(message: Message, state: FSMContext) -> None:
    number = message.text.strip()
    if not validate_whatsapp(number):
        await message.answer("Invalid number. Use 10-15 digits with country code.")
        return
    await state.update_data(whatsapp=number)
    await state.set_state(ListingStates.maps_link)
    await message.answer("Paste <b>Google Maps link</b>:")


@router.message(ListingStates.maps_link)
async def listing_maps(message: Message, state: FSMContext) -> None:
    link = message.text.strip()
    if not validate_maps_link(link):
        await message.answer("Please provide a valid Google Maps URL.")
        return
    await state.update_data(maps_link=link)
    await state.set_state(ListingStates.description)
    await message.answer("Enter <b>description</b> (max 300 chars):")


@router.message(ListingStates.description)
async def listing_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.strip()[:300])
    await state.set_state(ListingStates.working_hours)
    await message.answer("Enter <b>working hours</b> (e.g. 10 AM - 9 PM):")


@router.message(ListingStates.working_hours)
async def listing_hours(message: Message, state: FSMContext) -> None:
    await state.update_data(working_hours=message.text.strip()[:80])
    data = await state.get_data()
    summary = (
        f"<b>📋 Review Your Listing</b>\n\n"
        f"<b>Name:</b> {data['business_name']}\n"
        f"<b>City:</b> {data['city'].title()}\n"
        f"<b>Area:</b> {data['area']}\n"
        f"<b>Category:</b> {category_label(data['category'])}\n"
        f"<b>Price:</b> {data['price_range']}\n"
        f"<b>WhatsApp:</b> {data['whatsapp']}\n"
        f"<b>Maps:</b> {data['maps_link']}\n"
        f"<b>Hours:</b> {data['working_hours']}\n"
        f"<b>Description:</b> {data['description']}\n\n"
        f"Submit for admin approval?"
    )
    await state.set_state(ListingStates.confirm)
    await message.answer(
        summary,
        reply_markup=confirm_cancel_kb("listing:submit", "menu:main"),
    )


@router.callback_query(F.data == "listing:submit", ListingStates.confirm)
async def listing_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await ListingRepository.create(
        submitter_id=callback.from_user.id,
        business_name=data["business_name"],
        city=data["city"],
        area=data["area"],
        category=data["category"],
        price_range=data["price_range"],
        whatsapp=data["whatsapp"],
        maps_link=data["maps_link"],
        description=data["description"],
        working_hours=data["working_hours"],
    )
    await state.clear()
    await callback.message.edit_text(
        "✅ <b>Listing submitted!</b>\n\n"
        "An admin will review it shortly. You'll be notified when approved.",
        reply_markup=main_menu_kb(is_admin=callback.from_user.id in config.admin_ids),
    )
    await callback.answer()
