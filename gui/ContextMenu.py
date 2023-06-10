import discord
from discord.ext import commands
from common.common import guildIDs
from common.common import userIdStub
from common.common import logCommand
from gui.GMListPanel import GMListPanel
# from gui.GMUpdatePanel import GMUpdatePanel
# from cogs.ScheduleCommand import SchedulePanel

#--------------------------------------------------------------------------
# Context Menu Commands
#--------------------------------------------------------------------------
class ContextMenu():
  def __init__(self, bot:commands.Bot) -> None:
    self.bot = bot

    # Display GM List
    @self.bot.tree.context_menu(name="Display GM List", guilds=guildIDs)
    async def displayGMList(interaction:discord.Interaction, message:discord.Message):
      await logCommand(interaction)
      content = "> " + userIdStub + " requested the GM list"
      gmListPanel = GMListPanel(interaction=interaction, content=content)
      await gmListPanel.run()

    # Save these two for a subsequent release
    # # Update GM List
    # @self.bot.tree.context_menu(name="Update GM List", guilds=guildIDs)
    # async def updateGMList(interaction:discord.Interaction, message:discord.Message):
    #   await logCommand(interaction)
    #   gmUpdatePanel = GMUpdatePanel(interaction=interaction)
    #   await gmUpdatePanel.run()

    # # Officer Schedule
    # @self.bot.tree.context_menu(name="Officer Schedule", guilds=guildIDs)
    # async def officerSchedule(interaction:discord.Interaction, message:discord.Message):
    #   await logCommand(interaction)
    #   schedulePanel = SchedulePanel(interaction=interaction)
    #   await schedulePanel.run()
