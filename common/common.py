import os
import discord
from typing import List
from replit import db

guild_ids=[discord.Object(id=os.environ['DISCORD_SERVER_ID'])]

noServer = "NoServer"
noSize = "NoSize"

# TODO: Make a superuser command '/season {on,off}' or '/cgconfig severlist'
# to update the server list when a Season is active
# gm_servers = [noServer, "SS1", "SS2", "SS3", "B1", "B2", "C1", "C2",
#               "M1", "M2", "S1", "S2", "Val", "Arsha"]
gm_servers = [noServer, "B1", "B2", "C1", "C2", "M1", "M2", "S1", "S2",
              "Rulu", "Val", "Arsha"]

gmSizes =[noSize, "20", "120", "2000", "3000", "4000", "5000"]

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
  def fromDict(gm_req:dict):
    return GMRequest(gm_req["name"], gm_req["server"], gm_req["gmsize"])

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
async def get_gm_requests() -> List[GMRequest]:
  gm_requests = []
  if "gm_reqs" in db.keys():
    for gm_req in db["gm_reqs"]:
      gm_requests.append(GMRequest.fromDict(gm_req))
  return gm_requests

#-------------------------------------------------------------------------------------------
# Find the GM req in the DB that matches the given name
#-------------------------------------------------------------------------------------------
async def find_gm_req(request:str):
  gm_req = None
  if "gm_reqs" in db.keys():
    gm_req = next((req for req in db["gm_reqs"] if req["name"] == request), None)
  return gm_req

#-------------------------------------------------------------------------------------------
# For a new GM request, change the given name slightly if the name already exists in the DB
#-------------------------------------------------------------------------------------------
async def validate_name(name:str, iter:int=0) -> str:
  if await find_gm_req(name):
    return await validate_name(name + "\u2071", iter + 1)
  else:
    return name

#-------------------------------------------------------------------------------------------
# For the GM request with the given index in the DB, update it with the given new
# GM request values
#-------------------------------------------------------------------------------------------
async def updateDB(index:int, newGMRequest:GMRequest):
  db["gm_reqs"][index]["name"]   = newGMRequest.name
  db["gm_reqs"][index]["server"] = newGMRequest.serverForDB()
  db["gm_reqs"][index]["gmsize"] = newGMRequest.gmsizeForDB()

#-------------------------------------------------------------------------------------------
# Insert the given GM request into the DB
#-------------------------------------------------------------------------------------------
async def insertIntoDB(newGMRequest:GMRequest):
  newGMRequest.server = newGMRequest.serverForDB()
  newGMRequest.gmsize = newGMRequest.gmsizeForDB()
  if "gm_reqs" in db.keys():
    db["gm_reqs"].append(vars(newGMRequest))
  else:
    db["gm_reqs"] = [vars(newGMRequest)]
  
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
async def add_gm_req(name:str, server:str, gmsize) -> str:
  newGMRequest = GMRequest(name, server, gmsize)
  await insertIntoDB(newGMRequest)
  return await genAddResponseMsg(newGMRequest)

#-------------------------------------------------------------------------------------------
# Add the given list of GM requests to the database
#-------------------------------------------------------------------------------------------
async def add_gm_reqs(reqs:List[str]) -> str:
  gm_requests = [GMRequest(req) for req in reqs if req]
  msg = "*Added **"
  dupnames = 0
  for gm_request in gm_requests:
    valname = await validate_name(gm_request.name)
    if valname != gm_request.name:
      gm_request.name = valname
      dupnames += 1
    msg += gm_request.name + "**  ,  **"
    if "gm_reqs" in db.keys():
      db["gm_reqs"].append(vars(gm_request))
    else:
      db["gm_reqs"] = [vars(gm_request)]
  msg += "END"
  msg = msg.replace("**  ,  **END", "***")
  if dupnames > 1:
    msg += "\n*(Request names modified due to duplicates)*"
  elif dupnames > 0:
    msg += "\n*(Request name modified due to duplicates)*"
  return msg

#-------------------------------------------------------------------------------------------
# Delete a single GM request from the database
#-------------------------------------------------------------------------------------------
async def delete_gm_req(request:str) -> str:
  gm_req = await find_gm_req(request)
  if gm_req:
    oldGMRequest = GMRequest.fromDict(gm_req)
    db["gm_reqs"].remove(gm_req)
    return await genDeleteResponseMsg(oldGMRequest)
  else:
    return None

#-------------------------------------------------------------------------------------------
# Edit a single GM request in the database
#-------------------------------------------------------------------------------------------
async def edit_gm_req(oldname:str, name:str, server:str, gmsize:str) -> str:
  gm_req = await find_gm_req(oldname)
  if gm_req:
    oldGMRequest = GMRequest.fromDict(gm_req)
    newGMRequest = GMRequest.withDefaults(name, server, gmsize, oldGMRequest)

    dupname = False
    if newGMRequest.name != oldGMRequest.name:
      valnewname = await validate_name(newGMRequest.name)
      if valnewname != newGMRequest.name:
        newGMRequest.name = valnewname
        dupname = True

    await updateDB(db["gm_reqs"].index(gm_req), newGMRequest)

    msg = await genChangeResponseMsg(oldGMRequest, newGMRequest)
    msg += "\n*(Request name modified due to duplicates)*" if dupname else ""
    return msg
  else:
    return None

#-------------------------------------------------------------------------------------------
# If a GM request exists for the given name, update its server and gmsize values.
# Otherwise, add it as a new gm request.
#-------------------------------------------------------------------------------------------
async def set_gm_req_server(name:str, server:str, gmsize:str) -> str:
  gm_req = await find_gm_req(name)
  if gm_req:
    oldGMRequest = GMRequest.fromDict(gm_req)
    newGMRequest = GMRequest(name, server, gmsize)
    await updateDB(db["gm_reqs"].index(gm_req), newGMRequest)
    return await genChangeResponseMsg(oldGMRequest, newGMRequest)
  else:
    return await add_gm_req(name, server, gmsize)

#-------------------------------------------------------------------------------------------
# Clear all GM requests from the DB
#-------------------------------------------------------------------------------------------
async def clear_gm_reqs():
  if "gm_reqs" in db.keys():
    del db["gm_reqs"]

#-------------------------------------------------------------------------------------------
# Update the number of Garmoth scroll pieces in the DB
#-------------------------------------------------------------------------------------------
async def update_garmy_pieces(pieces):
  db['garmy_pieces'] = pieces

#-------------------------------------------------------------------------------------------
# Generate and return an embed with the current list of GM requests
#-------------------------------------------------------------------------------------------
async def get_gm_list_embed() -> discord.Embed:
  embyTitle = "Current GM Requests"
  gm_requests = await get_gm_requests()
  if len(gm_requests):
    gm_list = "**"
    for gm_request in gm_requests:
      gm_list += str(gm_request.name)
      if gm_request.server:
        gm_list += " :white_check_mark: " + gm_request.server
        if gm_request.gmsize:
          gm_list += " " + gm_request.gmsize
      gm_list += "\n"
    gm_list += "**"
  else:
    gm_list = "*<GM request list is empty>*"
  gm_list += "\n"
  
  emby = discord.Embed(title=embyTitle,
                       description=gm_list,
                       colour=discord.Colour.green())
  
  pieces = 0
  if "garmy_pieces" in db.keys():
    pieces = db["garmy_pieces"]
    
  garmy_status = "Garmoth Scroll Status: "
  if pieces > 4:
    garmy_status += "Complete!"
  else:
    garmy_status += str(pieces) + "/5"
  
  emby.set_footer(
    text=garmy_status,
    icon_url="https://bdocodex.com/items/ui_artwork/ic_05154.png")

  return emby