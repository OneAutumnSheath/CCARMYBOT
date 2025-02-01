import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import check_permissions  # Berechtigungsprüfung
import yaml
import os

# Verzeichnis für die Konfiguration
config_dir = './config'
config_file = f'{config_dir}/permissions.yaml'

UNIT_CHANNEL = 1173700352403591189  # Kanal-ID für die Ankündigung
MGMT_ID = 1097648080020574260  # Management-ID

# Berechtigungsprüfung für den Befehl
async def is_allowed(interaction: discord.Interaction):
    permission_node = "units"  # Berechtigungs-Node für Unit-Eintritt, Austritt und Aufstieg
    if check_permissions(permission_node, interaction.user.id, [role.id for role in interaction.user.roles]):
        return True
    await interaction.response.send_message(f"Du hast keine Berechtigung, diesem Befehl auszuführen.", ephemeral=True)
    return False

# Zuweisung einer Rolle (Unit) an einen Benutzer
async def assign_unit_role(interaction, unit_name):
    units = load_units()
    
    if unit_name not in units:
        return f"Unit '{unit_name}' existiert nicht."
    
    # Hole die Rolle aus der Guild
    role = discord.utils.get(interaction.guild.roles, name=unit_name)
    if not role:
        return f"Die Rolle für Unit '{unit_name}' konnte nicht gefunden werden."
    
    # Füge die Rolle dem Benutzer hinzu
    try:
        await interaction.user.add_roles(role)
        return f"{interaction.user.mention} wurde der Unit '{unit_name}' erfolgreich zugewiesen!"
    except Exception as e:
        return f"Fehler beim Zuweisen der Rolle: {e}"

# Entferne eine Rolle (Unit) von einem Benutzer
async def remove_unit_role(interaction, unit_name):
    units = load_units()
    
    if unit_name not in units:
        return f"Unit '{unit_name}' existiert nicht."
    
    # Hole die Rolle aus der Guild
    role = discord.utils.get(interaction.guild.roles, name=unit_name)
    if not role:
        return f"Die Rolle für Unit '{unit_name}' konnte nicht gefunden werden."
    
    # Entferne die Rolle vom Benutzer
    try:
        await interaction.user.remove_roles(role)
        return f"{interaction.user.mention} wurde erfolgreich aus der Unit '{unit_name}' entfernt!"
    except Exception as e:
        return f"Fehler beim Entfernen der Rolle: {e}"

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
    if not await is_allowed(interaction):  # Berechtigungsprüfung
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
    channel = interaction.guild.get_channel(UNIT_CHANNEL)
    if channel:
        await channel.send(embed=embed)
    else:
        await interaction.response.send_message("Ankündigungskanal nicht gefunden.", ephemeral=True)

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
    if not await is_allowed(interaction):  # Berechtigungsprüfung
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
    channel = interaction.guild.get_channel(UNIT_CHANNEL)
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

# Slash-Befehl: unit-aufstieg
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
    if not await is_allowed(interaction):  # Berechtigungsprüfung
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

# Setup-Funktion, die den Cog dem Bot hinzufügt
async def setup(bot):
    await bot.add_cog(Unit(bot))
