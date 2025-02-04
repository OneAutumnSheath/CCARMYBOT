import discord
from discord.ext import commands, tasks
import yaml
import os
from datetime import datetime

# Die Datei für die Speicherung der Rollendaten
ROLES_FILE = "./config/roles.yml"
CONFIG_FILE = "./config/config.yml"

def load_roles():
    """Lädt die gespeicherten Rollen- und Mitgliedsdaten aus der YAML-Datei oder erstellt die Datei, wenn sie nicht existiert."""
    if not os.path.exists(ROLES_FILE):
        with open(ROLES_FILE, "w") as f:
            yaml.dump({}, f)  # Leere Datei initialisieren
    with open(ROLES_FILE, "r") as f:
        return yaml.safe_load(f) or {}

def save_roles(roles):
    """Speichert die Rollen- und Mitgliedsdaten in der YAML-Datei."""
    with open(ROLES_FILE, "w") as f:
        yaml.dump(roles, f)

def load_config():
    """Lädt die Konfigurationsdatei, um die Channel zu bekommen, in denen Nachrichten gesendet werden sollen."""
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            yaml.dump({"channels": {}})  # Default leere Channel-Struktur
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 1097625621875675188  # Die Guild ID
        self.role_update.start()  # Starte die Aufgabe, die regelmäßig Rollenabfragen durchführt

    @tasks.loop(seconds=30)  # Alle 30 Sekunden wird die Abfrage durchgeführt
    async def role_update(self):
        """Überprüft die Mitglieder jeder Rolle und speichert die Information."""
        roles = load_roles()
        config = load_config()

        # Hole die Channels für diese Guild
        if str(self.guild_id) in config["channels"]:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                return  # Wenn der Bot nicht im richtigen Server ist, breche ab

            for channel_id, channel_data in config["channels"][str(self.guild_id)].items():
                channel = self.bot.get_channel(int(channel_id))
                if not channel:
                    continue  # Falls der Channel nicht existiert, überspringen

                # Hole die Rollen in diesem Channel
                for role_name, members in channel_data["roles"].items():
                    role = discord.utils.get(guild.roles, name=role_name)
                    if not role:
                        continue  # Falls die Rolle nicht gefunden wird, überspringen
                    
                    # Hole alle Mitglieder mit dieser Rolle
                    role_members = [member.id for member in role.members]
                    channel_data["roles"][role_name] = role_members

                # Speichern der aktuellen Rollen und Mitglieder für den Channel
                save_roles(roles)

                # Erstelle ein Embed mit den Rollenmitgliedern für den Channel
                embed = discord.Embed(title=f"Rollen Mitglieder Update: {channel.name}", color=discord.Color.blue())
                for role_name, member_ids in channel_data["roles"].items():
                    members = [f"<@{member_id}>" for member_id in member_ids]
                    embed.add_field(name=role_name, value="\n".join(members), inline=False)

                embed.set_footer(text=f"Letzte Aktualisierung: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await channel.send(embed=embed)

    @role_update.before_loop
    async def before_role_update(self):
        """Warten, bis der Bot bereit ist, bevor die Aufgabe gestartet wird."""
        await self.bot.wait_until_ready()

    @app_commands.command(name="setrolechannel", description="Setzt den Channel und die Rollen für eine Einheit.")
    async def set_role_channel(self, interaction: discord.Interaction, channel: discord.TextChannel, roles: str):
        """Setzt den Channel für die Rollenmitgliedsdaten und definiert die Rollen."""
        config = load_config()

        # Konvertiere die Rollen-IDs in eine Liste und speichere sie
        role_list = [role.strip() for role in roles.split(',')]

        if str(self.guild_id) not in config["channels"]:
            config["channels"][str(self.guild_id)] = {}

        config["channels"][str(self.guild_id)][str(channel.id)] = {
            "roles": {role: [] for role in role_list}
        }

        # Speichern der Änderungen
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(config, f)

        await interaction.response.send_message(f"Die Channel-ID {channel.mention} wurde mit den Rollen {', '.join(role_list)} konfiguriert.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleManager(bot))
