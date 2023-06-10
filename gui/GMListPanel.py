import discord
from discord import ui
from common.common import resolveUserID
from common.common import getConfig
from common.common import gmListPanelViewCustomId
from common.GuildMission import genGMListEmbed
from common.Sweeper import Sweeper
from gui.CommonView import CommonView

#--------------------------------------------------------------------------
# GMListPanel
#--------------------------------------------------------------------------
class GMListPanel():
  def __init__(self, interaction:discord.Interaction, content:str):
    self.interaction = interaction
    self.content = resolveUserID(content, interaction.user.mention)
    self.view = GMListPanelView()

  async def run(self):
    await self.sendProcessingMessage()
    await self.sendContentAndEmbed()
    await Sweeper.sweepChannel(interaction=self.interaction, currentMsg=self.view.parentMsg)

  async def sendProcessingMessage(self):
    await self.interaction.response.send_message(content="Processing...", 
                                                 ephemeral=getConfig('processingPrivate'))
    msg = await self.interaction.original_response()
    await msg.delete(delay=0.4) # Delay delete so posts get removed in a less jarring flow

  async def sendContentAndEmbed(self):
    emby = await genGMListEmbed()
    await self.interaction.channel.send(self.content)
    self.view.parentMsg = await self.interaction.channel.send(view=self.view, embed=emby)

#--------------------------------------------------------------------------
# View for GMListPanel
#--------------------------------------------------------------------------
class GMListPanelView(CommonView):
  def __init__(self):
    super().__init__(timeout=None) # no timeout
    self.updateButton = ui.Button(label="Update", style=discord.ButtonStyle.primary,
                                  custom_id=gmListPanelViewCustomId)
    self.updateButton.callback = self.updateButtonCallback
    self.add_item(self.updateButton)

  async def updateButtonCallback(self, interaction:discord.Interaction) -> None:
    from gui.GMUpdatePanel import GMUpdatePanel 
    gmUpdatePanel = GMUpdatePanel(interaction)
    await gmUpdatePanel.run()
    # Note: If the user has scrolled up the channel to push the Update button, they
    # will have to manually scroll down to see the UpdatePanel
