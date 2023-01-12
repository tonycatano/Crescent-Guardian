import discord
from discord import app_commands
from discord.ext import commands
from common.common import guildIDs
from common.GuildMission import updateFerridPieces
from common.GuildMission import updateMudsterPieces
from common.GuildMission import updateGarmothPieces
from common.GuildMission import genGMListEmbed

#--------------------------------------------------------------------------
# The gmscroll* group of commands
#--------------------------------------------------------------------------
class GMScrollCommands(commands.GroupCog,
                       name="gmscroll",
                       description="Update a boss scroll status"):

  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot

  #----------------------------------------------
  # ferrid
  #----------------------------------------------
  @app_commands.command(name="ferrid",
                        description="Update the Ferrid scroll status")
  @app_commands.describe(pieces="Enter the current number of scroll pieces")
  async def ferrid(self, interaction:discord.Interaction, pieces:int) -> None:
    await self.bot.logCommand(interaction)
    msg = await updateFerridPieces(pieces)
    emby = await genGMListEmbed()
    await interaction.response.send_message(content=msg, embed=emby)

  #----------------------------------------------
  # mudster
  #----------------------------------------------
  @app_commands.command(name="mudster",
                        description="Update the Mudster scroll status")
  @app_commands.describe(pieces="Enter the current number of scroll pieces")
  async def mudster(self, interaction:discord.Interaction, pieces:int) -> None:
    await self.bot.logCommand(interaction)
    msg = await updateMudsterPieces(pieces)
    emby = await genGMListEmbed()
    await interaction.response.send_message(content=msg, embed=emby)

  #----------------------------------------------
  # garmoth
  #----------------------------------------------
  @app_commands.command(name="garmoth",
                        description="Update the Garmoth scroll status")
  @app_commands.describe(pieces="Enter the current number of scroll pieces")
  async def garmoth(self, interaction:discord.Interaction, pieces:int) -> None:
    await self.bot.logCommand(interaction)
    msg = await updateGarmothPieces(pieces)
    emby = await genGMListEmbed()
    await interaction.response.send_message(content=msg, embed=emby)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GMScrollCommands(bot), guilds=guildIDs)
