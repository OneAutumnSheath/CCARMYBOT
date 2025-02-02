import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import check_permissions, set_permissions, view_permissions, unset_permissions, reset_permissions  # Import aus der neuen Datei

class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash-Befehl: viewpermissions
    @app_commands.command(name="viewpermissions", description="Zeigt Berechtigungen für einen Benutzer oder eine Rolle")
    async def viewpermissions(self, interaction, user: discord.User = None, role: discord.Role = None):
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
    async def unsetpermissions(self, interaction, role: discord.Role = None, user: discord.User = None, command_name: str = None):
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
    async def resetpermissions(self, interaction, role: discord.Role = None, user: discord.User = None):
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
