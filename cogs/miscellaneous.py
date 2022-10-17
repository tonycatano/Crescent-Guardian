import discord
from discord import app_commands
from discord.ext import commands
from common.common import guild_ids

class Miscellaneous(commands.Cog):
  def __init__(self, bot:commands.Bot) -> None:
    self.bot = bot
    self.emby_color=discord.Colour.blue()
    self.bot_cmds={
      # GUILD MISSON COMMANDS
      "/gmlist":["Display the GM request list",True],
      "/gmadd":["Add a GM request to the list",True],
      "/gmfound":["Indicate that a GM request has been found",True],
      "/gmedit":["Edit a GM request in the list",True],
      "/gmdelete":["Delete a GM request from the list",True],
      "/gmclear":["Clear the entire GM request list",True],
      "/gmgarmy":["Update the Garmoth Scroll Status",True],
      # MISCELLANEOUS COMMANDS
      #"/nightschedule":["Display the current Night Crew schedule",False],
      #"/help":"View all Crescent Guardian commands"
    }
    self.nightoffsched="```" \
      "Sun  -  Ginger\n" \
      "Mon  -  Postal\n" \
      "Tue  -  N/A\n" \
      "Wed  -  Lycos\n" \
      "Thu  -  N/A\n" \
      "Fri  -  N/A\n" \
      "Sat  -  Texi" \
      "```"

  #----------------------------------------------
  @app_commands.command(name="help",
                        description="View all Crescent Guardian commands")
  async def help(self, interaction:discord.Interaction) -> None:
    await self.bot.log_command("help", interaction.user.name)
    emby = discord.Embed(title="Crescent Guardian Commands",
                         colour=self.emby_color)
    for key in self.bot_cmds.keys():
      emby.add_field(name=key, value=self.bot_cmds[key][0], inline=self.bot_cmds[key][1])
    await interaction.response.send_message(embed=emby)

  #----------------------------------------------
  @app_commands.command(name="nightschedule",
                        description="Display the current Night Crew schedule")
  async def nightschedule(self, interaction:discord.Interaction) -> None:
    await self.bot.log_command("nightschedule", interaction.user.name)
    emby = discord.Embed(title="Night Off Schedule for Night Crew",
                         description=self.nightoffsched,
                         colour=self.emby_color)
    await interaction.response.send_message(embed=emby)

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Miscellaneous(bot), guilds=guild_ids)
