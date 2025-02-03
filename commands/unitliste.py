import discord
from discord.ext import commands
from discord import app_commands
import yaml
import os

# Die Datei für die Speicherung der Mitglieder und Einheiten
UNIT_FILE = "./config/units.yaml"

def load_units():
    """Lädt die gespeicherten Einheiten und Mitglieder aus der YAML-Datei oder erstellt die Datei, wenn sie nicht existiert."""
    if not os.path.exists(UNIT_FILE):
        # Wenn die Datei nicht existiert, erstelle eine neue mit der Standardstruktur
        with open(UNIT_FILE, "w") as f:
            yaml.dump({"units": {}}, f)  # Leere Struktur für Einheiten und Mitglieder
        return {"units": {}}
    try:
        with open(UNIT_FILE, "r") as f:
            return yaml.safe_load(f) or {"units": {}}
    except yaml.YAMLError:
        return {"units": {}}

def save_units(units):
    """Speichert die Einheiten und Mitglieder in der YAML-Datei."""
    with open(UNIT_FILE, "w") as f:
        yaml.dump(units, f)

class UnitManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_unit_list(self, unit_name: str):
        """Aktualisiert die Mitgliederliste im spezifizierten Channel für die Einheit."""
        units = load_units()

        # Überprüfen, ob die Einheit existiert
        if unit_name not in units["units"]:
            return

        unit = units["units"][unit_name]
        channel_id = unit["channel_id"]
        member_ids = unit["members"]

        # Mitglieder der Einheit abrufen
        members = [await self.bot.fetch_user(int(member_id)) for member_id in member_ids]
        member_mentions = [member.mention for member in members]

        # Channel finden und Nachricht senden/bearbeiten
        channel = self.bot.get_channel(channel_id)
        if channel:
            # Überprüfen, ob bereits eine Nachricht existiert
            async for message in channel.history(limit=1):
                # Bearbeite die letzte Nachricht
                await message.edit(content=f"📊 Mitglieder der Einheit {unit_name}:\n" + "\n".join(member_mentions))
                return  # Nachricht gefunden und bearbeitet, daher zurückkehren
            
            # Falls keine Nachricht existiert, sende eine neue
            await channel.send(f"📊 Mitglieder der Einheit {unit_name}:\n" + "\n".join(member_mentions))


    @app_commands.command(name="addmember", description="Fügt ein Mitglied einer Einheit hinzu.")
    async def addmember(self, interaction: discord.Interaction, unit_name: str, member: discord.Member):
        """Fügt ein Mitglied zu einer bestimmten Einheit hinzu."""
        units = load_units()
        
        # Wenn die Einheit nicht existiert, erstelle sie
        if unit_name not in units["units"]:
            units["units"][unit_name] = {"channel_id": interaction.channel_id, "members": []}
        
        # Prüfen, ob das Mitglied bereits in der Einheit ist
        if str(member.id) in units["units"][unit_name]["members"]:
            await interaction.response.send_message(f"{member.mention} ist bereits in der Einheit {unit_name}.", ephemeral=True)
            return
        
        # Mitglied zur Einheit hinzufügen
        units["units"][unit_name]["members"].append(str(member.id))
        save_units(units)
        
        # Aktualisiere die Mitgliederliste im Channel der Einheit
        await self.update_unit_list(unit_name)
        
        await interaction.response.send_message(f"{member.mention} wurde erfolgreich zur Einheit {unit_name} hinzugefügt.", ephemeral=True)

    @app_commands.command(name="removemember", description="Entfernt ein Mitglied aus einer Einheit.")
    async def removemember(self, interaction: discord.Interaction, unit_name: str, member: discord.Member):
        """Entfernt ein Mitglied aus einer bestimmten Einheit."""
        units = load_units()

        # Überprüfen, ob die Einheit existiert
        if unit_name not in units["units"] or str(member.id) not in units["units"][unit_name]["members"]:
            await interaction.response.send_message(f"{member.mention} ist nicht in der Einheit {unit_name}.", ephemeral=True)
            return
        
        # Mitglied aus der Einheit entfernen
        units["units"][unit_name]["members"].remove(str(member.id))
        save_units(units)
        
        # Aktualisiere die Mitgliederliste im Channel der Einheit
        await self.update_unit_list(unit_name)
        
        await interaction.response.send_message(f"{member.mention} wurde erfolgreich aus der Einheit {unit_name} entfernt.", ephemeral=True)

    @app_commands.command(name="unitmembers", description="Zeigt alle Mitglieder einer Einheit an.")
    async def unitmembers(self, interaction: discord.Interaction, unit_name: str):
        """Zeigt alle Mitglieder einer bestimmten Einheit an."""
        units = load_units()

        # Überprüfen, ob die Einheit existiert
        if unit_name not in units["units"]:
            await interaction.response.send_message(f"Die Einheit {unit_name} existiert nicht.", ephemeral=True)
            return
        
        # Mitglieder der Einheit anzeigen
        member_ids = units["units"][unit_name]["members"]
        members = [await self.bot.fetch_user(int(member_id)) for member_id in member_ids]
        member_mentions = [member.mention for member in members]
        
        if member_mentions:
            await interaction.response.send_message(f"Mitglieder der Einheit {unit_name}:\n" + "\n".join(member_mentions), ephemeral=True)
        else:
            await interaction.response.send_message(f"Es gibt keine Mitglieder in der Einheit {unit_name}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnitManager(bot))
