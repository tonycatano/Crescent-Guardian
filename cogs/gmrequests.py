import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from typing import List
import common.common as common
from common.common import guild_ids
from common.common import gm_servers
from common.common import gmSizes
from common.common import noServer
from common.common import noSize
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
                        description="Display the GM request list")
  # TODO: @check_for_purge
  async def gmlist(self, interaction:discord.Interaction) -> None:
    await self.bot.log_command("gmlist", interaction.user.name)
    emby = await common.get_gm_list_embed()
    await interaction.response.send_message(embed=emby)

  #----------------------------------------------
  # gmadd
  #----------------------------------------------
  @app_commands.command(name="gmadd",
                        description="Add a GM request to the list")
  @app_commands.describe(request  = "Enter a request (ex. Pollys - Patty)",
                         request2 = "Enter a second request",
                         request3 = "Enter a third request",
                         request4 = "Enter a fourth request",
                         request5 = "Enter a final request")
  async def gmadd(self, interaction:discord.Interaction,
                  request:str, request2:str=None, request3:str=None,
                  request4:str=None, request5:str=None) -> None:
    await self.bot.log_command("gmadd", interaction.user.name)
    reqs = [request, request2, request3, request4, request5]
    reqstr = await common.add_gm_reqs(reqs)
    # FIXME: Trying to syncronize add commands, but it's not working so far.
    # async with self.bot.db_lock:
    #     - or - 
    # asyncio.sleep(1)
    emby = await common.get_gm_list_embed()
    await interaction.response.send_message(content=reqstr, embed=emby)

  #----------------------------------------------
  # gmfound
  #----------------------------------------------
  @app_commands.command(name="gmfound",
                        description="Indicate that a GM request has been found")
  @app_commands.describe(request = "Select an existing request (or enter a new request)")
  @app_commands.describe(server = "Enter the server for the GM (Select '" + noServer + "' to leave blank)")
  @app_commands.describe(size = "Enter the size of the GM (Select '" + noSize + "' to leave blank)")
  async def gmfound(self, interaction:discord.Interaction,
                    request:str, server:str, size:str):
    await self.bot.log_command("gmfound", interaction.user.name)
    msg = await common.set_gm_req_server(request, server, size)
    emby = await common.get_gm_list_embed()
    await interaction.response.send_message(content=msg, embed=emby)

  @gmfound.autocomplete('request')
  async def gmfound_autocomplete_request(self, interaction: discord.Interaction,
                                         current: str) -> List[Choice[str]]:
    gm_requests = await common.get_gm_requests()
    return [Choice(name=gm_request.name, value=gm_request.name)
            for gm_request in gm_requests if current.lower() in gm_request.name.lower()]

  @gmfound.autocomplete('server')
  async def gmfound_autocomplete_server(self, interaction: discord.Interaction,
                                        current: str) -> List[Choice[str]]:
    return [Choice(name=server, value=server)
            for server in gm_servers if current.lower() in server.lower()]

  @gmfound.autocomplete('size')
  async def gmfound_autocomplete_size(self, interaction: discord.Interaction,
                                      current: str) -> List[Choice[str]]:
    return [Choice(name=size, value=size)
            for size in gmSizes if current.lower() in size.lower()]

  #----------------------------------------------
  # gmedit
  #----------------------------------------------
  @app_commands.command(name="gmedit", description="Edit a GM request in the list")
  @app_commands.describe(request = "Select the request to edit")
  @app_commands.describe(newtext = "Enter the new text for the request")
  @app_commands.describe(server = "Enter the server for the GM (Select '" + noServer + "' to leave blank)")
  @app_commands.describe(size = "Enter the size of the GM (Select '" + noSize + "' to leave blank)")
  async def gmedit(self, interaction: discord.Interaction, request:str,
                   newtext:str, server:str=None, size:str=None):
    await self.bot.log_command("gmedit", interaction.user.name)
    msg = await common.edit_gm_req(request, newtext, server, size)
    if msg:
      emby = await common.get_gm_list_embed()
      await interaction.response.send_message(content=msg, embed=emby)
    else:
      await interaction.response.send_message(
        content=f':frowning: *Sorry, there is no GM request in the list called **{request}***')

  @gmedit.autocomplete('request')
  async def gmedit_autocomplete(self, interaction: discord.Interaction,
                                current: str) -> List[Choice[str]]:
    gm_requests = await common.get_gm_requests()
    return [Choice(name=gm_request.name, value=gm_request.name)
            for gm_request in gm_requests if current.lower() in gm_request.name.lower()]

  @gmedit.autocomplete('server')
  async def gmedit_autocomplete_server(self, interaction: discord.Interaction,
                                       current: str) -> List[Choice[str]]:
    return [Choice(name=server, value=server)
            for server in gm_servers if current.lower() in server.lower()]

  @gmedit.autocomplete('size')
  async def gmedit_autocomplete_size(self, interaction: discord.Interaction,
                                     current: str) -> List[Choice[str]]:
    return [Choice(name=size, value=size)
            for size in gmSizes if current.lower() in size.lower()]

  #----------------------------------------------
  # gmdelete
  #----------------------------------------------
  @app_commands.command(name="gmdelete",
                        description="Delete a GM request from the list")
  @app_commands.describe(request = "Select the request to delete")
  async def gmdelete(self, interaction: discord.Interaction, request:str):
    await self.bot.log_command("gmdelete", interaction.user.name)
    msg = await common.delete_gm_req(request) 
    if msg:
      emby = await common.get_gm_list_embed()
      await interaction.response.send_message(content=msg, embed=emby)
    else:
      await interaction.response.send_message(
        content=f':frowning: *Sorry, there is no GM request in the list called **{request}***')
    
  @gmdelete.autocomplete('request')
  async def gmdelete_autocomplete(self, interaction:discord.Interaction,
                                  current:str) -> List[Choice[str]]:
    gm_requests = await common.get_gm_requests()
    return [Choice(name=gm_request.name, value=gm_request.name)
            for gm_request in gm_requests if current.lower() in gm_request.name.lower()]

  #----------------------------------------------
  # gmclear
  #----------------------------------------------
  @app_commands.command(name="gmclear",
                        description="Clear the entire GM request list")
  async def gmclear(self, interaction:discord.Interaction) -> None:
    await self.bot.log_command("gmclear", interaction.user.name)
    await common.clear_gm_reqs()
    emby = await common.get_gm_list_embed()
    await interaction.response.send_message(content="*Request list cleared*",
                                            embed=emby)

  #----------------------------------------------
  # gmgarmy
  #----------------------------------------------
  @app_commands.command(name="gmgarmy",
                        description="Update the Garmoth Scroll Status")
  @app_commands.describe(pieces="Enter the current number of scroll pieces")
  async def gmgarmy(self, interaction:discord.Interaction, pieces:int):
    await self.bot.log_command("gmgarmy", interaction.user.name)
    await common.update_garmy_pieces(pieces)
    emby = await common.get_gm_list_embed()
    await interaction.response.send_message(
      content="*Updated **Garmoth Scroll Status** to **" + str(pieces) + "** pieces*", 
      embed=emby)

async def setup(bot:commands.Bot) -> None:
  await bot.add_cog(GMRequests(bot), guilds=guild_ids)
