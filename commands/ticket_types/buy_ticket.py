import discord
from discord.ui import Modal, TextInput
from discord import TextStyle
from discord.ext import commands


class BuyTicketModal(Modal):
    def __init__(self, admin_role_id: int, tickets_cat_id: int):
        super().__init__(title="Buy a Service")
        self.admin_role_id = admin_role_id
        self.tickets_cat_id = tickets_cat_id

        # Champs du formulaire
        self.product = TextInput(
            label="What product do you want to purchase?",
            style=TextStyle.short,
            required=True,
            placeholder="Enter the product name"
        )
        self.add_item(self.product)

        self.number = TextInput(
            label="How many do you want to buy?",
            style=TextStyle.short,
            required=True,
            placeholder="Enter the quantity"
        )
        self.add_item(self.number)

        self.tos = TextInput(
            label="Do you accept the TOS?",
            style=TextStyle.short,
            required=True,
            placeholder="yes/no (yes required to buy)"
        )
        self.add_item(self.tos)

        self.payment = TextInput(
            label="How do you want to pay?",
            style=TextStyle.short,
            required=True,
            placeholder="e.g., PayPal"
        )
        self.add_item(self.payment)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        product = self.product.value
        number = self.number.value
        tos = self.tos.value
        payment_method = self.payment.value

        # Récupération de la catégorie
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

        # Création de l'embed récapitulatif
        recap_embed = discord.Embed(
            color=0xf300ff,
            title="Ticket Summary",
            description="A staff member will handle your request very soon. Thanks for trusting us 💛"
        )
        recap_embed.add_field(name="Product", value=product, inline=True)
        recap_embed.add_field(name="Number", value=number, inline=True)
        recap_embed.add_field(name="TOS Accepted?", value=tos, inline=True)
        recap_embed.add_field(name="Payment Method", value=payment_method, inline=True)
        recap_embed.set_footer(
            text=f"| Ticket opened by {interaction.user.name} on {interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            icon_url="https://cdn.discordapp.com/attachments/1267140283611611258/1307098808903012444/113E567F-E6B5-4E1B-BD7B-B974E9F339D2.jpg"
        )
        recap_embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1267140283611611258/1307098808903012444/113E567F-E6B5-4E1B-BD7B-B974E9F339D2.jpg"
        )

        # Envoi de l'embed dans le salon du ticket
        await ticket_channel.send(
            content=f"<@&{self.admin_role_id}> <@{interaction.user.id}>",
            embed=recap_embed
        )

        # startInactivityTimer(ticket_channel)  # À implémenter si nécessaire

        # Réponse à l'utilisateur
        await interaction.response.send_message(
            f"A new ticket has been created for your request: <#{ticket_channel.id}>.\n"
            "Please follow the instructions sent in this channel.\n"
            "Thank you very much for trusting us 🧡",
            ephemeral=True
        )


async def BuyTicket(interaction: discord.Interaction):
    # Récupération des IDs depuis les variables du bot
    admin_role_id = interaction.client.ADMIN_ROLE_ID
    tickets_cat_id = interaction.client.TICKETS_CAT_ID

    # Envoi du modal à l'utilisateur
    modal = BuyTicketModal(admin_role_id=admin_role_id, tickets_cat_id=tickets_cat_id)
    await interaction.response.send_modal(modal)
