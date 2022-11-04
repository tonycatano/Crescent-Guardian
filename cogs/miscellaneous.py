import discord
from discord import app_commands
from discord.ext import commands
from common.common import guildIDs

class Miscellaneous(commands.Cog):
  def __init__(self, bot:commands.Bot) -> None:
    self.bot = bot
    self.embyColor=discord.Colour.blue()

    self.releaseNotes="**Crescent Guardian 1.1.0 Release Notes**\n" \
      "First a quick FYI so that the notes below are more clear. A fully qualified GM consists " \
      "of three fields: `name`, `server`, `size`.\n\n" \
      "The **/gmadd** command now allows you to populate all three GM fields. The `name` field is required, " \
      "but the other two fields are optional. \n\n" \
      "Likewise, the **/gmedit** command now gives you the option to edit any of the three GM fields. You " \
      "can edit all three, or just one, or none. It’s very flexible now. \n\n" \
      "For simplicity, the **/gmadd** command takes only one GM now. However, to retain some of the " \
      "functionality that **/gmadd** used to have, a new command called **/gmquickadd** is now available. \n\n" \
      "The new **/gmquickadd** command allows you to add a bunch of GM names at once. Note, only `name` values. No " \
      "`server` or `size` info.\n\n" \
      "Final note: The enhancements to **/gmadd** and **/gmedit** have subsumed all of the functionality of " \
      "the **/gmfound** command. Therefore, **/gmfound** is no longer available. \n\n" \
      "**Crescent Guardian Commands**\n"

    self.botCmds={
      # GUILD MISSON COMMANDS
      "/gmlist":["Display the GM list",True],
      "/gmadd":["Add a GM to the list",True],
      "/gmedit":["Edit a GM in the list",True],
      "/gmdelete":["Delete a GM from the list",True],
      "/gmclear":["Clear the entire GM list",True],
      "/gmquickadd":["Add several GM `names` to the list",True],
      "/gmgarmy":["Update the Garmoth Scroll Status",True],
      # MISCELLANEOUS COMMANDS
      #"/nightschedule":["Display the current Night Crew schedule",False],
      #"/help":"View all Crescent Guardian commands"
    }

    self.nightOffSched="```" \
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
    await self.bot.logCommand("help", interaction.user.name)
    emby = discord.Embed(description=self.releaseNotes,
                         colour=self.embyColor)
    for key in self.botCmds.keys():
      emby.add_field(name=key, value=self.botCmds[key][0], inline=self.botCmds[key][1])
    await interaction.response.send_message(embed=emby)

  #----------------------------------------------
  @app_commands.command(name="nightschedule",
                        description="Display the current Night Crew schedule")
  async def nightschedule(self, interaction:discord.Interaction) -> None:
    await self.bot.logCommand("nightschedule", interaction.user.name)
    emby = discord.Embed(title="Night Off Schedule for Night Crew",
                         description=self.nightOffSched,
                         colour=self.embyColor)
    await interaction.response.send_message(embed=emby)

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Miscellaneous(bot), guilds=guildIDs)
