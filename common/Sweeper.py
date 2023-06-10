import discord
from common.common import guildIDs
from common.common import gmListPanelViewCustomId
from common.Logger import Logger
from typing import List

#------------------------------------------------------------------------------------------------
# Utility class to sweep and clean the Update buttons from messsages
#------------------------------------------------------------------------------------------------
class Sweeper():
  
  # Helper Function: Return a list of channels for which this bot has certain permissions
  async def getChannels(guild, botMember) -> List[discord.TextChannel]:
    return [channel for channel in guild.channels if channel.type == discord.ChannelType.text
            and channel.permissions_for(botMember).view_channel
            and channel.permissions_for(botMember).send_messages
            and channel.permissions_for(botMember).read_messages
            and channel.permissions_for(botMember).read_message_history]

  # Helper Function: Return a list of messages in the specified channel/thread that contain
  # an Update button
  async def getMessagesWithUpdateButton(channel, botMember) -> List[discord.Message]:
    return [message async for message in channel.history(limit=25)
            if message.author == botMember and len(message.components) > 0
            and message.components[0].type == discord.ComponentType.action_row
            and len(message.components[0].children) > 0
            and hasattr(message.components[0].children[0], "custom_id")
            and message.components[0].children[0].custom_id == gmListPanelViewCustomId]
  
  #------------------------------------------------------------------------------------------------
  # Remove the Update button from all messages except the latest one
  # This is intended to be run once at boot time, as it hits all guilds in the guildIDs list.
  async def sweepMessages(bot:discord.ext.commands.Bot) -> None:
    messageList = []

    for guild in [bot.get_guild(guildId.id) for guildId in guildIDs if bot.get_guild(guildId.id)]:
      botMember = guild.get_member(bot.user.id)
      Logger.logInfo(None, "Guild Name(ID): " + str(guild.name) + "(" + str(guild.id) + ")")
      Logger.logInfo(None, "  Bot Name(ID): " + str(botMember.name) + "(" + str(bot.user.id) + ")")
      Logger.logInfo(None, "Sweeping Channels and Threads")
      for channel in await Sweeper.getChannels(guild, botMember):
        Logger.logInfo(None, "Channel Name(ID): " + str(channel.name) + "(" + str(channel.id) + ")")
        for message in await Sweeper.getMessagesWithUpdateButton(channel, botMember):
          Logger.logInfo(None, "^^^ Found an Update button")
          messageList.append(message)
        for thread in [thread for thread in channel.threads]:
          Logger.logInfo(None, "Thread Name(ID): " + str(thread.name) + "(" + str(thread.id) + ")")
          for message in await Sweeper.getMessagesWithUpdateButton(thread, botMember):
            Logger.logInfo(None, "^^^ Found an Update button")
            messageList.append(message)

    if len(messageList) > 0:
      messageList.sort(key=lambda x: x.created_at)
      messageList.pop()
      for message in messageList:
        Logger.logInfo(None, "Removing view from message " + str(message.jump_url))
        await message.edit(view=None)

    return

  #------------------------------------------------------------------------------------------------
  # Find all messages in the specified interaction's channel/thread that contain Update buttons.
  # Stop the associated view and remove the Update button for all messages except the current one.
  # Permissions are assumed to be granted for the channel/thread.
  async def sweepChannel(interaction:discord.Interaction, currentMsg:discord.Message) -> None:
    channel = interaction.channel
    channelType = ""
    if channel.type == discord.ChannelType.text:
      channelType = "Channel"
    elif channel.type == discord.ChannelType.public_thread:
      channelType = "Thread"
    else:
      Logger.logError(None, "Unsupported channel type: " + str(channel.type))
      return

    messageList = []
    botMember = interaction.guild.get_member(interaction.client.user.id)
    Logger.logInfo(None, "Sweeping " + channelType + " Name(ID): " + str(channel.name) + "(" + str(channel.id) + ")")
    for message in await Sweeper.getMessagesWithUpdateButton(channel, botMember):
      if message != currentMsg:
        Logger.logInfo(None, "^^^ Found an Update button")
        messageList.append(message)

    if len(messageList) > 0:
      messageList.sort(key=lambda x: x.created_at)
      for message in messageList:
        Logger.logInfo(None, "Stopping and removing view from message " + str(message.jump_url))
        discord.ui.View.from_message(message).stop()
        await message.edit(view=None)

    return
