import discord
import asyncio
from discord import ui
from common.common import resolveUserID
from common.common import getConfig
from common.GuildMission import genGMListEmbed
from common.Logger import Logger
from gui.CommonView import CommonView

#--------------------------------------------------------------------------
# GMListPanel
#--------------------------------------------------------------------------
class GMListPanel():
  def __init__(self, interaction:discord.Interaction, content:str):
    self.interaction = interaction
    self.content = resolveUserID(content, interaction.user.mention)
    self.updateButton = ui.Button(label="Update", style=discord.ButtonStyle.primary)
    self.updateButton.callback = self.updateButtonCallback
    self.view = CommonView(timeout=None) # no timeout
    self.view.add_item(self.updateButton)
    self.emby = None

  async def run(self):
    await self.interaction.response.send_message(content="Processing...",
                                                 ephemeral=getConfig('processingPrivate'))
    msg = await self.interaction.original_response()
    await msg.delete(delay=0.4) # Delay slightly so posts get removed in a less jarring flow

    self.emby = await genGMListEmbed()
    await self.interaction.channel.send(self.content)
    self.view.parentMsg = await self.interaction.channel.send(view=self.view, embed=self.emby)

    while self.emby == await genGMListEmbed():
      await asyncio.sleep(2) # Keep the Update button alive until the gm list is modified
    self.view.stop()
    try:
      await self.view.parentMsg.edit(view=None)
    except discord.errors.NotFound:
      Logger.logWarning(self, "Parent message not found for update (likely deleted)")

  async def updateButtonCallback(self, interaction:discord.Interaction) -> None:
    from gui.GMUpdatePanel import GMUpdatePanel 
    gmUpdatePanel = GMUpdatePanel(interaction)
    await gmUpdatePanel.run()
    # Note: If the user has scrolled up the channel to push the Update button, they
    # will have to manually scroll down to see the UpdatePanel
