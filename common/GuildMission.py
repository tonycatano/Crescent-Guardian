import discord
from typing import List
from replit import db

gmReqTable = "gm_reqs"
gmReqNameKey = "name"
gmReqServerKey = "server"
gmReqSizeKey = "gmsize"

blankMark = ""
checkMark = " :white_check_mark: "
serverDelim = " ✓ "
nameModifier = "ⁱ"
garmyURL = "https://bdocodex.com/items/ui_artwork/ic_05154.png"

noServer = "-ERASE-"
noSize = "-ERASE-"

# TODO: Make a superuser command '/season {on,off}' or '/cgconfig severlist'
# to update the server list when a Season is active
gmServers = [noServer, "SS1", "SS2", "SS3", "B1", "B2", "C1", "C2",
             "M1", "M2", "S1", "S2", "Val", "Arsha"]
#gmServers = [noServer, "B1", "B2", "C1", "C2", "M1", "M2", "S1", "S2",
#              "Rulu", "Val", "Arsha"]

gmSizes = [noSize]

quickNames = ["Hasrah Ruins", "Soldiers", "Bashims", "Cadrys", "Crescents", "Nagas "]

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
async def getCurrentGuildMissionList() -> List[GuildMission]:
  guildMissions = []
  if gmReqTable in db.keys():
    for gmReqEntry in db[gmReqTable]:
      guildMissions.append(GuildMission.fromDict(gmReqEntry))
  return guildMissions

#-------------------------------------------------------------------------------------------
# Get the GMs from the DB and return them as a list of strings in the following format:
# "Pollys - Pat ✓ SS1 x3000"
#-------------------------------------------------------------------------------------------
async def getGMList() -> List[str]:
  gmList = []
  guildMissions = await getCurrentGuildMissionList() 
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
async def genDeleteResponseMsg(guildMission:GuildMission):
  guildMission = guildMission.forDB()
  msg="Deleted **" + guildMission.name
  if guildMission.server:
    if guildMission.gmsize:
      msg += serverDelim + guildMission.server + " " + guildMission.gmsize
    else:
      msg += serverDelim + guildMission.server
  msg += "**"
  return msg

#-------------------------------------------------------------------------------------------
# Generate a response message for a GM that has been changed
#-------------------------------------------------------------------------------------------
async def genChangeResponseMsg(oldGuildMission:GuildMission, newGuildMission:GuildMission):
  oldGuildMission = oldGuildMission.forDB()
  newGuildMission = newGuildMission.forDB()
  if oldGuildMission != newGuildMission:
    msg = "Changed **" + oldGuildMission.name
    if oldGuildMission.server:
      if oldGuildMission.gmsize:
        msg += serverDelim + oldGuildMission.server + " " + oldGuildMission.gmsize
      else:
        msg += serverDelim + oldGuildMission.server
    msg += "**\n             to **" + newGuildMission.name
    if newGuildMission.server:
      if newGuildMission.gmsize:
        msg += serverDelim + newGuildMission.server + " " + newGuildMission.gmsize
      else:
        msg += serverDelim + newGuildMission.server
    msg += "**"
    return msg
  else:
    return "Nothing changed for **" + oldGuildMission.name + "**"

#-------------------------------------------------------------------------------------------
# Add the given list of GMs to the database
#-------------------------------------------------------------------------------------------
async def addGMReqEntries(guildMissions:List[GuildMission]) -> str:
  msg = "Added "
  dupNames = 0
  iteration = 0
  for guildMission in guildMissions:
    iteration += 1
    if guildMission.name:

      valname = await validateName(guildMission.name)
      if valname != guildMission.name:
        guildMission.name = valname
        dupNames += 1

      msg += "**" if iteration == 1 else ",  **" 
      msg += guildMission.name
      msg += serverDelim + guildMission.server if guildMission.server else ""
      msg += " " + guildMission.gmsize if guildMission.gmsize and guildMission.server else ""
      msg += "**"

      await insertIntoDB(guildMission)

  if dupNames > 1:
    msg += "\n*(GM names modified due to duplicates)*"
  elif dupNames > 0:
    msg += "\n*(GM name modified due to duplicates)*"
  return msg

#-------------------------------------------------------------------------------------------
# Delete a GM from the database
#-------------------------------------------------------------------------------------------
async def deleteGMReqEntry(gm:str) -> str:
  gmReqEntry = await findGMReqEntry(await extractName(gm))
  if gmReqEntry:
    oldGuildMission = GuildMission.fromDict(gmReqEntry)
    db[gmReqTable].remove(gmReqEntry)
    return await genDeleteResponseMsg(oldGuildMission)
  else:
    return None

#-------------------------------------------------------------------------------------------
# Edit a GM in the database
#-------------------------------------------------------------------------------------------
async def editGMReqEntry(gm:str, name:str, server:str, gmsize:str) -> str:
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

    msg = await genChangeResponseMsg(oldGuildMission, newGuildMission)
    msg += "\n*(GM name modified due to duplicates)*" if dupName else ""
    return msg
  else:
    return None

#-------------------------------------------------------------------------------------------
# Edit the server and gmsize for a GM
#-------------------------------------------------------------------------------------------
async def setGMServerAndSize(gm:str, server:str, gmsize:str) -> str:
  gmReqEntry = await findGMReqEntry(await extractName(gm))
  if gmReqEntry:
    oldGuildMission = GuildMission.fromDict(gmReqEntry)
    newGuildMission = GuildMission.withDefaults(None, server, gmsize, oldGuildMission)
    await updateDB(db[gmReqTable].index(gmReqEntry), newGuildMission)
    return await genChangeResponseMsg(oldGuildMission, newGuildMission)
  else:
    return None

#-------------------------------------------------------------------------------------------
# Clear all GMs from the DB
#-------------------------------------------------------------------------------------------
async def clearGMReqTable():
  if gmReqTable in db.keys():
    del db[gmReqTable]

#-------------------------------------------------------------------------------------------
# Update the number of Garmoth scroll pieces in the DB
#-------------------------------------------------------------------------------------------
async def updateGarmyPieces(pieces:int) -> str:
  db['garmy_pieces'] = pieces
  msg = "Updated **Garmoth Scroll Status** to **"
  if pieces > 4:
    msg += "Complete!**"
  else:
    msg += str(pieces) + "** "
    msg += "piece" if pieces == 1 else "pieces"
  return msg

#-------------------------------------------------------------------------------------------
# Generate and return an embed with the current list of GMs
#-------------------------------------------------------------------------------------------
async def genGMListEmbed() -> discord.Embed:
  embyTitle = "Guild Missions"
  guildMissions = await getCurrentGuildMissionList()
  if len(guildMissions):
    gmList = "**"
    for guildMission in guildMissions:
      gmList += str(guildMission.name)
      gmList += checkMark + guildMission.server if guildMission.server else blankMark
      gmList += " " + guildMission.gmsize if guildMission.gmsize else ""
      gmList += "\n"
    gmList += "**"
  else:
    gmList = "*<GM list is empty>*"
  
  emby = discord.Embed(title=embyTitle,
                       description=gmList,
                       colour=discord.Colour.blue())

  pieces = db["garmy_pieces"] if "garmy_pieces" in db.keys() else 0
  garmy_status = "Garmoth Scroll Status: "
  garmy_status += "Complete!" if pieces > 4 else str(pieces) + "/5"
  emby.set_footer(text=garmy_status, icon_url=garmyURL)

  return emby