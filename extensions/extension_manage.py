import os
import datetime
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from .core.class_init import ExtensionCog, BasicView

ViewRequestType = Literal["loaded_extensions", "all_extensions"]

class ExtensionManage(ExtensionCog):

    @app_commands.command(name="導入", description="Bot運行時載入模組")
    @app_commands.guilds(ExtensionCog.get_test_guild())
    async def load_extension(self, interaction: discord.Interaction) -> None:
        view = self.__get_view(
            interaction=interaction, 
            type_="all_extensions"
            )

        async def select_callback(interaction: discord.Interaction) -> None:
            view.on_select_used()

            await view.ctx.edit_original_response(content="導入處理中", view=view)
            await interaction.response.send_message(content=f"{view.select.placeholder}導入中", ephemeral=True)
            try:
                await self.bot.load_extension(f"extensions.{view.select.placeholder}")
            except commands.errors.ExtensionAlreadyLoaded:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}已經成功導入")
            except commands.errors.ExtensionNotFound:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}不存在")
            except commands.errors.NoEntryPointError:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}沒有定義setup函數")
            except commands.errors.ExtensionFailed as extension_error:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}本身或調用模組的setup函數時出現問題\n問題：{extension_error.original}")
            except Exception as exception:
                await interaction.edit_original_response(content=f"發生無法預期的錯誤\n錯誤：{exception}")
            else:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}導入成功")
            finally:
                await view.ctx.edit_original_response(content="導入處理完畢", view=view)
        view.select.callback = select_callback

        await interaction.response.send_message(content="請選擇想導入的模組", view=view)    

    @app_commands.command(name="移除", description="Bot運行時移除模組")
    @app_commands.guilds(ExtensionCog.get_test_guild())
    async def unload_extension(self, interaction: discord.Interaction) -> None:
        view = self.__get_view(
            interaction=interaction, 
            type_="loaded_extensions"
            )

        async def select_callback(interaction: discord.Interaction) -> None:
            view.on_select_used()

            await view.ctx.edit_original_response(content="移除處理中", view=view)
            await interaction.response.send_message(content=f"{view.select.placeholder}移除中", ephemeral=True)
            try:
                await self.bot.unload_extension(f"extensions.{view.select.placeholder}")
            except commands.errors.ExtensionNotLoaded:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}沒有導入，無法移除")
            except Exception as exception:
                await interaction.edit_original_response(content=f"發生無法預期的錯誤\n錯誤：{exception}")
            else:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}移除成功")
            finally:
                await view.ctx.edit_original_response(content="移除處理完畢", view=view)
        view.select.callback = select_callback

        await interaction.response.send_message(content="請選擇想移除的模組", view=view)    

    @app_commands.command(name="重載", description="Bot運行時更新模組")
    @app_commands.guilds(ExtensionCog.get_test_guild())
    async def reload_extension(self, interaction: discord.Interaction) -> None:
        view = self.__get_view(
            interaction=interaction, 
            type_="loaded_extensions"
            )

        async def select_callback(interaction: discord.Interaction) -> None:
            view.on_select_used()

            await view.ctx.edit_original_response(content="重載處理中", view=view)
            await interaction.response.send_message(content=f"{view.select.placeholder}重載中", ephemeral=True)
            try:
                await self.bot.reload_extension(f"extensions.{view.select.placeholder}")
            except commands.errors.ExtensionNotLoaded:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}沒有導入，無法重載")
            except commands.errors.NoEntryPointError:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}沒有定義setup函數")
            except commands.errors.ExtensionFailed as extension_error:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}本身或調用模組的setup函數時出現問題\n問題：{extension_error.original}")
            except Exception as exception:
                await interaction.edit_original_response(content=f"發生無法預期的錯誤\n錯誤：{exception}")
            else:
                await interaction.edit_original_response(content=f"模組{view.select.placeholder}重載成功")
            finally:
                await view.ctx.edit_original_response(content="重載處理完畢", view=view)
        view.select.callback = select_callback

        await interaction.response.send_message(content="請選擇想重載的模組", view=view)    

    @app_commands.command(name="同步", description="Bot運行時同步指令")
    @app_commands.guilds(ExtensionCog.get_test_guild())
    async def sync_commands(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(content="指令同步中")
        try:
            await self.bot.tree.sync(guild=ExtensionCog.get_test_guild())
        except Exception as exception:
            await interaction.edit_original_response(content=f"發生無法預期的錯誤\n錯誤:{exception}")
        else:
            await interaction.edit_original_response(content="同步成功")

    @app_commands.command(name="模組一覽", description="查看已導入的模組")
    @app_commands.guilds(ExtensionCog.get_test_guild())
    async def view_loaded_extensions(self, interaction: discord.Interaction) -> None:
        extensions_embed = self.__get_extensions_embed()
        await interaction.response.send_message(embed=extensions_embed)

    def __get_view(self, interaction: discord.Interaction, type_: ViewRequestType) -> "ExtensionSelectView":  
        return ExtensionSelectView(
            timeout=30, 
            bot=self.bot, 
            interaction=interaction, 
            type_=type_
            )

    def __get_extensions_embed(self) -> discord.Embed:
        loaded_extension = "\n".join(key[11:] for key in self.bot.extensions.keys())
        embed = discord.Embed(
            title="模組一覽",
            description=loaded_extension,
            timestamp=datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))
            )
        embed.set_author(
            name=self.bot.application.name if self.bot.application else "",
            icon_url=ExtensionCog.get_bot_icon()
            )
        return embed

class ExtensionSelectView(BasicView):

    ctx: discord.Interaction
    select: discord.ui.Select

    def __init__(
            self, 
            *, 
            timeout: float | None = 180, 
            bot: commands.Bot,
            interaction: discord.Interaction, 
            type_: ViewRequestType
            ):
        super(ExtensionSelectView, self).__init__(timeout)
        self.bot = bot
        self.ctx = interaction
        self.__add_select(type_=type_)

    def __add_select(self, type_: ViewRequestType) -> None:
        if type_ == "loaded_extensions":
            select = discord.ui.Select(
                placeholder="模組名稱",
                options=[
                    discord.SelectOption(label=extension[11:], value=extension[11:]) 
                    for extension 
                    in self.bot.extensions.keys()
                    ],
                max_values=1,
                min_values=1
                )
        elif type_ == "all_extensions":
            select = discord.ui.Select(
                placeholder="模組名稱",
                options=[
                    discord.SelectOption(label=extension[:-3], value=extension[:-3]) 
                    for extension in os.listdir("./extensions") 
                    if extension.endswith(".py")
                    ],
                max_values=1,
                min_values=1
                )
        else:
            assert False, "無法預期的錯誤"

        self.add_item(item=select)
        self.select = select

    def on_select_used(self) -> None:
        self.disable_on_timeout = True
        self.select.disabled = True
        self.select.placeholder = "/n".join(self.select.values)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ExtensionManage(bot=bot))

async def teardown(bot: commands.Bot) -> None:
    pass