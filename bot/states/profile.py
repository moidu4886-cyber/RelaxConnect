from aiogram.fsm.state import State, StatesGroup


class ProfileStates(StatesGroup):
    set_display_name = State()
