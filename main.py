import os
import discord
from discord.ext import commands
from common import guild_ids
import datetime
import asyncio

class MyBot(commands.Bot):
  def __init__(self):
    super().__init__(command_prefix='/',
                     case_insensitive=True, 
                     strip_after_prefix=True,
                     intents=discord.Intents.all(),
                     help_command=None,
                     application_id=os.environ['BOT_APP_ID'])

    self.synced = False
    self.connection_logfile = "logs/rocg.connection.log"
    self.command_logfile = "logs/rocg.command.log"
    self.db_lock = asyncio.Lock()

  async def setup_hook(self):
    filenames = [os.path.join(dp, f) for dp, dn, fn in os.walk("./cogs") for f in fn if f.endswith('.py')]
    for filename in filenames:
      extension = filename.replace("./", "").replace("/", ".").replace(".py", "")
      await self.load_extension(extension)
    if not self.synced:
      for guild_id in guild_ids:
        await self.tree.sync(guild=guild_id)

  async def on_ready(self):
    await self.log_connection("Logged in as " + str(self.user.name))
    print("\nLogged in as " + '\033[95m' + str(self.user.name) + '\033[0m')
    await self.change_presence(activity=discord.Activity(
      type=discord.ActivityType.watching, name="Guild"))

  async def on_command_error(self, ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
      print("Unrecognized Command")
      return
    raise error

  async def log_connection(self, msg:str):
    x = datetime.datetime.now()
    msg = str(x) + ": " + msg + "\n"
    f = open(my_bot.connection_logfile, "a")
    f.write(msg)
    f.close()

  async def log_command(self, cmd:str, usr:str):
    x = datetime.datetime.now()
    msg = str(x) + ": command:" + cmd + ", user:" + usr + "\n"
    f = open(my_bot.command_logfile, "a")
    f.write(msg)
    f.close()

try:
  my_bot = MyBot()
  my_bot.run(os.environ['BOT_TOKEN'])
except discord.errors.HTTPException:
  os.system("kill 1")