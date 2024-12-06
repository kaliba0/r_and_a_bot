import os
import discord
from discord import app_commands
from discord.ext import commands

adminRoleId = int(os.getenv('ADMIN_ROLE_ID'))

class ClearCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Clear all messages in the current channel")
    async def clear_cmd(self, interaction: discord.Interaction):
        # Vérification des permissions
        if adminRoleId not in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)
            return

        # Envoi d'un message éphémère pour indiquer le début de la suppression
        await interaction.response.send_message("Deleting all messages...", ephemeral=True)
        
        channel = interaction.channel
        try:
            # Purge tous les messages du salon
            await channel.purge()
            
            # Une fois la purge terminée, on supprime le message éphémère initial
            await interaction.delete_original_response()

        except discord.Forbidden:
            await interaction.followup.send("I do not have permission to delete messages here.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ClearCog(bot))
