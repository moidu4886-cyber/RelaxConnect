from aiogram.fsm.state import State, StatesGroup


class FeedStates(StatesGroup):
    composing = State()
    replying = State()
    report_reason = State()
