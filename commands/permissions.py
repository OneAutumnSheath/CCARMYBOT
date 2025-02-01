import discord
from discord.ext import commands
from discord import app_commands
import yaml
import os

# Verzeichnis für die Konfiguration
config_dir = './config'
config_file = f'{config_dir}/permissions.yaml'
status_file = f'{config_dir}/setup_status.yaml'  # Datei zur Speicherung des Setup-Status

# Stelle sicher, dass der Config-Ordner existiert
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

# Überprüfen des Setup-Status
def is_setup_done():
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            status = yaml.safe_load(f)
            return status.get('setup_done', False)
    return False

# Setze den Setup-Status auf 'done'
def mark_setup_done():
    if not os.path.exists(status_file):
        with open(status_file, 'w') as f:
            yaml.dump({"setup_done": True}, f)
    else:
        with open(status_file, 'r+') as f:
            status = yaml.safe_load(f)
            status["setup_done"] = True
            f.seek(0)
            yaml.dump(status, f)

# Laden der Berechtigungen aus der YAML-Datei
def load_permissions():
    if not os.path.exists(config_file):
        return {}
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

# Berechtigungen für einen Befehl überprüfen
def check_permissions(command_name, user_id, role_ids):
    permissions = load_permissions()
    for role_id in role_ids:
        if str(role_id) in permissions.get("roles", {}):
            if command_name in permissions["roles"][str(role_id)] or "*" in permissions["roles"][str(role_id)]:
                return True
    if str(user_id) in permissions.get("roles", {}):
        if "*" in permissions["roles"][str(user_id)]:
            return True
    return False

# Berechtigungen für eine Rolle setzen
def set_permissions(role_id, commands):
    permissions = load_permissions()
    if "roles" not in permissions:
        permissions["roles"] = {}
    if str(role_id) not in permissions["roles"]:
        permissions["roles"][str(role_id)] = []
    permissions["roles"][str(role_id)] += commands
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f, default_flow_style=False)

# Setzt den ersten Admin-User (für setup)
def set_admin(user_id):
    permissions = load_permissions()
    if "roles" not in permissions:
        permissions["roles"] = {}
    permissions["roles"][str(user_id)] = ["*"]
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f, default_flow_style=False)

# Neuer Befehl zum Anzeigen der Berechtigungen
def view_permissions(user_id=None, role_id=None):
    permissions = load_permissions()
    permissions_info = []

    if user_id:  # Zeige Berechtigungen für einen Benutzer
        if str(user_id) in permissions.get("roles", {}):
            permissions_info.append(f"Permissions for User {user_id}: {permissions['roles'][str(user_id)]}")
        else:
            permissions_info.append(f"No permissions found for User {user_id}")
    
    if role_id:  # Zeige Berechtigungen für eine Rolle
        if str(role_id) in permissions.get("roles", {}):
            permissions_info.append(f"Permissions for Role {role_id}: {permissions['roles'][str(role_id)]}")
        else:
            permissions_info.append(f"No permissions found for Role {role_id}")

    return "\n".join(permissions_info) if permissions_info else "No permissions data found."

class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Erstellt die Berechtigungsdatei und setzt den Admin.")
    async def setup(self, interaction: discord.Interaction):
        """Erstellt die Berechtigungsdatei und setzt den Benutzer als Admin."""
        
        if is_setup_done():  # Überprüfen, ob das Setup bereits ausgeführt wurde
            await interaction.response.send_message("Setup wurde bereits ausgeführt. Dieser Befehl ist nicht mehr verfügbar.", ephemeral=True)
            return
        
        # Setze den Benutzer, der das Setup ausführt, als Admin
        set_admin(interaction.user.id)
        
        # Markiere das Setup als abgeschlossen
        mark_setup_done()

        # Bestätigungsnachricht
        await interaction.response.send_message(f"{interaction.user.mention}, du wurdest als Admin gesetzt und alle Befehle stehen dir zur Verfügung.", ephemeral=True)

    @app_commands.command(name="setpermissions", description="Setze Berechtigungen für eine Rolle")
    async def setpermissions(self, interaction: discord.Interaction, role: discord.Role, command_name: str):
        """Setzt Berechtigungen für eine Rolle."""
        
        set_permissions(role.id, [command_name])
        await interaction.response.send_message(f"Berechtigungen für die Rolle {role.name} wurden gesetzt: {command_name}", ephemeral=True)

    @app_commands.command(name="checkpermissions", description="Überprüft Berechtigungen für einen Befehl")
    async def checkpermissions(self, interaction: discord.Interaction, command_name: str):
        """Überprüft, ob der Benutzer berechtigt ist, einen Befehl auszuführen."""

        if check_permissions(command_name, interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message(f"Du bist berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Du bist nicht berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)

    @app_commands.command(name="viewpermissions", description="Zeigt Berechtigungen für einen Benutzer oder eine Rolle")
    async def viewpermissions(self, interaction: discord.Interaction, user: discord.User = None, role: discord.Role = None):
        """Zeigt Berechtigungen für einen Benutzer oder eine Rolle."""
        
        # Berechtigungen anzeigen
        if user:
            permissions_info = view_permissions(user_id=user.id)
        elif role:
            permissions_info = view_permissions(role_id=role.id)
        else:
            permissions_info = "Bitte gebe entweder einen Benutzer oder eine Rolle an."

        await interaction.response.send_message(permissions_info, ephemeral=True)

# Setup-Funktion, die den Cog dem Bot hinzufügt
async def setup(bot):
    await bot.add_cog(Permissions(bot))
