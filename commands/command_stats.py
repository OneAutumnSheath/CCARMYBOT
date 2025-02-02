import discord
from discord.ext import commands
from discord import app_commands
import yaml
import os

# Admin-Rollen-ID (Management ID für Berechtigungsprüfung)
MGMT_ID = 1097648080020574260

# Datei für die Speicherung der Nutzungsstatistiken
STATS_FILE = "./config/command_usage.yaml"

def load_stats():
    """Lädt die gespeicherten Nutzungsdaten aus der YAML-Datei. Erstellt die Datei, falls sie nicht existiert."""
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            yaml.dump({}, f)  # Leere Datei initialisieren
        return {}
    """Lädt die gespeicherten Nutzungsdaten aus der YAML-Datei."""
    if not os.path.exists(STATS_FILE):
        return {}
    try:
        with open(STATS_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError:
        return {}

def save_stats(stats):
    """Speichert die Nutzungsdaten in der YAML-Datei."""
    with open(STATS_FILE, "w") as f:
        yaml.dump(stats, f)

class CommandStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def is_admin(self, interaction):
        """Prüft, ob der Benutzer ein Admin ist."""
        return MGMT_ID in [role.id for role in interaction.user.roles]

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Erhöht die Nutzungszahl eines Befehls, wenn er erfolgreich ausgeführt wurde."""
        stats = load_stats()
        user_id = str(ctx.author.id)
        command_name = ctx.command.name
        
        if user_id not in stats:
            stats[user_id] = {}
        
        if command_name not in stats[user_id]:
            stats[user_id][command_name] = 0
        
        stats[user_id][command_name] += 1
        save_stats(stats)

    @app_commands.command(name="commandstats", description="Zeigt die Befehlsnutzung eines Benutzers an.")
    async def commandstats(self, interaction: discord.Interaction, user: discord.Member = None):
        """Zeigt an, wie oft ein Benutzer welche Befehle benutzt hat."""
        if not await self.is_admin(interaction):
            await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        
        stats = load_stats()
        user_id = str(user.id if user else interaction.user.id)
        
        if user_id not in stats:
            await interaction.response.send_message(f"ℹ️ Keine Befehlsdaten für {user.mention if user else 'dich'} gefunden.", ephemeral=True)
            return
        
        usage_data = stats[user_id]
        message = f"📊 Befehlsnutzung von {user.mention if user else 'dir'}:\n"
        for cmd, count in usage_data.items():
            message += f"- **{cmd}**: {count} mal\n"
        
        await interaction.response.send_message(message, ephemeral=True)

    @app_commands.command(name="resetstats", description="Setzt die Befehlsnutzung eines Benutzers oder aller Benutzer zurück.")
    async def resetstats(self, interaction: discord.Interaction, user: discord.Member = None):
        """Setzt die Nutzungsstatistik zurück."""
        if not await self.is_admin(interaction):
            await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        
        stats = load_stats()
        
        if user:
            user_id = str(user.id)
            if user_id in stats:
                del stats[user_id]
        else:
            stats.clear()
        
        save_stats(stats)
        await interaction.response.send_message("✅ Nutzungsstatistik wurde erfolgreich zurückgesetzt.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CommandStats(bot))
