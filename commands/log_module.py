import discord
from discord.ext import commands

# Beispielwert für den Log-Kanal (ersetze dies durch die tatsächliche Kanal-ID)
BOT_LOG_CHANNEL = 1097625981671448698  # Ersetze dies durch deine Log-Kanal-ID

class LogModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Speichern der Bot-Instanz, um sie im gesamten Cog zu verwenden

    @commands.Cog.listener()
    async def on_command_completion(self, interaction):
        """Event: Loggt ausgeführte Slash-Befehle."""
        log_channel = self.bot.get_channel(BOT_LOG_CHANNEL)
        if not log_channel:
            print(f"Log channel with ID {BOT_LOG_CHANNEL} not found.")
            return

        # Informationen über den Befehl und die Argumente sammeln
        command_name = interaction.command.name if interaction.command else "Unbekannt"
        user = interaction.user
        arguments = interaction.data.get('options', [])

        # Argumente extrahieren und formatieren
        arguments_text = ""
        for arg in arguments:
            name = arg['name']
            value = arg['value']
            arguments_text += f"**{name}**: `{value}`\n"

        # Erstelle die Log-Nachricht
        embed = discord.Embed(
            title="Slash-Befehlsausführung",
            description=(
                f"**Befehl:** `{command_name}`\n"
                f"**Ausgeführt von:** {user.mention} (`{user}`)\n"
                f"**Argumente:**\n{arguments_text}"
            ),
            color=discord.Color.blue()  # Farbcode: Blau für Logs
        )
        embed.set_footer(text=f"Benutzer-ID: {user.id}")
        embed.timestamp = discord.utils.utcnow()

        try:
            # Sende die Log-Nachricht
            await log_channel.send(embed=embed)
        except discord.DiscordException as e:
            print(f"Error sending log message: {e}")

# Die Setup-Funktion, um den Cog zu registrieren
async def setup(bot):
    await bot.add_cog(LogModule(bot))  # Hier wird der LogModule-Cog dem Bot hinzugefügt
