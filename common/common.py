import os
import discord
from typing import List
from replit import db

guild_ids=[discord.Object(id=os.environ['DISCORD_SERVER_ID'])]

# TODO: Make a superuser command '/season {on,off}' or '/cgconfig severlist'
# to update the server list when a Season is active
# gm_servers = ["SS1", "SS2", "SS3", "B1", "B2", "C1", "C2",
#               "M1", "M2", "S1", "S2", "Val", "Arsha", "None"]
gm_servers = ["B1", "B2", "C1", "C2", "M1", "M2", "S1", "S2",
              "Rulu", "Val", "Arsha", "None"]

class GMRequest:
  def __init__(self, name:str, server:str=None):
    self.name = name
    self.server = server

async def get_gm_requests() -> List[GMRequest]:
  gm_requests = []
  if "gm_reqs" in db.keys():
    for gm_req in db["gm_reqs"]:
      gm_requests.append(GMRequest(gm_req['name'], gm_req['server']))
  gm_requests.sort(key=lambda request : request.name)
  return gm_requests

async def find_gm_req(request:str):
  gm_req = None
  if "gm_reqs" in db.keys():
    gm_req = next((req for req in db["gm_reqs"] if req["name"] == request), None)
  return gm_req

async def validate_name(name:str, iter:int=0) -> str:
  if await find_gm_req(name):
    return await validate_name(name + "\u2071", iter + 1)
  else:
    return name

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

async def delete_gm_req(request:str) -> str:
  gm_req = await find_gm_req(request)
  if gm_req:
    msg=f'*Deleted **{request}'
    index = db["gm_reqs"].index(gm_req)
    server = db["gm_reqs"][index]["server"]
    if server:
      msg += " (" + server + ")"
    msg += "***"
    db["gm_reqs"].remove(gm_req)
    return msg
  else:
    return None

async def edit_gm_req(request:str, newtext:str, newserver:str) -> str:
  gm_req = await find_gm_req(request)
  if gm_req:
    dupname = False
    if newtext != request:
      valnewtex = await validate_name(newtext)
      if valnewtex != newtext:
        newtext = valnewtex
        dupname = True
    index = db["gm_reqs"].index(gm_req)
    db["gm_reqs"][index]["name"] = newtext
    oldserver = db["gm_reqs"][index]["server"]
    msg = "*Changed **" + request
    if oldserver:
      msg += " (" + oldserver + ")"
    msg += "** to **" + newtext
    if newserver:
      await set_gm_req_server(newtext, newserver)
      msg += " (" + newserver + ")"
    elif oldserver:
      msg += " (" + oldserver + ")"
    msg += "***"
    if dupname:
      msg += "\n*(Request name modified due to duplicates)*"
    return msg
  else:
    return None

async def set_gm_req_server(request:str, server:str) -> str:
  gm_req = await find_gm_req(request)
  msg = ""
  gm_req_added = False
  
  # If not found, add it
  if not gm_req:
    reqs = [request]
    await add_gm_reqs(reqs)
    msg = "*Added **" + request
    gm_req_added = True
    gm_req = await find_gm_req(request)

  # Set the server value
  if gm_req:
    index = db["gm_reqs"].index(gm_req)
    if not gm_req_added:
      msg = "*Changed **" + request
      oldserver = db["gm_reqs"][index]["server"]
      if oldserver:
        msg += " (" + oldserver + ")"
      msg += "** to **" + request
    if server.lower() == "none":
      server = None
      msg += " (None)***"
    else:
      msg += " (" + server + ")***"
    db["gm_reqs"][index]["server"] = server
  else:
    msg = ":frowning: *Sorry, something went wrong. Try again.*"

  return msg

async def clear_gm_reqs():
  if "gm_reqs" in db.keys():
    del db["gm_reqs"]

async def update_garmy_pieces(pieces):
  db['garmy_pieces'] = pieces

async def get_gm_list_embed() -> discord.Embed:
  embyTitle = "Current GM Requests"
  gm_requests = await get_gm_requests()
  if len(gm_requests):
    gm_list = "**"
    for gm_request in gm_requests:
      gm_list += str(gm_request.name)
      if gm_request.server:
        gm_list += " :white_check_mark: " + gm_request.server
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
  if pieces == 5:
    garmy_status += "Complete!"
  else:
    garmy_status += str(pieces) + "/5"
  
  emby.set_footer(
    text=garmy_status,
    icon_url="https://bdocodex.com/items/ui_artwork/ic_05154.png")

  return emby