import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import check_permissions
# Beispielwert für den Sanktions-Kanal
SANKTION_CHANNEL = 1143288582136664225

class Sanktion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_allowed(self, interaction):
        """Überprüft, ob der Benutzer berechtigt ist, den Befehl auszuführen."""
        if not check_permissions("sanktion", interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return False  # Korrigiert von Ture auf False
        return True  # Sicherstellen, dass True zurückgegeben wird, wenn Berechtigung vorhanden ist.

    @app_commands.command(name="sanktion", description="Erstellt eine Sanktion für einen Benutzer und fügt optional Rollen hinzu.")
    async def sanktion(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        sanktionsmaß: str,
        grund: str,
        zusätzliche_rolle_1: discord.Role = None,
        zusätzliche_rolle_2: discord.Role = None
    ):
        if not await self.is_allowed(interaction):
            return

        # Erstelle den Embed
        embed = discord.Embed(
            title="Sanktion",
            description=(
                f"╔════════════════ Sanktion ═══════════════════╗\n\n"
                f"Hiermit erhält {user.mention} eine Sanktion:\n\n"
                f"Sanktionsmaß: {sanktionsmaß}\n\n"
                f"Grund: {grund}\n\n"
                f"<@&1289716541658497055>\n\n"
                f"<@&1097648080020574260>\n\n"
                f"╚═════════════════════════════════════════╝"
            ),
            color=discord.Color.orange()  # Farbcode: #FFA500
        )
        embed.set_footer(text="U.S. ARMY Management")

        # Sende die Nachricht im Sanktions-Kanal
        channel = self.bot.get_channel(SANKTION_CHANNEL)
        if not channel:
            await interaction.response.send_message("Der Sanktions-Kanal wurde nicht gefunden!", ephemeral=True)
            return

        await channel.send(embed=embed)

        # Rollen hinzufügen
        roles_to_add = []
        if zusätzliche_rolle_1:
            roles_to_add.append(zusätzliche_rolle_1)
        if zusätzliche_rolle_2:
            roles_to_add.append(zusätzliche_rolle_2)

        try:
            if roles_to_add:
                await user.add_roles(*roles_to_add, reason=f"Sanktion: {sanktionsmaß} - Grund: {grund}")
        except discord.DiscordException as e:
            await interaction.response.send_message(f"Fehler beim Hinzufügen der Rollen: {e}", ephemeral=True)
            return

        # Bestätigungsnachricht für den Ausführenden
        await interaction.response.send_message(
            f"Sanktion für {user.mention} wurde erfolgreich erstellt und im entsprechenden Kanal angekündigt.\n"
            f"Zusätzliche Rollen wurden {'hinzugefügt' if roles_to_add else 'nicht hinzugefügt'}.",
            ephemeral=True
        )

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(Sanktion(bot))  # Hier wird der Sanktion-Cog dem Bot hinzugefügt
