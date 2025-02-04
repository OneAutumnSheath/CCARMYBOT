import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    await bot.load_extension("commands.RoleManager")  # Stelle sicher, dass der Pfad korrekt ist

bot.run("DEIN_TOKEN")
