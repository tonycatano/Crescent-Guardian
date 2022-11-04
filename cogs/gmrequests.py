import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from typing import List
import common.common as common
from common.common import guildIDs
from common.common import gmServers
from common.common import gmSizes
from common.common import noServer
from common.common import noSize
from common.common import GMRequest

#import asyncio

# TODO:
# async def check_for_purge(func):
#   async def inner(self, interaction):
#     print("Hello world")
#     await func(self, interaction)
#   return inner

class GMRequests(commands.Cog):
  def __init__(self, bot:commands.Bot) -> None:
    self.bot = bot
  
  #----------------------------------------------
  # gmlist
  #----------------------------------------------
  @app_commands.command(name="gmlist",
                        description="Display the GM list")
  # TODO: @check_for_purge
  async def gmlist(self, interaction:discord.Interaction) -> None:
    await self.bot.logCommand("gmlist", interaction.user.name)
    emby = await common.genGMListEmbed()
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
    await self.bot.logCommand("gmadd", interaction.user.name)
    gmRequests = [GMRequest(name,server,size)]
    msg = await common.addGMReqEntries(gmRequests)
    # FIXME: Trying to syncronize add commands, but it's not working so far.
    # async with self.bot.db_lock:
    #     - or - 
    # asyncio.sleep(1)
    emby = await common.genGMListEmbed()
    await interaction.response.send_message(content=msg, embed=emby)

  @gmadd.autocomplete('server')
  async def gmadd_autocomplete_server(self, interaction: discord.Interaction,
                                       current: str) -> List[Choice[str]]:
    return [Choice(name=server, value=server)
            for server in common.gmServers if current.lower() in server.lower() and server != noServer]

  #----------------------------------------------
  # gmfound
  #----------------------------------------------
  # @app_commands.command(name="gmfound",
  #                       description="Edit the server and size for a GM")
  # @app_commands.describe(gm = "Select an existing GM")
  # @app_commands.describe(server = "Enter the GM server (Select " + noServer + " to erase the current server)")
  # @app_commands.describe(size = "Enter the GM size (Select " + noSize + " to erase the current size)")
  # async def gmfound(self, interaction:discord.Interaction,
  #                   gm:str, server:str=None, size:str=None):
  #   await self.bot.logCommand("gmfound", interaction.user.name)
  #   msg = await common.setGMServerAndSize(gm, server, size)
  #   if msg:
  #     emby = await common.genGMListEmbed()
  #     await interaction.response.send_message(content=msg, embed=emby)
  #   else:
  #     await interaction.response.send_message(
  #       content=f':frowning: Sorry, there is no GM in the list called **{gm}**')

  # @gmfound.autocomplete('gm')
  # async def gmfound_autocomplete_gm(self, interaction: discord.Interaction,
  #                                   current: str) -> List[Choice[str]]:
  #   gmList = await common.getGMList()
  #   return [Choice(name=gm, value=gm)
  #           for gm in gmList if current.lower() in gm.lower()]

  # @gmfound.autocomplete('server')
  # async def gmfound_autocomplete_server(self, interaction: discord.Interaction,
  #                                       current: str) -> List[Choice[str]]:
  #   return [Choice(name=server, value=server)
  #           for server in gmServers if current.lower() in server.lower()]

  # @gmfound.autocomplete('size')
  # async def gmfound_autocomplete_size(self, interaction: discord.Interaction,
  #                                     current: str) -> List[Choice[str]]:
  #   return [Choice(name=size, value=size)
  #           for size in gmSizes if current.lower() in size.lower()]

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
    await self.bot.logCommand("gmedit", interaction.user.name)
    msg = await common.editGMReqEntry(gm, name, server, size)
    if msg:
      emby = await common.genGMListEmbed()
      await interaction.response.send_message(content=msg, embed=emby)
    else:
      await interaction.response.send_message(
        content=f':frowning: Sorry, there is no GM in the list called **{gm}**')

  @gmedit.autocomplete('gm')
  async def gmedit_autocomplete_gm(self, interaction: discord.Interaction,
                                   current: str) -> List[Choice[str]]:
    gmList = await common.getGMList()
    return [Choice(name=gm, value=gm)
            for gm in gmList if current.lower() in gm.lower()]
                      
  @gmedit.autocomplete('server')
  async def gmedit_autocomplete_server(self, interaction: discord.Interaction,
                                       current: str) -> List[Choice[str]]:
    return [Choice(name=server, value=server)
            for server in gmServers if current.lower() in server.lower()]

  @gmedit.autocomplete('size')
  async def gmedit_autocomplete_size(self, interaction: discord.Interaction,
                                     current: str) -> List[Choice[str]]:
    return [Choice(name=size, value=size)
            for size in gmSizes if current.lower() in size.lower()]

  #----------------------------------------------
  # gmdelete
  #----------------------------------------------
  @app_commands.command(name="gmdelete",
                        description="Delete a GM from the list")
  @app_commands.describe(gm = "Select the GM to delete")
  async def gmdelete(self, interaction: discord.Interaction, gm:str):
    await self.bot.logCommand("gmdelete", interaction.user.name)
    msg = await common.deleteGMReqEntry(gm) 
    if msg:
      emby = await common.genGMListEmbed()
      await interaction.response.send_message(content=msg, embed=emby)
    else:
      await interaction.response.send_message(
        content=f':frowning: Sorry, there is no GM in the list called **{gm}**')
    
  @gmdelete.autocomplete('gm')
  async def gmdelete_autocomplete_gm(self, interaction:discord.Interaction,
                                     current:str) -> List[Choice[str]]:
    gmList = await common.getGMList()
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
    await self.bot.logCommand("gmquickadd", interaction.user.name)
    gmRequests = [GMRequest(name), GMRequest(name2), GMRequest(name3),
                  GMRequest(name4), GMRequest(name5), GMRequest(name6)]
    msg = await common.addGMReqEntries(gmRequests)
    emby = await common.genGMListEmbed()
    await interaction.response.send_message(content=msg, embed=emby)

  #----------------------------------------------
  # gmclear
  #----------------------------------------------
  @app_commands.command(name="gmclear",
                        description="Clear the entire GM list")
  async def gmclear(self, interaction:discord.Interaction) -> None:
    await self.bot.logCommand("gmclear", interaction.user.name)
    await common.clearGMReqTable()
    emby = await common.genGMListEmbed()
    await interaction.response.send_message(content="GM list cleared",
                                            embed=emby)

  #----------------------------------------------
  # gmgarmy
  #----------------------------------------------
  @app_commands.command(name="gmgarmy",
                        description="Update the Garmoth Scroll Status")
  @app_commands.describe(pieces="Enter the current number of scroll pieces")
  async def gmgarmy(self, interaction:discord.Interaction, pieces:int):
    await self.bot.logCommand("gmgarmy", interaction.user.name)
    msg = await common.updateGarmyPieces(pieces)
    emby = await common.genGMListEmbed()
    await interaction.response.send_message(content=msg, embed=emby)

async def setup(bot:commands.Bot) -> None:
  await bot.add_cog(GMRequests(bot), guilds=guildIDs)
