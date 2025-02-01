import discord
from discord.ext import commands
import os
import sys
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
# Füge den 'commands' Ordner zum sys.path hinzu
sys.path.insert(0, os.path.abspath('./commands'))

@bot.event
async def on_ready():
    print(f"Bot ist bereit! Eingeloggt als {bot.user} (ID: {bot.user.id})")
    
    # Cogs asynchron laden
    for filename in os.listdir('./commands'):
        if filename.endswith('.py') and filename != "__init__.py":
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
                print(f"Loaded {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    try:
        await bot.tree.sync()  # Synchronisiert alle Befehle global
        print("Globale Slash-Befehle erfolgreich synchronisiert!")
    except Exception as e:
        print(f"Fehler bei der globalen Synchronisierung: {e}")


token = os.getenv("DISCORD_TOKEN")
bot.run(token)
