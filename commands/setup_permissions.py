import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import set_permissions, check_permissions  # Import aus der neuen Datei


class SetupPermissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Erstellt die Berechtigungsdatei und setzt den Admin.")
    async def setup(self, interaction: discord.Interaction):
        """Erstellt die Berechtigungsdatei und setzt den Benutzer als Admin."""
        
        # Setze den Benutzer, der das Setup ausführt, als Admin
        set_permissions(interaction.user.id, ["*"], is_user=True)

        # Bestätigungsnachricht
        await interaction.response.send_message(f"{interaction.user.mention}, du wurdest als Admin gesetzt und alle Befehle stehen dir zur Verfügung.", ephemeral=True)

    @app_commands.command(name="setpermissions", description="Setze Berechtigungen für einen Benutzer oder eine Rolle")
    async def setpermissions(self, interaction: discord.Interaction, role: discord.Role = None, user: discord.User = None, command_name: str = None):
        """Setzt Berechtigungen für eine Rolle oder einen Benutzer."""
        
        if not role and not user:
            await interaction.response.send_message("Bitte gib entweder einen Benutzer oder eine Rolle an, um die Berechtigungen zu setzen.", ephemeral=True)
            return
        
        if role:
            # Berechtigungen für eine Rolle setzen
            set_permissions(role.id, [command_name], is_user=False)
            await interaction.response.send_message(f"Berechtigungen für die Rolle {role.name} wurden gesetzt: {command_name}", ephemeral=True)
        elif user:
            # Berechtigungen für einen Benutzer setzen
            set_permissions(user.id, [command_name], is_user=True)
            await interaction.response.send_message(f"Berechtigungen für den Benutzer {user.name} wurden gesetzt: {command_name}", ephemeral=True)

    @app_commands.command(name="checkpermissions", description="Überprüft Berechtigungen für einen Benutzer oder eine Rolle")
    async def checkpermissions(self, interaction: discord.Interaction, role: discord.Role = None, user: discord.User = None, command_name: str = None):
        """Überprüft, ob der Benutzer berechtigt ist, einen Befehl auszuführen."""
        
        if not role and not user:
            await interaction.response.send_message("Bitte gib entweder einen Benutzer oder eine Rolle an, um die Berechtigungen zu überprüfen.", ephemeral=True)
            return
        
        if role:
            # Überprüfe Berechtigungen für die Rolle
            if check_permissions(command_name, interaction.user.id, [role.id for role in interaction.user.roles]):
                await interaction.response.send_message(f"Die Rolle {role.name} ist berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Die Rolle {role.name} hat keine Berechtigung, den Befehl '{command_name}' auszuführen.", ephemeral=True)
        elif user:
            # Überprüfe Berechtigungen für den Benutzer
            if check_permissions(command_name, interaction.user.id, [role.id for role in interaction.user.roles]):
                await interaction.response.send_message(f"Der Benutzer {user.name} ist berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Der Benutzer {user.name} hat keine Berechtigung, den Befehl '{command_name}' auszuführen.", ephemeral=True)


# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(SetupPermissions(bot))  # Hier wird der SetupPermissions-Cog dem Bot hinzugefügt
