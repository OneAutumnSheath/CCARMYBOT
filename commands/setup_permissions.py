import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import set_permissions, check_permissions, view_permissions  # Import aus der neuen Datei


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

    #@app_commands.command(name="setpermissions", description="Setze Berechtigungen für eine Rolle")
    #async def setpermissions(self, interaction: discord.Interaction, role: discord.Role, command_name: str):
     #   """Setzt Berechtigungen für eine Rolle."""
        
        # Berechtigungen setzen
      #ä  set_permissions(role.id, [command_name], is_user=False)

        #await interaction.response.send_message(f"Berechtigungen für die Rolle {role.name} wurden gesetzt: {command_name}", ephemeral=True)
    @app_commands.command(name="checkpermissions", description="Überprüft Berechtigungen für einen Befehl")
    async def checkpermissions(self, interaction: discord.Interaction, command_name: str):
        """Überprüft, ob der Benutzer berechtigt ist, einen Befehl auszuführen."""

        # Überprüfe Berechtigungen
        if check_permissions(command_name, interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message(f"Du bist berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Du bist nicht berechtigt, den Befehl '{command_name}' auszuführen.", ephemeral=True)

# Setup-Funktion, die den Cog dem Bot hinzufügt
async def setup(bot):
    await bot.add_cog(SetupPermissions(bot))  # Hier wird der Permissions-Cog dem Bot hinzugefügt