# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from config import GUILD_ID
from data.database import get_profile, create_profile, update_field

# Class for Profiles Cog.
class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View your or another user's profile.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(user="The user to view (optional)")
    async def profile(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        profile = get_profile(user.id)
        if not profile:
            await interaction.response.send_message(f"No profile found for {user.display_name}.", ephemeral=True)
            return

        # Build a neat embed to display profile info
        embed = discord.Embed(
            title=f"{profile.get('Name', user.display_name)}'s Profile",
            colour=discord.Colour.blue()
        )
        embed.add_field(name="Device:", value=profile.get("Device", "Not set"), inline=False)
        embed.add_field(name="Description:", value=profile.get("Description", "Not set"), inline=False)
        embed.add_field(name="Pronouns:", value=profile.get("Pronouns", "Not set"), inline=False)
        await interaction.response.send_message(embed=embed)

# Adds Cog to AMT Bot's Class.
async def setup(bot):
    await bot.add_cog(Profiles(bot))
