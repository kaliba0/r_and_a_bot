import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import os


class CloseTicket(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="close", description="Close the current ticket.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def close_ticket(self, interaction: discord.Interaction):
        channel = interaction.channel
        category = channel.category

        # Vérifiez si le channel est dans la catégorie des tickets
        if not category or "ticket" not in category.name.lower():
            await interaction.response.send_message(
                "This command can only be used in a ticket channel.",
                ephemeral=True
            )
            return

        # Logs : Log de fermeture dans le salon des logs
        logs_channel = interaction.guild.get_channel(int(os.getenv("LOGS_ID")))
        if logs_channel:
            log_embed = discord.Embed(
                color=0xff0000,
                title="Ticket Closed",
                description=(
                    f"Ticket {channel.name} has been closed.\n"
                    f"Closed by: {interaction.user.mention}\n"
                    f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            )
            await logs_channel.send(embed=log_embed)

        # Supprimer le channel
        await channel.delete(reason=f"Ticket closed by {interaction.user.name}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(CloseTicket(bot))
