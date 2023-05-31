import discord
from common.Logger import Logger

#--------------------------------------------------------------------------
# CommonModal
# Note: The API limits modals to a max of 5 items.
#--------------------------------------------------------------------------
class CommonModal(discord.ui.Modal):
  def __init__(self, title, timeout=75):
    super().__init__(title=title, timeout=timeout)

  async def on_timeout(self) -> None:
    Logger.logWarning(self, "Timed out after " + str(self.timeout) + " seconds, stopping modal")
    self.stop()
    # There is no way to update or remove the modal. Let the user cancel it.
