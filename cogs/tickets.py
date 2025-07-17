# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

from config import GUILD_ID

# Class for Ticket Close.
class TicketCloseButton(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Close Ticket", emoji="🔒")
    
    async def callback(self, interaction: discord.Interaction):
        channel = interaction.channel
        guild = interaction.guild

        await channel.delete(reason=f"Ticket Closed by {interaction.user.mention}")

        await interaction.response.send_message("Closing Ticket...", ephemeral=True)


# Class for Tickets Cog.
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="open-ticket", description="Opens a Support Ticket")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.choices(platform=[app_commands.Choice(name="PCVR", value="Platform: PCVR"), app_commands.Choice(name="Standalone", value="Platform: Standalone")])
    async def open_ticket(self, interaction: discord.Interaction, platform: app_commands.Choice[str], reason: str = None):
        await interaction.response.defer()
        guild = interaction.guild
        user = interaction.user

        LOG_CHANNEL_ID = 1030517102416773181
        LOG_CHANNEL = guild.get_channel(LOG_CHANNEL_ID)

        TICKET_CATEGORY_ID = 1294385317004050462

        TICKET_CATEGORY = guild.get_channel(TICKET_CATEGORY_ID)

        if not TICKET_CATEGORY:
            await interaction.followup.send("Category Not Found!", ephemeral=True)
            return


        existing = discord.utils.get(guild.text_channels, name=f"{platform.value.replace('Platform: ', '').lower()}-{user.id}")
        if existing:
            await interaction.followup.send(f"You already have an Open Ticket: {existing.mention}", ephemeral=True)
            return

        
        staffRole = discord.utils.get(guild.roles, name="Staff Team")

        overwrites = dict(TICKET_CATEGORY.overwrites)
        overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
        overwrites[staffRole] = discord.PermissionOverwrite(
        view_channel=True,
            send_messages=True,
            read_message_history=True,
            attach_files=True,
            embed_links=True
            )
        overwrites[user] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            attach_files=True,
            embed_links=True
        )

        TICKET_CHANNEL = await guild.create_text_channel(
            name=f"{platform.value.replace('Platform: ', '').lower()}-{user.id}",
            overwrites=overwrites,
            category=TICKET_CATEGORY,
            topic=reason if reason is not None else "No Reason Provided"
        )
        
        embed = discord.Embed(
            title="🎫 Ticket Opened",
            description=f"Reason: {reason}",
            colour=discord.Colour.blurple()
        )
        embed.set_footer(text="Use the Button Below to Close this Ticket.")

        view = View()
        view.add_item(TicketCloseButton())

        await TICKET_CHANNEL.send(embed=embed, view=view)
        await TICKET_CHANNEL.send(f"{staffRole.mention} will Respond Soon!")

        await interaction.followup.send(f"Your Ticket has been Created: {TICKET_CHANNEL.mention}", ephemeral=True)
        

        if LOG_CHANNEL:
            LogEmbed = discord.Embed(
                title=f"{platform.value.replace('Platform: ', '').lower()}-{interaction.user.id}",
                description=f"**New Ticket has been Opened by:** {interaction.user.mention}",
                colour=discord.Colour.blurple()
            )
            LogEmbed.set_footer(text=f"{interaction.user.display_name}", icon_url=user.display_avatar.url)
            LogEmbed.set_thumbnail(url=user.display_avatar.url)
            await LOG_CHANNEL.send(embed=LogEmbed)

# Adds Cog to AMT Bots Class.
async def setup(bot):
    await bot.add_cog(Tickets(bot))
