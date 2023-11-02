from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def get_confirm_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(InlineKeyboardButton(text='Add button', callback_data='add_button'))
    keyboard_builder.add(InlineKeyboardButton(text='No button', callback_data='no_button'))
    keyboard_builder.adjust()
    return keyboard_builder.as_markup()