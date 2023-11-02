import asyncpg
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from core.utils.dbconnect import Request
from typing import Callable, Awaitable, Dict, Any


# Middleware
class DbSession(BaseMiddleware):
    def __init__(self, connector: asyncpg.pool.Pool):
        super().__init__()
        self.connector = connector

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        print(f"Type of self.connector: {type(self.connector)}")
        if hasattr(self.connector, 'acquire'):
            print("self.connector has 'acquire' method")
        else:
            print("self.connector does not have 'acquire' method")
        
        async with self.connector.acquire() as connect:
            try:
                data['request'] = Request(connect)
                return await handler(event, data)
            except Exception as e:
                print(e)
