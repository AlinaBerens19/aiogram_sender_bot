import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
import asyncpg
from aiogram.utils.chat_action import ChatActionMiddleware
from core.utils.commands import set_commands
from core.middleware.settings import settings
from core.middleware.dbmiddleware import DbSession
from aiogram import F
from core.utils.sender_list import SenderList
from aiogram.enums import ParseMode
from core.handlers.new_sender import form_router, context
from aiogram.fsm.context import FSMContext
from core.utils.context import Context




async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, "Hey there! Please enter /start command to start bot!")

async def stop_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, "Bot Stopped Successfully!")

async def create_pool():
    return await asyncpg.create_pool(
        user='postgres',
        password='marsik19',
        host='127.0.0.1',
        port='5432',
        database='users',
        command_timeout=60
    )


async def start():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bots.token, parse_mode=ParseMode.HTML)

    dp = Dispatcher()

    # Inside the start() function
    try:
        pool = await create_pool()  # Call the create_pool function to get the pool object
        dp.update.middleware.register(DbSession(pool))  # Pass the pool object to DbSession
        dp.update.middleware.register(ChatActionMiddleware())

        sender_list_instance = SenderList(bot, pool)
        
        context.sender_list = sender_list_instance

        print(f'sender_list_instance in start: {context.sender_list}')
        
    except Exception as e:
        print(f'Exception {e} occurred during create middleware')
   

    # HANDLERS
    try:
        dp.startup.register(start_bot)
        dp.shutdown.register(stop_bot)

        dp.include_router(form_router)
        
        

    except Exception as e:
        logging.exception(f"Exception during registering handlers: {e}")

    try:
        await dp.start_polling(bot)
        print('Polling started!')
    except Exception as e:
        logging.exception(f"Exception during starting polling: {e}")
    finally:
        await stop_bot(bot)

if __name__ == '__main__':
    logging.basicConfig(filename='bot.log', level=logging.INFO)
    asyncio.run(start())