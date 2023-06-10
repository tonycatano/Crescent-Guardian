import os
import discord
import datetime
from discord.ext import commands
from common.common import guildIDs
from common.common import connectionLogFile
from common.Sweeper import Sweeper
from common.Logger import Logger
from common.Format import Format as F
from gui.ContextMenu import ContextMenu
from gui.GMListPanel import GMListPanelView

class CrescentGuardianBot(commands.Bot):
  def __init__(self):
    super().__init__(command_prefix='/',
                     case_insensitive=True, 
                     strip_after_prefix=True,
                     intents=discord.Intents.all(),
                     help_command=None,
                     application_id=os.environ['BOT_APP_ID'])
    Logger.initLogger("EventLogger")
    self.contextMenu = ContextMenu(self)

  async def setup_hook(self):
    Logger.logInfo(self, "Booting " + str(self.user.name))
    Logger.logInfo(self, "Adding persistent view: GMListPanelView")
    self.add_view(GMListPanelView())
    Logger.logInfo(self, "Loading cogs:")
    cogs = [f'cogs.{f[:-3]}' for f in os.listdir('./cogs') if f.endswith('.py')]
    for cog in cogs:
      Logger.logInfo(self, cog)
      await self.load_extension(cog)
    Logger.logInfo(self, "Syncing bot commands:")
    for guild in guildIDs:
      Logger.logInfo(self, "Guild ID: " + str(guild.id))
      commands = await self.tree.sync(guild=guild)
    for command in commands:
      Logger.logInfo(self, "command: " + command.name)

  async def on_ready(self):
    msg = "Logged in as " + str(self.user.name)
    with open(connectionLogFile, "a") as file:
      file.write(str(datetime.datetime.now()) + ": " + msg + "\n")
    Logger.logInfo(self, msg)
    await Sweeper.sweepMessages(self)
    await self.change_presence(activity=discord.Activity(
      type=discord.ActivityType.watching, name="Guild"))
    msg = "------------------>READY"
    Logger.logInfo(self, msg)
    print(F.MAGENTA + msg + F.END)

  async def on_command_error(self, ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
      Logger.logError(self, "Unrecognized Command: " + str(error))
      return
    raise error

try:
  cgBot = CrescentGuardianBot()
  cgBot.run(os.environ['BOT_TOKEN'])
except Exception as error:
  print(F.RED + "\nException Encountered: "  + F.END + str(error) + "\n")
  os.system("kill 1")