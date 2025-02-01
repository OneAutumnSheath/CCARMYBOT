import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import check_permissions  # Importiere die Berechtigungslogik

PERSONAL_CHANNEL = 1097625981671448698  # Kanal-ID, in dem die Ankündigung gemacht wird
MGMT_ID = 1097648080020574260  # Management ID für Ankündigungen

class Personal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash-Befehl: einstellen

    # Slash-Befehl: derank
    @app_commands.command(name="derank", description="Senkt den Rang eines Benutzers und ändert ggf. Division/Dienstnummer.")
    async def derank(
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
        """Senkt den Rang eines Benutzers und ändert ggf. Division/Dienstnummer."""
        
        # Berechtigungsprüfung
        if not check_permissions("personal", interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return

        # Erstelle den Embed für die Ankündigung
        if neue_division:  # Wenn neue Division angegeben wurde
            embed = discord.Embed(
                title="Rang Abstieg",
                description=(
                    f"╔══════════════════════════════════════════════╗\n\n"
                    f"Hiermit bekleidet {user.mention} nun den Dienstgrad eines {neuer_rang.mention}.\n\n"
                    f"Grund: {grund}\n\n"
                    f"Alte DN: {alte_dn}\n"
                    f"Neue DN: {neue_dn}\n\n"
                    f"Hochachtungsvoll,\n"
                    f"<@&{MGMT_ID}>\n\n"
                    f"╚══════════════════════════════════════════════╝"
                ),
                color=discord.Color.blue()  # Blau für Rang-Abstieg
            )
        else:  # Wenn keine neue Division angegeben wurde
            embed = discord.Embed(
                title="Rang Abstieg",
                description=(
                    f"╔══════════════════════════════════════════════╗\n\n"
                    f"Hiermit bekleidet {user.mention} nun den Posten als {neuer_rang.mention}.\n\n"
                    f"Grund: {grund}\n\n"
                    f"Hochachtungsvoll,\n"
                    f"<@&{MGMT_ID}>\n\n"
                    f"╚══════════════════════════════════════════════╝"
                ),
                color=discord.Color.blue()  # Blau für Rang-Abstieg
            )

        embed.set_footer(text="U.S. ARMY Management")

        # Sende die Ankündigung nur im Personal-Kanal
        personal_channel = self.bot.get_channel(PERSONAL_CHANNEL)
        if personal_channel:
            await personal_channel.send(embed=embed)
        else:
            await interaction.response.send_message("Der Personal-Kanal wurde nicht gefunden!", ephemeral=True)
            return

        # Rollen aktualisieren
        try:
            # Alte Rolle entfernen und neue Rolle hinzufügen
            await user.remove_roles(alter_rang, reason=f"Rang Abstieg: {grund}")
            await user.add_roles(neuer_rang, reason=f"Rang Abstieg: {grund}")

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
                    await interaction.response.send_message(
                        f"Der Benutzer konnte nicht umbenannt werden. Möglicherweise fehlen mir die Berechtigungen.", ephemeral=True
                    )
                    return
                except discord.HTTPException as e:
                    await interaction.response.send_message(f"Fehler beim Umbenennen: {e}", ephemeral=True)
                    return
        except discord.DiscordException as e:
            await interaction.response.send_message(f"Fehler beim Aktualisieren der Rollen: {e}", ephemeral=True)
            return

        # Bestätigung für den ausführenden Benutzer
        await interaction.response.send_message(
            f"{user.mention} wurde erfolgreich vom Rang {alter_rang.mention} zum Rang {neuer_rang.mention} herabgestuft.",
            ephemeral=True
        )

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(Personal(bot))  # Hier wird der Personal-Cog dem Bot hinzugefügt
