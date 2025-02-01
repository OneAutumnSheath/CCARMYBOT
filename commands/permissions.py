import discord
from discord.ext import commands
from discord import app_commands
from discord import Interaction
from permissions_logic import check_permissions, set_permissions, view_permissions, unset_permissions, reset_permissions  # Import aus der neuen Datei

class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash-Befehl: checkpermissions
    @app_commands.command(name="checkpermissions", description="Überprüft Berechtigungen für einen Befehl")
    async def checkpermissions(self, interaction: Interaction, command_name: str):
        """Überprüft, ob der Benutzer berechtigt ist, einen Befehl auszuführen."""
        
        permission_node = f"checkpermissions.{command_name}"  # Beispiel-Node für Berechtigung
        if check_permissions(command_name, interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message(f"Du bist berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Du bist nicht berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)

# Slash-Befehl: setpermissions
@ app_commands.command(name="setpermissions", description="Setze Berechtigungen für eine Rolle oder einen Benutzer")
async def setpermissions(self, interaction: discord.Interaction, role: discord.Role = None, user: discord.User = None, command_name: str = None):
    # ...
    if role:
        set_permissions(role.id, [command_name], is_user=False)  # Korrektur: is_user=False
    elif user:
        set_permissions(user.id, [command_name], is_user=True)   # Korrektur: is_user=True

    # Slash-Befehl: viewpermissions
    @app_commands.command(name="viewpermissions", description="Zeigt Berechtigungen für einen Benutzer oder eine Rolle")
    async def viewpermissions(self, interaction: discord.Interaction, user: discord.User = None, role: discord.Role = None):
        """Zeigt Berechtigungen für eine Rolle oder einen Benutzer an."""
        
        permission_node = "viewpermissions"  # Beispiel-Node für Berechtigung
        if check_permissions(permission_node, interaction.user.id, [role.id for role in interaction.user.roles]):
            # Berechtigungen anzeigen
            if user:
                permissions_info = view_permissions(user_id=user.id)
            elif role:
                permissions_info = view_permissions(role_id=role.id)
            else:
                permissions_info = "Bitte gebe entweder einen Benutzer oder eine Rolle an."
            
            await interaction.response.send_message(permissions_info, ephemeral=True)
        else:
            await interaction.response.send_message("Du hast keine Berechtigung, Berechtigungen anzuzeigen.", ephemeral=True)

    # Slash-Befehl: unsetpermissions
    @app_commands.command(name="unsetpermissions", description="Entfernt Berechtigungen für eine Rolle oder einen Benutzer")
    async def unsetpermissions(self, interaction: discord.Interaction, role: discord.Role = None, user: discord.User = None, command_name: str = None):
        """Entfernt Berechtigungen für eine Rolle oder einen Benutzer."""
        
        if not role and not user:
            await interaction.response.send_message("Gebe Rolle oder User an, dem die Berechtigung entfernt werden soll.", ephemeral=True)
            return

        if role:
            unset_permissions(role.id, [command_name])  # Berechtigungen für die Rolle entfernen
            await interaction.response.send_message(f"Berechtigungen für die Rolle {role.name} wurden entfernt: {command_name}", ephemeral=True)
        elif user:
            unset_permissions(user.id, [command_name])  # Berechtigungen für den Benutzer entfernen
            await interaction.response.send_message(f"Berechtigungen für den Benutzer {user.name} wurden entfernt: {command_name}", ephemeral=True)

    # Slash-Befehl: resetpermissions
    @app_commands.command(name="resetpermissions", description="Setzt alle Berechtigungen einer Rolle oder eines Benutzers zurück")
    async def resetpermissions(self, interaction: discord.Interaction, role: discord.Role = None, user: discord.User = None):
        """Setzt alle Berechtigungen einer Rolle oder eines Benutzers zurück."""
        
        if not role and not user:
            await interaction.response.send_message("Gebe Rolle oder User an, dessen Berechtigungen zurückgesetzt werden sollen.", ephemeral=True)
            return

        if role:
            reset_permissions(role.id)  # Berechtigungen für die Rolle zurücksetzen
            await interaction.response.send_message(f"Alle Berechtigungen für die Rolle {role.name} wurden zurückgesetzt.", ephemeral=True)
        elif user:
            reset_permissions(user.id)  # Berechtigungen für den Benutzer zurücksetzen
            await interaction.response.send_message(f"Alle Berechtigungen für den Benutzer {user.name} wurden zurückgesetzt.", ephemeral=True)

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(Permissions(bot))  # Hier wird der Permissions-Cog dem Bot hinzugefügt
