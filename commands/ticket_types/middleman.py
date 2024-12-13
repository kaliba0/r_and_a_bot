import os
import discord
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))
MIDDLEMAN_ROLE_ID = int(os.getenv("MIDDLEMAN_ROLE_ID"))
TICKETS_CAT_ID = int(os.getenv("TICKETS_CAT_ID"))
LOGS_CHANNEL_ID = int(os.getenv("LOGS_ID"))

async def Middleman(interaction: discord.Interaction):
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
        discord.Object(id=MIDDLEMAN_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }

    # Création du channel
    ticket_channel = await guild.create_text_channel(name=f"middleman-{user.name}", category=category, overwrites=overwrites)

    # Mentionner le rôle middleman dans le channel
    middleman_mention = f"<@&{MIDDLEMAN_ROLE_ID}>"

    # Création de l'embed récapitulatif
    embed = discord.Embed(
        color=0x000000,
        title="**__MIDDLEMAN TICKET__**",
        description=(
            f"**Opened by:** {user.mention}\n\n"
            "This ticket is for a middleman service."
        )
    )
    embed.set_footer(text=f"Ticket opened by {user.name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    await ticket_channel.send(content=middleman_mention, embed=embed)
    await interaction.response.send_message(f"Your middleman ticket has been created here: {ticket_channel.mention}", ephemeral=True)

    # Envoyer un log dans le salon de logs
    logs_channel = guild.get_channel(LOGS_CHANNEL_ID)
    if logs_channel:
        log_embed = discord.Embed(
            color=0x000000,
            description=(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {ticket_channel.mention}\n"
                f"```{user.name} ({user.id}) opened a Middleman Ticket```"
            )
        )
        await logs_channel.send(embed=log_embed)
