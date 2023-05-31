import discord
from discord import app_commands
from discord.ext import commands
from common.common import guildIDs
from common.GMPrompts import GMPrompts as gmp
from common.GuildMission import ScrollPieces
from common.GuildMission import getScrollPieces
from common.GuildMission import updateBossScrollPieces
from common.common import sendErrorMessage
from common.common import logCommand
from gui.GMListPanel import GMListPanel

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
  @app_commands.describe(pieces=gmp.ferridPrompt)
  async def ferrid(self, interaction:discord.Interaction, pieces:str) -> None:
    await logCommand(interaction)
    scrollPieces = getScrollPieces()
    scrollPieces.ferrid = pieces
    result = await updateBossScrollPieces(scrollPieces)    
    if result.good:
      gmListPanel = GMListPanel(interaction=interaction, content=result.msg)
      await gmListPanel.run()
    else:
      await sendErrorMessage(interaction=interaction, content=result.msg)

  #----------------------------------------------
  # mudster
  #----------------------------------------------
  @app_commands.command(name="mudster",
                        description="Update the Mudster scroll status")
  @app_commands.describe(pieces=gmp.mudsterPrompt)
  async def mudster(self, interaction:discord.Interaction, pieces:str) -> None:
    await logCommand(interaction)
    scrollPieces = getScrollPieces()
    scrollPieces.mudster = pieces
    result = await updateBossScrollPieces(scrollPieces)    
    if result.good:
      gmListPanel = GMListPanel(interaction=interaction, content=result.msg)
      await gmListPanel.run()
    else:
      await sendErrorMessage(interaction=interaction, content=result.msg)

  #----------------------------------------------
  # garmoth
  #----------------------------------------------
  @app_commands.command(name="garmoth",
                        description="Update the Garmoth scroll status")
  @app_commands.describe(pieces=gmp.garmothPrompt)
  async def garmoth(self, interaction:discord.Interaction, pieces:str) -> None:
    await logCommand(interaction)
    scrollPieces = getScrollPieces()
    scrollPieces.garmoth = pieces
    result = await updateBossScrollPieces(scrollPieces)    
    if result.good:
      gmListPanel = GMListPanel(interaction=interaction, content=result.msg)
      await gmListPanel.run()
    else:
      await sendErrorMessage(interaction=interaction, content=result.msg)

  #----------------------------------------------
  # clear
  #----------------------------------------------
  @app_commands.command(name="clear",
                        description="Set all scroll pieces to zero")
  async def clear(self, interaction:discord.Interaction) -> None:
    await logCommand(interaction)
    scrollPieces = ScrollPieces(garmoth=0, ferrid=0, mudster=0)
    result = await updateBossScrollPieces(scrollPieces)
    if result.good:
      gmListPanel = GMListPanel(interaction=interaction, content=result.msg)
      await gmListPanel.run()
    else:
      await sendErrorMessage(interaction=interaction, content=result.msg)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GMScrollCommands(bot), guilds=guildIDs)
