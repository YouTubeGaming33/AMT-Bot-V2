# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from random import randint
import time

from data.database import get_level, create_level, update_level, add_achievement, get_achievements

# Function for Generating XP
def XP():
    Num = randint(1,5)
    return Num

# Class for Levelling Cog.
class Levelling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        user = message.author
        user_id = user.id
        now = time.time()

        # Cooldown of 5 seconds
        cooldown_period = 5  
        last_used = self.cooldowns.get(user_id)

        if last_used and (now - last_used) < cooldown_period:
            return  # still on cooldown, no XP

        # Record current time
        self.cooldowns[user_id] = now

        # Fetch or create user level entry
        user_data = get_level(user_id)
        if user_data is None:
            create_level(user_id, xp=0, level=1)
            user_data = {"XP": 0, "Level": 1}

        xp_gain = XP()
        new_xp = user_data["XP"] + xp_gain
        current_level = user_data["Level"]
        xp_needed = 250 * current_level

        # Check if user levels up
        if new_xp >= xp_needed:
            new_xp -= xp_needed
            current_level += 1
            await message.channel.send(f"🎉 {user.mention} leveled up to **Level {current_level}**!")

        copper_id = 1056226447380992030
        copper = message.guild.get_role(copper_id)

        iron_id = 1056226650481770576
        iron = message.guild.get_role(iron_id)

        silver_id = 1056226902018367618
        silver = message.guild.get_role(silver_id)

        mythril_id = 1056226591774101584
        mythril = message.guild.get_role(mythril_id)

        achievements = get_achievements(user_id)

        if current_level >= 10 and "Copper Turabada <:CopperTurabada:1396909606902435850>" not in achievements:
            add_achievement(user_id, "Copper Turabada <:CopperTurabada:1396909606902435850>")
            await message.channel.send(f"<:CopperTurabada:1396909606902435850> {user.mention} Unlocked Copper Turabada Achievement!")
            await message.author.add_roles(copper)

        
        if current_level >= 20 and "Iron Turabada <:IronTurabada:1396910171208548372>" not in achievements:
            add_achievement(user_id, "Iron Turabada <:IronTurabada:1396910171208548372>")
            await message.channel.send(f"<:IronTurabada:1396910171208548372> {user.mention} Unlocked Iron Turabada Achievement!")
            await message.author.add_roles(iron)
        
        if current_level >= 30 and "Silver Turabada <:SilverTurabada:1396910177990737991>" not in achievements:
            add_achievement(user_id, "Silver Turabada <:SilverTurabada:1396910177990737991>")
            await message.channel.send(f"<:SilverTurabada:1396910177990737991> {user.mention} Unlocked Silver Turabada Achievement!")
            await message.author.add_roles(silver)
        
        if current_level >= 40 and "Mythril Turabada <:MythrilTurabada:1396910174723244203>" not in achievements:
            add_achievement(user_id, "Mythril Turabada <:MythrilTurabada:1396910174723244203>")
            await message.channel.send(f"<:MythrilTurabada:1396910174723244203> {user.mention} Unlocked Mythril Turabada Achievement!")
            await message.author.add_roles(mythril)

        # Update database
        update_level(user_id, xp=new_xp, level=current_level)

# Adds Cog to AMT Bots Class.
async def setup(bot):
    await bot.add_cog(Levelling(bot))