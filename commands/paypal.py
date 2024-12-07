import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))

paypal_email = 'rafaaa.antterzn.shop@gmail.com'

class PayPalView(discord.ui.View):
    def __init__(self, admin_role_id: int, paypal_email: str):
        super().__init__(timeout=60)
        self.admin_role_id = admin_role_id
        self.paypal_email = paypal_email

    @discord.ui.button(label="Copy PayPal", style=discord.ButtonStyle.primary, custom_id="copy_paypal")
    async def copy_paypal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Envoi de l'adresse PayPal en éphémère, visible seulement par l'utilisateur qui a cliqué
        await interaction.response.send_message(content=self.paypal_email, ephemeral=True)


class PayPalCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def admin_check(interaction: discord.Interaction):
        if ADMIN_ROLE_ID not in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="paypal", description="Affiche les informations PayPal")
    @app_commands.check(admin_check)
    async def paypal_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            color=0x0070BA,
            title="PayPal Instructions"
        )
        embed.add_field(name='Paypal Email Address:', value=f"**```{paypal_email}```**", inline=False)
        embed.add_field(
            name='\u200B\nInstructions:',
            value=(
                "**<:verified:1308789503535616032> Do not add any __NOTES__ to the payment**\n"
                "**<:verified:1308789503535616032> SEND THROUGH __FRIENDS AND FAMILY__ ONLY**\n"
                "**<:verified:1308789503535616032> Once sent, take a __screenshot of the Payment Summary__**\n"
            ),
            inline=False
        )
        embed.add_field(
            name='\u200B',
            value=(
                "When you have sent the payment, click on the **`Send the screenshot`** button in your ticket.\n"
                "If you need a staff member, click the **`Contact Support`** button in your ticket\n\n"
                "**<a:warning:1308790567563558934> If you simply do not follow these rules, "
                "we will not refund you or give you the products.**"
            ),
            inline=False
        )
        embed.set_footer(text="| Rafaaa & Antterzn", icon_url="https://cdn.discordapp.com/attachments/1267140283611611258/1307098808903012444/113E567F-E6B5-4E1B-BD7B-B974E9F339D2.jpg")
        embed.set_thumbnail(url="https://companieslogo.com/img/orig/PYPL-3570673e.png?t=1720244493")

        view = PayPalView(admin_role_id=ADMIN_ROLE_ID, paypal_email=paypal_email)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(PayPalCog(bot))
