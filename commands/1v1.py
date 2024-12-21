import os
import discord
from discord.ui import View, Modal, TextInput, Button
from discord import app_commands, TextStyle, ButtonStyle
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))
ONEVONE_CAT_ID = int(os.getenv("1V1_CAT_ID"))

class ChallengeModal(Modal):
    def __init__(self, challenger: discord.Member):
        super().__init__(title="Enter challenge details")
        self.challenger = challenger
        self.game = TextInput(label="Game", style=TextStyle.short, required=True, placeholder="Ex: Fortnite")
        self.amount = TextInput(label="Amount (€)", style=TextStyle.short, required=True, placeholder="Ex: 20")
        self.notes = TextInput(label="Notes (optional)", style=TextStyle.paragraph, required=False, placeholder="Ex: Conditions, special rules")
        self.add_item(self.game)
        self.add_item(self.amount)
        self.add_item(self.notes)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not self.amount.value.isdigit():
            await interaction.followup.send("Enter a valid number for the amount.", ephemeral=True)
            return
        amount_val = int(self.amount.value)
        fee = amount_val * 0.1
        net = amount_val - fee
        embed = discord.Embed(color=0x000000, title="__CHALLENGE OFFER__")
        embed.description = (
            f"```Challenger: {self.challenger.name}\nGame: {self.game.value}\nAmount: {amount_val}€\nFees: {fee:.2f}€ (10%)\nNet: {net:.2f}€```\n"
            f"{'Notes:\n```' + self.notes.value + '```' if self.notes.value else ''}"
        )
        embed.set_footer(text=f"Challenge issued on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await interaction.followup.send(embed=embed, view=ChallengeView(self.challenger, self.game.value, amount_val, self.notes.value), ephemeral=False)

class LaunchView(View):
    def __init__(self, challenger: discord.Member):
        super().__init__(timeout=None)
        self.challenger = challenger

    @discord.ui.button(label="Launch a challenge", style=ButtonStyle.primary)
    async def launch(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.challenger.id:
            await interaction.response.send_message("Only the command user can launch a challenge.", ephemeral=True)
            return
        await interaction.response.send_modal(ChallengeModal(self.challenger))

class ChallengeView(View):
    def __init__(self, challenger: discord.Member, game: str, amount: int, notes: str):
        super().__init__(timeout=None)
        self.challenger = challenger
        self.game = game
        self.amount = amount
        self.notes = notes

    @discord.ui.button(label="Launch Another Challenge", style=ButtonStyle.primary)
    async def another(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.challenger.id:
            await interaction.response.send_message("Only the challenger can launch another challenge.", ephemeral=True)
            return
        await interaction.response.send_modal(ChallengeModal(self.challenger))

    @discord.ui.button(label="Accept Challenge", style=ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        category = guild.get_channel(ONEVONE_CAT_ID)
        if category is None:
            await interaction.response.send_message("Category not found.", ephemeral=True)
            return
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True),
            self.challenger: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        ticket_channel = await guild.create_text_channel(name=f"1v1-{self.challenger.name}-{interaction.user.name}", category=category, overwrites=overwrites)
        embed = discord.Embed(color=0x000000, title="__1v1 CHALLENGE__")
        embed.description = (
            f"```Challenger: {self.challenger.name}\nOpponent: {interaction.user.name}\nGame: {self.game}\nAmount: {self.amount}€```"
            f"{f'\nNotes:\n```{self.notes}```' if self.notes else ''}"
        )
        embed.set_footer(text=f"Ticket opened on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await ticket_channel.send(embed=embed)
        await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

class Token1v1Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def admin_check(interaction: discord.Interaction):
        return True

    @app_commands.command(name="token-1v1", description="Launch a 1v1 challenge with a bet")
    @app_commands.check(admin_check)
    async def token_1v1(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0x000000, title="__1v1 TOKEN CHALLENGE__")
        embed.description = (
            "**You can start a challenge by betting money against another player.**\n"
            "**A 10% fee will be applied.**\n"
            "**Anyone who doesn't follow the conditions will be instantly banned.**\n"
        )
        embed.set_footer(text=f"Invoked on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await interaction.response.send_message(embed=embed, view=LaunchView(interaction.user))

async def setup(bot: commands.Bot):
    await bot.add_cog(Token1v1Cog(bot))
