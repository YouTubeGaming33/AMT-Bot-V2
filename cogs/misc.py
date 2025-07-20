# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from config import GUILD_ID

# Class for Misc Cog.
class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Slash Command for Providing Information for Helping Users.
    @app_commands.command(name="help", description="Provides Information to get Help")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="A Mythical Tale - Help",
            description="See Below for the different options for getting help:",
            colour=discord.Colour.yellow()
        )
        embed.add_field(name="/ticket", value="Open a Ticket for AMT Related Support.", inline=False)
        embed.add_field(name="Open an ATT Support Ticket", value="Open a Support Ticket for Problems relating to the Game itself.", inline=False)
        embed.add_field(name="Ask Others", value="If you are struggling to find an item, ask other players or search the Wiki, both are full of information!", inline=False)
        await interaction.response.send_message(embed=embed)

# Adds Cog to AMT Bots Class.
async def setup(bot):
    await bot.add_cog(Misc(bot))