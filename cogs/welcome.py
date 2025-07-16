import discord
from discord.ext import commands
from discord import app_commands

from main import GUILD_ID

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self):
        print ("test")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
