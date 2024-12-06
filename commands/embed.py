import os
import json
import discord
from discord import app_commands
from discord.ext import commands

TEMPLATES_DIR = "data/embed-templates"
TICKET_CHANNEL_ID = os.getenv("TICKET_CHANNEL_ID")
adminRoleId = int(os.getenv('ADMIN_ROLE_ID'))

def get_embed(template_name: str) -> discord.Embed:
    template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.json")
    
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Le template {template_name}.json n'existe pas dans {TEMPLATES_DIR}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Conversion de la couleur hex en int
    color_int = 0x000000
    if "color" in data:
        color_str = data["color"]
        if color_str.startswith("#"):
            color_int = int(color_str[1:], 16)
        else:
            color_int = int(color_str, 16)

    description = data.get("description", "")
    # Remplace la chaîne si nécessaire
    if TICKET_CHANNEL_ID:
        description = description.replace("TICKET_CHANNEL_ID", TICKET_CHANNEL_ID)

    embed = discord.Embed(
        title=data.get("title"),
        description=description,
        color=color_int
    )

    if "thumbnail" in data:
        embed.set_thumbnail(url=data["thumbnail"])

    if "image" in data:
        embed.set_image(url=data["image"])

    if "footer" in data:
        footer_data = data["footer"]
        embed.set_footer(text=footer_data.get("text", ""), icon_url=footer_data.get("icon_url", ""))

    if "fields" in data:
        for field in data["fields"]:
            embed.add_field(
                name=field["name"], 
                value=field["value"], 
                inline=field.get("inline", False)
            )

    return embed



class EmbedCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Send an embed")
    @app_commands.describe(type="Embed Templates")
    @app_commands.choices(type=[
        app_commands.Choice(name="Hacker", value="hacker"),
        app_commands.Choice(name="TOS", value="tos"),
        app_commands.Choice(name="Server-Boosts", value="server-boosts"),
        app_commands.Choice(name="Rank-Up", value="rank-up"),
        app_commands.Choice(name="Nitro-Boosts", value="nitro-boosts")
    ])
    async def embed_cmd(self, interaction: discord.Interaction, type: app_commands.Choice[str]):
        # Vérification des permissions
        if adminRoleId not in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)
            return

        try:
            chosen_embed = get_embed(type.value)
            await interaction.response.send_message(embed=chosen_embed)
        except FileNotFoundError:
            await interaction.response.send_message("Le template demandé n'existe pas.", ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message("Une erreur est survenue lors de la création de l'embed.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(EmbedCog(bot))
