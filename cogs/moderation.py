# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

import random
import string

from datetime import timedelta, datetime

from config import GUILD_ID

from data.database import insert_warning, get_warnings

def generate_warn_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Class for Moderation Cog.
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def generate_warn_id(length=6):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    # Slash Command for Purging Messages.
    @app_commands.command(name="purge", description="Purge messages")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(amount="Amount of Messages to Delete")
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)

        user_roles = [role.id for role in interaction.user.roles]
        trial_admin_role = 935793809437098034
        admin_role = 927724509522432031

        if trial_admin_role not in user_roles and admin_role not in user_roles:
            await interaction.followup.send("🚫 You don't have permission to use this command.", ephemeral=True)
            return
        
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"{len(deleted)} Messages Deleted", ephemeral=True)

    # Pulls Warnings for a Member, if applicable.
    @app_commands.command(name="warnings", description="Check how many warnings a user has")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(member="The member whose warnings you want to check")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True)

        user_roles = [role.id for role in interaction.user.roles]
        trial_admin_role = 935793809437098034
        admin_role = 927724509522432031

        if trial_admin_role not in user_roles and admin_role not in user_roles:
            await interaction.followup.send("🚫 You don't have permission to use this command.", ephemeral=True)
            return

        if member == interaction.user:
            await interaction.followup.send("You can't view your own warnings.", ephemeral=True)
            return

        if member.top_role >= interaction.user.top_role:
            await interaction.followup.send("You can't view someone with a higher or equal role.", ephemeral=True)
            return


        warnings = get_warnings(str(interaction.guild.id), str(member.id))
        warning_count = len(warnings)

        print("Debug: warning_count =", warning_count)  # Debug print to confirm count
        for w in warnings[:5]:
            print("Debug: Warning Date =", w.get("Date"), type(w.get("Date")))  # Debug each date type

        if warning_count == 0:
            await interaction.followup.send(f"{member.mention} has no warnings.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Warnings for {member}",
            description=f"Total warnings: **{warning_count}**",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        for i, warning in enumerate(warnings[:5], start=1):  # Limit to latest 5
            date_obj = warning.get("Date")
            if not isinstance(date_obj, datetime):
                date_obj = datetime.utcnow()  # fallback if missing or wrong type

            date_str = f"<t:{int(date_obj.timestamp())}:F>"

            embed.add_field(
                name=f"Warning #{i} — ID `{warning.get('WarnNum', 'N/A')}`",
                value=(
                    f"**Reason:** {warning.get('Reason', 'N/A')}\n"
                    f"**Date:** {date_str}"
                ),
                inline=False
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    # Slash Command for Warning a User - Saves to DB allowing for later pull.
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        await interaction.response.defer(ephemeral=True)  # Defer immediately

        user_roles = [role.id for role in interaction.user.roles]
        trial_admin_role = 935793809437098034
        admin_role = 927724509522432031

        if trial_admin_role not in user_roles and admin_role not in user_roles:
            await interaction.followup.send("🚫 You don't have permission to use this command.", ephemeral=True)
            return

        if member == interaction.user:
            await interaction.followup.send("You can't warn yourself.", ephemeral=True)
            return

        if member.top_role >= interaction.user.top_role:
            await interaction.followup.send("You can't warn someone with a higher or equal role.", ephemeral=True)
            return

        if not reason:
            reason = "No reason provided"

        warn_id = generate_warn_id()
        MOD_LOG_ID = 1395444039339217108
        mod_log = interaction.guild.get_channel(MOD_LOG_ID)

        embed = discord.Embed(
            title="**User Warned**",
            description=(
                f"**User:** {member} ({member.id})\n"
                f"**Moderator:** {interaction.user} ({interaction.user.id})\n"
                f"**Reason:** {reason}\n"
                f"**Warn ID:** `{warn_id}`\n"
                f"**Date:** {discord.utils.format_dt(datetime.utcnow(), style='F')}"
            ),
            colour=discord.Colour.orange()
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        log_msg = None
        if mod_log:
            log_msg = await mod_log.send(embed=embed)

        # Attempt to DM the user
        try:
            await member.send(
                f"⚠️ You have been warned in **{interaction.guild.name}**.\n"
                f"**Reason:** {reason}"
            )
        except discord.Forbidden:
            await interaction.followup.send(
                f"⚠️ Could not DM {member.mention} — they may have DMs disabled.",
                ephemeral=True
            )

        # Insert into MongoDB
        insert_warning(
            guild_id=interaction.guild.id,
            user_id=member.id,
            reason=reason,
            moderator_id=interaction.user.id,
            warn_num=warn_id,
            message_id=log_msg.id if log_msg else None,
            channel_id=log_msg.channel.id if log_msg else None
        )

        # Count warnings
        warnings = get_warnings(str(interaction.guild.id), str(member.id))
        warning_count = len(warnings)

        await interaction.followup.send(
            f"{interaction.user.mention} has warned {member.mention}.\n"
            f"Reason: {reason}\n"
            f"{member.mention} now has {warning_count} warning(s).\n",
            ephemeral=True
        )


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

    # Slash Command for Kick, includes member and reason.
    @app_commands.command(name="kick", description="Kicks a User")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(member="Member to Kick", reason="Reason for the Kick")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        await interaction.response.defer(ephemeral=True)
        user_roles = [role.id for role in interaction.user.roles]
        
        trial_admin_role = 935793809437098034
        admin_role = 927724509522432031

        # Check if the user has one of the allowed roles
        if trial_admin_role not in user_roles and admin_role not in user_roles:
            await interaction.followup.send("🚫 You don't have permission to use this command.", ephemeral=True)
            return

        # If Member is the Interaction User, Don't Allow.
        if member == interaction.user:
            await interaction.followup.send("❌You can't kick yourself.", ephemeral=True)
            return
        
        # If Members Role is not Above The Interaction Users Role, Don't Allow.
        if member.top_role >= interaction.user.top_role:
            await interaction.followup.send("❌You can't kick someone with a higher or equal role.", ephemeral=True)
            return

        await member.kick(reason=reason)

        await interaction.followup.send(f"{member.mention} was Kicked for {reason}")

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
