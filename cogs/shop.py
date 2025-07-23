import datetime
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput

from config import GUILD_ID
from data.database import save_listing, get_listing_by_message_id, delete_listing_by_message_id

MARKET_ID = 1397599947783672008

class AcceptButton(Button):
    def __init__(self, seller_id: int, message_id: int):
        super().__init__(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
        self.seller_id = seller_id
        self.message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        listing = get_listing_by_message_id(self.message_id)
        if not listing:
            await interaction.response.send_message("Listing not found.", ephemeral=True)
            return

        seller = interaction.guild.get_member(self.seller_id)
        if seller:
            try:
                await seller.send(f"{interaction.user.mention} is interested in your listing for **{listing['item']}** ({listing['price']} coins).")
            except discord.Forbidden:
                pass

        try:
            await interaction.message.delete()
        except discord.HTTPException:
            pass

        delete_listing_by_message_id(self.message_id)
        await interaction.response.send_message("Offer sent to seller. Listing removed.", ephemeral=True)


class CounterModal(Modal, title="Counter Offer"):
    def __init__(self, seller_id: int, market_message_id: int, item: str):
        super().__init__()
        self.seller_id = seller_id
        self.market_message_id = market_message_id
        self.item = item
        self.counter_amount = TextInput(label="Counter Amount", placeholder="Enter your offer...", required=True)
        self.add_item(self.counter_amount)

    async def on_submit(self, interaction: discord.Interaction):
        listing = get_listing_by_message_id(self.market_message_id)
        if not listing:
            await interaction.response.send_message("Listing not found.", ephemeral=True)
            return

        seller = interaction.guild.get_member(self.seller_id)
        if not seller:
            await interaction.response.send_message("Seller not found.", ephemeral=True)
            return

        view = CounterResponseView(seller_id=self.seller_id, buyer_id=interaction.user.id, market_message_id=self.market_message_id, item=self.item, amount=self.counter_amount.value)
        try:
            await seller.send(
                f"{interaction.user.mention} has made a counter offer for **{self.item}**:\n"
                f"💰 {self.counter_amount.value} coins\nRespond below:",
                view=view
            )
            await interaction.response.send_message("Counter offer sent to seller.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Could not DM seller.", ephemeral=True)


class CounterButton(Button):
    def __init__(self, seller_id: int, message_id: int, item: str):
        super().__init__(label="Counter", style=discord.ButtonStyle.blurple, emoji="🔄")
        self.seller_id = seller_id
        self.message_id = message_id
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CounterModal(self.seller_id, self.message_id, self.item))


class ListingView(View):
    def __init__(self, seller_id: int, message_id: int, item: str):
        super().__init__(timeout=None)
        self.add_item(AcceptButton(seller_id, message_id))
        self.add_item(CounterButton(seller_id, message_id, item))


class CounterResponseView(View):
    def __init__(self, seller_id: int, buyer_id: int, market_message_id: int, item: str, amount: str):
        super().__init__(timeout=None)
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.market_message_id = market_message_id
        self.item = item
        self.amount = amount

    @discord.ui.button(label="Accept Offer", style=discord.ButtonStyle.green, emoji="✅")
    async def accept_offer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.seller_id:
            await interaction.response.send_message("Only the seller can respond.", ephemeral=True)
            return

        buyer = interaction.client.get_user(self.buyer_id) or await interaction.client.fetch_user(self.buyer_id)
        if buyer:
            try:
                await buyer.send(f"Your counter offer of {self.amount} coins for **{self.item}** was accepted!")
                await buyer.send(f"Wait for a Message from the Buyer in regards for Receiving your **{self.item}**")
            except discord.Forbidden:
                pass

        guilds = [g for g in interaction.client.guilds if g.get_member(self.seller_id)]
        market_message_deleted = False
        for g in guilds:
            listing = get_listing_by_message_id(self.market_message_id)
            if listing:
                ch = g.get_channel(listing["channel_id"])
                if ch:
                    try:
                        msg = await ch.fetch_message(self.market_message_id)
                        await msg.delete()
                        market_message_deleted = True
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        pass
                delete_listing_by_message_id(self.market_message_id)

        await interaction.response.send_message("Offer accepted.", ephemeral=True if interaction.guild else False)
        self.stop()

    @discord.ui.button(label="Decline Offer", style=discord.ButtonStyle.red, emoji="❌")
    async def decline_offer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.seller_id:
            await interaction.response.send_message("Only the seller can respond.", ephemeral=True)
            return

        buyer = interaction.client.get_user(self.buyer_id) or await interaction.client.fetch_user(self.buyer_id)
        if buyer:
            try:
                await buyer.send(f"Your counter offer for **{self.item}** was declined.")
            except discord.Forbidden:
                pass

        await interaction.response.send_message("Offer declined.", ephemeral=True if interaction.guild else False)
        self.stop()


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create-listing", description="Create a Shop Listing")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.choices(platform=[
        app_commands.Choice(name="PCVR", value="PCVR"),
        app_commands.Choice(name="Standalone", value="Standalone")
    ])
    async def open_ticket(self, interaction: discord.Interaction, platform: app_commands.Choice[str], item: str, price: int):
        embed = discord.Embed(
            title="Item Listing",
            description=f"{interaction.user.mention} is Selling an Item on {platform.value}",
            colour=discord.Colour.yellow()
        )
        embed.add_field(name="Item:", value=item, inline=False)
        embed.add_field(name="Price:", value=f"{price} <:GoldCoin:1303103326539481199>", inline=False)

        market = interaction.guild.get_channel(MARKET_ID)
        if not market:
            await interaction.response.send_message("Market channel not found.", ephemeral=True)
            return

        message = await market.send(embed=embed)
        view = ListingView(interaction.user.id, message.id, item)
        await message.edit(view=view)

        save_listing({
            "owner_id": interaction.user.id,
            "message_id": message.id,
            "channel_id": market.id,
            "guild_id": interaction.guild.id,
            "item": item,
            "price": price,
            "platform": platform.value,
            "created_at": datetime.datetime.utcnow(),
            "status": "active"
        })

        await interaction.response.send_message(f"Listing created for: {item}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Shop(bot))
