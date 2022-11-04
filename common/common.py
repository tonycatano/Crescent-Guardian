import os
import discord
from typing import List
from replit import db

# TODO: The following few items will be moved to a new file called 'genutils'
guildIDs=[discord.Object(id=os.environ['DISCORD_SERVER_ID'])]
connectionLogFile = "logs/rocg.connection.log"
commandLogFile = "logs/rocg.command.log"

# TODO: The rest of this stuff will remain in this file, but the file will be
#       renamed to 'gmrequest.py' after the class defined in this file.
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
# The GMRequest class encapsulates the different attributes of a GM request
#-------------------------------------------------------------------------------------------
class GMRequest:
  # Create an instance of GMRequest
  def __init__(self, name:str, server:str=None, gmsize=None):
    self.name = name
    self.server = server
    self.gmsize = self.fixSize(gmsize)

  # Define the equality comparison operator
  def __eq__(self, other):
    if (isinstance(other, GMRequest)):
      return self.name == other.name and \
             self.serverForDB() == other.serverForDB() and \
             self.gmsizeForDB() == other.gmsizeForDB()
    return False

  # Create and return an instance of GMRequest from a DB dict type
  @staticmethod
  def fromDict(gmReqEntry:dict):
    return GMRequest(gmReqEntry[gmReqNameKey], gmReqEntry[gmReqServerKey], gmReqEntry[gmReqSizeKey])

  # Create and return an instance of GMRequest, replacing None values with the
  # given default values
  @staticmethod
  def withDefaults(name:str, server:str, gmsize:str, defaults):
    gmRequest = GMRequest(name, server, gmsize)
    gmRequest.name   = defaults.name   if not gmRequest.name   else gmRequest.name
    gmRequest.server = defaults.server if not gmRequest.server else gmRequest.server
    gmRequest.gmsize = defaults.gmsize if not gmRequest.gmsize else gmRequest.gmsize
    gmRequest.gmsize = None if not gmRequest.server else gmRequest.gmsize
    return gmRequest

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
    return GMRequest(self.name, self.serverForDB(), self.gmsizeForDB())

#-------------------------------------------------------------------------------------------
# Get the GMs from the DB and return them as a list of GMRequest types 
#-------------------------------------------------------------------------------------------
async def getCurrentGMRequestList() -> List[GMRequest]:
  gmRequests = []
  if gmReqTable in db.keys():
    for gmReqEntry in db[gmReqTable]:
      gmRequests.append(GMRequest.fromDict(gmReqEntry))
  return gmRequests

#-------------------------------------------------------------------------------------------
# Get the GMs from the DB and return them as a list of strings in the following format:
# "Pollys - Pat ✓ SS1 x3000"
#-------------------------------------------------------------------------------------------
async def getGMList() -> List[str]:
  gmList = []
  gmRequests = await getCurrentGMRequestList() 
  for gmRequest in gmRequests:
    gm = gmRequest.name
    if gmRequest.server:
      if gmRequest.gmsize:
        gm += serverDelim + gmRequest.server + " " + gmRequest.gmsize
      else:
        gm += serverDelim + gmRequest.server
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
async def updateDB(index:int, newGMRequest:GMRequest):
  newGMRequest = newGMRequest.forDB()
  db[gmReqTable][index][gmReqNameKey]   = newGMRequest.name
  db[gmReqTable][index][gmReqServerKey] = newGMRequest.server
  db[gmReqTable][index][gmReqSizeKey]   = newGMRequest.gmsize if newGMRequest.server else None

#-------------------------------------------------------------------------------------------
# Insert the given GM into the DB
#-------------------------------------------------------------------------------------------
async def insertIntoDB(newGMRequest:GMRequest):
  newGMRequest = newGMRequest.forDB()
  if gmReqTable in db.keys():
    db[gmReqTable].append(vars(newGMRequest))
  else:
    db[gmReqTable] = [vars(newGMRequest)]

#-------------------------------------------------------------------------------------------
# Generate a response message for a GM that has been deleted
#-------------------------------------------------------------------------------------------
async def genDeleteResponseMsg(oldGMRequest:GMRequest):
  oldGMRequest = oldGMRequest.forDB()
  msg="Deleted **" + oldGMRequest.name
  if oldGMRequest.server:
    if oldGMRequest.gmsize:
      msg += serverDelim + oldGMRequest.server + " " + oldGMRequest.gmsize
    else:
      msg += serverDelim + oldGMRequest.server
  msg += "**"
  return msg

#-------------------------------------------------------------------------------------------
# Generate a response message for a GM that has been changed
#-------------------------------------------------------------------------------------------
async def genChangeResponseMsg(oldGMRequest:GMRequest, newGMRequest:GMRequest):
  oldGMRequest = oldGMRequest.forDB()
  newGMRequest = newGMRequest.forDB()
  if oldGMRequest != newGMRequest:
    msg = "Changed **" + oldGMRequest.name
    if oldGMRequest.server:
      if oldGMRequest.gmsize:
        msg += serverDelim + oldGMRequest.server + " " + oldGMRequest.gmsize
      else:
        msg += serverDelim + oldGMRequest.server
    msg += "**\n             to **" + newGMRequest.name
    if newGMRequest.server:
      if newGMRequest.gmsize:
        msg += serverDelim + newGMRequest.server + " " + newGMRequest.gmsize
      else:
        msg += serverDelim + newGMRequest.server
    msg += "**"
    return msg
  else:
    return "Nothing changed for **" + oldGMRequest.name + "**"

#-------------------------------------------------------------------------------------------
# Add the given list of GMs to the database
#-------------------------------------------------------------------------------------------
async def addGMReqEntries(gmRequests:List[GMRequest]) -> str:
  msg = "Added "
  dupNames = 0
  iteration = 0
  for gmRequest in gmRequests:
    iteration += 1
    if gmRequest.name:

      valname = await validateName(gmRequest.name)
      if valname != gmRequest.name:
        gmRequest.name = valname
        dupNames += 1

      msg += "**" if iteration == 1 else ",  **" 
      msg += gmRequest.name
      msg += serverDelim + gmRequest.server if gmRequest.server else ""
      msg += " " + gmRequest.gmsize if gmRequest.gmsize and gmRequest.server else ""
      msg += "**"

      await insertIntoDB(gmRequest)

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
    oldGMRequest = GMRequest.fromDict(gmReqEntry)
    db[gmReqTable].remove(gmReqEntry)
    return await genDeleteResponseMsg(oldGMRequest)
  else:
    return None

#-------------------------------------------------------------------------------------------
# Edit a GM in the database
#-------------------------------------------------------------------------------------------
async def editGMReqEntry(gm:str, name:str, server:str, gmsize:str) -> str:
  gmReqEntry = await findGMReqEntry(await extractName(gm))
  if gmReqEntry:
    oldGMRequest = GMRequest.fromDict(gmReqEntry)
    newGMRequest = GMRequest.withDefaults(name, server, gmsize, oldGMRequest)

    dupName = False
    if newGMRequest.name != oldGMRequest.name:
      valnewname = await validateName(newGMRequest.name)
      if valnewname != newGMRequest.name:
        newGMRequest.name = valnewname
        dupName = True

    await updateDB(db[gmReqTable].index(gmReqEntry), newGMRequest)

    msg = await genChangeResponseMsg(oldGMRequest, newGMRequest)
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
    oldGMRequest = GMRequest.fromDict(gmReqEntry)
    newGMRequest = GMRequest.withDefaults(None, server, gmsize, oldGMRequest)
    await updateDB(db[gmReqTable].index(gmReqEntry), newGMRequest)
    return await genChangeResponseMsg(oldGMRequest, newGMRequest)
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
  gmRequests = await getCurrentGMRequestList()
  if len(gmRequests):
    gmList = "**"
    for gmRequest in gmRequests:
      gmList += str(gmRequest.name)
      gmList += checkMark + gmRequest.server if gmRequest.server else blankMark
      gmList += " " + gmRequest.gmsize if gmRequest.gmsize else ""
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