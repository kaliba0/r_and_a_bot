import discord
from discord import app_commands
from discord.ext import commands
import os


class CloseTicket(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="close", description="Close the current ticket.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def close_ticket(self, interaction: discord.Interaction):
        channel = interaction.channel
        tickets_cat_id = int(os.getenv("TICKETS_CAT_ID"))
        battle_cat_id = int(os.getenv("1V1_CAT_ID"))

        # Vérifiez si le channel est dans la catégorie des tickets
        if not channel.category or channel.category.id != tickets_cat_id or channel.category.id != battle_cat_id:
            await interaction.response.send_message(
                "This command can only be used in a ticket channel under the Tickets category.",
                ephemeral=True
            )
            return

        # Supprimer le channel
        await channel.delete(reason=f"Ticket closed by {interaction.user.name}.")

    @close_ticket.error
    async def close_ticket_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(CloseTicket(bot))
