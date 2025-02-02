import discord
from discord.ext import commands
import os
import sys
from dotenv import load_dotenv
import yaml

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

# Verbose Logging: Detaillierte Ausgabe, wenn verbose auf True gesetzt ist
def log(message):
    if verbose:
        print(f"[VERBOSE] {message}")

# Bot-Setup
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
    log(f"Bot ist bereit! Eingeloggt als {bot.user} (ID: {bot.user.id})")
    print(f"Bot ist bereit! Eingeloggt als {bot.user} (ID: {bot.user.id})")
    
    # Cogs asynchron laden
    for filename in os.listdir('./commands'):
        if filename.endswith('.py') and filename != "__init__.py":
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
                log(f"Loaded {filename}")  # Verwende log(), um die geladenen Cogs im verbose-Modus anzuzeigen
            except Exception as e:
                log(f"Error loading {filename}: {e}")  # Fehler im verbose-Modus anzeigen
    try:
        await bot.tree.sync()  # Synchronisiert alle Befehle global
        log("Globale Slash-Befehle erfolgreich synchronisiert!")  # Log, wenn die Synchronisierung erfolgreich war
    except Exception as e:
        log(f"Fehler bei der globalen Synchronisierung: {e}")  # Fehler im verbose-Modus anzeigen
    await bot.load_extension('log_module')

# Bot starten
bot.run(token)
