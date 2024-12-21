import os
import json
import discord
from discord.ui import View, Select, Modal, TextInput, Button
from discord import TextStyle, ButtonStyle
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logs_channel_id = int(os.getenv("LOGS_ID"))
payment_channel_id = int(os.getenv("PAYMENT_CHANNEL_ID"))
PRICES_FILE = "data/prices.json"
paypal_email = 'rafaaa.antterzn.shop@gmail.com'
ticket_info = {}

if not os.path.isfile(PRICES_FILE):
    raise FileNotFoundError(f"Prices file {PRICES_FILE} not found.")
with open(PRICES_FILE, "r", encoding="utf-8") as f:
    prices_data = json.load(f)

ltc_address = prices_data["ltc_address"]

def get_price(platform: str, service: str, quantity: int):
    if platform not in prices_data or service not in prices_data[platform]: return None
    service_prices = prices_data[platform][service]
    # Si un palier exact existe
    if str(quantity) in service_prices: return service_prices[str(quantity)]
    # Sinon on utilise le price_per_unit si disponible
    ppu = service_prices.get("price_per_unit")
    return ppu * quantity if ppu else None

def create_payment_embed(user, service_display, quantity, price_str):
    embed = discord.Embed(
        color=0x000000,
        title="**__ORDER SUMMARY__**",
        description=f"```{quantity}x {service_display} | {price_str}```\n\u200b"
    )
    embed.add_field(
        name="__PAYMENT__",
        value=(
            f"Please send **{price_str}** by PayPal to : **```{paypal_email}```**\n"
            f"**Or by LTC to :** ```{ltc_address}```\n"
            f"**Before sending the money, read carefully the instructions in the <#{payment_channel_id}> channel.**"
        ),
        inline=False
    )
    embed.set_footer(text=f"| Ticket opened by {user.name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return embed

class ContactSupportView(View):
    def __init__(self, admin_role_id, user, service_display, ticket_channel):
        super().__init__(timeout=None)
        self.admin_role_id, self.user, self.service_display, self.ticket_channel = admin_role_id, user, service_display, ticket_channel

    @discord.ui.button(label="Contact Support", style=ButtonStyle.primary)
    async def contact_support(self, interaction, button):
        ow = interaction.channel.overwrites_for(self.user)
        ow.send_messages = True; ow.attach_files = True
        await interaction.channel.set_permissions(self.user, overwrite=ow)
        await interaction.response.send_message("Staff members have been noticed! You will receive help soon.", ephemeral=False)
        self.contact_support.disabled = True
        await interaction.edit_original_response(view=self)
        logs = interaction.guild.get_channel(logs_channel_id)
        if logs:
            mention = f"<@&{self.admin_role_id}>"
            e = discord.Embed(color=0x000000, description=f"```Support requested by {self.user.name} for {self.service_display}```.\nTicket: {self.ticket_channel.mention}   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await logs.send(content=mention, embed=e)

    @discord.ui.button(label="Send the screenshot", style=ButtonStyle.success, custom_id="send_screenshot")
    async def send_screenshot(self, interaction, button):
        ow = interaction.channel.overwrites_for(self.user)
        ow.send_messages = True; ow.attach_files = True
        await interaction.channel.set_permissions(self.user, overwrite=ow)
        await interaction.response.send_message("You can now send your screenshot and/or message. Once sent, a staff member will handle your request.", ephemeral=True)
        self.send_screenshot.disabled = True
        await interaction.edit_original_response(view=self)

class QuantityModal(Modal):
    def __init__(self, service_key, admin_role_id, ticket_channel, user):
        super().__init__(title="Enter the desired quantity")
        self.service_key, self.admin_role_id, self.ticket_channel, self.user = service_key, admin_role_id, ticket_channel, user
        self.quantity = TextInput(label="Desired Quantity", style=TextStyle.short, required=True, placeholder="Ex: 1000")
        self.add_item(self.quantity)

    async def on_submit(self, interaction):
        await interaction.response.defer(ephemeral=True)
        if not self.quantity.value.isdigit():
            await interaction.followup.send("Please enter a valid number.", ephemeral=True)
            return
        q = int(self.quantity.value)
        platform, service = self.service_key.split("_", 1)
        price = get_price(platform, service, q)
        if price is None:
            await interaction.followup.send("This quantity is unavailable. Please try another.", ephemeral=True)
            return

        price_str = f"{price:.2f}€"
        await self.ticket_channel.edit(name=f"{platform}-{service}-{self.user.name}")
        embed = create_payment_embed(self.user, f"{platform.title()} {service.title()}", q, price_str)
        msg = await self.ticket_channel.send(content=f"<@&{self.admin_role_id}>", embed=embed, view=ContactSupportView(self.admin_role_id, self.user, f"{platform.title()} {service.title()}", self.ticket_channel))
        def check_msg(m): return m.id != msg.id
        await self.ticket_channel.purge(check=check_msg)

        ticket_info[self.ticket_channel.id] = {"user_id": self.user.id, "service_display": f"{platform.title()} {service.title()}", "price": price_str}
        logs = interaction.guild.get_channel(logs_channel_id)
        if logs:
            e = discord.Embed(color=0x000000, description=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {self.ticket_channel.mention} ```{self.user.name} | {platform.title()} {service.title()} | {price_str}```")
            await logs.send(embed=e)

class ServiceSelectMenu(Select):
    def __init__(self, admin_role_id, ticket_channel, user):
        self.admin_role_id, self.ticket_channel, self.user = admin_role_id, ticket_channel, user
        opts = [
            discord.SelectOption(emoji="<:tiktok:1320099361069203487>", label="TikTok Followers", value="tiktok_followers", description="Increase your TikTok followers"),
            discord.SelectOption(emoji="<:tiktok:1320099361069203487>", label="TikTok Likes", value="tiktok_likes", description="Boost your TikTok likes"),
            discord.SelectOption(emoji="<:tiktok:1320099361069203487>", label="TikTok Views", value="tiktok_views", description="Get more TikTok views"),
            discord.SelectOption(emoji="<:insta:1320099401556951052>", label="Instagram Followers", value="instagram_followers", description="Gain Instagram followers"),
            discord.SelectOption(emoji="<:insta:1320099401556951052>", label="Instagram Likes", value="instagram_likes", description="Boost your Instagram likes"),
            discord.SelectOption(emoji="<:insta:1320099401556951052>", label="Instagram Views", value="instagram_views", description="Increase Instagram views")
        ]
        super().__init__(placeholder="Select a service...", min_values=1, max_values=1, options=opts)

    async def callback(self, interaction):
        await interaction.response.send_modal(QuantityModal(self.values[0], self.admin_role_id, self.ticket_channel, self.user))

class ServiceSelectView(View):
    def __init__(self, admin_role_id, ticket_channel, user):
        super().__init__(timeout=60)
        self.add_item(ServiceSelectMenu(admin_role_id, ticket_channel, user))

async def Social(interaction):
    admin_role_id, guild, user = interaction.client.ADMIN_ROLE_ID, interaction.guild, interaction.user
    category = guild.get_channel(int(interaction.client.TICKETS_CAT_ID))
    if category is None:
        await interaction.response.send_message("Category not found. Please check your configuration.", ephemeral=True)
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True, attach_files=False),
        discord.Object(id=admin_role_id): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }
    ticket_channel = await guild.create_text_channel(name=f"social-{user.name}", category=category, overwrites=overwrites)
    await ticket_channel.send(f"{user.mention} Please select the desired service from the menu below:", view=ServiceSelectView(admin_role_id, ticket_channel, user))
    await interaction.response.send_message(f"Your ticket has been created here: <#{ticket_channel.id}>. Thanks for your order!", ephemeral=True)
