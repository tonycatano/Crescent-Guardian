import discord
from common.Logger import Logger

#--------------------------------------------------------------------------
# CommonView
#--------------------------------------------------------------------------
class CommonView(discord.ui.View):
  def __init__(self, timeout=75, parentMsg=None,
               cancelButtonCallback=None, submitButtonCallback=None):
    super().__init__(timeout=timeout)
    self.parentMsg = parentMsg
    self.cancelButton = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
    self.submitButton = discord.ui.Button(label="Submit", style=discord.ButtonStyle.primary)
    self.cancelButton.callback = cancelButtonCallback if cancelButtonCallback else self.cancelButtonCallback
    self.submitButton.callback = submitButtonCallback
    self.on_timeout = self.deleteMessageOnTimeout

  def addCancelButton(self) -> None:
    self.add_item(self.cancelButton)

  def addSubmitButton(self) -> None:
    self.add_item(self.submitButton)

  async def cancelButtonCallback(self, interaction:discord.Interaction) -> None:
    Logger.logInfo(self, "Deleting message")
    self.stop()
    await interaction.response.edit_message(view=None)
    await self.deleteMessage()

  async def deleteMessageOnTimeout(self) -> None:
    Logger.logWarning(self, "Timed out after " + str(self.timeout) + " seconds, deleting message")
    await self.deleteMessage()

  async def removeViewOnTimeout(self) -> None:
    Logger.logWarning(self, "Timed out after " + str(self.timeout) + " seconds, removing view (input components)")
    await self.removeView()

  async def deleteMessage(self) -> None:
    try:
      await self.parentMsg.delete()
    except discord.errors.NotFound:
      Logger.logWarning(self, "Parent message not found (likely already deleted)")

  async def removeView(self) -> None:
    try:
      await self.parentMsg.edit(view=None)
    except discord.errors.NotFound:
      Logger.logWarning(self, "Parent message not found (likely already deleted)")
