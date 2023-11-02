from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from core.utils.sender_list import SenderList
from core.utils.sender_state import Step
from core.utils.dbconnect import Request
from core.utils.commands import set_commands
from core.keyboards.inline import get_confirm_keyboard
from core.middleware.settings import settings
from core.utils.context import Context
import asyncio


form_router = Router()

context: Context = Context()

@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Step.initial)
    await message.answer(
        "Hi there!"
    )
    await message.answer(
        "To create new commercial please enter /sender command and name of your campaign!"
    )


@form_router.message(Step.initial, Command('sender'))
async def get_started(message: Message, bot: Bot, state: FSMContext, command: CommandObject):

    if not command.args:
        await message.answer("Hey there! To create new commercial please enter /sender command and name of your campaign!")

    else:
        await message.answer(f"Let's start! Your campaign name is {command.args} \n Please enter a message for your campaign!")
        await state.update_data(name_camp = command.args)
        await state.set_state(Step.get_message)


@form_router.message(Step.get_message)
async def get_message(message: Message, state: FSMContext):

    await message.answer(f"Your message is {message.text} \n Would you like to add a button?", reply_markup=get_confirm_keyboard())
    await state.update_data(message_id = message.message_id, chat_id = message.from_user.id)
    await state.set_state(Step.get_button_or_continue)



@form_router.callback_query(Step.get_button_or_continue)
async def get_text_button(call: CallbackQuery, state: FSMContext, bot: Bot):
    # Ensure the callback type is CallbackQuery, not Message
    if call.data == 'add_button':
        await call.message.answer("Please enter a button text!", reply_markup=None)
        await state.set_state(Step.get_text_for_button)
        await call.answer() 
    elif call.data == 'no_button':
        await call.message.edit_reply_markup(reply_markup=None)
        data = await state.get_data()
        message_id = int(data.get('message_id'))
        chat_id = int(data.get('chat_id'))
        await confirm(call.message, bot, message_id, chat_id)
        await call.answer() 
        await state.set_state(Step.confirm_or_cancel)



@form_router.message(Step.get_text_for_button)
async def get_url_button(message: Message, state: FSMContext):
    await state.update_data(text_button = message.text)
    print(f"button_text: {message.text}")
    await message.answer(f"Please enter a button link!")
    await state.set_state(Step.get_url_for_button)



@form_router.message(Step.get_url_for_button)
async def confirm_campaign(message: Message, bot: Bot, state: FSMContext):
    print('Inside confirm_campaign')  # Add a print statement to verify the function is reached
    try:
        data = await state.get_data()
        print(f'State data before update: {data}')  # Verify the state data before updating

        await state.update_data(url_button=message.text)
        data = await state.get_data()
        print(f'State data after update: {data}')  # Verify the state data after updating

        url = message.text
        

        if url:
            # Assuming the button text is already in state data
            button = data.get('text_button')
            print(f'button: {button}')  # Log the received button text
            print(f'url: {url}')  # Log the received URL

            added_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=button, url=url)
                    ]
                ]
            )

            message_id = int(data.get('message_id'))
            chat_id = int(data.get('chat_id'))
            await confirm(message, bot, message_id, chat_id, added_keyboard)
            await state.set_state(Step.confirm_or_cancel)
        else:
            print("URL is None. Check the data being stored in the state.")
    except Exception as e:
        print(f"An error occurred: {e}")




@form_router.callback_query(Step.confirm_or_cancel)
async def sender_decide(call: CallbackQuery, bot: Bot, state: FSMContext, request: Request):
    print('Inside sender_decide')  # Add a print statement to verify the function is reached
    print(f"Callback data: {call.data}")  # Print callback data for verification
    
    data = await state.get_data()
    message_id = int(data.get('message_id'))
    chat_id = int(data.get('chat_id'))
    text_button = data.get('text_button')
    url_button = data.get('url_button')
    name_camp = data.get('name_camp')
    print(f'data: {data}')

    if call.data == 'confirm_sender':
        await call.message.edit_text(f"I start sending your campaign {name_camp}!")

        if not await request.check_table(name_camp):
            await request.create_table(name_camp)

        await call.message.answer(f"Your campaign {name_camp} was sent successfully!")

        global context
        print(f'sender_list_instance in handler: {context.sender_list}')

        try:
            count = await context.sender_list.broadcaster(name_camp, chat_id, message_id, text_button, url_button)

            print(f'count: {count}')

            await call.message.answer(f"Your campaign {name_camp} was sent to {count} users!")

            await request.delete_table(name_camp)
            print(f'TABLE {name_camp} was deleted!')
 
        except Exception as e:
            print(f'Exception {e} occurred during sender_list_instance')

    elif call.data == 'cancel_sender':
        await call.message.edit_text(f"I cancel sending your campaign {name_camp}!")

    await state.clear()




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

    