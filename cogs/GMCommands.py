import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from typing import List
from common.common import gmCommandList
from common.common import guildIDs
from common.common import serverListFile
from common.common import userIdStub
from common.common import logCommand
from common.GMPrompts import GMPrompts as gmp
from common.GuildMission import GuildMission
from common.GuildMission import addGMReqEntries
from common.GuildMission import getGMList
from common.GuildMission import editGMReqEntry
from common.GuildMission import deleteGMReqEntry
from common.GuildMission import clearGMReqTable
from common.GuildMission import processResult
from common.GuildMission import updateBossScroll
from gui.GMListPanel import GMListPanel
from gui.GMUpdatePanel import GMUpdatePanel

#--------------------------------------------------------------------------
# The main set of gm* commands
#--------------------------------------------------------------------------
class GMCommands(commands.Cog):
  def __init__(self, bot:commands.Bot) -> None:
    self.bot = bot

  async def readServerList(self) -> str:
    with open(serverListFile, "r") as file:
      servers = file.read().splitlines()
      return servers

  #----------------------------------------------
  # gmlist
  #----------------------------------------------
  gmCmd = next(cmd for cmd in gmCommandList if cmd.name == "gmlist") 
  @app_commands.command(name=gmCmd.name, description=gmCmd.descr)
  async def gmlist(self, interaction:discord.Interaction) -> None:
    await logCommand(interaction)
    content = "> " + userIdStub + " requested the GM list"
    gmListPanel = GMListPanel(interaction=interaction, content=content)
    await gmListPanel.run()

  #----------------------------------------------
  # gmadd
  #----------------------------------------------
  gmCmd = next(cmd for cmd in gmCommandList if cmd.name == "gmadd") 
  @app_commands.command(name=gmCmd.name, description=gmCmd.descr)
  @app_commands.describe(target=gmp.targetPrompt1, server=gmp.serverPrompt, size=gmp.sizePrompt)
  async def gmadd(self, interaction:discord.Interaction,
                  target:str, server:str=None, size:str=None) -> None:
    await logCommand(interaction)
    guildMissions = [GuildMission(target,server,size)]
    result = await addGMReqEntries(guildMissions)
    await processResult(interaction=interaction, result=result)

  @gmadd.autocomplete('server')
  async def gmadd_autocomplete_server(self, interaction: discord.Interaction,
                                      current: str) -> List[Choice[str]]:
    gmServers = await self.readServerList()
    return [Choice(name=server, value=server)
            for server in gmServers if current.lower() in server.lower()]

  #----------------------------------------------
  # gmedit
  #----------------------------------------------
  gmCmd = next(cmd for cmd in gmCommandList if cmd.name == "gmedit")
  @app_commands.command(name=gmCmd.name, description=gmCmd.descr)
  @app_commands.describe(gm=gmp.gmPromptEdit, target=gmp.targetPrompt1,
                         server=gmp.serverPromptLong, size=gmp.sizePromptLong)
  async def gmedit(self, interaction:discord.Interaction, gm:str,
                   server:str=None, size:str=None, target:str=None):
    await logCommand(interaction)
    result = await editGMReqEntry(gm, target, server, size)
    await processResult(interaction=interaction, result=result)

  @gmedit.autocomplete('gm')
  async def gmedit_autocomplete_gm(self, interaction:discord.Interaction,
                                   current: str) -> List[Choice[str]]:
    gmList = getGMList()
    return [Choice(name=gm, value=gm)
            for gm in gmList if current.lower() in gm.lower()]

  @gmedit.autocomplete('server')
  async def gmedit_autocomplete_server(self, interaction: discord.Interaction,
                                       current: str) -> List[Choice[str]]:
    gmServers = await self.readServerList()
    return [Choice(name=server, value=server)
            for server in gmServers if current.lower() in server.lower()]

  #----------------------------------------------
  # gmdelete
  #----------------------------------------------
  gmCmd = next(cmd for cmd in gmCommandList if cmd.name == "gmdelete") 
  @app_commands.command(name=gmCmd.name, description=gmCmd.descr)
  @app_commands.describe(gm=gmp.gmPromptDelete)
  async def gmdelete(self, interaction:discord.Interaction, gm:str):
    await logCommand(interaction)
    result = await deleteGMReqEntry(gm)
    await processResult(interaction=interaction, result=result)
  
  @gmdelete.autocomplete('gm')
  async def gmdelete_autocomplete_gm(self, interaction:discord.Interaction,
                                     current:str) -> List[Choice[str]]:
    gmList = getGMList()
    return [Choice(name=gm, value=gm)
            for gm in gmList if current.lower() in gm.lower()]

  #----------------------------------------------
  # gmquickadd
  #----------------------------------------------
  gmCmd = next(cmd for cmd in gmCommandList if cmd.name == "gmquickadd") 
  @app_commands.command(name=gmCmd.name, description=gmCmd.descrLong)
  @app_commands.describe(target=gmp.targetPrompt1, target2=gmp.targetPrompt2, target3=gmp.targetPrompt3,
                         target4=gmp.targetPrompt4, target5=gmp.targetPrompt5, target6=gmp.targetPrompt6)
  async def gmquickadd(self, interaction:discord.Interaction, target:str,
                       target2:str=None, target3:str=None, target4:str=None,
                       target5:str=None, target6:str=None) -> None:
    await logCommand(interaction)
    guildMissions = [GuildMission(target),  GuildMission(target2), GuildMission(target3),
                     GuildMission(target4), GuildMission(target5), GuildMission(target6)]
    result = await addGMReqEntries(guildMissions)
    await processResult(interaction=interaction, result=result)

  #----------------------------------------------
  # gmclear
  #----------------------------------------------
  gmCmd = next(cmd for cmd in gmCommandList if cmd.name == "gmclear") 
  @app_commands.command(name=gmCmd.name, description=gmCmd.descr)
  async def gmclear(self, interaction:discord.Interaction) -> None:
    await logCommand(interaction)
    result = await clearGMReqTable()
    await processResult(interaction=interaction, result=result)

  #----------------------------------------------
  # gmscroll
  #----------------------------------------------
  gmCmd = next(cmd for cmd in gmCommandList if cmd.name == "gmscroll")
  @app_commands.command(name=gmCmd.name, description=gmCmd.descr)
  @app_commands.describe(scroll="Choose a boss scroll", pieces="Enter the numbr of scroll pieces")
  async def gmscroll(self, interaction:discord.Interaction, scroll:str, pieces:str):
    await logCommand(interaction)
    result = await updateBossScroll(scroll=scroll, pieces=pieces)
    await processResult(interaction=interaction, result=result)

  @gmscroll.autocomplete('scroll')
  async def gmscroll_autocomplete_scroll(self, interaction:discord.Interaction,
                                         current:str) -> List[Choice[str]]:
    scrollList = ["garmoth", "khan", "puturum", "ferrid", "mudster"]
    return [Choice(name=scroll, value=scroll)
            for scroll in scrollList if current.lower() in scroll.lower()]

  #----------------------------------------------
  # gmupdate
  #----------------------------------------------
  gmCmd = next(cmd for cmd in gmCommandList if cmd.name == "gmupdate") 
  @app_commands.command(name=gmCmd.name, description=gmCmd.descr)
  async def gmupdate(self, interaction:discord.Interaction) -> None:
    await logCommand(interaction)
    gmUpdatePanel = GMUpdatePanel(interaction=interaction)
    await gmUpdatePanel.run()

async def setup(bot:commands.Bot) -> None:
  await bot.add_cog(GMCommands(bot), guilds=guildIDs)
