import os
import json
import discord
from discord.ui import View, Select, Modal, TextInput, Button
from discord import TextStyle, ButtonStyle
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict

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

def get_price(category: str, service: str, quantity: int):
    if category not in prices_data or service not in prices_data[category]:
        return None
    service_prices = prices_data[category][service]
    if "1" not in service_prices or service_prices["1"] is None:
        return None
    unit_price = service_prices["1"] 
    return unit_price * quantity 


class ContactSupportView(View):
    def __init__(self, admin_role_id: int, user: discord.Member, service_display: str, ticket_channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.admin_role_id, self.user, self.service_display, self.ticket_channel = admin_role_id, user, service_display, ticket_channel

    @discord.ui.button(label="Contact Support", style=ButtonStyle.primary)
    async def contact_support(self, interaction: discord.Interaction, button: Button):
        overwrites = interaction.channel.overwrites_for(self.user)
        overwrites.send_messages = True; overwrites.attach_files = True
        await interaction.channel.set_permissions(self.user, overwrite=overwrites)
        await interaction.response.send_message("Staff members have been noticed! You will receive help soon.", ephemeral=False)
        self.contact_support.disabled = True
        await interaction.edit_original_response(view=self)
        logs_channel = interaction.guild.get_channel(logs_channel_id)
        if logs_channel:
            admin_mention = f"<@&{self.admin_role_id}>"
            embed = discord.Embed(color=0x000000, description=f"```Support requested by {self.user.name} for {self.service_display}```.\nTicket: {self.ticket_channel.mention}   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await logs_channel.send(content=admin_mention, embed=embed)

    @discord.ui.button(label="Send the screenshot", style=ButtonStyle.success, custom_id="send_screenshot")
    async def send_screenshot(self, interaction: discord.Interaction, button: Button):
        overwrites = interaction.channel.overwrites_for(self.user)
        overwrites.send_messages = True; overwrites.attach_files = True
        await interaction.channel.set_permissions(self.user, overwrite=overwrites)
        await interaction.response.send_message("You can now send your screenshot and/or message. Once sent, a staff member will handle your request.", ephemeral=True)
        self.send_screenshot.disabled = True
        await interaction.edit_original_response(view=self)

class QuantityModal(Modal):
    def __init__(self, service_name: str, admin_role_id: int, ticket_channel: discord.TextChannel, user: discord.Member):
        super().__init__(title=f"Enter the desired quantity for {service_name}")
        self.service_name, self.admin_role_id, self.ticket_channel, self.user = service_name, admin_role_id, ticket_channel, user
        self.quantity = TextInput(label="Quantity", style=TextStyle.short, required=True, placeholder="Ex: 1")
        self.add_item(self.quantity)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not self.quantity.value.isdigit():
            await interaction.followup.send("Please enter a valid number.", ephemeral=True); return
        q = int(self.quantity.value)
        price_val = get_price("game_boost", self.service_name, q)
        if price_val is None:
            await interaction.followup.send("This quantity is unavailable. Please try another quantity.", ephemeral=True); return
        price_str = f"{price_val:.2f}€"
        short_name = self.service_name.replace(" ", "")
        await self.ticket_channel.edit(name=f"game-{short_name}-{self.user.name}")
        service_display = self.service_name.title()

        embed = discord.Embed(color=0x000000, title="**__ORDER SUMMARY__**", description=f"```{q}x {service_display} | {price_str}```\n\u200b")
        embed.add_field(name="__PAYMENT__", value=(
            f"Please send **{price_str}** by PayPal to : **```{paypal_email}```**\n"
            f"**Or by LTC to :** ```{ltc_address}```\n"
            f"**Before sending the money, read carefully the instructions in the <#{payment_channel_id}> channel.**"
        ), inline=False)
        embed.set_footer(text=f"|  Ticket opened by {self.user.name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", icon_url="https://cdn.discordapp.com/attachments/1267140283611611258/1307098808903012444/113E567F-E6B5-4E1B-BD7B-B974E9F339D2.jpg")

        recap = await self.ticket_channel.send(content=f"<@&{self.admin_role_id}>", embed=embed, view=ContactSupportView(self.admin_role_id, self.user, service_display, self.ticket_channel))
        def check_msg(m): return m.id != recap.id
        await self.ticket_channel.purge(check=check_msg)
        ticket_info[self.ticket_channel.id] = {'user_id': self.user.id, 'service_display': service_display, 'price': price_str}

        logs_channel = interaction.guild.get_channel(logs_channel_id)
        if logs_channel:
            log_embed = discord.Embed(color=0x000000, description=(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}     {self.ticket_channel.mention}"
                f"```{self.user.name} | {service_display} | {price_str}```"
            ))
            await logs_channel.send(embed=log_embed)

        await interaction.followup.send("Your order has been processed! Please follow the instructions in the ticket channel.", ephemeral=True)

class ServiceSelectMenu(Select):
    def __init__(self, admin_role_id: int, tickets_cat_id: str, ticket_channel: discord.TextChannel, user: discord.Member):
        self.admin_role_id, self.tickets_cat_id, self.ticket_channel, self.user = admin_role_id, tickets_cat_id, ticket_channel, user
        options = [
            discord.SelectOption(label="BrawlPass +", value="brawlpass +", description="Buy BrawlPass +", emoji="🎟️"),
            discord.SelectOption(label="Tier Max", value="tier max", description="Get Tier Max", emoji="📈"),
            discord.SelectOption(label="Ranked Ranks", value="ranked ranks", description="Boost Ranked Ranks", emoji="🏆")
        ]
        super().__init__(placeholder="Select a game boost...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        product = self.values[0]
        # Pour toutes ces options, on utilise QuantityModal (logique similaire)
        await interaction.response.send_modal(QuantityModal(product, self.admin_role_id, self.ticket_channel, self.user))

class ServiceSelectView(View):
    def __init__(self, admin_role_id: int, tickets_cat_id: str, ticket_channel: discord.TextChannel, user: discord.Member):
        super().__init__(timeout=60)
        self.add_item(ServiceSelectMenu(admin_role_id, tickets_cat_id, ticket_channel, user))

async def GameBoost(interaction: discord.Interaction):
    admin_role_id, tickets_cat_id = interaction.client.ADMIN_ROLE_ID, interaction.client.TICKETS_CAT_ID
    guild, user = interaction.guild, interaction.user
    category = guild.get_channel(int(tickets_cat_id))
    if category is None:
        await interaction.response.send_message("Category not found. Please check your configuration.", ephemeral=True)
        return
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True, attach_files=False),
        discord.Object(id=admin_role_id): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }
    ticket_channel = await guild.create_text_channel(name=f"game-{user.name}", category=category, overwrites=overwrites)
    view = ServiceSelectView(admin_role_id, tickets_cat_id, ticket_channel, user)
    emoji = "<:loading:1314701526614282271>"
    await ticket_channel.send(f"{emoji} {user.mention} Please select the desired game boost service from the menu below:", view=view)
    await interaction.response.send_message(f"Your ticket has been created here: <#{ticket_channel.id}>. Thanks a lot for your order!", ephemeral=True)
