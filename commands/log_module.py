import discord
from discord.ext import commands

BOT_LOG_CHANNEL = 123456789012345678  # Setze hier die Log-Kanal-ID ein

class LogModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Event: Logs für ausgeführte Befehle."""
        # Hole den Log-Channel
        log_channel = self.bot.get_channel(BOT_LOG_CHANNEL)
        if not log_channel:
            print(f"Bot-Log-Channel mit ID {BOT_LOG_CHANNEL} nicht gefunden.")
            return

        # Informationen über den Befehl und die Argumente sammeln
        command_name = ctx.command.name if ctx.command else "Unbekannt"
        user = ctx.author
        arguments = ctx.kwargs  # Enthält die übergebenen Argumente

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
            print(f"Fehler beim Senden der Log-Nachricht: {e}")
