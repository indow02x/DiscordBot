import os
from typing import Callable, Optional, NoReturn

import discord
from discord.ext import commands 

from .errors import KeyNotFoundError, NotAllowedError 


class ExtensionCog(commands.Cog):

    def __init__(self, *, bot: commands.Bot) -> None:
        if type(self) is ExtensionCog:
            raise NotAllowedError("類別ExtensionCog不允許實例化")
        else:
            self.bot = bot

    def __init_subclass__(cls, **kwarg) -> None:
        for func_name in ["get_test_guild", "get_bot_icon"]:
            setattr(
                cls, 
                func_name, 
                ExtensionCog.__illegal_call(func_name)
                )

    @staticmethod
    def get_test_guild() -> discord.abc.Snowflake:
        if test_guild_id := os.getenv(key="TEST_GUILD_ID"):
            return discord.Object(id=test_guild_id)
        elif test_guild_id is None:
            raise KeyNotFoundError("TEST_GUILD_ID不在.env內")
        else:
            assert False, "無法預期的錯誤"

    @staticmethod
    def get_bot_icon() -> Optional[str]:
        return os.getenv(key="BOT_ICON_URL")

    @staticmethod    
    def __illegal_call(func_name: str) -> Callable[[], NoReturn]:
        @staticmethod
        def call() -> NoReturn:
            raise NotAllowedError(f"子類與物件不能調用{func_name}函數")
        return call

class BasicView(discord.ui.View):

    ctx: Optional[discord.Interaction]
    disable_on_timeout: bool

    def __init__(self, timeout: Optional[float] = 180) -> None:
        super().__init__(timeout=timeout)
        self.ctx = None
        self.disable_on_timeout = False
        
    async def on_timeout(self) -> None:
        if self.ctx and not self.disable_on_timeout:
            await self.ctx.edit_original_response(content="已超時", view=None)

