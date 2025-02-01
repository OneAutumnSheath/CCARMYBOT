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
@bot.tree.command(name="einstellen", description="Stellt einen neuen Rekruten ein und fügt die entsprechenden Rollen hinzu.")
    async def einstellen(self, interaction: discord.Interaction, user: discord.Member, name: str, dn: str, dienstgrad: discord.Role, division: discord.Role, grund: str):
        "Stellt einen neuen Rekruten ein und fügt die entsprechenden Rollen hinzu."

        if not check_permissions("personal", interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        
        # Feste Rollen
        MAIN_UNIT_ROLE_ID = 1134170231275782154
        INFANTRY_ROLE_ID = 1187756956425920645
        ARMY_ROLE_ID = 1097625926243733536
        
        # Abrufen der festen Rollen
        main_unit_role = interaction.guild.get_role(MAIN_UNIT_ROLE_ID)
        infantry_role = interaction.guild.get_role(INFANTRY_ROLE_ID)
        army_role = interaction.guild.get_role(ARMY_ROLE_ID)
        
        # Benutzer umbenennen
        new_nickname = f"[USA-{dn}] {name}"
        try:
            await user.edit(nick=new_nickname, reason="Einstellung in die Army")
        except discord.Forbidden:
            await interaction.response.send_message(f"Der Benutzer konnte nicht umbenannt werden. Möglicherweise fehlen mir die Berechtigungen.", ephemeral=True)
            return
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Fehler beim Umbenennen: {e}", ephemeral=True)
            return
        
        # Erstelle den Embed
        embed = discord.Embed(
            title="Neueinstellung",
            description=(
                f"╔══════════════════════════════════════════════╗\n\n"
                f"Hiermit tritt {user.mention} der Army als {dienstgrad.mention} bei.\n\n"
                f"Grund: {grund}\n\n"
                f"Hochachtungsvoll,\n"
                f"<@&{MGMT_ID}>\n\n"
                f"╚══════════════════════════════════════════════╝"
            ),
            color=discord.Color.green()  # Farbcode: #00FF00
        )
        embed.set_footer(text="U.S. ARMY Management")

        # Sende die Ankündigung im festgelegten Kanal
        channel = self.bot.get_channel(PERSONAL_CHANNEL)
        if not channel:
            await interaction.response.send_message("Der Personal-Kanal wurde nicht gefunden!", ephemeral=True)
            return
        await channel.send(embed=embed)

        # Rollen hinzufügen
        try:
            roles_to_add = [dienstgrad, division, main_unit_role, infantry_role, army_role]
            for role in roles_to_add:
                if role:
                    await user.add_roles(role, reason=f"Einstellung: {grund}")
        except discord.DiscordException as e:
            await interaction.response.send_message(f"Fehler beim Hinzufügen der Rollen: {e}", ephemeral=True)
            return

        # Bestätigungsnachricht für den Ausführenden
        await interaction.response.send_message(
            f"{user.mention} wurde erfolgreich als {dienstgrad.mention} eingestellt, hat die entsprechenden Rollen erhalten und wurde umbenannt zu `{new_nickname}`.",
            ephemeral=True
        )

    # Slash-Befehl: uprank
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
        """Befördert einen Benutzer und ändert ggf. seine Division und Dienstnummer."""
        
        # Berechtigungsprüfung
        if not check_permissions("personal", interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
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
