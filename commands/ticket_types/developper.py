import os
import discord
from discord.ui import View
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))
DEVELOPPER_ROLE_ID = int(os.getenv("DEVELOPPER_ROLE_ID"))
TICKETS_CAT_ID = int(os.getenv("TICKETS_CAT_ID"))
LOGS_CHANNEL_ID = int(os.getenv("LOGS_ID"))


async def Developer(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user

    # Récupérer la catégorie
    category = guild.get_channel(TICKETS_CAT_ID)
    if category is None:
        await interaction.response.send_message("Category not found. Please check your configuration.", ephemeral=True)
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        discord.Object(id=ADMIN_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        discord.Object(id=DEVELOPPER_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }

    # Création du channel
    ticket_channel = await guild.create_text_channel(name=f"developper-{user.name}", category=category, overwrites=overwrites)

    # Mentionner uniquement le rôle middleman à l'ouverture
    middleman_mention = f"<@&{DEVELOPPER_ROLE_ID}>"
    # Message d'instructions
    instructions_msg = await ticket_channel.send(
        content=(
            f"{middleman_mention}\n"
            f"<a:lding:1317221095715115089> {user.mention}, please send your request in this channel. Once you have sent your request, it will be processed."
        )
    )

    # Envoi d'une réponse éphémère à l'utilisateur
    await interaction.response.send_message(f"Your developper ticket has been created here: {ticket_channel.mention}", ephemeral=True)

    def check_author(m):
        return m.author.id == user.id and m.channel.id == ticket_channel.id

    try:
        # Attendre que l'utilisateur envoie son message (sa requête)
        request_msg = await interaction.client.wait_for("message", timeout=300.0, check=check_author)
    except TimeoutError:
        # Si l'utilisateur n'envoie rien dans les 5 minutes
        await ticket_channel.send("No request was sent. Closing the ticket.")
        return
    
    await ticket_channel.purge()

    # Création de l'embed récapitulatif
    embed = discord.Embed(
        color=0x000000,
        title="**__DEVELOPPER TICKET__**",
        description=(
            f"**Request from:** {user.mention}\n\n"
            f"```{request_msg.content}```"
        )
    )
    embed.set_footer(text=f"Ticket opened by {user.name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    recap_msg = await ticket_channel.send(embed=embed)

    # Envoyer un log dans le salon de logs
    logs_channel = guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        log_embed = discord.Embed(
            color=0x000000,
            description=(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {ticket_channel.mention}\n"
                f"```{user.name} ({user.id}) | DEV service: {request_msg.content}```"
            )
        )
        await logs_channel.send(embed=log_embed)
