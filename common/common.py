import os
import discord

guildIDs = [discord.Object(id=os.environ['DISCORD_SERVER_ID'])]

connectionLogFile = "logs/rocg.connection.log"
commandLogFile    = "logs/rocg.command.log"
officerSchedFile  = "config/officerSchedule.txt"
relNotesFile      = "config/relNotesAbridged.txt"
serverListFile    = "config/serverList.txt"

botCmds = { #------------------------------------------------------------
            # command name | description                        | inline?
            #------------------------------------------------------------
            "/gmlist":     ["Display the GM list",                  True],
            "/gmadd":      ["Add a GM to the list",                 True],
            "/gmedit":     ["Edit a GM in the list",                True],
            "/gmdelete":   ["Delete a GM from the list",            True],
            "/gmclear":    ["Clear the entire GM list",             True],
            "/gmquickadd": ["Add several GM `names` to the list",   True],
            "/gmscroll":   ["Update a boss scroll status",          True],
          # "/schedule":   ["Display the officer schedule",        False],
          # "/help":       ["View all Crescent Guardian commands", False]
  }