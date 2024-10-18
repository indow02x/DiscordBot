import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from extensions.core.errors import KeyNotFoundError


async def main() -> None:
    if DISCORD_BOT_TOKEN := os.getenv(key="DISCORD_BOT_TOKEN"):
        bot = commands.Bot(command_prefix="ud2test_", intents=discord.Intents.all(), help_command=None)
    elif DISCORD_BOT_TOKEN is None:
        raise KeyNotFoundError("DISCORD_BOT_TOKEN不在.env內")
    else: 
        assert False, "無法預期的錯誤"
    
    extension_load_tasks = [
        try_to_load_extension(bot=bot, extension=extension)
        for extension in os.listdir("./extensions") 
        if extension.endswith(".py")
        ]
    await asyncio.gather(*extension_load_tasks)

    await bot.start(DISCORD_BOT_TOKEN)

async def try_to_load_extension(bot: commands.Bot, extension: str) -> None:
    if not extension.endswith(".py"):   
        print(f"輸入值{extension}並沒有以'.py'結尾")
        return
    else:
        extension_name = extension[:-3]
    
    try:
        await bot.load_extension(f"extensions.{extension_name}")
    except commands.errors.ExtensionNotFound:
        print(f"模組{extension_name}不存在")
    except commands.errors.NoEntryPointError:
        print(f"模組{extension_name}沒有定義setup函數")
    except commands.errors.ExtensionFailed as extension_error:
        print(f"模組{extension_name}本身或調用模組的setup函數時出現問題\n問題：{extension_error.original}")
    except Exception as exception:
        print(f"發生無法預期的錯誤\n錯誤：{exception}")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
