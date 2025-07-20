# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from data.database import autoresponders_collection

# Class for AutoResponder Cog.
class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Listens for a Message that starts with one of the Listeners in the DB.
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content.strip().lower()

        # Find an exact listener match for AMT, case insesitve.
        responder_entry = autoresponders_collection.find_one({
            "Guild": str(message.guild.id),
            "Listener": {"$regex": f"^{content}$", "$options": "i"}
        })

        if responder_entry:
            response = responder_entry.get("Response")
            if response:
                await message.channel.send(response)
    
# Adds Cog to AMT Bots Class.
async def setup(bot):
    await bot.add_cog(AutoResponder(bot))
