# Import Required Discord Library and Imports.
import discord
from discord.ext import commands
from discord import app_commands

from datetime import datetime, timedelta
from data.database import assign_missions
from config import GUILD_ID

class Missions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daily", description="View your daily missions")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Do not set ephemeral here

        user_id = str(interaction.user.id)
        missions = assign_missions(user_id)

        now = datetime.utcnow()
        try:
            last_daily = datetime.fromisoformat(missions["daily"]["last_claimed"])
        except (KeyError, ValueError) as e:
            await interaction.followup.send("❌ Error loading your daily missions. Please try again later.", ephemeral=True)
            return
        daily_reset = last_daily + timedelta(hours=24)

        embed = discord.Embed(
            title=f"🗓️ Daily Missions for {interaction.user.display_name}",
            color=discord.Color.green(),
            timestamp=now
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        mission = missions["daily"]["missions"][0]

        embed.add_field(
            name=f"📝 {mission['title']}",
            value=(
                f"**Mission:** {mission['mission']}\n"
                f"**Reward:** {mission['reward']}\n"
                f"**Time Limit:** {mission['timelimit']}"
            ),
            inline=False
        )

        embed.add_field(
            name="⏱️ Resets",
            value=f"<t:{int(daily_reset.timestamp())}:R> (<t:{int(daily_reset.timestamp())}:F>)",
            inline=False
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="weekly", description="View your weekly missions")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def weekly(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        missions = assign_missions(user_id)

        now = datetime.utcnow()
        try:
            last_weekly = datetime.fromisoformat(missions["weekly"]["last_claimed"])
        except (KeyError, ValueError) as e:
            await interaction.followup.send("❌ Error loading your daily missions. Please try again later.", ephemeral=True)
            return
        weekly_reset = last_weekly + timedelta(days=7)

        embed = discord.Embed(
            title=f"📅 Weekly Missions for {interaction.user.display_name}",
            color=discord.Color.orange(),
            timestamp=now
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        mission = missions["weekly"]["missions"][0]

        embed.add_field(
            name=f"📝 {mission['title']}",
            value=(
                f"**Mission:** {mission['mission']}\n"
                f"**Reward:** {mission['reward']}\n"
                f"**Time Limit:** {mission['timelimit']}"
            ),
            inline=False
        )

        embed.add_field(
            name="⏱️ Resets",
            value=f"<t:{int(weekly_reset.timestamp())}:R> (<t:{int(weekly_reset.timestamp())}:F>)",
            inline=False
        )

        await interaction.followup.send(embed=embed, ephemeral=True)


# Adds Cog to Bot
async def setup(bot):
    await bot.add_cog(Missions(bot))
