import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from typing import List
import common
from common import guild_ids
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
  #----------------------------------------------
  @app_commands.command(name="gmlist",
                        description="Display the GM request list")
  # TODO: @check_for_purge
  async def gmlist(self, interaction: discord.Interaction) -> None:
    await self.bot.log_command("gmlist", interaction.user.name)
    emby = await common.get_gm_list_embed()
    await interaction.response.send_message(embed=emby)

  #----------------------------------------------
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
  #----------------------------------------------
  @app_commands.command(name="gmfound", 
                        description="Indicate that a GM has been found for a request")
  @app_commands.describe(request = "Select an existing request or enter a new request")
  @app_commands.describe(server = "Select the server where the GM was found \n(Select 'None' if not found)")
  async def gmfound(self, interaction: discord.Interaction, 
                    request: str, server: str):
    await self.bot.log_command("gmfound", interaction.user.name)
    msg = await common.set_gm_req_server(request, server)
    emby = await common.get_gm_list_embed()
    await interaction.response.send_message(content=msg, embed=emby)
    
  @gmfound.autocomplete('request')
  async def gmfound_autocomplete_request(self, interaction: discord.Interaction,
                                         current: str) -> List[Choice[str]]:
    gm_requests = await common.get_gm_requests()
    return [Choice(name=gm_request.name, value=gm_request.name)
            for gm_request in gm_requests if current.lower() in gm_request.name.lower()]
                                           ### and not gm_request.server]

  @gmfound.autocomplete('server')
  async def gmfound_autocomplete_server(self, interaction: discord.Interaction,
                                        current: str) -> List[Choice[str]]:
    # TODO: Make a superuser command '/season {on,off}' or '/cgconfig severlist'
    # to toggle the server list when a Season is active
    # servers = ["None", "SS1", "SS2", "SS3", "B1", "B2", "C1", "C2",
    #            "M1", "M2", "S1", "S2", "Rulu", "Val", "Arsha"]
    servers = ["None", "B1", "B2", "C1", "C2", "M1", "M2", "S1", "S2",
               "Rulu", "Val", "Arsha"]
    return [Choice(name=server, value=server)
            for server in servers if current.lower() in server.lower()]

  #----------------------------------------------
  #----------------------------------------------
  @app_commands.command(name="gmedit",
                        description="Edit a GM request in the list")
  @app_commands.describe(request = "Select the request to edit")
  @app_commands.describe(newtext = "Enter the new text for the request")
  async def gmedit(self, interaction: discord.Interaction, 
                   request: str, newtext: str):
    await self.bot.log_command("gmedit", interaction.user.name)
    if await common.edit_gm_req(request, newtext):
      emby = await common.get_gm_list_embed()
      await interaction.response.send_message(
        content=f'*Changed **{request}** to **{newtext}***', embed=emby)
    else:
      await interaction.response.send_message(
        content=f':frowning: *Sorry, there is no GM request in the list called **{request}***')
    
  @gmedit.autocomplete('request')
  async def gmedit_autocomplete(self, interaction: discord.Interaction,
                                current: str) -> List[Choice[str]]:
    gm_requests = await common.get_gm_requests()
    return [Choice(name=gm_request.name, value=gm_request.name)
            for gm_request in gm_requests if current.lower() in gm_request.name.lower()]

  #----------------------------------------------
  #----------------------------------------------
  @app_commands.command(name="gmdelete",
                        description="Delete a GM request from the list")
  @app_commands.describe(request = "Select the request to delete")
  async def gmdelete(self, interaction: discord.Interaction, request:str):
    await self.bot.log_command("gmdelete", interaction.user.name)
    if await common.delete_gm_req(request):
      emby = await common.get_gm_list_embed()
      await interaction.response.send_message(
        content=f'*Deleted* ***{request}***', embed=emby)
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
