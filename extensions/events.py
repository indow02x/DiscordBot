from discord.ext import commands

from .core.class_init import ExtensionCog


class Event(ExtensionCog):

    @commands.Cog.listener(name="on_ready")
    async def when_on_ready(self) -> None:
        await self.bot.tree.sync(guild=ExtensionCog.get_test_guild())
        print("啟動完成")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Event(bot=bot))

async def teardown(bot: commands.Bot) -> None:
    pass