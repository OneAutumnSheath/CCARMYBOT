 import discord
from discord.ext import commands
import yaml
import os
from dotenv import load_dotenv

# Verzeichnis und Dateipfad für die Konfiguration
config_dir = './config'
config_file = f'{config_dir}/config.yaml'

# Standard-Konfiguration
default_config = {
    'verbose': True
}

# Lese die Konfiguration oder erstelle sie, wenn sie nicht existiert
def load_config():
    # Prüfe, ob das Verzeichnis existiert, andernfalls erstelle es
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Wenn die config.yaml nicht existiert, erstelle sie mit Standardwerten
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f)  # Schreibe die Standardkonfiguration in die Datei
        print(f"Config file not found. Creating default config at {config_file}")

    # Lade die Konfigurationsdatei
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config

# Konfiguration laden
config = load_config()

# Überprüfen, ob verbose aktiviert ist
verbose = config.get('verbose', False)

# Lade die Umgebungsvariablen aus der .env-Datei
load_dotenv()
# Holen des Tokens aus der Umgebungsvariablen
token = os.getenv('DISCORD_TOKEN')
# Überprüfen, ob der Token vorhanden ist
if not token:
    raise ValueError("No DISCORD_TOKEN found. Please set it in the .env file.")
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
bot.run(token)