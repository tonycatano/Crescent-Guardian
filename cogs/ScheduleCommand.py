import discord
import json
from discord import app_commands
from discord.ext import commands
from common.common import guildIDs
from common.common import officerSchedFile
from common.common import logCommand
from common.common import getConfig
from common.Logger import Logger
from gui.CommonView import CommonView

#--------------------------------------------------------------
# SchedulePanel
#--------------------------------------------------------------
class SchedulePanel():
  def __init__(self, interaction:discord.Interaction):
    self.interaction = interaction
    self.view = CommonView(timeout=getConfig('scheduleTimeout'))
    self.view.cancelButton.label = "Dismiss"
    self.view.addCancelButton()
    with open(officerSchedFile, 'r') as f:
      data = json.load(f)
    self.emby = discord.Embed.from_dict(data)
    self.view.on_timeout = self.view.removeViewOnTimeout

  async def run(self):
    await self.interaction.response.send_message(view=self.view, embed=self.emby,
                                                 ephemeral=getConfig('schedulePrivate'))
    self.view.parentMsg = await self.interaction.original_response()

#--------------------------------------------------------------
# ScheduleCommand
#--------------------------------------------------------------
class ScheduleCommand(commands.Cog):
  def __init__(self, bot:commands.Bot) -> None:
    self.bot = bot

  @app_commands.command(name="schedule",
                        description="Display the officer schedule")
  async def schedule(self, interaction:discord.Interaction) -> None:
    await logCommand(interaction)
    schedulePanel = SchedulePanel(interaction=interaction)
    await schedulePanel.run()

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(ScheduleCommand(bot), guilds=guildIDs)
