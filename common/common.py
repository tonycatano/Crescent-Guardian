import os
import discord
import uuid
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
  def __init__(self, req_uuid:str, req_name:str, req_server:str=None):
    self.uuid = req_uuid
    self.name = req_name
    self.server = req_server
    
async def gen_uuid() -> str:
  req_uuid = "CGUUID-" + str(uuid.uuid1())
  return req_uuid

# Return all GM requests from the DB as a list of GMRequest type
async def get_gm_requests() -> List[GMRequest]:
  gm_requests = []
  if "gm_reqs" in db.keys():
    for gm_req in db["gm_reqs"]:
      gm_requests.append(GMRequest(gm_req['uuid'], gm_req['name'], gm_req['server']))
  return gm_requests

# Given a uuid, find the associated gm_req in the DB and return it as a dict type
async def find_gm_req(req_uuid:str):
  gm_req = None
  if "gm_reqs" in db.keys():
    gm_req = next((req for req in db["gm_reqs"] if req["uuid"] == req_uuid), None)
  return gm_req

async def add_gm_reqs(reqs:List[str]) -> str:
  gm_requests = [GMRequest(await gen_uuid(), req) for req in reqs if req]
  msg = "*Added **"
  for gm_request in gm_requests:
    # FIXME
    gm_request.name += "\u0020\u2063\u3164"
    msg += gm_request.name + "** / **"
    if "gm_reqs" in db.keys():
      db["gm_reqs"].append(vars(gm_request))
    else:
      db["gm_reqs"] = [vars(gm_request)]
  msg += "END"
  msg = msg.replace("** / **END", "***")
  return msg

async def delete_gm_req(req_uuid:str) -> str:
  gm_req = await find_gm_req(req_uuid)
  req_name = gm_req['name']
  if gm_req:
    db["gm_reqs"].remove(gm_req)
    msg = f'*Deleted* ***{req_name}***'
    return msg
  else:
    return False

async def edit_gm_req(req_uuid:str, newtext:str, newserver:str) -> str:
  gm_req = await find_gm_req(req_uuid)
  if gm_req:
    index = db["gm_reqs"].index(gm_req)
    db["gm_reqs"][index]["name"] = newtext
    oldserver = db["gm_reqs"][index]["server"]
    msg = "*Changed **" + gm_req['name']
    if oldserver:
      msg += " (" + oldserver + ")"
    msg += "** to **" + newtext
    if newserver:
      if newserver.lower() == "none":
        newserver = None
      db["gm_reqs"][index]["server"] = newserver
      if newserver != "None":
        msg += " (" + newserver + ")"
    elif oldserver:
      msg += " (" + oldserver + ")"
    msg += "***"
    return msg
  else:
    return None

async def set_gm_req_server(req_uuid:str, server:str) -> str:
  gm_req = await find_gm_req(req_uuid)
  msg = ""
  # If not found, the user didn't select an existing GM,
  # and the req_uuid is actually a req_name, so add it
  if not gm_req:
    req_name = req_uuid
    req_uuid = await gen_uuid()
    msg = await add_gm_reqs([GMRequest(req_uuid, req_name)])
    gm_req = await find_gm_req(req_uuid)
  else:
    req_name = gm_req['name']
    msg = f'*Updated **{req_name}***'

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
      #DEBUG
      print(gm_request.name, gm_request.server, gm_request.uuid)
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