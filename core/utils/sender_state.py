from aiogram.fsm.state import State, StatesGroup



class Step(StatesGroup):
    initial = State()
    get_message = State()
    get_button_or_continue = State()
    get_text_for_button = State()
    get_url_for_button = State()
    confirm_or_cancel = State()



