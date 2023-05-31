import discord
from typing import List
from replit import db
from common.common import embyColour
from common.common import userIdStub
from common.common import sendErrorMessage
from common.common import Result

gmReqTable = "gm_reqs"
gmReqNameKey = "name"
gmReqServerKey = "server"
gmReqSizeKey = "gmsize"

blankMark = ""
checkMark = " :white_check_mark: "
serverDelim = " ✓ "
nameModifier = "ⁱ"
circleBullet = "\u2022 "
spacer = "\u2800"

noServer = "X"
noSize = "X"

#-------------------------------------------------------------------------------------------
# The GuildMission class encapsulates the different attributes of a Guild Mission
#-------------------------------------------------------------------------------------------
class GuildMission:
  # Create an instance of GuildMission
  def __init__(self, name:str, server:str=None, gmsize=None):
    self.name = name
    self.server = server
    self.gmsize = self.fixSize(gmsize)

  # Define the equality comparison operator
  def __eq__(self, other):
    if (isinstance(other, GuildMission)):
      return self.name == other.name and \
             self.serverForDB() == other.serverForDB() and \
             self.gmsizeForDB() == other.gmsizeForDB()
    return False

  # Create and return an instance of GuildMission from a DB dict type
  @staticmethod
  def fromDict(gmReqEntry:dict):
    return GuildMission(gmReqEntry[gmReqNameKey], gmReqEntry[gmReqServerKey], gmReqEntry[gmReqSizeKey])

  # Create and return an instance of GuildMission, replacing None values with the
  # given default values
  @staticmethod
  def withDefaults(name:str, server:str, gmsize:str, defaults):
    guildMission = GuildMission(name, server, gmsize)
    guildMission.name   = defaults.name   if not guildMission.name   else guildMission.name
    guildMission.server = defaults.server if not guildMission.server else guildMission.server
    guildMission.gmsize = defaults.gmsize if not guildMission.gmsize else guildMission.gmsize
    guildMission.gmsize = None if not guildMission.server else guildMission.gmsize
    return guildMission

  # If the given gmsize is a numeric, add an 'x' at the beginning
  def fixSize(self, gmsize:str):
    if gmsize and gmsize.isnumeric():
      gmsize = "x" + gmsize
    return gmsize

  # If the user specified noServer for server, return None so the server
  # value will be cleared in the DB
  def serverForDB(self):
    if self.server and self.server.lower() == noServer.lower():
      return None
    else:
      return self.server

  # If the user specified noSize for gmsize or noServer for server, return None
  # so the gmsize value will be cleared in the DB
  def gmsizeForDB(self):
    if self.gmsize and self.gmsize.lower() == noSize.lower() or \
       self.server and self.server.lower() == noServer.lower() or \
       not self.server:
      return None
    else:
      return self.gmsize

  # Prep for the DB by setting any noSize and noServer values to None
  def forDB(self):
    return GuildMission(self.name, self.serverForDB(), self.gmsizeForDB())

#-------------------------------------------------------------------------------------------
# Get the GMs from the DB and return them as a list of GuildMission types 
#-------------------------------------------------------------------------------------------
def getCurrentGuildMissionList() -> List[GuildMission]:
  guildMissions = []
  if gmReqTable in db.keys():
    for gmReqEntry in db[gmReqTable]:
      guildMissions.append(GuildMission.fromDict(gmReqEntry))
  return guildMissions

#-------------------------------------------------------------------------------------------
# Get the GMs from the DB and return them as a list of strings in the following format:
# "Pollys - Pat ✓ SS1 x3000"
#-------------------------------------------------------------------------------------------
def getGMList() -> List[str]:
  gmList = []
  guildMissions = getCurrentGuildMissionList() 
  for guildMission in guildMissions:
    gm = guildMission.name
    if guildMission.server:
      if guildMission.gmsize:
        gm += serverDelim + guildMission.server + " " + guildMission.gmsize
      else:
        gm += serverDelim + guildMission.server
    gmList.append(gm)
  return gmList

#-------------------------------------------------------------------------------------------
# Find the GM req entry in the DB that matches the given name
#-------------------------------------------------------------------------------------------
async def findGMReqEntry(name:str):
  gmReqEntry = None
  if gmReqTable in db.keys():
    gmReqEntry = next((req for req in db[gmReqTable] if req[gmReqNameKey] == name), None)
  return gmReqEntry

#-------------------------------------------------------------------------------------------
# Find the GM req entry in the DB that matches the given name
# and return it as a GuildMisson type
#-------------------------------------------------------------------------------------------
async def findGuildMission(gm:str) -> GuildMission:
  guildMission = None
  gmReqEntry = await findGMReqEntry(await extractName(gm))
  if gmReqEntry:
    guildMission = GuildMission.fromDict(gmReqEntry)
  return guildMission

#-------------------------------------------------------------------------------------------
# For a new GM whose name already exists in the database, change the given name slightly
# by repeatedly appending a name modifier until the name is unique
#-------------------------------------------------------------------------------------------
async def validateName(name:str, iter:int=0) -> str:
  if await findGMReqEntry(name):
    return await validateName(name + nameModifier, iter + 1)
  else:
    return name

#-------------------------------------------------------------------------------------------
# Extract the GM name from a string that has this format: "Pollys - Pat ✓ SS1 x3000"
#-------------------------------------------------------------------------------------------
async def extractName(gm:str) -> str:
  pos = gm.find(serverDelim)
  if pos > -1:
    name = gm[0:pos]
    return name
  else:
    return gm

#-------------------------------------------------------------------------------------------
# For the GM with the given index in the DB, update it with the given new GM values
#-------------------------------------------------------------------------------------------
async def updateDB(index:int, guildMission:GuildMission):
  guildMission = guildMission.forDB()
  db[gmReqTable][index][gmReqNameKey]   = guildMission.name
  db[gmReqTable][index][gmReqServerKey] = guildMission.server
  db[gmReqTable][index][gmReqSizeKey]   = guildMission.gmsize if guildMission.server else None

#-------------------------------------------------------------------------------------------
# Insert the given GM into the DB
#-------------------------------------------------------------------------------------------
async def insertIntoDB(guildMission:GuildMission):
  guildMission = guildMission.forDB()
  if gmReqTable in db.keys():
    db[gmReqTable].append(vars(guildMission))
  else:
    db[gmReqTable] = [vars(guildMission)]

#-------------------------------------------------------------------------------------------
# Generate a response message for a GM that has been deleted
#-------------------------------------------------------------------------------------------
async def genDeleteResponseMsg(gm:str) -> Result:
  result = Result(msg="> " + userIdStub + " deleted")
  result.msg += "\n> " if gm.find(serverDelim) > -1 else " "
  result.msg += "**" + gm + "**"
  return result

#-------------------------------------------------------------------------------------------
# Generate a response message for a GM that has been edited
#-------------------------------------------------------------------------------------------
async def genChangeResponseMsg(gmOld:str, newGuildMission:GuildMission) -> Result:
  newGuildMission = newGuildMission.forDB()
  gmNew = newGuildMission.name
  gmNew += serverDelim + newGuildMission.server if newGuildMission.server else ""
  gmNew += " " + newGuildMission.gmsize if newGuildMission.gmsize and newGuildMission.server else ""

  result = Result()
  if gmOld != gmNew:
    result.msg = "> " + userIdStub + " changed\n> **" + gmOld + "** to\n> **" + gmNew + "**"
  else:
    result.msg = userIdStub + "\nYou made no changes to **" + gmOld + "**"
    result.good = False

  return result

#-------------------------------------------------------------------------------------------
# Add the given list of GMs to the database
#-------------------------------------------------------------------------------------------
async def addGMReqEntries(guildMissions:List[GuildMission]) -> Result:
  # Enforce a max of 25 GMs because the Select object can hold only 25 items
  if (len(getGMList()) + len([gm for gm in guildMissions if gm.name])) > 25:
    msg = userIdStub + "\nThe number of GMs you are trying to add will exceed the max of **25** GMs"
    return(Result(msg=msg, good=False))

  result = Result(msg="> " + userIdStub + " added ")
  dupNames = 0
  iteration = 0
  for guildMission in guildMissions:
    iteration += 1
    if guildMission.name:

      valname = await validateName(guildMission.name)
      if valname != guildMission.name:
        guildMission.name = valname
        dupNames += 1

      result.msg += "\n> " if guildMission.server else ""
      result.msg += "**" if iteration == 1 else ",  **" 
      result.msg += guildMission.name
      result.msg += serverDelim + guildMission.server if guildMission.server else ""
      result.msg += " " + guildMission.gmsize if guildMission.gmsize and guildMission.server else ""
      result.msg += "**"

      await insertIntoDB(guildMission)

  if dupNames > 1:
    result.msg += "\n> *(GM targets modified to make unique)*"
  elif dupNames > 0:
    result.msg += "\n> *(GM target modified to make unique)*"
  return result

#-------------------------------------------------------------------------------------------
# Delete a GM from the database
#-------------------------------------------------------------------------------------------
async def deleteGMReqEntry(gm:str) -> Result:
  gmReqEntry = await findGMReqEntry(await extractName(gm))
  if gmReqEntry:
    db[gmReqTable].remove(gmReqEntry)
    return await genDeleteResponseMsg(gm)
  else:
    return Result(good=False, msg=userIdStub + "\nI couldn't find a GM in the list called **" + gm + "**")

#-------------------------------------------------------------------------------------------
# Edit a GM in the database
#-------------------------------------------------------------------------------------------
async def editGMReqEntry(gm:str, name:str, server:str, gmsize:str) -> Result:
  gmReqEntry = await findGMReqEntry(await extractName(gm))
  if gmReqEntry:
    oldGuildMission = GuildMission.fromDict(gmReqEntry)
    newGuildMission = GuildMission.withDefaults(name, server, gmsize, oldGuildMission)

    dupName = False
    if newGuildMission.name != oldGuildMission.name:
      valnewname = await validateName(newGuildMission.name)
      if valnewname != newGuildMission.name:
        newGuildMission.name = valnewname
        dupName = True

    await updateDB(db[gmReqTable].index(gmReqEntry), newGuildMission)

    result = await genChangeResponseMsg(gm, newGuildMission)
    result.msg += "\n> *(GM name modified due to duplicates)*" if dupName else ""
    return result
  else:
    result = Result(msg=userIdStub + "\nI couldn't find a GM in the list called **" + gm + "**")
    result.good = False
    return result

#-------------------------------------------------------------------------------------------
# Clear all GMs from the DB
#-------------------------------------------------------------------------------------------
async def clearGMReqTable() -> Result:
  if gmReqTable in db.keys():
    del db[gmReqTable]
  return Result(msg="> " + userIdStub + " cleared the GM list")

#-------------------------------------------------------------------------------------------
# The ScrollPieces class encapsulates the three different types of boss scroll pieces
#-------------------------------------------------------------------------------------------
class ScrollPieces:
  def __init__(self, garmoth:str, ferrid:str, mudster:str):
    self.garmoth = garmoth
    self.ferrid = ferrid
    self.mudster = mudster

#-------------------------------------------------------------------------------------------
# Get the current number of scroll pieces
#-------------------------------------------------------------------------------------------
def getScrollPieces() -> ScrollPieces:
  return ScrollPieces(garmoth=db['garmy_pieces'],
                      ferrid=db['ferrid_pieces'],
                      mudster=db['mudster_pieces'])

#-------------------------------------------------------------------------------------------
# Update the number of boss scroll pieces in the DB
#-------------------------------------------------------------------------------------------
async def updateBossScrollPieces(scrollPieces:ScrollPieces) -> Result:
  result = Result(msg="> " + userIdStub + " updated")
  result.good = False

  try:
    garmoth = int(scrollPieces.garmoth)
    ferrid = int(scrollPieces.ferrid)
    mudster = int(scrollPieces.mudster)
  except:
    result.msg = userIdStub + "\nPlease enter numbers only for **Boss Scroll** pieces"
    return result

  if garmoth != None:
    garmoth = 5 if garmoth > 5 else garmoth
    garmothOld = db['garmy_pieces']
    if garmothOld != garmoth:
      db['garmy_pieces'] = garmoth
      result.msg += "\n> **Garmoth** scroll pieces from **" + str(garmothOld) + "** to **" + str(garmoth) + "**"
      result.good = True

  if ferrid != None:
    ferrid  = 4 if ferrid > 4 else ferrid
    ferridOld = db['ferrid_pieces'] 
    if ferridOld != ferrid:
      db['ferrid_pieces'] = ferrid
      result.msg += "\n> **Ferrid** scroll pieces from **" + str(ferridOld) + "** to **" + str(ferrid) + "**"
      result.good = True

  if mudster != None:
    mudster = 4 if mudster > 4 else mudster
    mudsterOld = db['mudster_pieces']
    if mudsterOld != mudster:
      db['mudster_pieces'] = mudster
      result.msg += "\n> **Mudster** scroll pieces from **" + str(mudsterOld) + "** to **" + str(mudster) + "**"
      result.good = True

  if not result.good:
    result.msg = userIdStub + "\nYou made no changes to **Boss Scrolls**"
    return result

  if db['garmy_pieces'] == 0 and db['ferrid_pieces'] == 0 and db['mudster_pieces'] == 0:
    result.msg = "> " + userIdStub + " set all **Boss Scroll** pieces to **zero**"

  return result

#-------------------------------------------------------------------------------------------
# Process a final result status
#-------------------------------------------------------------------------------------------
async def processResult(interaction:discord.Interaction, result:Result) -> None:
  if result.good:
    from gui.GMListPanel import GMListPanel
    gmListPanel = GMListPanel(interaction=interaction, content=result.msg)
    await gmListPanel.run()
  else:
    await sendErrorMessage(interaction=interaction, content=result.msg)

#-------------------------------------------------------------------------------------------
# Generate and return an embed with the current list of GMs
#-------------------------------------------------------------------------------------------
async def genGMListEmbed() -> discord.Embed:
  embyTitle = "**Guild Missions**"
  guildMissions = getCurrentGuildMissionList()
  totalGMs = len(guildMissions)
  if totalGMs > 0:
    gmList = "**"
    for guildMission in guildMissions:
      gmList += circleBullet
      gmList += str(guildMission.name)
      gmList += checkMark + guildMission.server if guildMission.server else blankMark
      gmList += " " + guildMission.gmsize if guildMission.gmsize else ""
      gmList += "\n"
    gmList += "**"
  else:
    gmList = " "

  ferridPieces  = db["ferrid_pieces"] if "ferrid_pieces" in db.keys() else 0
  mudsterPieces = db["mudster_pieces"] if "mudster_pieces" in db.keys() else 0
  garmothPieces = db["garmy_pieces"] if "garmy_pieces" in db.keys() else 0

  lineLimit = 56 if totalGMs < 10 else 54
  scrollStatusTitle = "*__**"
  for i in range (lineLimit):
    scrollStatusTitle += " "
  scrollStatusTitle += "Total GMs: **" + str(totalGMs) + "__*\n"    
  scrollStatusTitle += "***Boss Scrolls***"
  scrollStatus = "***Garmoth:** " + str(garmothPieces) + "/5" + spacer + \
                 "**Ferrid:** " + str(ferridPieces) + "/4" + spacer + \
                 "**Mudster:** " + str(mudsterPieces) + "/4*"

  emby = discord.Embed(title=embyTitle,
                       description=gmList,
                       colour=embyColour)

  emby.add_field(name=scrollStatusTitle,
                 value=scrollStatus,
                 inline=False)

  return emby
