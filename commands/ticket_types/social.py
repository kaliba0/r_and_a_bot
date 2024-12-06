import os
import json
import discord
from discord.ui import View, Select, Modal, TextInput, Button
from discord import app_commands, TextStyle, ButtonStyle
from typing import Dict
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

logs_channel_id = int(os.getenv("LOGS_ID"))
PRICES_FILE = "data/prices.json"


def load_prices():
    if not os.path.isfile(PRICES_FILE):
        raise FileNotFoundError(f"Prices file {PRICES_FILE} not found.")
    with open(PRICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


prices_data = load_prices()


def get_price(platform: str, service: str, quantity: int):
    if platform not in prices_data:
        return None
    if service not in prices_data[platform]:
        return None

    service_prices = prices_data[platform][service]
    tiers = sorted(int(k) for k in service_prices.keys())

    # Exact match
    if str(quantity) in service_prices:
        return service_prices[str(quantity)]

    # Find surrounding tiers
    lower_tier = None
    upper_tier = None
    for t in tiers:
        if t < quantity:
            lower_tier = t
        if t > quantity and upper_tier is None:
            upper_tier = t
            break

    if lower_tier is None or upper_tier is None:
        return None

    lower_price = service_prices[str(lower_tier)]
    upper_price = service_prices[str(upper_tier)]
    if lower_price is None or upper_price is None:
        return None

    # Interpolation linéaire
    ratio = (quantity - lower_tier) / (upper_tier - lower_tier)
    interpolated_price = lower_price + (upper_price - lower_price) * ratio
    return interpolated_price


class ContactSupportView(View):
    def __init__(self, admin_role_id: int, user: discord.Member, service_display: str, ticket_channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.admin_role_id = admin_role_id
        self.user = user
        self.service_display = service_display
        self.ticket_channel = ticket_channel

    @discord.ui.button(label="Contact Support", style=ButtonStyle.primary)
    async def contact_support(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel

        # Donner la permission d'envoyer des messages à l'utilisateur
        overwrites = channel.overwrites_for(self.user)
        overwrites.send_messages = True
        await channel.set_permissions(self.user, overwrite=overwrites)

        # Réponse dans le ticket
        await interaction.response.send_message(
            f"Staff members have been noticed! You will receive help soon.",
            ephemeral=False
        )

        # Désactiver le bouton après utilisation
        for child in self.children:
            child.disabled = True
        await interaction.edit_original_response(view=self)

        # Logs : Ping admins dans le channel logs
        logs_channel = interaction.guild.get_channel(int(logs_channel_id))
        admin_mention = f"<@&{self.admin_role_id}>"
        if logs_channel:
            log_embed = discord.Embed(
                color=0x000000,
                description=f"{admin_mention} **Support requested** by {self.user.name} for {self.service_display}.\nTicket: {self.ticket_channel.mention} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            await logs_channel.send(embed=log_embed)


class QuantityModal(Modal):
    def __init__(self, service_key: str, admin_role_id: int, tickets_cat_id: str, ticket_channel: discord.TextChannel, user: discord.Member):
        super().__init__(title="Enter the desired quantity")
        self.service_key = service_key
        self.admin_role_id = admin_role_id
        self.tickets_cat_id = tickets_cat_id
        self.ticket_channel = ticket_channel
        self.user = user

        self.quantity = TextInput(
            label="Desired Quantity",
            style=TextStyle.short,
            required=True,
            placeholder="Ex: 1000"
        )
        self.add_item(self.quantity)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)  # Prévenir Discord que l'interaction prend du temps
        quantity_str = self.quantity.value
        if not quantity_str.isdigit():
            await interaction.followup.send("Please enter a valid number.", ephemeral=True)
            return
        quantity = int(quantity_str)

        parts = self.service_key.split("_", 1)
        platform = parts[0]  # tiktok ou insta
        full_service = parts[1]  # followers, likes, views

        price_value = get_price(platform, full_service, quantity)
        if price_value is None:
            await interaction.followup.send("This quantity is unavailable. Please try another quantity.", ephemeral=True)
            return

        price_str = f"{price_value:.2f}€"

        # Renommer le canal
        prefix = "tt" if platform == "tiktok" else "insta"
        service_short = full_service
        new_name = f"{prefix}-{service_short}-{self.user.name}"
        await self.ticket_channel.edit(name=new_name)

        recap_embed = discord.Embed(
            color=0xf300ff,
            title="Ticket Summary",
        )
        service_display = f"{platform.title()} {full_service.title()}"
        recap_embed.add_field(name="Service", value=service_display, inline=True)
        recap_embed.add_field(name="Quantity", value=str(quantity), inline=True)
        recap_embed.add_field(name="Price", value=price_str, inline=True)
        recap_embed.set_footer(text=f"|  Ticket opened by {self.user.name}")

        # Envoi de l'embed + bouton "Contact Support"
        recap_message = await self.ticket_channel.send(
            content=f"<@&{self.admin_role_id}> <@{self.user.id}>",
            embed=recap_embed,
            view=ContactSupportView(self.admin_role_id, self.user, service_display, self.ticket_channel)
        )

        # Suppression de tous les autres messages sauf le récap
        def check_msg(m):
            return m.id != recap_message.id

        await self.ticket_channel.purge(check=check_msg)

        # Logs : Embeds court dans le channel de logs
        logs_channel = interaction.guild.get_channel(int(logs_channel_id))
        if logs_channel:
            log_embed = discord.Embed(
                color=0x000000,
                description=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} **New Ticket Created** ```{self.user.name} | {service_display} | {price_str}```",
            )
            await logs_channel.send(embed=log_embed)
            

class ServiceSelectMenu(Select):
    def __init__(self, admin_role_id: int, tickets_cat_id: str, ticket_channel: discord.TextChannel, user: discord.Member):
        self.admin_role_id = admin_role_id
        self.tickets_cat_id = tickets_cat_id
        self.ticket_channel = ticket_channel
        self.user = user

        options = [
            discord.SelectOption(label="TikTok Followers", value="tiktok_followers", description="Increase your TikTok followers", emoji="<:tikotk:1314611766390558802>"),
            discord.SelectOption(label="TikTok Likes", value="tiktok_likes", description="Boost your TikTok likes",  emoji="<:tikotk:1314611766390558802>"),
            discord.SelectOption(label="TikTok Views", value="tiktok_views", description="Get more TikTok views",  emoji="<:tikotk:1314611766390558802>"),
            discord.SelectOption(label="Instagram Followers", value="instagram_followers", description="Gain Instagram followers", emoji="<:insta:1314611896342544486>"),
            discord.SelectOption(label="Instagram Likes", value="instagram_likes", description="Boost your Instagram likes", emoji="<:insta:1314611896342544486>"),
            discord.SelectOption(label="Instagram Views", value="instagram_views", description="Increase Instagram views", emoji="<:insta:1314611896342544486>")
        ]

        super().__init__(
            placeholder="Select a service...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        service_key = self.values[0]
        modal = QuantityModal(service_key, self.admin_role_id, self.tickets_cat_id, self.ticket_channel, self.user)
        await interaction.response.send_modal(modal)


class ServiceSelectView(View):
    def __init__(self, admin_role_id: int, tickets_cat_id: str, ticket_channel: discord.TextChannel, user: discord.Member):
        super().__init__(timeout=60)  # Timeout de 60 secondes
        self.add_item(ServiceSelectMenu(admin_role_id, tickets_cat_id, ticket_channel, user))


async def Social(interaction: discord.Interaction):
    admin_role_id = interaction.client.ADMIN_ROLE_ID
    tickets_cat_id = interaction.client.TICKETS_CAT_ID
    guild = interaction.guild
    user = interaction.user

    category = guild.get_channel(int(tickets_cat_id))
    if category is None:
        await interaction.response.send_message("Category not found. Please check your configuration.", ephemeral=True)
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True),
        discord.Object(id=admin_role_id): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }

    ticket_channel = await guild.create_text_channel(
        name=f"social-{user.name}",
        category=category,
        overwrites=overwrites
    )

    view = ServiceSelectView(admin_role_id, tickets_cat_id, ticket_channel, user)
    await ticket_channel.send(
        "<:loading:1314701526614282271> Please select the desired service from the menu below:",
        view=view
    )

    await interaction.response.send_message(
        f"Your ticket has been created here: <#{ticket_channel.id}>. Thanks a lot for your order!",
        ephemeral=True
    )
