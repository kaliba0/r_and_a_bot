import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Import des fonctions spécifiques pour les tickets
from commands.ticket_types.social import Social
from commands.ticket_types.ban import Ban
from commands.ticket_types.buy_ticket import BuyTicket
from commands.ticket_types.game_boost import GameBoost
from commands.ticket_types.accounts import GameAccounts
from commands.ticket_types.support import SupportTicket
from commands.ticket_types.developper import Developer
from commands.ticket_types.middleman import Middleman

load_dotenv()

ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))
TICKETS_CAT_ID = os.getenv("TICKETS_CAT_ID")
ACCOUNTS_CAT_ID = os.getenv("ACCOUNTS_CAT_ID")


class ServiceSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="BUY TICKET", value="ticket", description="N1tr0, Serv B00sts, Movies, Ban, ...", emoji="<a:nitro:1320099432234225674>"),
            discord.SelectOption(label="SOCIAL BOOST", value="social", description="Inst4/T1kt0k followers, views, likes, ...", emoji="<:tiktok:1320099361069203487>"),
            discord.SelectOption(label="GAME BOOST", value="game", description="BrawlPass +, V-Bucks, Brawl Stars tiermax, ranked ranks, ...", emoji="<:bpass:1320099475653398558>"),
            discord.SelectOption(label="GAME ACCOUNTS", value="accounts", description="Buy/Sell Brawl Stars, Fortnite accounts", emoji="<:paypal:1320099594851586069>"),
            discord.SelectOption(label="DEVELOPPER", value="dev", emoji="<:hacker:1320099658571448390>", description="App, bot, software development"),
            discord.SelectOption(label="MIDDLEMAN SERVICES", value="middleman", emoji="<:shield:1320099722651766895>", description="Get a trusted middleman to secure your transactions"),
            discord.SelectOption(label="CONTACT SUPPORT", value="support", emoji="<a:settings:1320099766394421280>", description="In case of issue or question"),
        ]

        super().__init__(
            placeholder="Select an option",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="select-service",
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        if choice == "social":
            await Social(interaction)
        elif choice == "game":
            await GameBoost(interaction)
        elif choice == "ticket":
            await BuyTicket(interaction)
        elif choice == "accounts":
            await GameAccounts(interaction)
        elif choice == "support":
            await SupportTicket(interaction)
        elif choice=="dev":
            await Developer(interaction)
        elif choice=="middleman":
            await Middleman(interaction)
        else:
            await interaction.response.send_message("Incorrect Input", ephemeral=True)


class ServiceSelectView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.add_item(ServiceSelect(bot))


class TicketsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.TICKETS_CAT_ID = TICKETS_CAT_ID
        self.bot.ACCOUNTS_CAT_ID = ACCOUNTS_CAT_ID
        self.bot.ADMIN_ROLE_ID = ADMIN_ROLE_ID

    @app_commands.command(name="tickets", description="Display the ticket creation panel")
    async def tickets_cmd(self, interaction: discord.Interaction):
        # Vérification des permissions
        if ADMIN_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)
            return

        embed = discord.Embed(
            color=0x000,
            title="Rafaaa's Shop 🛍\n\u200B",
        )

        embed.add_field(
            name="**TICKETS <a:diams:1317192167965327412>**",
            value=(
                "**<a:tiket:1317192702345089134> Open a Buy Ticket to Purchase a Product.\n"
                "<a:bot:1317192345367609394> Open a Support ticket if you require Support by our Staff Team.\n\u200B**"
            ),
            inline=False,
        )

        embed.add_field(
            name="**SOCIAL BOOSTS <a:diams:1317192167965327412>**",
            value="**<:tiktok:1317192232620527648> TikTok\n<:insta:1317192314501726299> Instagram\n\u200B**",
            inline=False,
        )

        embed.add_field(
            name="**BRAWLSTARS <a:diams:1317192167965327412>**",
            value=(
                "**<:r35:1307121920851836948> Tier Max\n<:master:1318743158552531036> Ranked Ranks\n\u200B**"
            ),
            inline=False,
        )

        embed.add_field(
            name="**H4CK3R/DEVELOPPER <a:diams:1317192167965327412>**",
            value=(
                "**<:hacker:1317222692553883790> h4ck a social media account or anything else\n"
                ":computer: Create a bot/app/program\n"
                ":prohibited: Ban any BrawlStars account**"
            ),
            inline=False,
        )

        embed.add_field(
            name="\u200B",
            value=(
                "**<:infini:1317192661777518592> We are the fastest service ever\n"
                "<:infini:1317192661777518592> If your Product is not in Stock, your Ticket will be closed**"
            ),
            inline=False,
        )

        embed.set_footer(
            text="|  Rafaaa & Antterzn",
            icon_url="https://cdn.discordapp.com/attachments/1267140283611611258/1307098808903012444/113E567F-E6B5-4E1B-BD7B-B974E9F339D2.jpg?ex=67391220&is=6737c0a0&hm=3402606aa1f6bdf7a1fce5d9cfc3aae0ed179fc43d935aabd530d5afe91803fb&",
        )

        view = ServiceSelectView(self.bot)

        # Envoi du message embed et suppression de la réponse slash
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.delete_original_response()


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketsCog(bot))
