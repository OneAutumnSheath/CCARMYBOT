import discord
from discord.ext import commands
from discord import app_commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ready", description="Überprüft, ob der Bot bereit ist.")
    async def ready(self, interaction: discord.Interaction):
        """Zeigt an, ob der Bot bereit ist."""
        
        # Antwort, die bestätigt, dass der Bot bereit ist
        await interaction.response.send_message(f"Bot ist bereit! Eingeloggt als {self.bot.user} (ID: {self.bot.user.id})", ephemeral=True)

# Setup-Funktion, die den Cog dem Bot hinzufügt
async def setup(bot):
    await bot.add_cog(General(bot))
