import os
import discord
import datetime
import json
from common.Logger import Logger

guildIDs = [discord.Object(id=os.environ['DISCORD_SERVER_ID'])]

connectionLogFile = "logs/rocg.connection.log"
commandLogFile    = "logs/rocg.command.log"
configOptionsFile = "config/configOptions.txt"
devOptionsFile    = "config/devOptions.txt"
officerSchedFile  = "config/officerSchedule.txt"
relNotesFile      = "config/relNotesAbridged.txt"
serverListFile    = "config/serverList.txt"

embyColour = discord.Colour.blue()
userIdStub = "xxXX_USERID_XXxx"

genericErrorMsg = userIdStub + " I'm sorry, something went wrong :frowning:"

class CommandDescr():
  def __init__(self, name, namePretty, descr, descrLong=None):
    self.name = name
    self.namePretty = namePretty
    self.descr = descr
    self.descrLong = descr if not descrLong else descrLong

gmCommandList = [
  CommandDescr("gmlist",     "List",         "Display the GM list"),
  CommandDescr("gmadd",      "Add",          "Add a GM to the list"),
  CommandDescr("gmquickadd", "Quick Add",    "Add several GMs to the list",
                                             "Add several GMs to the list (no Server, no Size)"),
  CommandDescr("gmedit",     "Edit",         "Edit a GM in the list"),
  CommandDescr("gmdelete",   "Delete",       "Delete a GM from the list"),
  CommandDescr("gmclear",    "Clear",        "Clear the entire GM list"),
  CommandDescr("gmscroll",   "Boss Scrolls", "Update boss scroll pieces"),
  CommandDescr("gmupdate",   "Update",       "Update any part of the GM list")]

miscCommandList = [
  CommandDescr("schedule",   "Schedule",     "Display the officer schedule"),
  CommandDescr("help",       "Help",         "View Crescent Guardian help info")]

# Default config options (timeouts are in seconds)
defaultConfigs = {"helpPrivate":           True,
                  "helpTimeout":           60,
                  "schedulePrivate":       True,
                  "scheduleTimeout":       75,
                  "gmUpdatePanelPrivate":  True,
                  "gmUpdatePanelTimeout":  75,
                  "gmAddTimeout":          75,
                  "gmQuickAddTimeout":     75,
                  "gmEditTimeout":         75,
                  "gmBossScrollTimeout":   75,
                  "processingPrivate":     True,
                  "errorMessagePrivate":   True
                 }

# Default dev options
defaultDevOptions = {"debugMode": False
                    }

# Return the specified config option from the config file. If it is not specified
# in the file, return the default option value. These options are dynamic.
def getConfig(option:str):
  value = None
  with open(configOptionsFile, 'r') as file:
    configOptions = json.load(file)
  if configOptions:
    value = configOptions.get(option, defaultConfigs.get(option))
    Logger.logDebug(None, "Config option " + option + "=" + str(value))
  return value

# Return the specified dev option from the dev option file. If it is not specified
# in the file, return the default option value. These options are NOT dynamic, a
# bot restart is required.
def getDevOption(option:str):
  value = None
  with open(devOptionsFile, 'r') as file:
    devOptions = json.load(file)
  if devOptions:
    value = devOptions.get(option, defaultDevOptions.get(option))
  return value

# A container for functions to return an indication of whether the result
# was "good" and an optional message
class Result():
  def __init__(self, msg:str=None, good:bool=True):
    self.good = good
    self.msg = msg

# Return the specified number of special unicode blank chars to be used as spaces 
def space(n:int) -> str:
  spaces = ""
  for i in range(1,n):
    spaces += "\u2800"
  return spaces

# Replace the userIdStub with the provided user string 
def resolveUserID(content:str, user:str) -> str:
  content = content.replace(userIdStub, user)
  return content

# Send an error message within a final response message and log the error too
async def sendErrorMessage(interaction:discord.Interaction, content:str) -> None:
  msgContent = resolveUserID(content, interaction.user.mention)
  await interaction.response.send_message(content=msgContent, ephemeral=getConfig('errorMessagePrivate'))
  logContent = resolveUserID(content, interaction.user.name)
  logContent = logContent.replace("**", "").replace("\n", ": ")
  Logger.logError(None, logContent)

# Log the current command to the command log file
async def logCommand(interaction:discord.Interaction, cmdNameOverride:str=None) -> None:
  timeStamp = str(datetime.datetime.now())
  user = interaction.user.name if rhasattr(interaction, "user.name") else "NoUserName"
  if cmdNameOverride:
    cmd = cmdNameOverride
  elif rhasattr(interaction, "command.qualified_name"):
    cmd = interaction.command.qualified_name
  else:
    cmd = "NoCommandName"
  msg = timeStamp + ": " + user + ": " + cmd + "\n"
  with open(commandLogFile, "a") as logFile:
    logFile.write(msg)

# A recursive implementation of hasattr
def rhasattr(obj, attr):
  try: firstAttr, remainingAttrs = attr.split('.', 1)
  except: return hasattr(obj, attr)
  return rhasattr(getattr(obj, firstAttr), remainingAttrs)

# Remove any message components left over by this bot from previous runs 
async def sweepMessages(bot:discord.ext.commands.Bot):
  for guild in [bot.get_guild(guildId.id) for guildId in guildIDs if bot.get_guild(guildId.id)]:
    botMember = guild.get_member(bot.user.id)
    Logger.logInfo(None, "Guild Name(ID): " + str(guild.name) + "(" + str(guild.id) + ")")
    Logger.logInfo(None, "  Bot Name(ID): " + str(botMember.name) + "(" + str(bot.user.id) + ")")
    # Sweep all channels for which this bot has view permission
    Logger.logInfo(None, "Sweeping Channels")
    for channel in [channel for channel in guild.channels
                    if channel.type == discord.ChannelType.text
                    and channel.permissions_for(botMember).view_channel]:
      Logger.logInfo(None, "Channel Name(ID): " + str(channel.name) + "(" + str(channel.id) + ")")
      for message in [message async for message in channel.history(limit=50)
                      if message.author == botMember and message.components]:
        Logger.logInfo(None, "Found a " + botMember.display_name + " message with components")
        Logger.logInfo(None, "Removing components from message " + str(message.jump_url))
        await message.edit(view=None)
    # Sweep all threads for which this bot has view permission
    Logger.logInfo(None, "Sweeping Threads")
    for thread in [thread for thread in guild.threads
                  if thread.type == discord.ChannelType.public_thread
                  and thread.permissions_for(botMember).view_channel]:
      Logger.logInfo(None, "Thread Name(ID): " + str(thread.name) + "(" + str(thread.id) + ")")
      for message in [message async for message in thread.history(limit=50)
                      if message.author == botMember and message.components]:
        Logger.logInfo(None, "Found a " + botMember.display_name + " message with components")
        Logger.logInfo(None, "Removing components from message " + str(message.jump_url))
        await message.edit(view=None)

# Print all users to the console screen
# async def printAllUsers(bot:commands.Bot):
#   botName = F.MAGENTA + str(bot.user.name) + F.END
#   print("\nLogged in as " + botName)
#   users = [user for user in bot.users if not user.bot]
#   print("\n" + botName + " can see " + str(len(users)) + " users:")
#   for user in users:
#     name = " " + F.YELLOW + user.name + F.END + \
#            " (" + user.display_name + ")"
#     print(name)
#   print()
