import discord
from discord.ext import commands

# Beispielwert für den Log-Kanal (ersetze dies durch die tatsächliche Kanal-ID)
BOT_LOG_CHANNEL = 1097625981671448698  # Ersetze dies durch deine Log-Kanal-ID

class LogModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Event: Logs für ausgeführte Befehle."""
        # Hole den Log-Channel
        log_channel = self.bot.get_channel(BOT_LOG_CHANNEL)
        if not log_channel:
            print(f"Log channel with ID {BOT_LOG_CHANNEL} not found.")
            return
        
        # Überprüfe, ob die Nachricht überhaupt erzeugt wird
        print(f"Logging command: {ctx.command.name} by {ctx.author}.")

        # Erstelle die Log-Nachricht
        embed = discord.Embed(
            title="Befehlsausführung",
            description=(
                f"**Befehl:** `{ctx.command.name}`\n"
                f"**Ausgeführt von:** {ctx.author.mention} (`{ctx.author}`)\n"
                f"**Argumente:**\n" +
                "\n".join([f"`{key}`: `{value}`" for key, value in ctx.kwargs.items()]) +
                "\n"
            ),
            color=discord.Color.blue()  # Farbcode: Blau für Logs
        )
        embed.set_footer(text=f"Benutzer-ID: {ctx.author.id}")
        embed.timestamp = discord.utils.utcnow()

        try:
            # Sende die Log-Nachricht
            await log_channel.send(embed=embed)
        except discord.DiscordException as e:
            print(f"Error sending log message: {e}")

# Die Setup-Funktion, um den Cog zu registrieren
async def setup(bot):
    await bot.add_cog(LogModule(bot))  # Hier wird der LogModule-Cog dem Bot hinzugefügt
