import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Bot-Setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Variablen für Channel und Rollen-IDs
PERSONAL_CHANNEL = 1097625981671448698  # Beispielwert für den persönlichen Kanal
UNIT_CHANNEL = 1173700352403591189  # Beispielwert für den Unit-Kanal
SANKTION_CHANNEL = 1143288582136664225  # Beispielwert für den Sanktion-Kanal
MGMT_ID = 1097648080020574260  # Beispielwert für Management-Rolle

# Event: Bot ist bereit
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()  # Synchronisiert alle Befehle global
        print("Globale Slash-Befehle erfolgreich synchronisiert!")
    except Exception as e:
        print(f"Fehler bei der globalen Synchronisierung: {e}")
    print(f"Bot ist bereit! Eingeloggt als {bot.user} (ID: {bot.user.id})")

# Neue Berechtigungsprüfung
ALLOWED_ROLE_IDS = {1097648080020574260, 1196072112977358968}  # Rollen-IDs

async def is_allowed(interaction: discord.Interaction) -> bool:
    user_roles = [role.id for role in interaction.user.roles]
    if any(role_id in ALLOWED_ROLE_IDS for role_id in user_roles):
        return True

    await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
    return False


# Slash-Befehl: unit-eintritt
@bot.tree.command(name="unit-eintritt", description="Lässt einen Benutzer einer Unit beitreten.")
async def unit_eintritt(
    interaction: discord.Interaction,
    user: discord.Member,
    unit: discord.Role,
    grund: str,
    zusätzliche_rolle_1: discord.Role = None,
    zusätzliche_rolle_2: discord.Role = None,
    zusatz: str = None  # Neuer optionaler Parameter
):
    if not await is_allowed(interaction):
        return

    # Zusatztext in der Nachricht vorbereiten
    zusatz_text = f"\n\nZusatz: {zusatz}" if zusatz else ""

    # Erstelle den Embed
    embed = discord.Embed(
        title="Unit Eintritt",
        description=(
            f"╔══════════════════════════════════════════════╗\n\n"
            f"Hiermit tritt {user.mention} der Unit {unit.mention} bei.\n\n"
            f"Grund: {grund}{zusatz_text}\n\n"  # Zusatztext wird hier hinzugefügt, wenn vorhanden
            f"Hochachtungsvoll,\n"
            f"<@&{MGMT_ID}>\n\n"
            f"╚══════════════════════════════════════════════╝"
        ),
        color=discord.Color.green()  # Farbcode: #00FF00
    )
    embed.set_footer(text="U.S. ARMY Management")

    # Rollen hinzufügen
    try:
        roles_to_add = [unit]
        if zusätzliche_rolle_1:
            roles_to_add.append(zusätzliche_rolle_1)
        if zusätzliche_rolle_2:
            roles_to_add.append(zusätzliche_rolle_2)

        await user.add_roles(*roles_to_add, reason=f"Unit Eintritt: {grund}")
    except discord.DiscordException as e:
        await interaction.response.send_message(f"Fehler beim Hinzufügen der Rollen: {e}", ephemeral=True)
        return

    # Sende die Nachricht in den festgelegten Kanal
    channel = bot.get_channel(UNIT_CHANNEL)
    await channel.send(embed=embed)

    # Bestätigung für den ausführenden Benutzer
    await interaction.response.send_message(f"{user.mention} wurde erfolgreich der Unit {unit.mention} zugefügt.", ephemeral=True)

# Slash-Befehl: unit-austritt
@bot.tree.command(name="unit-austritt", description="Lässt einen Benutzer aus einer Unit austreten und entfernt angegebene Rollen.")
async def unit_austritt(
    interaction: discord.Interaction,
    user: discord.Member,
    unit: discord.Role,
    grund: str,
    zu_entfernende_rolle_1: discord.Role = None,
    zu_entfernende_rolle_2: discord.Role = None
):
    if not await is_allowed(interaction):
        return

    # Erstelle den Embed
    embed = discord.Embed(
        title="Unit Austritt",
        description=(
            f"╔══════════════════════════════════════════════╗\n\n"
            f"Hiermit tritt {user.mention} aus der Unit {unit.mention} aus.\n\n"
            f"Grund: {grund}\n\n"
            f"Hochachtungsvoll,\n"
            f"<@&{MGMT_ID}>\n\n"
            f"╚══════════════════════════════════════════════╝"
        ),
        color=discord.Color.red()  # Farbcode: #FF0000
    )
    embed.set_footer(text="U.S. ARMY Management")

    # Sende die Nachricht in den festgelegten Kanal
    channel = bot.get_channel(UNIT_CHANNEL)
    await channel.send(embed=embed)

    # Rollen entfernen
    try:
        roles_to_remove = [unit]
        if zu_entfernende_rolle_1:
            roles_to_remove.append(zu_entfernende_rolle_1)
        if zu_entfernende_rolle_2:
            roles_to_remove.append(zu_entfernende_rolle_2)

        await user.remove_roles(*roles_to_remove, reason=f"Unit Austritt: {grund}")
    except discord.DiscordException as e:
        await interaction.response.send_message(f"Fehler beim Entfernen der Rollen: {e}", ephemeral=True)
        return

    # Bestätigung für den ausführenden Benutzer
    await interaction.response.send_message(
        f"{user.mention} wurde erfolgreich aus der Unit {unit.mention} entfernt, und die angegebenen Rollen wurden ebenfalls entfernt.",
        ephemeral=True
    )

@bot.tree.command(name="kuendigen", description="Erstellt eine Kündigung für einen Benutzer mit angegebenem Grund.")
async def kuendigen(interaction: discord.Interaction, user: discord.Member, grund: str):
    if not await is_allowed(interaction):
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
    channel = bot.get_channel(PERSONAL_CHANNEL)
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

@bot.tree.command(name="unit-aufstieg", description="Lässt einen Benutzer zu einer höheren Unit aufsteigen.")
async def unit_aufstieg(
    interaction: discord.Interaction,
    user: discord.Member,
    unit: discord.Role,
    grund: str,
    neuerposten: discord.Role = None,  # Neue Variable für den Posten als Rolle
    entfernte_rolle: discord.Role = None,
    zusätzliche_rolle: discord.Role = None
):
    if not await is_allowed(interaction):
        return

    # Erstelle den Embed für die Ankündigung
    if neuerposten:  # Wenn neuer Posten als Rolle angegeben wurde
        embed = discord.Embed(
            title="Unit Aufstieg",
            description=(
                f"╔══════════════════════════════════════════════╗\n\n"
                f"Hiermit steigt {user.mention} in der Unit {unit.mention} zum {neuerposten.mention} auf.\n\n"
                f"Grund: {grund}\n\n"
                f"Hochachtungsvoll,\n"
                f"<@&{MGMT_ID}>\n\n"
                f"╚══════════════════════════════════════════════╝"
            ),
            color=discord.Color.blue()  # Blau für Aufstieg
        )
    else:  # Wenn kein neuer Posten angegeben wurde
        embed = discord.Embed(
            title="Unit Aufstieg",
            description=(
                f"╔══════════════════════════════════════════════╗\n\n"
                f"Hiermit steigt {user.mention} zum Vollwertigen {unit.mention} Mitglied auf.\n\n"
                f"Grund: {grund}\n\n"
                f"Hochachtungsvoll,\n"
                f"<@&{MGMT_ID}>\n\n"
                f"╚══════════════════════════════════════════════╝"
            ),
            color=discord.Color.blue()  # Blau für Aufstieg
        )

    embed.set_footer(text="U.S. ARMY Management")

    # Sende die Nachricht in den festgelegten Kanal (Unit-Kanal)
    channel = bot.get_channel(UNIT_CHANNEL)
    if not channel:
        await interaction.response.send_message("Der Unit-Kanal wurde nicht gefunden!", ephemeral=True)
        return
    await channel.send(embed=embed)

    # Rolle hinzufügen, optionale Rolle hinzufügen und alte Rolle entfernen
    try:
        await user.add_roles(unit, reason=f"Unit Aufstieg: {grund}")
        
        # Neuer Posten als Rolle hinzufügen, falls angegeben
        if neuerposten:
            await user.add_roles(neuerposten, reason=f"Unit Aufstieg: {grund}")

        # Zusätzliche Rolle hinzufügen, falls angegeben
        if zusätzliche_rolle:
            await user.add_roles(zusätzliche_rolle, reason=f"Zusätzliche Rolle beim Unit Aufstieg: {grund}")
        
        # Alte Rolle entfernen, falls angegeben
        if entfernte_rolle:
            await user.remove_roles(entfernte_rolle, reason=f"Entfernung alter Rolle beim Unit Aufstieg: {grund}")
    except discord.DiscordException as e:
        await interaction.response.send_message(f"Fehler beim Bearbeiten der Rollen: {e}", ephemeral=True)
        return

    # Bestätigung für den ausführenden Benutzer
    await interaction.response.send_message(
        f"{user.mention} wurde erfolgreich zum Vollwertigen Mitglied der Unit {unit.mention} befördert. "
        f"Zusätzliche Rolle: {zusätzliche_rolle.mention if zusätzliche_rolle else 'Keine angegeben'}.",
        ephemeral=True
    )



# Slash-Befehl: einstellen
@bot.tree.command(name="einstellen", description="Stellt einen neuen Rekruten ein und fügt die entsprechenden Rollen hinzu.")
async def einstellen(
    interaction: discord.Interaction,
    user: discord.Member,
    name: str,
    dn: str,
    dienstgrad: discord.Role,
    division: discord.Role,
    grund: str
):
    if not await is_allowed(interaction):
        return

    # ID der festen Rollen
    MAIN_UNIT_ROLE_ID = 1134170231275782154
    INFANTRY_ROLE_ID = 1187756956425920645
    ARMY_ROLE_ID = 1097625926243733536

    # Feste Rollen basierend auf IDs abrufen
    main_unit_role = interaction.guild.get_role(MAIN_UNIT_ROLE_ID)
    infantry_role = interaction.guild.get_role(INFANTRY_ROLE_ID)
    army_role = interaction.guild.get_role(ARMY_ROLE_ID)

    # Benutzer umbenennen
    new_nickname = f"[USA-{dn}] {name}"
    try:
        await user.edit(nick=new_nickname, reason="Einstellung in die Army")
    except discord.Forbidden:
        await interaction.response.send_message(
            f"Der Benutzer konnte nicht umbenannt werden. Möglicherweise fehlen mir die Berechtigungen.", ephemeral=True
        )
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
    channel = bot.get_channel(PERSONAL_CHANNEL)
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
@bot.tree.command(name="uprank", description="Erhöht den Rang eines Benutzers und fügt neue Division und/oder Dienstnummer hinzu.")
async def uprank(
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
    if not await is_allowed(interaction):
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
    personal_channel = bot.get_channel(PERSONAL_CHANNEL)
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
@bot.tree.command(name="derank", description="Senkt den Rang eines Benutzers und ändert ggf. Division/Dienstnummer.")
async def derank(
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
    if not await is_allowed(interaction):
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
    personal_channel = bot.get_channel(PERSONAL_CHANNEL)
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
# Slash-Befehl: sanktion
@bot.tree.command(name="sanktion", description="Erstellt eine Sanktion für einen Benutzer und fügt optional Rollen hinzu.")
async def sanktion(
    interaction: discord.Interaction,
    user: discord.Member,
    sanktionsmaß: str,
    grund: str,
    zusätzliche_rolle_1: discord.Role = None,
    zusätzliche_rolle_2: discord.Role = None
):
    if not await is_allowed(interaction):
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
    channel = bot.get_channel(SANKTION_CHANNEL)
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
@bot.tree.command(name="unit-abstieg", description="Degradiert einen Benutzer innerhalb einer Unit von einem Posten und entfernt den alten Posten.")
async def unit_abstieg(
    interaction: discord.Interaction,
    user: discord.Member,
    unit: discord.Role,
    alter_posten: discord.Role,
    grund: str,
    neuer_posten: discord.Role = None
):
    # Berechtigung prüfen
    if not await is_allowed(interaction):
        return

    # Sicherstellen, dass der Benutzer, die Unit und der alte Posten existieren
    if not user or not unit or not alter_posten:
        await interaction.response.send_message("Benutzer, Unit oder alter Posten fehlen oder sind ungültig.", ephemeral=True)
        return

    # Erstelle den Embed
    if neuer_posten:
        embed = discord.Embed(
            title="Unit Abstieg",
            description=(
                f"╔══════════════════════════════════════════════╗\n\n"
                f"Hiermit wird {user.mention} innerhalb der Unit {unit.mention} vom Posten des {alter_posten.mention} "
                f"zum {neuer_posten.mention} degradiert.\n\n"
                f"Grund: {grund}\n\n"
                f"Hochachtungsvoll,\n"
                f"<@&1097648080020574260>\n\n"
                f"╚══════════════════════════════════════════════╝"
            ),
            color=discord.Color.orange()  # Farbcode: Orange
        )
    else:
        embed = discord.Embed(
            title="Unit Abstieg",
            description=(
                f"╔══════════════════════════════════════════════╗\n\n"
                f"Hiermit wird {user.mention} innerhalb der Unit {unit.mention} vom Posten des {alter_posten.mention} "
                f"degradiert.\n\n"
                f"Grund: {grund}\n\n"
                f"Hochachtungsvoll,\n"
                f"<@&1097648080020574260>\n\n"
                f"╚══════════════════════════════════════════════╝"
            ),
            color=discord.Color.orange()  # Farbcode: Orange
        )

    embed.set_footer(text="U.S. ARMY Management")

    # Sende die Nachricht in den festgelegten Kanal (Unit Update Kanal)
    channel = bot.get_channel(1173700352403591189)  # ID des Unit Update Kanals
    if channel:
        await channel.send(embed=embed)
    else:
        await interaction.response.send_message("Der Kanal konnte nicht gefunden werden.", ephemeral=True)
        return

    # Entferne den alten Posten und füge den neuen Posten hinzu (falls angegeben)
    try:
        # Entferne den alten Posten
        await user.remove_roles(alter_posten, reason=f"Degradiert: {grund}")

        # Füge den neuen Posten hinzu, falls angegeben
        if neuer_posten:
            await user.add_roles(neuer_posten, reason=f"Degradiert zu {neuer_posten.name}")
        
    except discord.DiscordException as e:
        await interaction.response.send_message(f"Fehler beim Degradieren des Benutzers: {e}", ephemeral=True)
        return

    # Bestätigung für den ausführenden Benutzer
    await interaction.response.send_message(
        f"{user.mention} wurde erfolgreich vom Posten des {alter_posten.mention} degradiert.",
        ephemeral=True
    )
@bot.tree.command(name="ready", description="Prüft, ob der Bot bereit ist.")
async def ready(interaction: discord.Interaction):
    # Sende eine Bestätigung nur an den ausführenden Benutzer
    await interaction.response.send_message(
        "✅ Der Bot ist bereit und funktioniert einwandfrei!",
        ephemeral=True
    )
@bot.tree.command(name="aufstellung", description="Erstellt eine Aufstellung für einen Benutzer und sendet sie im Aufstellungs-Kanal.")
async def aufstellung(
    interaction: discord.Interaction,
    user: discord.Member,
    wann: str,
    uhrzeit: str,
    position: discord.Role
):
    # Rollenabfrage: Der Befehl darf nur von bestimmten Rollen ausgeführt werden
    allowed_roles = {1196072112977358968, 1331306902897823745, 1097648080020574260}
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
        return

    # Erstelle die Nachricht im gewünschten Format
    message = (
        f"<@&1097625926243733536>\n\n"
        f"Hiermit wird eine Aufstellung angekündigt.\n\n"
        f"**Wann?**: {wann} um {uhrzeit} Uhr\n\n"
        f"Hochachtungsvoll,\n"
        f"{user.mention}\n"
        f"{position.mention}"
    )

    # Sende die Nachricht im Aufstellungs-Kanal
    channel = bot.get_channel(1136004218436722688)  # ID des Aufstellungs-Kanals
    if not channel:
        await interaction.response.send_message("Der Aufstellungs-Kanal konnte nicht gefunden werden.", ephemeral=True)
        return

    await channel.send(message)

    # Bestätigung für den ausführenden Benutzer
    await interaction.response.send_message(
        f"Die Aufstellung für {user.mention} wurde erfolgreich erstellt und im Aufstellungs-Kanal gesendet.",
        ephemeral=True
    )

# Lade Token und starte den Bot
load_dotenv()
token = os.getenv("DISCORD_TOKEN")  # Token aus .env-Datei laden
bot.run(token)
