import discord
from discord.ext import commands
import os
from dotenv import load_dotenv


load_dotenv()

intents = discord.Intents.default()

intents.messages = True  # Für Nachrichten
intents.guilds = True  # Für Guilds (Server)
intents.members = True  # Für Mitglieder
intents.bans = True  # Für Bans
intents.emojis = True  # Für Emojis
intents.reactions = True  # Für Reaktionen
intents.presences = True  # Für Benutzerstatus (online/offline)
intents.typing = True  # Für das Tippen
intents.message_content = True  # Für das Abrufen des Inhalts von Nachrichten (nur erforderlich, wenn der Bot auf Nachrichteninhalte zugreifen muss)


bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
def on_ready():
    print(f"Bot ist bereit! Eingeloggt als {bot.user} (ID: {bot.user.id})")

    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
        bot.load_extension(f'commands.{filename[:-3]}')


token = os.getenv("DISCORD_TOKEN")
bot.run(token)
