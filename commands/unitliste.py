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
        with open(UNIT_FILE, "w") as f:
            yaml.dump({"units": {}}, f)  # Leere Datei initialisieren
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
        unit_members = unit["members"]

        # Mitglieder der Einheit abrufen
        members = [await self.bot.fetch_user(int(member["member_id"])) for member in unit_members]  # Zugriff auf "member_id"
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

    @app_commands.command(name="setchannel", description="Setzt die Channel-ID für eine Einheit.")
    async def setchannel(self, interaction: discord.Interaction, unit_name: str, channel: discord.TextChannel):
        """Setzt den Channel für eine Einheit."""
        units = load_units()

        # Überprüfen, ob die Einheit existiert, oder erstelle sie
        if unit_name not in units["units"]:
            units["units"][unit_name] = {"channel_id": channel.id, "members": []}
        else:
            # Wenn die Einheit schon existiert, aktualisiere die Channel-ID
            units["units"][unit_name]["channel_id"] = channel.id

        # Speichern der Änderungen
        save_units(units)

        await interaction.response.send_message(f"Die Channel-ID für die Einheit {unit_name} wurde auf {channel.mention} gesetzt.", ephemeral=True)

    @app_commands.command(name="addmember", description="Fügt ein Mitglied einer Einheit hinzu und weist ihm einen Rang zu.")
    async def addmember(self, interaction: discord.Interaction, unit_name: str, member: discord.Member, rank: discord.Role, sort_id: int = None):
        """Fügt ein Mitglied zu einer bestimmten Einheit hinzu und weist ihm einen Rang zu."""
        units = load_units()

        # Wenn die Einheit nicht existiert, erstelle sie
        if unit_name not in units["units"]:
            units["units"][unit_name] = {"channel_id": interaction.channel_id, "members": []}
        
        # Prüfen, ob das Mitglied bereits in der Einheit ist
        if str(member.id) in units["units"][unit_name]["members"]:
            await interaction.response.send_message(f"{member.mention} ist bereits in der Einheit {unit_name}.", ephemeral=True)
            return
        
        # Mitglied zur Einheit hinzufügen und Rang zuweisen
        units["units"][unit_name]["members"].append({
            "member_id": str(member.id),
            "rank": rank.id,  # Rolle als ID speichern
            "sort_id": sort_id or len(units["units"][unit_name]["members"])  # Wenn keine Sortier-ID angegeben, wird das Mitglied ans Ende gesetzt
        })
        
        # Mitglied die Rolle zuweisen
        await member.add_roles(rank)
        save_units(units)

        # Aktualisiere die Mitgliederliste im Channel der Einheit
        await self.update_unit_list(unit_name)
        
        await interaction.response.send_message(f"{member.mention} wurde erfolgreich zur Einheit {unit_name} hinzugefügt und der Rang {rank.name} zugewiesen.", ephemeral=True)

    @app_commands.command(name="removemember", description="Entfernt ein Mitglied aus einer Einheit.")
    async def removemember(self, interaction: discord.Interaction, unit_name: str, member: discord.Member):
        """Entfernt ein Mitglied aus einer bestimmten Einheit."""
        units = load_units()

        # Überprüfen, ob die Einheit existiert
        if unit_name not in units["units"] or str(member.id) not in [m["member_id"] for m in units["units"][unit_name]["members"]]:
            await interaction.response.send_message(f"{member.mention} ist nicht in der Einheit {unit_name}.", ephemeral=True)
            return
        
        # Mitglied aus der Einheit entfernen
        unit_members = units["units"][unit_name]["members"]
        member_data = next(m for m in unit_members if m["member_id"] == str(member.id))
        units["units"][unit_name]["members"].remove(member_data)
        save_units(units)

        # Mitglied die Rolle entfernen
        rank = discord.utils.get(member.guild.roles, id=member_data["rank"])
        if rank:
            await member.remove_roles(rank)

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
        unit_members = units["units"][unit_name]["members"]
        sorted_members = sorted(unit_members, key=lambda x: x["sort_id"])  # Mitglieder nach Sortier-ID sortieren
        member_mentions = [await self.bot.fetch_user(int(m["member_id"])) for m in sorted_members]
        member_mentions = [member.mention for member in member_mentions]
        
        if member_mentions:
            await interaction.response.send_message(f"Mitglieder der Einheit {unit_name}:\n" + "\n".join(member_mentions), ephemeral=True)
        else:
            await interaction.response.send_message(f"Es gibt keine Mitglieder in der Einheit {unit_name}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnitManager(bot))
