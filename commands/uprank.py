import discord
from discord.ext import commands
from discord import app_commands
from commands.log_module import LogModule
from commands.permissions_logic import check_permissions  # Importiere die check_permissions-Funktion

# Definiere PERSONAL_CHANNEL direkt im Cog
PERSONAL_CHANNEL = 1097625981671448698  # Ersetze dies mit der tatsächlichen Kanal-ID
MGMT_ID = 1097648080020574260  # Beispielwert für die Management-Rolle

class Uprank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_module = LogModule(bot)

    async def is_allowed(self, interaction):
        """Überprüft, ob der Benutzer berechtigt ist, den Befehl auszuführen."""
        if not check_permissions("personal", interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return False  # Wenn keine Berechtigung, gebe False zurück
        return True  # Wenn Berechtigung vorhanden, gebe True zurück

    @app_commands.command(name="uprank", description="Erhöht den Rang eines Benutzers und fügt neue Division und/oder Dienstnummer hinzu.")
    async def uprank(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        alter_rang: discord.Role,
        neuer_rang: discord.Role,
        grund: str,
        alte_division: discord.Role = None,
        neue_division: discord.Role = None,
        alte_dn: str = None,
        neue_dn: str = None,
        name: str = None  # Optional, Name des Benutzers, wenn geändert werden soll
    ):
        if not await self.is_allowed(interaction):
            return

        # Bestätige die Interaktion vorab, um die Interaktion gültig zu halten
        await interaction.response.defer(ephemeral=True)

        # Erstelle den Embed für die Ankündigung
        if neue_division:  # Wenn neue Division angegeben wurde
            embed = discord.Embed(
                title="Beförderung",
                description=(
                    f"╔══════════════════════════════════════════════╗\n\n"
                    f"Hiermit bekleidet {user.mention} den Dienstgrad eines {neuer_rang.mention}.\n\n"
                    f"Grund: {grund}\n\n"
                    f"Alte DN: {alte_dn}\n"
                    f"Neue DN: {neue_dn}\n\n"
                    f"Hochachtungsvoll,\n"
                    f"<@&{MGMT_ID}>\n\n"
                    f"╚══════════════════════════════════════════════╝"
                ),
                color=discord.Color.blue()  # Blau für Rang-Aufstieg
            )
        else:  # Wenn keine neue Division angegeben wurde
            embed = discord.Embed(
                title="Beförderung",
                description=(
                    f"╔══════════════════════════════════════════════╗\n\n"
                    f"Hiermit bekleidet {user.mention} nun den Posten als {neuer_rang.mention}.\n\n"
                    f"Grund: {grund}\n\n"
                    f"Hochachtungsvoll,\n"
                    f"<@&{MGMT_ID}>\n\n"
                    f"╚══════════════════════════════════════════════╝"
                ),
                color=discord.Color.blue()  # Blau für Rang-Aufstieg
            )

        embed.set_footer(text="U.S. ARMY Management")

        # Sende die Ankündigung nur im Personal-Kanal
        personal_channel = self.bot.get_channel(PERSONAL_CHANNEL)
        if personal_channel:
            await personal_channel.send(f"{user.mention}")
            await personal_channel.send(embed=embed)
        else:
            await interaction.followup.send("Der Personal-Kanal wurde nicht gefunden!", ephemeral=True)
            return

        # Rollen aktualisieren
        try:
            # Alte Rolle entfernen und neue Rolle hinzufügen
            await user.remove_roles(alter_rang, reason=f"Rang Aufstieg: {grund}")
            await user.add_roles(neuer_rang, reason=f"Rang Aufstieg: {grund}")

            # Optionale Divisionen bearbeiten
            if alte_division:
                await user.remove_roles(alte_division, reason=f"Division geändert: {grund}")
            if neue_division:
                await user.add_roles(neue_division, reason=f"Division geändert: {grund}")

            # Wenn eine neue DN angegeben wurde, den Benutzer umbenennen
            if neue_dn:
                new_nickname = f"[USA-{neue_dn}] {user.display_name}"  # Neue Nickname-Formatierung
                if name:
                    new_nickname = f"[USA-{neue_dn}] {name}"  # Falls Name angegeben, diesen verwenden
                try:
                    await user.edit(nick=new_nickname, reason=f"Neue Dienstnummer: {neue_dn}")
                except discord.Forbidden:
                    await interaction.followup.send(
                        f"Der Benutzer konnte nicht umbenannt werden. Möglicherweise fehlen mir die Berechtigungen.", ephemeral=True
                    )
                    return
                except discord.HTTPException as e:
                    await interaction.followup.send(f"Fehler beim Umbenennen: {e}", ephemeral=True)
                    return
        except discord.DiscordException as e:
            await interaction.followup.send(f"Fehler beim Aktualisieren der Rollen: {e}", ephemeral=True)
            return

        # Logge den Befehl
        await self.log_module.on_command_completion(interaction)

        # Bestätigung für den ausführenden Benutzer
        await interaction.followup.send(
            f"{user.mention} wurde erfolgreich vom Rang {alter_rang.mention} zum Rang {neuer_rang.mention} befördert.",
            ephemeral=True
        )

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(Uprank(bot))  # Hier wird der Uprank-Cog dem Bot hinzugefügt
