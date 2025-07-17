# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from datetime import timedelta, datetime

from config import GUILD_ID

# Class for Moderation Cog.
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Slash Command for Warning a User.
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        user_roles = [role.id for role in interaction.user.roles]
        
        trial_admin_role = 935793809437098034
        admin_role = 927724509522432031

        # Check if the user has one of the allowed roles
        if trial_admin_role not in user_roles and admin_role not in user_roles:
            await interaction.response.send_message("🚫 You don't have permission to use this command.", ephemeral=True)
            return

        # If Member is the Interaction User, Don't Allow.
        if member == interaction.user:
            await interaction.response.send_message("You can't Warn yourself.", ephemeral=True)
            return
        
        # If Members Role is not Above The Interaction Users Role, Don't Allow.
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You can't Warn someone with a higher or equal role.", ephemeral=True)
            return
        
        # Send Message in Channel.
        await interaction.response.send_message(f"{interaction.user.mention} has Warned {member.mention} Reason: {reason}")

        MOD_LOG_ID = 1395444039339217108
        mod_log = interaction.guild.get_channel(MOD_LOG_ID)

        if mod_log:
            embed = discord.Embed(
                title="**User Warned**",
                description=(
                f"**User:** {member} ({member.id})\n"
                f"**Moderator:** {interaction.user} ({interaction.user.id})\n"
                f"**Reason:** - {reason}\n"
                f"**Date:** {discord.utils.format_dt(datetime.utcnow(), style='F')}\n\n"
                f"A Mythical Tale"),
                colour=discord.Colour.orange()
            )

            await mod_log.send(embed=embed)

    # Slash Command for Timeout.
    @app_commands.command(name="timeout", description="Timesout a User")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(member="Member to Timeout", reason="Reason for the Timeout", minutes="Time in Minutes")
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes:int, reason: str = None):
        user_roles = [role.id for role in interaction.user.roles]

        admin_role = 927724509522432031

        # Check if the user has one of the allowed role.
        if admin_role not in user_roles:
            await interaction.response.send_message("🚫 You don't have permission to use this command.", ephemeral=True)
            return

        # If Member is the Interaction User, Don't Allow.
        if member == interaction.user:
            await interaction.response.send_message("❌ You can't timeout yourself.", ephemeral=True)
            return
        
        # If Members Role is not Above The Interaction Users Role, Don't Allow.
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You can't timeout someone with an equal or higher role.", ephemeral=True)
            return
        
        # If Minutes is not Between 0 and 10080 then send message.
        if minutes <= 0 or minutes > 10080:  # 7 days max
            await interaction.response.send_message("⚠️ Timeout must be between 1 and 10080 minutes.", ephemeral=True)
            return

        duration = timedelta(minutes=minutes)

        try:
            await member.timeout(duration, reason=reason)
            await interaction.response.send_message(
                f"⏳ {member.mention} has been timed out for **{minutes} minute(s)**.\n**Reason:** {reason}"
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to timeout that user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Error: `{str(e)}`", ephemeral=True)

        MOD_LOG_ID = 1395444039339217108
        mod_log = interaction.guild.get_channel(MOD_LOG_ID)

        if mod_log:
            embed = discord.Embed(
                title="**User Timed-out**",
                description=(
                f"**User:** {member} ({member.id})\n"
                f"**Moderator:** {interaction.user} ({interaction.user.id})\n"
                f"**Reason:** - {reason}\n"
                f"**Duration:** - {minutes} Minutes\n"
                f"**Date:** {discord.utils.format_dt(datetime.utcnow(), style='F')}\n\n"
                f"A Mythical Tale"),
                colour=discord.Colour.orange()
            )

            await mod_log.send(embed=embed)

    @app_commands.command(name="kick", description="Kicks a User")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(member="Member to Kick", reason="Reason for the Kick")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        user_roles = [role.id for role in interaction.user.roles]
        
        trial_admin_role = 935793809437098034
        admin_role = 927724509522432031

        # Check if the user has one of the allowed roles
        if trial_admin_role not in user_roles and admin_role not in user_roles:
            await interaction.response.send_message("🚫 You don't have permission to use this command.", ephemeral=True)
            return

        # If Member is the Interaction User, Don't Allow.
        if member == interaction.user:
            await interaction.response.send_message("❌You can't kick yourself.", ephemeral=True)
            return
        
        # If Members Role is not Above The Interaction Users Role, Don't Allow.
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌You can't kick someone with a higher or equal role.", ephemeral=True)
            return

        await member.kick(reason=reason)

        MOD_LOG_ID = 1395444039339217108
        mod_log = interaction.guild.get_channel(MOD_LOG_ID)

        if mod_log:
            embed = discord.Embed(
                title="**User Kicked**",
                description=(
                f"**User:** {member} ({member.id})\n"
                f"**Moderator:** {interaction.user} ({interaction.user.id})\n"
                f"**Reason:** - {reason}\n"
                f"**Date:** {discord.utils.format_dt(datetime.utcnow(), style='F')}\n\n"
                f"A Mythical Tale"),
                colour=discord.Colour.orange()
            )

            await mod_log.send(embed=embed)
# Adds Cog to AMT Bots Class.
async def setup(bot):
    await bot.add_cog(Moderation(bot))
