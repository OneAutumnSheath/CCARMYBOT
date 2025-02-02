import discord
from discord.ext import commands

# Beispielwert für den Log-Kanal (ersetze dies durch die tatsächliche Kanal-ID)
BOT_LOG_CHANNEL = 1097625981671448698  # Ersetze dies durch deine Log-Kanal-ID

class LogModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Variablen für Log-Channel-ID
BOT_LOG_CHANNEL = 1333208767059464243  # Beispielwert für den Bot-Log-Channel

# Event: Logs für ausgeführte Befehle
@bot.event
async def on_command_completion(ctx):
    # Hole den Log-Channel
    log_channel = bot.get_channel(BOT_LOG_CHANNEL)
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

    # Sende die Log-Nachricht
    await log_channel.send(embed=embed)

# Slash-Befehle loggen
@bot.event
async def on_app_command_completion(interaction, command):
    # Hole den Log-Channel
    log_channel = bot.get_channel(BOT_LOG_CHANNEL)
    if not log_channel:
        print(f"Bot-Log-Channel mit ID {BOT_LOG_CHANNEL} nicht gefunden.")
        return

    # Informationen über den Befehl und die Argumente sammeln
    user = interaction.user
    arguments = interaction.namespace  # Enthält die übergebenen Argumente

    # Erstelle die Log-Nachricht
    embed = discord.Embed(
        title="Slash-Befehlsausführung",
        description=(
            f"**Befehl:** `{command.qualified_name}`\n"
            f"**Ausgeführt von:** {user.mention} (`{user}`)\n"
            f"**Argumente:**\n" +
            "\n".join([f"`{key}`: `{value}`" for key, value in vars(arguments).items()]) +
            "\n"
        ),
        color=discord.Color.green()  # Farbcode: Grün für Slash-Befehle
    )
    embed.set_footer(text=f"Benutzer-ID: {user.id}")
    embed.timestamp = discord.utils.utcnow()

    # Sende die Log-Nachricht
    await log_channel.send(embed=embed)

# Die Setup-Funktion, um den Cog zu registrieren
async def setup(bot):
    await bot.add_cog(LogModule(bot))  # Hier wird der LogModule-Cog dem Bot hinzugefügt
