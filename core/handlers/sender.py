from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from core.utils.dbconnect import Request
from core.utils.sender_list import SenderList
from core.utils.sender_state import Step
from core.keyboards.inline import get_confirm_keyboard


async def get_started(message: Message, command: CommandObject, state: FSMContext):
    if not command.args:
        await message.answer("To create new commercial please enter /sender command and name of your campaign!")
        return
    
    await message.answer(f"Let's start! Your campaign name is {command.args} \n Please enter a message for your campaign!")
    await state.update_data(name_camp = command.args)
    await state.set_state(Step.get_message)


async def get_message(message: Message, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    if current_state == Step.get_message:
        print(f'Current state: {current_state}')
        await message.answer(f"Your message is {message.text} \n Would you like to add a button?", reply_markup=get_confirm_keyboard())
        await state.update_data(message_id = message.message_id, chat_id = message.from_user.id)
        await state.set_state(Step.q_button)
        return
    else:
        print(f'Current State is not get_message {current_state}')
        if current_state == Step.get_text_button:
            await get_text_button(message, state)
        if current_state == Step.get_url_button:
            await get_url_button(message, bot, state)
    


async def q_button(call: CallbackQuery, bot: Bot, state: FSMContext, request: Request):
    current_state = await state.get_state()
    if current_state == Step.q_button:
        if call.data == 'add_button':
            await call.message.answer("Please enter a button text!", reply_markup=None)
            await state.set_state(Step.get_text_button)
        elif call.data == 'no_button':
            await call.message.edit_reply_markup(reply_markup=None)
            data = await state.get_data()
            message_id = int(data.get('message_id'))
            chat_id = int(data.get('chat_id'))
            await confirm(call.message, bot, message_id, chat_id)
    else:
        print(f'Current State is not q_button {current_state}')
        if current_state == Step.get_text_button:
            await get_text_button(call.message, state)

        if current_state == Step.get_url_button:
            await get_url_button(call.message, bot, state)    

        if current_state == Step.confirm_button:
            await sender_decide(call, bot, state, request)      

    await call.answer()     


async def get_text_button(message: Message, state: FSMContext):
    print('get_text_button')
    current_state = await state.get_state()
    if current_state == Step.get_text_button:
        print(f'Current state: {current_state}')
        await state.update_data(button_text = message.text)
        await message.answer(f"Please enter a button link!")
        await state.set_state(Step.get_url_button)
    else:
        print(f'Current State is not get_text_button {current_state}')



async def get_url_button(message: Message, bot: Bot, state: FSMContext): 
    current_state = await state.get_state()
    if current_state == Step.get_url_button:
        print(f'Current state: {current_state}')
        await state.update_data(button_text = message.text)

        data = await state.get_data()
        print(f'data: {data}')  
        button = data.get('button_text')
        print(f'button: {button}')
        url = message.text
        print(f'url: {url}')

        added_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=button,
                                          url=url)
                ]
            ]
        )
        
        message_id = int(data.get('message_id'))
        chat_id = int(data.get('chat_id'))
        await confirm(message, bot, message_id, chat_id, added_keyboard)
        await state.set_state(Step.confirm_button)
        
    else:
        print(f'Current State is not get_url_button {current_state}')


async def confirm(message: Message, bot: Bot, message_id: int, chat_id: int, reply_markup: InlineKeyboardMarkup = None):
    await bot.copy_message(chat_id=chat_id, from_chat_id=message.chat.id, message_id=message_id, reply_markup=reply_markup)
    await message.answer(f"Here is your campaign. Please confirm!", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Confirm", callback_data="confirm_sender")
            ],
            [
                InlineKeyboardButton(text="Cancel", callback_data="cancel_sender")
            ]
        ]
    ))


async def sender_decide(call: CallbackQuery, bot:Bot, state: FSMContext, request: Request, senderList: SenderList = None):
        data = await state.get_data()
        print(f'data: {data}')
        message_id = int(data.get('message_id'))
        chat_id = int(data.get('chat_id'))
        text_button = data.get('text_button')
        url_button = data.get('url_button')
        name_camp = data.get('name_camp')
        print(f'name_camp: {name_camp}')

        if call.data == 'confirm_sender':
            await call.message.edit_text(f"I start sending your campaign {name_camp}!")

            if not await request.check_table(name_camp):
                await request.create_table(name_camp)

            await call.message.answer(f"Your campaign {name_camp} was sent successfully!")

            count = await senderList(name_camp, chat_id, message_id, text_button, url_button)

            await call.message.answer(f"Your campaign {name_camp} was sent to {count} users!")

            # BREAKPOINT DOES NOT WORK HERE !!!
            # await request.delete_table(name_camp)    

            # print(f'TABLE {name_camp} was deleted!')

        elif call.data == 'cancel_sender':
            await call.message.edit_text(f"I cancel sending your campaign {name_camp}!")

        await state.clear()


