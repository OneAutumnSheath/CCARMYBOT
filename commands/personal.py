import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import check_permissions  # Berechtigungsprüfung

# Berechtigungsprüfung für den Befehl
async def is_allowed(interaction: discord.Interaction):
    permission_node = "personal"  # Berechtigungs-Node für den Personal-Befehl
    if check_permissions(permission_node, interaction.user.id, [role.id for role in interaction.user.roles]):
        return True
    await interaction.response.send_message(f"Du hast keine Berechtigung, diesem Befehl auszuführen.", ephemeral=True)
    return False

# Cog-Klasse für Personal-Operationen
class Personal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Hier können später die Personal-Befehle hinzugefügt werden.

# Setup-Funktion, die den Cog dem Bot hinzufügt
async def setup(bot):
    await bot.add_cog(Personal(bot))
