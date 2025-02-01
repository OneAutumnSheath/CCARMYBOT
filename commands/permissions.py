import discord
from discord.ext import commands
from discord import app_commands
import yaml
import os

config_dir = './config'
config_file = f'{config_dir}/permissions.yaml'

if not os.path.exists(config_dir):
    os.makedirs(config_dir)

def load_permissions():
    if not os.path.exists(config_file):
        return {}
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

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

def set_permissions(role_id, commands):
    permissions = load_permissions()

    if "roles" not in permissions:
        permissions["roles"] = {}

    if str(role_id) not in permissions["roles"]:
        permissions["roles"][str(role_id)] = []

    permissions["roles"][str(role_id)] += commands

    with open(config_file, 'w') as f:
        yaml.dump(permissions, f, default_flow_style=False)

def set_admin(user_id):
    permissions = load_permissions()

    if "roles" not in permissions:
        permissions["roles"] = {}

    permissions["roles"][str(user_id)] = ["*"]

    with open(config_file, 'w') as f:
        yaml.dump(permissions, f, default_flow_style=False)

class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Erstellt die Berechtigungsdatei und setzt den Admin.")
    async def setup(self, interaction: discord.Interaction):
        """Erstellt die Berechtigungsdatei und setzt den Benutzer als Admin."""
        
    
        set_admin(interaction.user.id)

        await interaction.response.send_message(f"{interaction.user.mention}, du wurdest als Admin gesetzt und alle Befehle stehen dir zur Verfügung.", ephemeral=True)

    @app_commands.command(name="setpermissions", description="Setze Berechtigungen für eine Rolle")
    async def setpermissions(self, interaction: discord.Interaction, role: discord.Role, *commands: str):
        """Setzt Berechtigungen für eine Rolle."""
        
        set_permissions(role.id, commands)

        await interaction.response.send_message(f"Berechtigungen für die Rolle {role.name} wurden gesetzt: {', '.join(commands)}", ephemeral=True)

    @app_commands.command(name="checkpermissions", description="Überprüft Berechtigungen für einen Befehl")
    async def checkpermissions(self, interaction: discord.Interaction, command_name: str):
        """Überprüft, ob der Benutzer berechtigt ist, einen Befehl auszuführen."""

        if check_permissions(command_name, interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message(f"Du bist berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Du bist nicht berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Permissions(bot))
