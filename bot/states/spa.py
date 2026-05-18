from aiogram.fsm.state import State, StatesGroup


class SpaSearchStates(StatesGroup):
    city_input = State()
