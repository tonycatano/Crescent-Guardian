import discord
from discord import ui
from common.common import userIdStub
from common.common import gmCommandList
from common.common import sendErrorMessage
from common.common import genericErrorMsg
from common.common import logCommand
from common.common import getConfig
from common.GMPrompts import GMPrompts as gmp
from common.GuildMission import GuildMission
from common.GuildMission import findGuildMission
from common.GuildMission import genGMListEmbed
from common.GuildMission import addGMReqEntries
from common.GuildMission import getGMList
from common.GuildMission import editGMReqEntry
from common.GuildMission import deleteGMReqEntry
from common.GuildMission import clearGMReqTable
from common.GuildMission import ScrollPieces
from common.GuildMission import getScrollPieces
from common.GuildMission import updateBossScrollPieces
from common.GuildMission import processResult
from common.Logger import Logger
from gui.CommonModal import CommonModal
from gui.CommonView import CommonView

gmListEmptyLabel = "-- GM list is empty --"

#--------------------------------------------------------------------------
# GMUpdatePanel
#--------------------------------------------------------------------------
class GMUpdatePanel():
  def __init__(self, interaction:discord.Interaction):
    self.interaction = interaction
    self.view = GMUpdatePanelView(actionSelectCallback=self.actionSelectCallback)
    self.emby = None
    self.action = None
    self.gm = None

  async def run(self):
    self.emby = await genGMListEmbed()
    await self.interaction.response.send_message(view=self.view, embed=self.emby, ephemeral=getConfig('gmUpdatePanelPrivate'))
    self.view.parentMsg = await self.interaction.original_response()

  #------------------------------------------------------------------------
  # Action Select Callback
  async def actionSelectCallback(self, interaction:discord.Interaction) -> None:
    self.action = str(self.view.actionSelect.values[0])
    self.view.stop()
    Logger.logInfo(self, "Action: " + self.action)
    # --- Add
    if self.action == "Add":
      await self.view.parentMsg.delete()
      await interaction.response.send_modal(GMAddModal())
    # --- Quick Add
    elif self.action == "Quick Add":
      await self.view.parentMsg.delete()
      await interaction.response.send_modal(GMQuickAddModal())
    # --- Edit / Delete
    elif self.action == "Edit" or self.action == "Delete":
      await interaction.response.defer()
      self.view = GMUpdatePanelView(parentMsg=self.view.parentMsg,
                                    chosenAction=self.action,
                                    actionSelectCallback=self.actionSelectCallback,
                                    gmListSelectCallback=self.gmSelectCallback,)
      await self.view.parentMsg.edit(embed=self.emby, view=self.view)
    # --- Clear
    elif self.action == "Clear":
      await interaction.response.defer()
      self.view = GMUpdatePanelView(parentMsg=self.view.parentMsg,
                                    chosenAction=self.action,
                                    actionSelectCallback=self.actionSelectCallback,
                                    submitButtonCallback=self.submitButtonCallback)
      await self.view.parentMsg.edit(embed=self.emby, view=self.view)
    # --- Boss Scrolls
    elif self.action == "Boss Scrolls":
      await self.view.parentMsg.delete()
      await interaction.response.send_modal(GMBossScrollsModal())
    else:
      Logger.logError(self, "Unsupported action for Action Select list")
      await sendErrorMessage(interaction=interaction, content=genericErrorMsg)

  #------------------------------------------------------------------------
  # GM Select Callback
  async def gmSelectCallback(self, interaction:discord.Interaction) -> None:
    self.view.stop()
    self.gm = self.view.gmListSelect.values[0]
    Logger.logInfo(self, "GM Selected: " + self.gm)
    await interaction.response.defer()
    if self.gm != gmListEmptyLabel:
      self.view = GMUpdatePanelView(parentMsg=self.view.parentMsg,
                                    chosenAction=self.action, chosenGM=self.gm,
                                    actionSelectCallback=self.actionSelectCallback,
                                    gmListSelectCallback=self.gmSelectCallback,
                                    submitButtonCallback=self.submitButtonCallback)
    else:
      self.view = GMUpdatePanelView(parentMsg=self.view.parentMsg,
                                    chosenAction=self.action,
                                    actionSelectCallback=self.actionSelectCallback,
                                    gmListSelectCallback=self.gmSelectCallback)
    await self.view.parentMsg.edit(embed=self.emby, view=self.view)

  #------------------------------------------------------------------------
  # Submit Button Callback
  async def submitButtonCallback(self, interaction:discord.Interaction) -> None:
    self.view.stop()
    await self.view.parentMsg.delete()
    # --- Edit
    if self.action == "Edit":
      guildMission = await findGuildMission(self.gm)
      if guildMission:
        await interaction.response.send_modal(GMEditModal(self.gm, guildMission))
      else:
        msg = userIdStub + " I couldn't find a GM in the list called **" + self.gm + "**"
        await sendErrorMessage(interaction=interaction, content=msg)
    # --- Delete
    elif self.action == "Delete":
      await logCommand(interaction=interaction, cmdNameOverride="Update - Delete")
      result = await deleteGMReqEntry(self.gm)
      await processResult(interaction=interaction, result=result)
    # --- Clear
    elif self.action == "Clear":
      await logCommand(interaction=interaction, cmdNameOverride="Update - Clear")
      result = await clearGMReqTable()
      await processResult(interaction=interaction, result=result)
    else:
      Logger.logError(self, "Unsupported action for Submit button")
      await sendErrorMessage(interaction=interaction, content=genericErrorMsg)

#--------------------------------------------------------------------------
# View for GMUpdatePanel
# The user can select/reselect an Action from a drop-down list.
# If the user has already chosen the Edit or Delete action, they can
# select/reselect a GM from second drop-down list.
#--------------------------------------------------------------------------
class GMUpdatePanelView(CommonView):
  def __init__(self, parentMsg=None,
               actionSelectCallback=None, chosenAction:str=None,
               gmListSelectCallback=None, chosenGM:str=None,
               cancelButtonCallback=None, submitButtonCallback=None):
    super().__init__(parentMsg=parentMsg, timeout=getConfig('gmUpdatePanelTimeout'),
                     cancelButtonCallback=cancelButtonCallback,
                     submitButtonCallback=submitButtonCallback)
    if actionSelectCallback:
      self.actionSelect = ui.Select(placeholder = "Select an action")
      self.actionSelect.callback = actionSelectCallback
      self.initActionSelect(chosenAction)
      self.add_item(self.actionSelect)
    if gmListSelectCallback:
      prompt = gmp.gmPromptEdit if chosenAction == "Edit" else gmp.gmPromptDelete
      self.gmListSelect = ui.Select(placeholder=prompt)
      self.gmListSelect.callback = gmListSelectCallback
      self.initGMListSelections(chosenGM)
      self.add_item(self.gmListSelect)
    self.addCancelButton()
    if chosenGM or chosenAction == "Clear":
      self.addSubmitButton()
    if chosenGM and chosenAction == "Edit":
      self.submitButton.label = "Continue"
  
  def initActionSelect(self, chosenAction:str):
    for cmd in gmCommandList:
      if cmd.namePretty != "List" and cmd.namePretty != "Update":
        default = True if cmd.namePretty == chosenAction else False
        self.actionSelect.add_option(label=cmd.namePretty, description=cmd.descrLong, default=default)
      else:
        continue

  def initGMListSelections(self, chosenGM:str):
    gmList = getGMList()
    if gmList:
      for gm in gmList:
        default = True if gm == chosenGM else False
        self.gmListSelect.add_option(label=gm, default=default)
    else:
      self.gmListSelect.add_option(label=gmListEmptyLabel)

#--------------------------------------------------------------------------
# Modal for Add
# Note: The API limits modals to a max of 5 items.
#--------------------------------------------------------------------------
class GMAddModal(CommonModal):
  def __init__(self):
    super().__init__(title="Add Guild Mission", timeout=getConfig('gmAddTimeout'))
    self.target = ui.TextInput(label='Target', placeholder=gmp.targetPrompt1,
                               required=True, min_length=1, max_length=80)
    self.server = ui.TextInput(label='Server (Optional)', placeholder=gmp.serverPrompt,
                               required=False, min_length=1, max_length=80)
    self.size   = ui.TextInput(label='Size (Optional)', placeholder=gmp.sizePrompt,
                               required=False, min_length=1, max_length=80)
    self.add_item(self.target)
    self.add_item(self.server)
    self.add_item(self.size)

  async def on_submit(self, interaction:discord.Interaction):
    await logCommand(interaction=interaction, cmdNameOverride="Update - Add")
    self.stop()
    guildMissions = [GuildMission(str(self.target.value), str(self.server.value), str(self.size.value))]
    result = await addGMReqEntries(guildMissions)
    await processResult(interaction=interaction, result=result)

#--------------------------------------------------------------------------
# Modal for Quick Add
# Note: The API limits modals to a max of 5 items.
#--------------------------------------------------------------------------
class GMQuickAddModal(CommonModal):
  def __init__(self):
    super().__init__(title="Add Several Guild Missions", timeout=getConfig('gmQuickAddTimeout'))
    self.target1 = ui.TextInput(label='Target', placeholder=gmp.targetPrompt1,
                                required=True, min_length=1, max_length=80)
    self.target2 = ui.TextInput(label='Target (Optional)', placeholder=gmp.targetPrompt2,
                                required=False, min_length=1, max_length=80)
    self.target3 = ui.TextInput(label='Target (Optional)', placeholder=gmp.targetPrompt3,
                                required=False, min_length=1, max_length=80)
    self.target4 = ui.TextInput(label='Target (Optional)', placeholder=gmp.targetPrompt4,
                                required=False, min_length=1, max_length=80)
    self.target5 = ui.TextInput(label='Target (Optional)', placeholder=gmp.targetPrompt5,
                                required=False, min_length=1, max_length=80)

    self.add_item(self.target1)
    self.add_item(self.target2)
    self.add_item(self.target3)
    self.add_item(self.target4)
    self.add_item(self.target5)

  async def on_submit(self, interaction:discord.Interaction):
    await logCommand(interaction=interaction, cmdNameOverride="Update - Quick Add")
    self.stop()
    guildMissions = [GuildMission(self.target1.value), GuildMission(self.target2.value),
                     GuildMission(self.target3.value), GuildMission(self.target4.value),
                     GuildMission(self.target5.value)]
    result = await addGMReqEntries(guildMissions)
    await processResult(interaction=interaction, result=result)

#--------------------------------------------------------------------------
# Modal for Edit
# Note: The API limits modals to a max of 5 items.
#--------------------------------------------------------------------------
class GMEditModal(CommonModal):
  def __init__(self, gm:str, guildMission):
    super().__init__(title="Edit Guild Mission", timeout=getConfig('gmEditTimeout'))
    self.gm = gm
    promptForTarget = gmp.targetPrompt1
    promptForServer = gmp.serverPromptLong if guildMission.server else gmp.serverPrompt
    promptForSize = gmp.sizePromptLong if guildMission.gmsize else gmp.sizePrompt
    self.target = ui.TextInput(label='Target',
                               placeholder=promptForTarget, default=guildMission.name,
                               required=False, min_length=1, max_length=80)
    self.server = ui.TextInput(label='Server (Optional)',
                               placeholder=promptForServer, default=guildMission.server,
                               required=False, min_length=1, max_length=80)
    self.size   = ui.TextInput(label='Size (Optional)',
                               placeholder=promptForSize, default=guildMission.gmsize,
                               required=False, min_length=1, max_length=80)
    self.add_item(self.target)
    self.add_item(self.server)
    self.add_item(self.size)

  async def on_submit(self, interaction:discord.Interaction):
    await logCommand(interaction=interaction, cmdNameOverride="Update - Edit")
    self.stop()
    result = await editGMReqEntry(str(self.gm), str(self.target), str(self.server), str(self.size))
    await processResult(interaction=interaction, result=result)

#--------------------------------------------------------------------------
# Modal for Boss Scrolls
# Note: The API limits modals to a max of 5 items.
#--------------------------------------------------------------------------
class GMBossScrollsModal(CommonModal):
  def __init__(self):
    super().__init__(title="Update Boss Scroll Pieces", timeout=getConfig('gmBossScrollTimeout'))
    scrollPieces = getScrollPieces()
    self.garmoth = ui.TextInput(label='Garmoth Scroll Pieces',
                                placeholder=gmp.garmothPrompt, default=str(scrollPieces.garmoth),
                                required=False, min_length=1, max_length=80)
    self.khan    = ui.TextInput(label='Khan Scroll Pieces',
                                placeholder=gmp.khanPrompt, default=str(scrollPieces.khan),
                                required=False, min_length=1, max_length=80)
    self.puturum = ui.TextInput(label='Puturum Scroll Pieces',
                                placeholder=gmp.puturumPrompt, default=str(scrollPieces.puturum),
                                required=False, min_length=1, max_length=80)
    self.ferrid  = ui.TextInput(label='Ferrid Scroll Pieces',
                                placeholder=gmp.ferridPrompt, default=str(scrollPieces.ferrid),
                                required=False, min_length=1, max_length=80)
    self.mudster = ui.TextInput(label='Mudster Scroll Pieces',
                                placeholder=gmp.mudsterPrompt, default=str(scrollPieces.mudster),
                                required=False, min_length=1, max_length=80)
    self.add_item(self.garmoth)
    self.add_item(self.khan)
    self.add_item(self.puturum)
    self.add_item(self.ferrid)
    self.add_item(self.mudster)

  async def on_submit(self, interaction:discord.Interaction):
    await logCommand(interaction=interaction, cmdNameOverride="Update - Boss Scrolls")
    self.stop()
    scrollPieces = ScrollPieces(garmoth=self.garmoth.value, khan=self.khan.value,
                                puturum=self.puturum.value, ferrid=self.ferrid.value,
                                mudster=self.mudster.value)
    result = await updateBossScrollPieces(scrollPieces)
    await processResult(interaction=interaction, result=result)
