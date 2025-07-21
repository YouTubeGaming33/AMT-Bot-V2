# Import Required Discord Library and Imports.
import discord
from discord.ext import commands
from discord import app_commands

from config import GUILD_ID
import datetime

from data.database import bounties_collection

# Class for Bounty Cog.
class Bounty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bounties_collection = bounties_collection

    def _generate_bounty_id(self):
        # Use self.bounties_collection consistently here
        return self.bounties_collection.count_documents({}) + 1

    @app_commands.command(name="set-bounty", description="Set a Bounty on a Player")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(platform="What Platform the Player is on", player="Player to Set Bounty on", reward="Reward in Gold Coins")
    @app_commands.choices(platform=[
        app_commands.Choice(name="PCVR", value="PCVR"),
        app_commands.Choice(name="Standalone", value="Standalone")
    ])
    async def setBounty(self, interaction: discord.Interaction, platform: app_commands.Choice[str], player: str, reward: int):
        await interaction.response.defer(ephemeral=True)
        try:
            bounty_id = self._generate_bounty_id()

            bounty_data = {
                "bounty_id": bounty_id,
                "creator_id": interaction.user.id,
                "platform": platform.value,
                "player": player,
                "reward": reward,
                "claimed": False,
                "created_at": datetime.datetime.utcnow()
            }

            self.bounties_collection.insert_one(bounty_data)

            embed = discord.Embed(
                title=f"Bounty Hunter Request - {interaction.user.display_name}",
                description=f"A bounty has been set!",
                colour=discord.Colour.purple()
            )
            embed.add_field(name="Platform:", value=platform.value, inline=False)
            embed.add_field(name="Player:", value=player, inline=False)
            embed.add_field(name="Reward Amount:", value=reward, inline=False)
            embed.add_field(name="Bounty ID:", value=bounty_id, inline=False)

            request_id = 1396962654978838588
            request_channel = interaction.guild.get_channel(request_id)

            if request_channel is None:
                await interaction.followup.send("❌ Could not find the request channel.", ephemeral=True)
                return

            await interaction.followup.send(f"Bounty #{bounty_id} set successfully!", ephemeral=True)
            await request_channel.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ An unexpected error occurred: {e}", ephemeral=True)

    @app_commands.command(name="claim", description="Claim a bounty by ID")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(bounty_id="The ID of the bounty to claim")
    async def claim(self, interaction: discord.Interaction, bounty_id: int):
        bounty = self.bounties_collection.find_one({"bounty_id": bounty_id})

        if not bounty:
            await interaction.response.send_message(f"❌ Bounty with ID {bounty_id} does not exist.", ephemeral=True)
            return

        if bounty.get("claimed"):
            await interaction.response.send_message(f"❌ Bounty #{bounty_id} has already been claimed.", ephemeral=True)
            return

        # Update bounty as claimed
        self.bounties_collection.update_one(
            {"bounty_id": bounty_id},
            {"$set": {"claimed": True, "claimed_by": interaction.user.id}}
        )

        # Notify bounty creator via DM
        creator = interaction.guild.get_member(bounty["creator_id"])
        if creator:
            try:
                await creator.send(
                    f"🎉 Your bounty #{bounty_id} on player **{bounty['player']}** "
                    f"has been claimed by {interaction.user.mention}!"
                )
            except discord.Forbidden:
                # Creator has DMs closed
                pass

        await interaction.response.send_message(
            f"✅ You have successfully claimed bounty #{bounty_id}!",
            ephemeral=True
        )

# Adds Cog to AMT Bots Class.
async def setup(bot):
    await bot.add_cog(Bounty(bot))
