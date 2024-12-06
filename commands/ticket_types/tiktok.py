import os
import discord
from discord.ui import View, Button, Modal, TextInput
from discord import ButtonStyle, TextStyle
from discord import app_commands

# Nous supposons que les variables d'environnement sont déjà chargées dans le bot (depuis main.py ou ticket.py)
# interaction.client contiendra bot, donc on pourra accéder à bot.TICKETS_CAT_ID, etc.

class QuantityModal(Modal):
    def __init__(self, selected_service: str, admin_role_id: int, tickets_cat_id: str):
        super().__init__(title=f"Order {selected_service}")
        self.selected_service = selected_service
        self.admin_role_id = admin_role_id
        self.tickets_cat_id = tickets_cat_id

        self.quantity = TextInput(
            label="Desired Quantity",
            style=TextStyle.short,
            required=True,
            placeholder="Ex: 1000"
        )
        self.add_item(self.quantity)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        quantity = self.quantity.value

        category = guild.get_channel(int(self.tickets_cat_id))
        if category is None:
            await interaction.response.send_message("Category not found. Please check your configuration.", ephemeral=True)
            return

        # Création du salon
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            discord.Object(id=self.admin_role_id): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        recap_embed = discord.Embed(
            color=0xf300ff,
            title='Ticket Summary',
            description='A staff member will handle your request very soon. Thanks for trusting us 💛'
        )
        recap_embed.add_field(name='Service', value=f'TikTok {self.selected_service}', inline=True)
        recap_embed.add_field(name='Quantity', value=quantity, inline=True)
        recap_embed.set_footer(text=f"|  Ticket opened by {interaction.user.name}")
        # Ajoutez thumbnail ou image si vous le souhaitez

        await ticket_channel.send(
            content=f"<@&{self.admin_role_id}> <@{interaction.user.id}>",
            embed=recap_embed
        )

        # startInactivityTimer(ticket_channel) # A implémenter vous-même si nécessaire

        await interaction.response.send_message(
            f"A new ticket has been created for your request: <#{ticket_channel.id}>.\nPlease follow the instructions sent in this channel.\nThank you very much for trusting us 🧡",
            ephemeral=True
        )


class ServiceButtons(View):
    def __init__(self, admin_role_id: int, tickets_cat_id: str):
        super().__init__(timeout=60)
        self.admin_role_id = admin_role_id
        self.tickets_cat_id = tickets_cat_id

    @discord.ui.button(label="Followers", style=ButtonStyle.primary, custom_id="followers")
    async def followers(self, interaction: discord.Interaction, button: Button):
        await self._show_modal(interaction, "Followers")

    @discord.ui.button(label="Views", style=ButtonStyle.primary, custom_id="views")
    async def views(self, interaction: discord.Interaction, button: Button):
        await self._show_modal(interaction, "Views")

    @discord.ui.button(label="Likes", style=ButtonStyle.primary, custom_id="likes")
    async def likes(self, interaction: discord.Interaction, button: Button):
        await self._show_modal(interaction, "Likes")

    async def _show_modal(self, interaction: discord.Interaction, service: str):
        modal = QuantityModal(selected_service=service, admin_role_id=self.admin_role_id, tickets_cat_id=self.tickets_cat_id)
        await interaction.response.send_modal(modal)


async def Tiktok(interaction: discord.Interaction):
    # On récupère les IDs stockés dans le bot
    admin_role_id = interaction.client.ADMIN_ROLE_ID
    tickets_cat_id = interaction.client.TICKETS_CAT_ID

    # Envoi du message initial avec les boutons
    view = ServiceButtons(admin_role_id=admin_role_id, tickets_cat_id=tickets_cat_id)
    await interaction.response.send_message(
        content="Choose your service",
        view=view,
        ephemeral=True
    )
