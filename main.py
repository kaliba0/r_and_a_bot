import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.guild_messages = True
intents.guild_reactions = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

async def setup_hook():
    await bot.load_extension("commands.embed")
    await bot.load_extension("commands.clear")
    await bot.load_extension("commands.tickets")
    await bot.load_extension("commands.close_ticket")
    await bot.load_extension("commands.paypal")
    await bot.load_extension("commands.1v1")

    await bot.tree.sync()
    print("Extensions chargées et commandes synchronisées.")

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

bot.run(TOKEN)
