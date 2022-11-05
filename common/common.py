import os
import discord

guildIDs=[discord.Object(id=os.environ['DISCORD_SERVER_ID'])]
connectionLogFile = "logs/rocg.connection.log"
commandLogFile = "logs/rocg.command.log"
