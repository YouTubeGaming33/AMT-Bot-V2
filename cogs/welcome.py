# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

# Class for Welcome Cog.
class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Event Listener for on_member_join (When a Member Joins), sends a Embed and Mention to General Chat.
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(925867676151197717)
        if channel:
            embed = discord.Embed(
                title=f"Welcome {member.display_name} to AMT!",
                colour=discord.Colour.yellow()
            )
            embed.add_field(name="Have a good time.", 
                            value="[Click Here!](https://discord.com/channels/925867675513659473/925868553335365662) to read Rules, and [Click Here!](https://discord.com/channels/925867675513659473/955217701838663700) to be added in-game!")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1395184172540235828/1395185791453495467/GeorgeHi.png?ex=68798785&is=68783605&hm=4d57df9221c0b58eb32166271bacfb7d5e60ea9dfac0c6bb60bae103342bf812&=&format=webp&quality=lossless&width=256&height=256")
            await channel.send(f"{member.mention}", embed=embed)

# Adds Cog to AMT Bots Class.
async def setup(bot):
    await bot.add_cog(Welcome(bot))
