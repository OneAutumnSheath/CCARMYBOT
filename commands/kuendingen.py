import discord
from discord.ext import commands
from discord import app_commands

# Beispielwerte für den persönlichen Kanal und Management-Rolle
PERSONAL_CHANNEL = 1097625981671448698
MGMT_ID = 1097648080020574260

class Kuendingen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_allowed(self, interaction):
        """Überprüft, ob der Benutzer berechtigt ist, den Befehl auszuführen."""
        if not check_permissions("personal", interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return Ture

    @app_commands.command(name="kuendigen", description="Erstellt eine Kündigung für einen Benutzer mit angegebenem Grund.")
    async def kuendigen(self, interaction: discord.Interaction, user: discord.Member, grund: str):
        if not await self.is_allowed(interaction):
            return

        # Der Nickname des Benutzers wird als String verwendet
        user_nickname = user.nick if user.nick else user.name  # Falls der Benutzer keinen Nicknamen hat, wird der Benutzername verwendet

        # Erstelle den Embed
        embed = discord.Embed(
            title="Kündigung",
            description=(
                f"╔══════════════════════════════════════════════╗\n\n"
                f"Hiermit tritt **{user_nickname}** aus der Army aus.\n\n"
                f"Grund: {grund}\n\n"
                f"Hochachtungsvoll,\n"
                f"<@&{MGMT_ID}>\n\n"
                f"╚══════════════════════════════════════════════╝"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="U.S. ARMY Human Resources")

        # Ankündigung im persönlichen Kanal
        channel = self.bot.get_channel(PERSONAL_CHANNEL)
        if not channel:
            await interaction.response.send_message("Der persönliche Kanal wurde nicht gefunden!", ephemeral=True)
            return

        await channel.send(embed=embed)

        # Benutzer kicken
        try:
            await user.kick(reason=f"Kündigung: {grund}")
        except discord.DiscordException as e:
            await interaction.response.send_message(f"Fehler beim Kicken des Benutzers: {e}", ephemeral=True)
            return

        # Bestätigung für den ausführenden Benutzer
        await interaction.response.send_message(f"{user_nickname} wurde erfolgreich gekündigt.", ephemeral=True)

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(Kuendingen(bot))  # Hier wird der HumanResources-Cog dem Bot hinzugefügt
