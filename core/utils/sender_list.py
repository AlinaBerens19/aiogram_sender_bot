from aiogram import Bot
import asyncpg
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from typing import List
from asyncpg import Record
import asyncio
from aiogram.types import InlineKeyboardMarkup
from aiogram.exceptions import TelegramRetryAfter


class SenderList:
    def __init__(self, bot: Bot, connector: asyncpg.pool.Pool):
        self.bot = bot
        self.connector = connector


    from aiogram.types import InlineKeyboardButton

    async def get_keyboard(self, text_button, url_button):
        try:
            keyboard_builder = InlineKeyboardBuilder()
            button = InlineKeyboardButton(text=text_button, url=url_button)
            keyboard_builder.add(button)
            keyboard_builder.adjust()
            return keyboard_builder.as_markup()
        except Exception as e:
            print(f"Oops: {e}")
            return None

    

    async def get_users(self, name_camp):
        try:
            async with self.connector.acquire() as connect:
                query = f"""
                    SELECT user_id FROM {name_camp} WHERE status = 'waiting'
                """
                result_query: List[Record] = await connect.fetch(query)
                return [result.get('user_id') for result in result_query]
        except asyncpg.exceptions.UndefinedTableError as e:
            print(f"The table '{name_camp}' does not exist: {e}")
            return []  # Or take alternative actions as needed
        except asyncpg.exceptions.PostgresError as e:
            print(f"Postgres error: {e}")
            return []  # Or take alternative actions as needed
        except Exception as e:
            print(f"An error occurred: {e}")
            return []  # Or take alternative actions as neededded

    

    async def update_status(self, table_name, user_id, status, description):
        async with self.connector.acquire() as connect:
            query = f"""
                UPDATE {table_name} SET status = $1, description = $2 WHERE user_id = $3;
            """
            await connect.execute(query, status, description, user_id)



    async def send_message(self, user_id: int, from_chat_id: int, message_id: int, name_camp: str, keyboard: InlineKeyboardMarkup):
        try:
            await self.bot.copy_message(user_id, from_chat_id, message_id, reply_markup=keyboard)
            await self.update_status(name_camp, user_id, 'sent', 'message sent successfully')
            return True
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            return await self.send_message(user_id, from_chat_id, message_id, name_camp, keyboard)
        except Exception as e:
            await self.update_status(name_camp, user_id, 'error', str(e))
            # Log the error for debugging purposes
            print(f"Error sending message to user {user_id} for campaign {name_camp}: {e}")
            return False



    async def broadcaster(self, name_camp: str, from_chat_id: int, message_id: int, text_button: str = None, url_button: str = None):
        keyboard = None

        if text_button and url_button:
            keyboard = await self.get_keyboard(text_button, url_button)

        else:
            print("text_button or url_button is None. Check the data being stored in the state.")

        users_ids = await self.get_users(name_camp)
        print(f'users_ids: {users_ids}')

        count = 0
        try:
            for user_id in users_ids:
                if await self.send_message(user_id, from_chat_id, message_id, name_camp, keyboard):
                    count += 1
                await asyncio.sleep(0.05)    
        except Exception as e:
            print(f'Exception {e} occurred during broadcast')
        finally:
            print(f'{count} messages sent successfully!')    

        return count    





