import discord
from discord.ui import Modal, TextInput
from discord import TextStyle
from discord.ext import commands


class BanModal(Modal):
    def __init__(self, admin_role_id: int, tickets_cat_id: int):
        super().__init__(title="Ban Request")
        self.admin_role_id = admin_role_id
        self.tickets_cat_id = tickets_cat_id

        # Champs du formulaire
        self.reason = TextInput(
            label="Reason ?",
            style=TextStyle.short,
            required=True,
            placeholder="Enter the reason for the ban request."
        )
        self.add_item(self.reason)

        self.profile = TextInput(
            label="Profile of the account",
            style=TextStyle.short,
            required=True,
            placeholder="Provide the profile to ban."
        )
        self.add_item(self.profile)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        reason = self.reason.value
        profile = self.profile.value

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
        recap_embed.add_field(name="Reason", value=reason, inline=True)
        recap_embed.add_field(name="Profile", value=profile, inline=True)
        recap_embed.add_field(name="Service", value="Ban Request", inline=True)
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


async def Ban(interaction: discord.Interaction):
    # Récupération des IDs depuis les variables du bot
    admin_role_id = interaction.client.ADMIN_ROLE_ID
    tickets_cat_id = interaction.client.TICKETS_CAT_ID

    # Envoi du modal à l'utilisateur
    modal = BanModal(admin_role_id=admin_role_id, tickets_cat_id=tickets_cat_id)
    await interaction.response.send_modal(modal)

