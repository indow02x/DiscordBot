import os
import datetime
from typing import Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands

from .core.class_init import ExtensionCog, BasicView

CommandType = Literal["導入", "移除", "重載"]
ViewRequestType = Literal["loaded_extensions", "all_extensions"]

class ExtensionManage(ExtensionCog):

    @app_commands.command(name="模組管理", description="可導入、移除、重載模組")
    @app_commands.guilds(ExtensionCog.get_test_guild())
    @app_commands.rename(command="指令")
    @app_commands.describe(command="請選擇想要執行的指令")
    async def extension_manage(self, interaction: discord.Interaction, command: CommandType) -> None:
        view = self.__get_view(
            interaction=interaction, 
            command=command
            )
        view.select.callback = self.__get_select_callback(view=view, command=command)
        await interaction.response.send_message(content=f"請選擇想{command}的模組", view=view)

    @app_commands.command(name="模組一覽", description="查看已導入的模組")
    @app_commands.guilds(ExtensionCog.get_test_guild())
    async def view_loaded_extensions(self, interaction: discord.Interaction) -> None:
        extensions_embed = self.__get_extensions_embed()
        await interaction.response.send_message(embed=extensions_embed)

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

    def __get_select_callback(self, view: "ExtensionSelectView", command: CommandType):
        async def callback(interaction: discord.Interaction):
            view.disable_on_timeout = True
            view.select.disabled = True
            view.select.placeholder = "/n".join(view.select.values)

            await view.ctx.edit_original_response(content=f"{command}處理中", view=view)
            await interaction.response.send_message(content=f"{view.select.placeholder}{command}中", ephemeral=True)

            if command == "導入":
                await self.__try_to_load(interaction=interaction, view=view)
            elif command == "移除":
                await self.__try_to_unload(interaction=interaction, view=view)
            elif command == "重載":
                await self.__try_to_reload(interaction=interaction, view=view)
            else:
                assert False, "無法預期的錯誤"

            await view.ctx.edit_original_response(content=f"{command}處理完畢", view=view)

        return callback

    def __get_view(self, interaction: discord.Interaction, command: CommandType) -> "ExtensionSelectView":  
        return ExtensionSelectView(
            timeout=30, 
            bot=self.bot, 
            interaction=interaction, 
            command=command
            )
    
    async def __try_to_load(self, *, interaction: discord.Interaction, view: "ExtensionSelectView"):
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

    async def __try_to_unload(self, *, interaction: discord.Interaction, view: "ExtensionSelectView"):
        try:
            await self.bot.unload_extension(f"extensions.{view.select.placeholder}")
        except commands.errors.ExtensionNotLoaded:
            await interaction.edit_original_response(content=f"模組{view.select.placeholder}沒有導入，無法移除")
        except Exception as exception:
            await interaction.edit_original_response(content=f"發生無法預期的錯誤\n錯誤：{exception}")
        else:
            await interaction.edit_original_response(content=f"模組{view.select.placeholder}移除成功")

    async def __try_to_reload(self, *, interaction: discord.Interaction, view: "ExtensionSelectView"):
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

class ExtensionSelectView(BasicView):

    ctx: discord.Interaction
    select: discord.ui.Select

    def __init__(
            self, 
            *, 
            timeout: Optional[float] = 180, 
            bot: commands.Bot,
            interaction: discord.Interaction, 
            command: CommandType
            ):
        super(ExtensionSelectView, self).__init__(timeout)
        self.bot = bot
        self.ctx = interaction
        self.__add_select(command=command)

    def __add_select(self, command: CommandType) -> None:
        if command == "導入":
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
        elif command == "移除" or command == "重載":
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
        else:
            assert False, "無法預期的錯誤"

        self.add_item(item=select)
        self.select = select

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ExtensionManage(bot=bot))

async def teardown(bot: commands.Bot) -> None:
    pass