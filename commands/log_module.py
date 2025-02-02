import discord
from discord.ext import commands

# Beispielwert für den Log-Kanal (ersetze dies durch die tatsächliche Kanal-ID)
BOT_LOG_CHANNEL = 1333208767059464243  # Ersetze dies durch deine Log-Kanal-ID

class LogModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Speichern der Bot-Instanz, um sie im gesamten Cog zu verwenden

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Event: Loggt ausgeführte Befehle."""
        log_channel = self.bot.get_channel(BOT_LOG_CHANNEL)
        if not log_channel:
            print(f"Log channel with ID {BOT_LOG_CHANNEL} not found.")
            return

        # Informationen über den Befehl und die Argumente sammeln
        command_name = ctx.command.name if ctx.command else "Unbekannt"
        
        # Verwende `interaction.user` statt `ctx.author`
        user = ctx.user if hasattr(ctx, 'user') else ctx.author  # Absicherung für Interaktionen vs. normale Befehle
        arguments = ctx.kwargs if hasattr(ctx, 'kwargs') else {}  # Argumente aus Interaktion

        # Erstelle die Log-Nachricht
        embed = discord.Embed(
            title="Befehlsausführung",
            description=(
                f"**Befehl:** `{command_name}`\n"
                f"**Ausgeführt von:** {user.mention} (`{user}`)\n"
                f"**Argumente:**\n" +
                "\n".join([f"`{key}`: `{value}`" for key, value in arguments.items()]) +
                "\n"
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
