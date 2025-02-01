import discord
from discord.ext import commands
import yaml
import os

# Lese die Konfiguration aus einer YAML-Datei
def load_config():
    config_file = './config/config.yaml'  # Pfad zur Konfigurationsdatei
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found at {config_file}")

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config

# Konfiguration laden
config = load_config()

# Überprüfen, ob verbose aktiviert ist
verbose = config.get('verbose', True)

# Setup der Bot-Instanz
intents = discord.Intents.default()
intents.message_content = True  # Um sicherzustellen, dass der Bot Nachrichten lesen kann

bot = commands.Bot(command_prefix="!", intents=intents)

# Verbose Logging: Detaillierte Ausgabe, wenn verbose auf True gesetzt ist
def log(message):
    if verbose:
        print(f"[VERBOSE] {message}")

@bot.event
async def on_ready():
    log(f'Bot is ready and logged in as {bot.user}')
    print(f'Logged in as {bot.user}')
    # Weitere initialisierende Aufgaben, die verbose nutzen könnten

@bot.command(name='ping')
async def ping(ctx):
    log(f'Ping command received from {ctx.author}')  # Detaillierte Ausgabe bei Verwendung von ping
    await ctx.send('Pong!')

# Beispiel für eine ausführliche Debugging-Ausgabe bei Fehlern
@bot.event
async def on_error(event, *args, **kwargs):
    log(f"An error occurred: {event}")
    # Weitere Fehlerbehandlung hier

# Start des Bots
token = os.getenv('DISCORD_TOKEN')  # Discord-Token sollte in einer .env-Datei oder auf andere Weise gespeichert sein
bot.run(token)
