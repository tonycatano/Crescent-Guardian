import discord
from discord import app_commands
from discord.ext import commands
from common.common import guildIDs
from common.common import officerSchedFile

class ScheduleCommand(commands.Cog):
  def __init__(self, bot:commands.Bot) -> None:
    self.bot = bot
    self.embyColor=discord.Colour.blue()

  async def readOfficerSchedule(self) -> str:
    f = open(officerSchedFile, "r")
    sched = f.read()
    f.close()
    return sched

  @app_commands.command(name="schedule",
                        description="Display the officer schedule")
  async def schedule(self, interaction:discord.Interaction) -> None:
    await self.bot.logCommand(interaction)
    sched = await self.readOfficerSchedule()
    emby = discord.Embed(title="**Night Off Schedule for Night Crew**",
                         description=sched,
                         colour=self.embyColor)
    await interaction.response.send_message(embed=emby, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(ScheduleCommand(bot), guilds=guildIDs)
