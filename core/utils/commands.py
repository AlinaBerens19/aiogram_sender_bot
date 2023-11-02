from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault




async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/stop", description="Stop the bot"),
        BotCommand(command="/sender", description="Create new campaign"),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


commands = set_commands