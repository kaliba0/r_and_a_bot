import os
import discord
from discord import Interaction
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))
TICKETS_CAT_ID = int(os.getenv("TICKETS_CAT_ID"))
LOGS_CHANNEL_ID = int(os.getenv("LOGS_ID"))

async def SupportTicket(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user

    # Vérification de la catégorie
    category = guild.get_channel(TICKETS_CAT_ID)
    if category is None:
        await interaction.response.send_message("Category not found. Please check your configuration.", ephemeral=True)
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        discord.Object(id=ADMIN_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }

    # Création du salon
    ticket_channel = await guild.create_text_channel(name=f"support-{user.name}", category=category, overwrites=overwrites)

    # Création de l'embed de récap
    embed = discord.Embed(color=0x000000, title="**__Support Ticket__**",
                          description="You can describe your issue here, and a staff member will assist you soon.")
    embed.set_footer(text=f"Ticket opened by {user.mention} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    # Envoi du message dans le ticket, pingant les admins
    admin_mention = f"<@&{ADMIN_ROLE_ID}>"
    await ticket_channel.send(content=admin_mention, embed=embed)

    # Envoi du log dans le canal dédié
    logs_channel = guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        log_embed = discord.Embed(color=0x000000, description=(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {ticket_channel.mention}\n"
            f"```{user.name} ({user.id}) | Support Ticket```"
        ))
        await logs_channel.send(content=admin_mention, embed=log_embed)

    # Envoi d'une confirmation à l'utilisateur
    await interaction.response.send_message(f"Your support ticket has been created here: {ticket_channel.mention}", ephemeral=True)
