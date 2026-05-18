from aiogram.fsm.state import State, StatesGroup


class ListingStates(StatesGroup):
    business_name = State()
    city = State()
    area = State()
    category = State()
    price_range = State()
    whatsapp = State()
    maps_link = State()
    description = State()
    working_hours = State()
    confirm = State()
