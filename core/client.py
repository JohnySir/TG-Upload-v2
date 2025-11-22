import asyncio
from pyrogram import Client, enums
from .config import Config

class TgClient:
    bot = None
    user = None
    is_bot = True
    
    @classmethod
    async def start(cls, api_id, api_hash, bot_token=None, session_string=None):
        Config.API_ID = api_id
        Config.API_HASH = api_hash
        
        if bot_token:
            cls.is_bot = True
            Config.BOT_TOKEN = bot_token
            cls.bot = Client(
                "bot",
                api_id=api_id,
                api_hash=api_hash,
                bot_token=bot_token,
                in_memory=True,
                parse_mode=enums.ParseMode.HTML
            )
            await cls.bot.start()
            return cls.bot
            
        if session_string:
            cls.is_bot = False
            Config.USER_SESSION_STRING = session_string
            cls.user = Client(
                "user",
                api_id=api_id,
                api_hash=api_hash,
                session_string=session_string,
                in_memory=True,
                parse_mode=enums.ParseMode.HTML
            )
            await cls.user.start()
            return cls.user

    @classmethod
    async def stop(cls):
        if cls.bot:
            await cls.bot.stop()
        if cls.user:
            await cls.user.stop()

    @classmethod
    def get_client(cls):
        return cls.bot if cls.is_bot else cls.user
