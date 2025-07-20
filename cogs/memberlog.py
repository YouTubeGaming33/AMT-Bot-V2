import discord
from discord.ext import commands
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

class MemberLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(
            title="📥 User Joined",
            description=f"<@{member.id}> | {member}\n({member.id})",
            color=discord.Color.green()
        )

        try:
            created = member.created_at.strftime('%d %B %Y %H:%M')
            rd = relativedelta(datetime.now(timezone.utc), member.created_at)
            age = f"{rd.years}y {rd.months}m"
        except Exception as e:
            created = "Unknown"
            age = "Unknown"

        embed.add_field(name="User Created:", value=f"{created} ({age} ago)", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        JOINLEAVE_LOG_ID = 1396225671075729600
        joinleave_log = member.guild.get_channel(JOINLEAVE_LOG_ID)

        if joinleave_log:
            await joinleave_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        embed = discord.Embed(
            title="📤 User Left",
            description=f"<@{member.id}> | {member}\n({member.id})",
            color=discord.Color.red()
        )

        try:
            created = member.created_at.strftime('%d %B %Y %H:%M')
            rd = relativedelta(datetime.now(timezone.utc), member.created_at)
            age = f"{rd.years}y {rd.months}m"
        except Exception as e:
            created = "Unknown"
            age = "Unknown"

        embed.add_field(name="User Created:", value=f"{created} ({age} ago)", inline=False)

        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        embed.add_field(name="Roles:", value=", ".join(roles) if roles else "@everyone", inline=False)

        embed.set_thumbnail(url=member.display_avatar.url)

        JOINLEAVE_LOG_ID = 1396225671075729600
        joinleave_log = member.guild.get_channel(JOINLEAVE_LOG_ID)

        if joinleave_log:
            await joinleave_log.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MemberLogger(bot))
