import discord
from discord import app_commands
from discord.ext import commands
from common.common import guildIDs
from common.common import botCmds
from common.common import relNotesFile

#--------------------------------------------------------------
# HelpEmbed
#--------------------------------------------------------------
class HelpEmbed(discord.Embed):

  def __init__(self):
    super().__init__(title="**Crescent Guardian Commands**",
                     colour=discord.Colour.blue())
    self.addCmdDescriptions()
    self.relNotesHeader = self.initRelNotesHeader()
    self.relNotes = self.initRelNotes()
    self.relNotesVisible = False
    self.relNotesIndex = 0

  def addCmdDescriptions(self):
    for key in botCmds.keys():
      self.add_field(name=key, value=botCmds[key][0],inline=botCmds[key][1])

  def initRelNotesHeader(self) -> str:
    hdr = "__"
    for i in range(77):
      hdr += " "
    hdr += "__"
    return hdr

  def initRelNotes(self) -> str:
    f = open(relNotesFile, "r")
    relNotes = f.read()
    f.close()
    return relNotes

  async def toggleRelNotes(self):
    if self.relNotesVisible:
      self.remove_field(self.relNotesIndex)
    else:
      self.add_field(name=self.relNotesHeader, value=self.relNotes, inline=False)
      self.relNotesIndex = len(self.fields) - 1
    self.relNotesVisible = not self.relNotesVisible

#--------------------------------------------------------------
# HelpPanel
#--------------------------------------------------------------
class HelpPanel():

  def __init__(self, timeout, interaction:discord.Interaction):
    self.intMsg = None
    self.interaction = interaction
    self.emby = HelpEmbed()
    self.view = discord.ui.View(timeout=timeout)
    self.button = discord.ui.Button(label="Release Notes ▼", style=discord.ButtonStyle.secondary)
    self.button.callback = self.button_callback
    self.view.add_item(self.button)
    self.view.on_timeout = self.on_timeout

  async def button_callback(self, interaction:discord.Interaction):
    await interaction.response.defer()
    await self.emby.toggleRelNotes()
    self.button.label = "Release Notes ▲" if self.emby.relNotesVisible else "Release Notes ▼"
    await self.intMsg.edit(embed=self.emby, view=self.view)
    await self.view.wait()

  async def on_timeout(self) -> None:
    self.view.clear_items()
    await self.intMsg.edit(view=self.view)

  async def run(self):
    await self.interaction.response.send_message(view=self.view, embed=self.emby, ephemeral=True)
    self.intMsg = await self.interaction.original_response()
    await self.view.wait()

#--------------------------------------------------------------
# HelpCommand
#--------------------------------------------------------------
class HelpCommand(commands.Cog):
  def __init__(self, bot:commands.Bot) -> None:
    self.bot = bot
    self.timeout = 60 # seconds

  @app_commands.command(name="help", description="View all Crescent Guardian commands")
  async def help(self, interaction:discord.Interaction) -> None:
    await self.bot.logCommand(interaction)
    helpPanel = HelpPanel(timeout=self.timeout, interaction=interaction)
    await helpPanel.run()

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(HelpCommand(bot), guilds=guildIDs)
