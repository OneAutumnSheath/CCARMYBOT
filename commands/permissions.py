import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import check_permissions, set_permissions, view_permissions  # Import aus der neuen Datei

class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="checkpermissions", description="Überprüft Berechtigungen für einen Befehl")
    async def checkpermissions(self, interaction: discord.Interaction, command_name: str):
        """Überprüft, ob der Benutzer berechtigt ist, einen Befehl auszuführen."""
        
        permission_node = f"checkpermissions.{command_name}"  # Beispiel-Node für Berechtigung
        if check_permissions(command_name, interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message(f"Du bist berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Du bist nicht berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)

    @app_commands.command(name="setpermissions", description="Setze Berechtigungen für eine Rolle")
    async def setpermissions(self, interaction: discord.Interaction, role: discord.Role, command_name: str):
        """Setzt Berechtigungen für eine Rolle."""
        
        permission_node = "setpermissions"  # Beispiel-Node für Berechtigung
        if check_permissions(command_name, interaction.user.id, [role.id for role in interaction.user.roles]):
            set_permissions(role.id, [command_name])  # Berechtigungen setzen
            await interaction.response.send_message(f"Berechtigungen für die Rolle {role.name} wurden gesetzt: {command_name}", ephemeral=True)
        else:
            await interaction.response.send_message("Du hast keine Berechtigung, Berechtigungen zu setzen.", ephemeral=True)

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

# Setup-Funktion, die den Cog dem Bot hinzufügt
async def setup(bot):
    await bot.add_cog(Permissions(bot))
