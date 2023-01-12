import os
import discord
from discord.ext import commands
from common.common import guildIDs
from common.common import connectionLogFile
from common.common import commandLogFile
import datetime
import asyncio

class CrescentGuardianBot(commands.Bot):
  def __init__(self):
    super().__init__(command_prefix='/',
                     case_insensitive=True, 
                     strip_after_prefix=True,
                     intents=discord.Intents.all(),
                     help_command=None,
                     application_id=os.environ['BOT_APP_ID'])
    self.synced = False
    self.dbLock = asyncio.Lock()

  async def setup_hook(self):
    filenames = [os.path.join(dp, f) for dp, dn, fn in os.walk("./cogs") for f in fn if f.endswith('.py')]
    for filename in filenames:
      extension = filename.replace("./", "").replace("/", ".").replace(".py", "")
      await self.load_extension(extension)
    if not self.synced:
      for guild_id in guildIDs:
        await self.tree.sync(guild=guild_id)

  async def on_ready(self):
    await self.logConnection("Logged in as " + str(self.user.name))
    print("\nLogged in as " + '\033[95m' + str(self.user.name) + '\033[0m')
    await self.change_presence(activity=discord.Activity(
      type=discord.ActivityType.watching, name="Guild"))

  async def on_command_error(self, ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
      print("Unrecognized Command")
      return
    raise error

  async def logConnection(self, msg:str):
    x = datetime.datetime.now()
    msg = str(x) + ": " + msg + "\n"
    f = open(connectionLogFile, "a")
    f.write(msg)
    f.close()

  async def logCommand(self, interaction:discord.Interaction):
    timeStamp = str(datetime.datetime.now())
    user = ": " + interaction.user.name
    cmd = ": " + interaction.command.name
    msg = timeStamp + user + cmd + "\n"
    f = open(commandLogFile, "a")
    f.write(msg)
    f.close()

try:
  cgBot = CrescentGuardianBot()
  cgBot.run(os.environ['BOT_TOKEN'])
except discord.errors.HTTPException:
  os.system("kill 1")