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

    # Slash Command for Updating Member.interaction profile.
    @app_commands.command(name="update_profile", description="Update your profile info")
    @app_commands.describe(device="Platform you play on.",description="Description of Yourself.",username="Username.",pronouns="Your Pronouns.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.choices(device=[app_commands.Choice(name="Standalone", value="Standalone"),app_commands.Choice(name="PCVR", value="PCVR")])
    async def update_profile(self,interaction: discord.Interaction, device: app_commands.Choice[str], description: str, username: str, pronouns: str):
        user_id = interaction.user.id

        # Update each field
        update_field(user_id, "Name", username)
        update_field(user_id, "Device", device.value)
        update_field(user_id, "Description", description)
        update_field(user_id, "Pronouns", pronouns)

        await interaction.response.send_message(
            f"✅ Profile updated!",
            ephemeral=True
        )

    # Pulls either Member.interaction Profile or another Users Profile.
    @app_commands.command(name="profile", description="View your or another user's profile.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(user="The user to view (optional)")
    async def profile(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user

        profile = get_profile(user.id)
        if not profile:
            create_profile(user_id=user.id, name=user.display_name)
            await interaction.response.send_message(f"No profile found for {user.display_name}.", ephemeral=True)
            return

        # Build a neat embed to display profile info.
        embed = discord.Embed(
            title=f"{profile.get('Name', user.display_name)}'s Profile",
            colour=discord.Colour.purple()
        )
        embed.add_field(name="Device:", value=profile.get("Device", "Not set"), inline=False)
        embed.add_field(name="Description:", value=profile.get("Description", "Not set"), inline=False)
        embed.add_field(name="Pronouns:", value=profile.get("Pronouns", "Not set"), inline=False)

        # ✅ Add Achievements section
        achievements = profile.get("Achievements", [])
        achievement_text = "\n".join([f"• {a}" for a in achievements]) if achievements else "*No achievements yet!*"
        embed.add_field(name="🏆 Achievements", value=achievement_text, inline=False)

        embed.set_footer(
            text="A Mythical Tale", 
            icon_url="https://media.discordapp.net/attachments/927723310559686707/1395181866289594520/AMTLogoCutOut.png?ex=687b7e1e&is=687a2c9e&hm=fa7627f8494175b9da68108870c5e9504f9d08475c4a4d10e8696e2b85585eb6&=&format=webp&quality=lossless&width=992&height=992"
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

# Adds Cog to AMT Bot Class.
async def setup(bot):
    await bot.add_cog(Profiles(bot))
