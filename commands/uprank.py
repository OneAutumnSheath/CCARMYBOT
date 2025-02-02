import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import check_permissions
# Beispielwerte für den persönlichen Kanal und Management-Rolle
PERSONAL_CHANNEL = 1097625981671448698
MGMT_ID = 1097648080020574260

class Uprank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_allowed(self, interaction):
        """Überprüft, ob der Benutzer berechtigt ist, den Befehl auszuführen."""
        if not check_permissions("personal", interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return False  # Korrigiert von Ture auf False
        return True  # Sicherstellen, dass True zurückgegeben wird, wenn Berechtigung vorhanden ist.

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
            await personal_channel.send(embed=embed)
        else:
            await interaction.response.send_message("Der Personal-Kanal wurde nicht gefunden!", ephemeral=True)
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
            f"{user.mention} wurde erfolgreich vom Rang {alter_rang.mention} zum Rang {neuer_rang.mention} befördert.",
            ephemeral=True
        )

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(Uprank(bot))  # Hier wird der Uprank-Cog dem Bot hinzugefügt
