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

superScript_i = "\u2071"
garmyURL = "https://bdocodex.com/items/ui_artwork/ic_05154.png"

noServer = "NoServer"
noSize = "NoSize"

# TODO: Make a superuser command '/season {on,off}' or '/cgconfig severlist'
# to update the server list when a Season is active
gmServers = [noServer, "SS1", "SS2", "SS3", "B1", "B2", "C1", "C2",
             "M1", "M2", "S1", "S2", "Val", "Arsha"]
#gmServers = [noServer, "B1", "B2", "C1", "C2", "M1", "M2", "S1", "S2",
#              "Rulu", "Val", "Arsha"]

gmSizes =[noSize, "2", "3", "4", "5", "120", "2000", "3000", "4000", "5000"]

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
    if not gmRequest.server:
      gmRequest.server = defaults.server
    if not gmRequest.gmsize:
      gmRequest.gmsize = defaults.gmsize
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
       self.server and self.server.lower() == noServer.lower():
      return None
    else:
      return self.gmsize

#-------------------------------------------------------------------------------------------
# Get the GM requests from the DB and return them as a list of GMRequest types 
#-------------------------------------------------------------------------------------------
async def getCurrentGMRequestList() -> List[GMRequest]:
  gmRequests = []
  if gmReqTable in db.keys():
    for gmReqEntry in db[gmReqTable]:
      gmRequests.append(GMRequest.fromDict(gmReqEntry))
  return gmRequests

#-------------------------------------------------------------------------------------------
# Find the GM req entry in the DB that matches the given name
#-------------------------------------------------------------------------------------------
async def findGMReqEntry(name:str):
  gmReqEntry = None
  if gmReqTable in db.keys():
    gmReqEntry = next((req for req in db[gmReqTable] if req[gmReqNameKey] == name), None)
  return gmReqEntry

#-------------------------------------------------------------------------------------------
# For a new GM request, change the given name slightly if the name already exists in the DB
#-------------------------------------------------------------------------------------------
async def validateName(name:str, iter:int=0) -> str:
  if await findGMReqEntry(name):
    return await validateName(name + superScript_i, iter + 1)
  else:
    return name

#-------------------------------------------------------------------------------------------
# For the GM request with the given index in the DB, update it with the given new
# GM request values
#-------------------------------------------------------------------------------------------
async def updateDB(index:int, newGMRequest:GMRequest):
  db[gmReqTable][index][gmReqNameKey]   = newGMRequest.name
  db[gmReqTable][index][gmReqServerKey] = newGMRequest.serverForDB()
  db[gmReqTable][index][gmReqSizeKey]   = newGMRequest.gmsizeForDB()

#-------------------------------------------------------------------------------------------
# Insert the given GM request into the DB
#-------------------------------------------------------------------------------------------
async def insertIntoDB(newGMRequest:GMRequest):
  newGMRequest.server = newGMRequest.serverForDB()
  newGMRequest.gmsize = newGMRequest.gmsizeForDB()
  if gmReqTable in db.keys():
    db[gmReqTable].append(vars(newGMRequest))
  else:
    db[gmReqTable] = [vars(newGMRequest)]
  
#-------------------------------------------------------------------------------------------
# Generate a response message for a GM request that has been added
#-------------------------------------------------------------------------------------------
async def genAddResponseMsg(newGMRequest:GMRequest):
  msg = "*Added **" + newGMRequest.name
  if newGMRequest.server and newGMRequest.server.lower() != noServer.lower():
    if newGMRequest.gmsize and newGMRequest.gmsize.lower() != noSize.lower():
      msg += " (" + newGMRequest.server + " " + newGMRequest.gmsize + ")"
    else:
      msg += " (" + newGMRequest.server + ")"
  msg += "***"
  return msg

#-------------------------------------------------------------------------------------------
# Generate a response message for a GM request that has been deleted
#-------------------------------------------------------------------------------------------
async def genDeleteResponseMsg(oldGMRequest:GMRequest):
  msg="*Deleted **" + oldGMRequest.name
  if oldGMRequest.server and oldGMRequest.server.lower() != noServer.lower():
    if oldGMRequest.gmsize and oldGMRequest.gmsize.lower() != noSize.lower():
      msg += " (" + oldGMRequest.server + " " + oldGMRequest.gmsize + ")"
    else:
      msg += " (" + oldGMRequest.server + ")"
  msg += "***"
  return msg

#-------------------------------------------------------------------------------------------
# Generate a response message for a GM request that has been changed
#-------------------------------------------------------------------------------------------
async def genChangeResponseMsg(oldGMRequest:GMRequest, newGMRequest:GMRequest):
  if oldGMRequest != newGMRequest:
    msg = "*Changed **" + oldGMRequest.name
    if oldGMRequest.server and oldGMRequest.server.lower() != noServer.lower():
      if oldGMRequest.gmsize and oldGMRequest.gmsize.lower() != noSize.lower():
        msg += " (" + oldGMRequest.server + " " + oldGMRequest.gmsize + ")"
      else:
        msg += " (" + oldGMRequest.server + ")"
    msg += "** to **" + newGMRequest.name
    if newGMRequest.server and newGMRequest.server.lower() != noServer.lower():
      if newGMRequest.gmsize and newGMRequest.gmsize.lower() != noSize.lower():
        msg += " (" + newGMRequest.server + " " + newGMRequest.gmsize + ")"
      else:
        msg += " (" + newGMRequest.server + ")"
    msg += "***"
    return msg
  else:
    return "*Nothing changed for **" + oldGMRequest.name + "***"

#-------------------------------------------------------------------------------------------
# Add a single GM request to the database
#-------------------------------------------------------------------------------------------
async def addGMReqEntry(name:str, server:str, gmsize) -> str:
  newGMRequest = GMRequest(name, server, gmsize)
  await insertIntoDB(newGMRequest)
  return await genAddResponseMsg(newGMRequest)

#-------------------------------------------------------------------------------------------
# Add the given list of GM requests to the database
#-------------------------------------------------------------------------------------------
async def addGMReqEntries(reqs:List[str]) -> str:
  gmRequests = [GMRequest(req) for req in reqs if req]
  msg = "*Added **"
  dupNames = 0
  for gmRequest in gmRequests:
    valname = await validateName(gmRequest.name)
    if valname != gmRequest.name:
      gmRequest.name = valname
      dupNames += 1
    msg += gmRequest.name + "**  ,  **"
    if gmReqTable in db.keys():
      db[gmReqTable].append(vars(gmRequest))
    else:
      db[gmReqTable] = [vars(gmRequest)]
  msg += "END"
  msg = msg.replace("**  ,  **END", "***")
  if dupNames > 1:
    msg += "\n*(Request names modified due to duplicates)*"
  elif dupNames > 0:
    msg += "\n*(Request name modified due to duplicates)*"
  return msg

#-------------------------------------------------------------------------------------------
# Delete a single GM request from the database
#-------------------------------------------------------------------------------------------
async def deleteGMReqEntry(request:str) -> str:
  gmReqEntry = await findGMReqEntry(request)
  if gmReqEntry:
    oldGMRequest = GMRequest.fromDict(gmReqEntry)
    db[gmReqTable].remove(gmReqEntry)
    return await genDeleteResponseMsg(oldGMRequest)
  else:
    return None

#-------------------------------------------------------------------------------------------
# Edit a single GM request in the database
#-------------------------------------------------------------------------------------------
async def editGMReqEntry(oldname:str, name:str, server:str, gmsize:str) -> str:
  gmReqEntry = await findGMReqEntry(oldname)
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
    msg += "\n*(Request name modified due to duplicates)*" if dupName else ""
    return msg
  else:
    return None

#-------------------------------------------------------------------------------------------
# For the GM request matching the given name, set the server and gmsize values.
# If a GM request exists, update its server and gmsize values.
# Otherwise, add it as a new GM request.
#-------------------------------------------------------------------------------------------
async def setGMServerAndSize(name:str, server:str, gmsize:str) -> str:
  gmReqEntry = await findGMReqEntry(name)
  if gmReqEntry:
    oldGMRequest = GMRequest.fromDict(gmReqEntry)
    newGMRequest = GMRequest(name, server, gmsize)
    await updateDB(db[gmReqTable].index(gmReqEntry), newGMRequest)
    return await genChangeResponseMsg(oldGMRequest, newGMRequest)
  else:
    return await addGMReqEntry(name, server, gmsize)

#-------------------------------------------------------------------------------------------
# Clear all GM requests from the DB
#-------------------------------------------------------------------------------------------
async def clearGMReqTable():
  if gmReqTable in db.keys():
    del db[gmReqTable]

#-------------------------------------------------------------------------------------------
# Update the number of Garmoth scroll pieces in the DB
#-------------------------------------------------------------------------------------------
async def updateGarmyPieces(pieces):
  db['garmy_pieces'] = pieces

#-------------------------------------------------------------------------------------------
# Generate and return an embed with the current list of GM requests
#-------------------------------------------------------------------------------------------
async def genGMListEmbed() -> discord.Embed:
  embyTitle = "Current GM Requests"
  gmRequests = await getCurrentGMRequestList()
  if len(gmRequests):
    gmList = "**"
    for gmRequest in gmRequests:
      gmList += str(gmRequest.name)
      if gmRequest.server:
        gmList += " :white_check_mark: " + gmRequest.server
        if gmRequest.gmsize:
          gmList += " " + gmRequest.gmsize
      gmList += "\n"
    gmList += "**"
  else:
    gmList = "*<GM request list is empty>*"
  gmList += "\n"
  
  emby = discord.Embed(title=embyTitle,
                       description=gmList,
                       colour=discord.Colour.blue())

  pieces = db["garmy_pieces"] if "garmy_pieces" in db.keys() else 0
  garmy_status = "Garmoth Scroll Status: "
  garmy_status += "Complete!" if pieces > 4 else str(pieces) + "/5"
  emby.set_footer(text=garmy_status, icon_url=garmyURL)

  return emby