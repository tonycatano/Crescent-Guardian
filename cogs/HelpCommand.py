import discord
from discord import app_commands
from discord.ext import commands
from common.common import guildIDs
from common.common import gmCommandList
from common.common import relNotesFile
from common.common import embyColour
from common.common import logCommand
from common.common import spacer
from common.common import getConfig
from common.Logger import Logger
from gui.CommonView import CommonView

#--------------------------------------------------------------
# HelpEmbed
#--------------------------------------------------------------
class HelpEmbed(discord.Embed):
  def __init__(self):
    super().__init__(colour=embyColour)
    self.imageURL = "https://www.dropbox.com/s/9t1xroelxn1gge8/HelpMenuShortClip2b-small.gif?raw=1"
    self.page = 1
    self.setPage()

  def addCommandInfo(self):
    for cmd in gmCommandList:
      self.add_field(name=spacer(1) + "/" + cmd.name, 
                     value=spacer(1) + " " + cmd.descr, 
                     inline=False)

  def readReleaseNotes(self) -> str:
    with open(relNotesFile, "r") as file:
      relNotes = file.read()
    return relNotes

  def setPage(self):
    if self.page == 1:
      self.clear_fields()
      self.description = spacer(7) + "**Crescent Guardian**\n" + \
                         spacer(9) + "**Graphical UI**"
      self.set_image(url=self.imageURL)
    elif self.page == 2:
      self.clear_fields()
      self.description = spacer(7)  + "**Crescent Guardian**\n" + \
                         spacer(10) + "**Commands**" + spacer(10)
      self.addCommandInfo()
      self.set_image(url="")
    elif self.page == 3:
      self.clear_fields()
      self.description = spacer(7) + "**Crescent Guardian**\n" + \
                         spacer(3) + " " + spacer(3) + " " + \
                         "**2.0.0 Release Notes\n\n**"
      self.description += self.readReleaseNotes()
      self.set_image(url="")
    else:
      Logger.logError(self, "Unsupported help page")

#--------------------------------------------------------------
# HelpPanel
#--------------------------------------------------------------
class HelpPanel():
  def __init__(self, timeout, interaction:discord.Interaction):
    self.interaction = interaction
    self.emby = HelpEmbed()
    self.view = CommonView(timeout=timeout)
    self.view.cancelButton.label = "Dismiss"
    self.view.addCancelButton()
    self.leftArrowButton = discord.ui.Button(label="◁", style=discord.ButtonStyle.primary)
    self.rightArrowButton = discord.ui.Button(label="▷", style=discord.ButtonStyle.primary)
    self.leftArrowButton.callback = self.leftArrowButtonCallback
    self.rightArrowButton.callback = self.rightArrowButtonCallback
    self.view.add_item(self.leftArrowButton)
    self.view.add_item(self.rightArrowButton)
    self.view.on_timeout = self.view.removeViewOnTimeout

  async def leftArrowButtonCallback(self, interaction:discord.Interaction):
    self.emby.page = 3 if self.emby.page == 1 else self.emby.page - 1
    self.emby.setPage()
    await interaction.response.edit_message(embed=self.emby, view=self.view)

  async def rightArrowButtonCallback(self, interaction:discord.Interaction):
    self.emby.page = 1 if self.emby.page == 3 else self.emby.page + 1
    self.emby.setPage()
    await interaction.response.edit_message(embed=self.emby, view=self.view)

  async def run(self):
    await self.interaction.response.send_message(view=self.view, embed=self.emby,
                                                 ephemeral=getConfig('helpPrivate'))
    self.view.parentMsg = await self.interaction.original_response()

#--------------------------------------------------------------
# HelpCommand
#--------------------------------------------------------------
class HelpCommand(commands.Cog):
  def __init__(self, bot:commands.Bot) -> None:
    self.bot = bot

  @app_commands.command(name="help", description="View all Crescent Guardian commands")
  async def help(self, interaction:discord.Interaction) -> None:
    await logCommand(interaction)
    
    helpPanel = HelpPanel(timeout=getConfig('helpTimeout'),
                          interaction=interaction)
    await helpPanel.run()

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(HelpCommand(bot), guilds=guildIDs)
