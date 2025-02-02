import discord
from discord.ext import commands
from commands.log_module import LogModule  # Importiere das Log-Modul
from discord import app_commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_module = LogModule(bot)  # Initialisiere das Log-Modul innerhalb des Cogs

    @app_commands.command(name="ready", description="Überprüft, ob der Bot bereit ist.")
    async def ready(self, interaction: discord.Interaction):
        """Zeigt an, ob der Bot bereit ist."""
        
        # Bestätige die Interaktion vorab, um sicherzustellen, dass sie gültig bleibt
        await interaction.response.defer(ephemeral=True)

        # Logge den Befehl, wenn er ausgeführt wird
        await self.log_module.on_command_completion(interaction)  # Protokolliere den Befehl

        # Antwort, die bestätigt, dass der Bot bereit ist
        await interaction.followup.send(f"Bot ist bereit! Eingeloggt als {self.bot.user} (ID: {self.bot.user.id})", ephemeral=True)

# Setup-Funktion, die den Cog dem Bot hinzufügt
async def setup(bot):
    await bot.add_cog(General(bot))  # Hier wird der General-Cog dem Bot hinzugefügt
