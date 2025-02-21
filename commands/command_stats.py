import discord
from discord.ext import commands
from discord import app_commands
import yaml
import os
from permissions_logic import check_permissions  # Importiere die Berechtigungsprüfung

# Datei für die Speicherung der Nutzungsstatistiken
STATS_FILE = "./config/command_usage.yaml"

def load_stats():
    """Lädt die gespeicherten Nutzungsdaten aus der YAML-Datei. Erstellt die Datei, falls sie nicht existiert."""
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            yaml.dump({}, f)  # Leere Datei initialisieren
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

    def is_allowed_users(self, interaction, user: discord.Member):
        """Überprüft, ob der Benutzer die Berechtigung hat, die Statistiken eines anderen Benutzers anzusehen."""
        # Wenn der Benutzer die eigene Statistik sehen möchte, ist das erlaubt
        if user == interaction.user:
            return True
        # Wenn nicht, prüfe die Berechtigungen
        return check_permissions("stats_all", interaction.user.id, [role.id for role in interaction.user.roles])

    def is_admin(self, interaction):
        """Überprüft, ob der Benutzer Administratorrechte für 'resetstats' oder 'statsreport' hat."""
        # Beispiel für Admin-Berechtigung: Wir prüfen, ob der Benutzer Admin-Rechte hat
        return check_permissions("stats_admin", interaction.user.id, [role.id for role in interaction.user.roles])

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Erhöht die Nutzungszahl eines Slash-Befehls, wenn er erfolgreich ausgeführt wurde."""
        if not interaction.command:
            return  # Ignoriere Interaktionen, die keine Befehle sind
        
        stats = load_stats()
        user_id = str(interaction.user.id)
        command_name = interaction.command.name
        
        if user_id not in stats:
            stats[user_id] = {}
        
        if command_name not in stats[user_id]:
            stats[user_id][command_name] = 0
        
        stats[user_id][command_name] += 1
        save_stats(stats)

    @app_commands.command(name="commandstats", description="Zeigt die Befehlsnutzung eines Benutzers an.")
    async def commandstats(self, interaction: discord.Interaction, user: discord.Member = None):
        """Zeigt an, wie oft ein Benutzer welche Befehle benutzt hat."""
        
        # Wenn ein Benutzer angegeben ist, überprüfen, ob der Zugriff erlaubt ist
        if user and not self.is_allowed_users(interaction, user):
            await interaction.response.send_message("❌ Du hast keine Berechtigung, die Statistiken dieses Benutzers zu sehen.", ephemeral=True)
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
        
        # Berechtigungsprüfung, nur Admins oder berechtigte Benutzer dürfen diesen Befehl ausführen
        if not self.is_admin(interaction):
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

    @app_commands.command(name="statsreport", description="Zeigt eine Übersicht aller Befehlsnutzungsstatistiken.")
    async def statsreport(self, interaction: discord.Interaction):
        """Zeigt eine Übersicht der Befehlsnutzung aller Benutzer."""
        
        # Berechtigungsprüfung, nur Admins oder berechtigte Benutzer dürfen diesen Befehl ausführen
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        
        stats = load_stats()
        
        if not stats:
            await interaction.response.send_message("ℹ️ Es wurden keine Befehlsstatistiken gefunden.", ephemeral=True)
            return
        
        message = "📊 Übersicht der Befehlsnutzung aller Benutzer:\n"
        
        for user_id, usage_data in stats.items():
            user = await self.bot.fetch_user(int(user_id))
            message += f"\n**{user.mention}**:\n"  # Hier wird der Benutzer markiert
            for cmd, count in usage_data.items():
                message += f"  - **{cmd}**: {count} mal\n"
        
        await interaction.response.send_message(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CommandStats(bot))
