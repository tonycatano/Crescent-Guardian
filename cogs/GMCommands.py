import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from typing import List
from common.common import guildIDs
from common.common import serverListFile
from common.GuildMission import GuildMission
from common.GuildMission import noServer
from common.GuildMission import noSize
from common.GuildMission import genGMListEmbed
from common.GuildMission import addGMReqEntries
from common.GuildMission import getGMList
from common.GuildMission import editGMReqEntry
from common.GuildMission import deleteGMReqEntry
from common.GuildMission import clearGMReqTable

#--------------------------------------------------------------------------
# The main set of gm* commands
#--------------------------------------------------------------------------
class GMCommands(commands.Cog):
  def __init__(self, bot:commands.Bot) -> None:
    self.bot = bot

  async def readServerList(self) -> str:
    f = open(serverListFile, "r")
    servers = f.read().splitlines()
    f.close()
    return servers

  #----------------------------------------------
  # gmlist
  #----------------------------------------------
  @app_commands.command(name="gmlist",
                        description="Display the GM list")
  async def gmlist(self, interaction:discord.Interaction) -> None:
    await self.bot.logCommand(interaction)
    emby = await genGMListEmbed()
    await interaction.response.send_message(embed=emby)

  #----------------------------------------------
  # gmadd
  #----------------------------------------------
  @app_commands.command(name="gmadd", description="Add a GM to the list")
  @app_commands.describe(name   = "Enter a GM name (ex. Pollys - Patty)",
                         server = "Enter the GM server",
                         size   = "Enter the GM size")
  async def gmadd(self, interaction:discord.Interaction,
                  name:str, server:str=None, size:str=None) -> None:
    await self.bot.logCommand(interaction)
    guildMissions = [GuildMission(name,server,size)]
    msg = await addGMReqEntries(guildMissions)
    emby = await genGMListEmbed()
    await interaction.response.send_message(content=msg, embed=emby)

  @gmadd.autocomplete('server')
  async def gmadd_autocomplete_server(self, interaction: discord.Interaction,
                                      current: str) -> List[Choice[str]]:
    gmServers = await self.readServerList()
    return [Choice(name=server, value=server)
            for server in gmServers if current.lower() in server.lower() and server != noServer]

  #----------------------------------------------
  # gmedit
  #----------------------------------------------
  @app_commands.command(name="gmedit", description="Edit a GM in the list")
  @app_commands.describe(gm = "Select the GM to edit")
  @app_commands.describe(name = "Enter a GM name (ex. Pollys - Patty)")
  @app_commands.describe(server = "Enter the GM server (Select " + noServer + " to erase the current server)")
  @app_commands.describe(size = "Enter the GM size (Select " + noSize + " to erase the current size)")
  async def gmedit(self, interaction: discord.Interaction, gm:str,
                   server:str=None, size:str=None, name:str=None):
    await self.bot.logCommand(interaction)
    msg = await editGMReqEntry(gm, name, server, size)
    if msg:
      emby = await genGMListEmbed()
      await interaction.response.send_message(content=msg, embed=emby)
    else:
      await interaction.response.send_message(
        content=f':frowning: Sorry, there is no GM in the list called **{gm}**')

  @gmedit.autocomplete('gm')
  async def gmedit_autocomplete_gm(self, interaction: discord.Interaction,
                                   current: str) -> List[Choice[str]]:
    gmList = await getGMList()
    return [Choice(name=gm, value=gm)
            for gm in gmList if current.lower() in gm.lower()]
                      
  @gmedit.autocomplete('server')
  async def gmedit_autocomplete_server(self, interaction: discord.Interaction,
                                       current: str) -> List[Choice[str]]:
    gmServers = await self.readServerList()
    return [Choice(name=server, value=server)
            for server in gmServers if current.lower() in server.lower()]

  @gmedit.autocomplete('size')
  async def gmedit_autocomplete_size(self, interaction: discord.Interaction,
                                     current: str) -> List[Choice[str]]:
    gmSizes = ["-ERASE-"]
    return [Choice(name=size, value=size)
            for size in gmSizes if current.lower() in size.lower()]

  #----------------------------------------------
  # gmdelete
  #----------------------------------------------
  @app_commands.command(name="gmdelete",
                        description="Delete a GM from the list")
  @app_commands.describe(gm = "Select the GM to delete")
  async def gmdelete(self, interaction: discord.Interaction, gm:str):
    await self.bot.logCommand(interaction)
    msg = await deleteGMReqEntry(gm) 
    if msg:
      emby = await genGMListEmbed()
      await interaction.response.send_message(content=msg, embed=emby)
    else:
      await interaction.response.send_message(
        content=f':frowning: Sorry, there is no GM in the list called **{gm}**')
    
  @gmdelete.autocomplete('gm')
  async def gmdelete_autocomplete_gm(self, interaction:discord.Interaction,
                                     current:str) -> List[Choice[str]]:
    gmList = await getGMList()
    return [Choice(name=gm, value=gm)
            for gm in gmList if current.lower() in gm.lower()]

  #----------------------------------------------
  # gmquickadd
  #----------------------------------------------
  @app_commands.command(name="gmquickadd",
                        description="Add several GM names to the list (no server or size info)")
  @app_commands.describe(name  = "Enter a GM name (ex. Pollys - Patty)",
                         name2 = "Enter a 2nd name",
                         name3 = "Enter a 3rd name",
                         name4 = "Enter a 4th name",
                         name5 = "Enter a 5th name",
                         name6 = "Enter a 6th name")
  async def gmquickadd(self, interaction:discord.Interaction, name:str,
                       name2:str=None, name3:str=None, name4:str=None,
                       name5:str=None, name6:str=None) -> None:
    await self.bot.logCommand(interaction)
    guildMissions = [GuildMission(name),  GuildMission(name2), GuildMission(name3),
                     GuildMission(name4), GuildMission(name5), GuildMission(name6)]
    msg = await addGMReqEntries(guildMissions)
    emby = await genGMListEmbed()
    await interaction.response.send_message(content=msg, embed=emby)
    #TODO: quickNames = ["Hasrah Ruins", "Soldiers", "Bashims", "Cadrys", "Crescents", "Nagas"]

  #----------------------------------------------
  # gmclear
  #----------------------------------------------
  @app_commands.command(name="gmclear",
                        description="Clear the entire GM list")
  async def gmclear(self, interaction:discord.Interaction) -> None:
    await self.bot.logCommand(interaction)
    await clearGMReqTable()
    emby = await genGMListEmbed()
    await interaction.response.send_message(content="GM list cleared",
                                            embed=emby)

async def setup(bot:commands.Bot) -> None:
  await bot.add_cog(GMCommands(bot), guilds=guildIDs)
