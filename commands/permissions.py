import discord
from discord.ext import commands
from discord import app_commands
from permissions import check_permissions as check_perm, set_permissions as set_perm, view_permissions as view_perm
import yaml
import os

# Verzeichnis für die Konfiguration
config_dir = './config'
config_file = f'{config_dir}/permissions.yaml'

# Überprüfen der Berechtigung anhand von Permission-Nodes
def has_permission(user, permission_node):
    permissions = load_permissions()
    # Überprüfen, ob der Benutzer die angeforderte Berechtigung hat
    user_roles = [role.id for role in user.roles]
    for role_id in user_roles:
        if str(role_id) in permissions.get("roles", {}):
            if permission_node in permissions["roles"][str(role_id)] or "*" in permissions["roles"][str(role_id)]:
                return True
    return False

# Laden der Berechtigungen aus der YAML-Datei
def load_permissions():
    if not os.path.exists(config_file):
        return {}
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="checkpermissions", description="Überprüft Berechtigungen für einen Befehl")
    async def checkpermissions(self, interaction: discord.Interaction, command_name: str):
        """Überprüft, ob der Benutzer berechtigt ist, einen Befehl auszuführen."""
        
        permission_node = f"checkpermissions.{command_name}"  # Beispiel-Node für Berechtigung
        if has_permission(interaction.user, permission_node):
            await interaction.response.send_message(f"Du bist berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Du bist nicht berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)

    @app_commands.command(name="setpermissions", description="Setze Berechtigungen für eine Rolle")
    async def setpermissions(self, interaction: discord.Interaction, role: discord.Role, command_name: str):
        """Setzt Berechtigungen für eine Rolle."""
        
        permission_node = "setpermissions"  # Beispiel-Node für Berechtigung
        if has_permission(interaction.user, permission_node):
            set_perm(role.id, [command_name])  # Berechtigungen setzen
            await interaction.response.send_message(f"Berechtigungen für die Rolle {role.name} wurden gesetzt: {command_name}", ephemeral=True)
        else:
            await interaction.response.send_message("Du hast keine Berechtigung, Berechtigungen zu setzen.", ephemeral=True)

    @app_commands.command(name="viewpermissions", description="Zeigt Berechtigungen für einen Benutzer oder eine Rolle")
    async def viewpermissions(self, interaction: discord.Interaction, user: discord.User = None, role: discord.Role = None):
        """Zeigt Berechtigungen für eine Rolle oder einen Benutzer an."""
        
        permission_node = "viewpermissions"  # Beispiel-Node für Berechtigung
        if has_permission(interaction.user, permission_node):
            # Berechtigungen anzeigen
            if user:
                permissions_info = view_perm(user_id=user.id)
            elif role:
                permissions_info = view_perm(role_id=role.id)
            else:
                permissions_info = "Bitte gebe entweder einen Benutzer oder eine Rolle an."
            
            await interaction.response.send_message(permissions_info, ephemeral=True)
        else:
            await interaction.response.send_message("Du hast keine Berechtigung, Berechtigungen anzuzeigen.", ephemeral=True)

# Setup-Funktion, die den Cog dem Bot hinzufügt
async def setup(bot):
    await bot.add_cog(Permissions(bot))
