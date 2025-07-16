# Required Discord Library(s)
import discord
from discord.ext import app_commands

# Required DOTENV Library(s)
import os
from dotenv import load_dotenv()

# Required Asyncio Library - Organisation 
import asyncio

# Load Token and Specify Guild
load_dotenv()
TOKEN = os.dotenv("DISCORD_TOKEN")
GUILD_ID = discord.Object(id=925867675513659473)

# Bot Class - Initiates, Loads Cog(s), Syncs Commands
