from aiogram.fsm.state import State, StatesGroup


class AdminBroadcastStates(StatesGroup):
    message = State()
    confirm = State()


class AdminBanStates(StatesGroup):
    user_id = State()
    reason = State()


class AdminUnbanStates(StatesGroup):
    user_id = State()


class AdminDeletePostStates(StatesGroup):
    post_id = State()


class AdminWordStates(StatesGroup):
    add_word = State()
    remove_word = State()
