# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

# Class for Moderation Cog.
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



# Adds Cog to AMT Bots Class.
async def setup(bot):
    await bot.add_cog(Moderation(bot))
