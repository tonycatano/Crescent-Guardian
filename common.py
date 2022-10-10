
import os
import discord
from typing import List
from replit import db

guild_ids=[discord.Object(id=os.environ['TRUE_SYNERGY_ID'])]
#guild_ids=[discord.Object(id=os.environ['TEST_SERVER_ID'])]

class GMRequest:
  def __init__(self, name:str, server:str=None):
    self.name = name
    self.server = server

async def get_gm_requests() -> List[GMRequest]:
  gm_requests = []
  if "gm_reqs" in db.keys():
    for gm_req in db["gm_reqs"]:
      gm_requests.append(GMRequest(gm_req['name'], gm_req['server']))
  return gm_requests

async def find_gm_req(request:str):
  gm_req = None
  if "gm_reqs" in db.keys():
    gm_req = next((req for req in db["gm_reqs"] if req["name"] == request), None)
  return gm_req

async def add_gm_reqs(reqs:List[str]) -> str:
  gm_requests = [GMRequest(req) for req in reqs if req]
  msg = "*Added **"
  for gm_request in gm_requests:
    msg += gm_request.name + "** / **"
    if "gm_reqs" in db.keys():
      db["gm_reqs"].append(vars(gm_request))
    else:
      db["gm_reqs"] = [vars(gm_request)]

  msg += "END"
  msg = msg.replace("** / **END", "***")
  return msg

async def delete_gm_req(request:str) -> bool:
  gm_req = await find_gm_req(request)
  if gm_req:
    db["gm_reqs"].remove(gm_req)
    return True
  else:
    return False

async def edit_gm_req(request:str, newtext:str) -> bool:
  gm_req = await find_gm_req(request)
  if gm_req:
    index = db["gm_reqs"].index(gm_req)
    db["gm_reqs"][index]["name"] = newtext
    return True
  else:
    return False

async def set_gm_req_server(request:str, server:str) -> str:
  gm_req = await find_gm_req(request)
  msg = f'*Updated **{request}***'
  
  # If not found, add it
  if not gm_req:
    reqs = [request]
    msg = await add_gm_reqs(reqs)
    gm_req = await find_gm_req(request)

  # Set the server value
  if gm_req:    
    index = db["gm_reqs"].index(gm_req)
    if server.lower() == "none":
      server = None
    db["gm_reqs"][index]["server"] = server

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