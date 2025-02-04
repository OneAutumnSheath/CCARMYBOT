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

    async def add_unit_member(self, unit_name: str, member: discord.Member, rank: discord.Role):
        """Fügt ein Mitglied einer Einheit hinzu und weist ihm einen Rang zu."""
        units = load_units()

        # Überprüfen, ob die Einheit existiert
        if unit_name not in units["units"]:
            return "Einheit existiert nicht."

        unit = units["units"][unit_name]

        # Mitglied zur Einheit und zum Rang hinzufügen
        unit["members"].append({
            "member_id": str(member.id),
            "rank": rank.id,
            "unit_id": unit_name,  # Einheit ID wird hinzugefügt
            "sort_id": len(unit["members"]) + 1  # Neue Mitglieder ans Ende der Liste hinzufügen
        })
        
        # Mitglied die Rolle zuweisen
        await member.add_roles(rank)
        
        # Änderungen speichern
        save_units(units)
        
        return f"{member.mention} wurde erfolgreich zur Einheit {unit_name} hinzugefügt und der Rang {rank.name} zugewiesen."

    async def remove_unit_member(self, unit_name: str, member: discord.Member):
        """Entfernt ein Mitglied aus der Einheit und entzieht ihm den Rang."""
        units = load_units()

        # Überprüfen, ob die Einheit existiert
        if unit_name not in units["units"]:
            return "Einheit existiert nicht."

        unit = units["units"][unit_name]

        # Mitglied aus der Einheit entfernen
        member_data = next((m for m in unit["members"] if m["member_id"] == str(member.id)), None)
        if member_data:
            unit["members"].remove(member_data)
            # Mitglied die Rolle entfernen
            rank = discord.utils.get(member.guild.roles, id=member_data["rank"])
            if rank:
                await member.remove_roles(rank)
            save_units(units)
            return f"{member.mention} wurde erfolgreich aus der Einheit {unit_name} entfernt und der Rang {rank.name} entzogen."
        else:
            return f"{member.mention} ist nicht in der Einheit {unit_name}."

    @app_commands.command(name="addunitmember", description="Fügt ein Mitglied einer Einheit hinzu.")
    async def addunitmember(self, interaction: discord.Interaction, unit_name: str, member: discord.Member, rank: discord.Role):
        """Fügt ein Mitglied der angegebenen Einheit hinzu und weist ihm einen Rang zu."""
        result = await self.add_unit_member(unit_name, member, rank)
        await interaction.response.send_message(result, ephemeral=True)

    @app_commands.command(name="removeunitmember", description="Entfernt ein Mitglied aus einer Einheit.")
    async def removeunitmember(self, interaction: discord.Interaction, unit_name: str, member: discord.Member):
        """Entfernt ein Mitglied aus der angegebenen Einheit und entzieht ihm den Rang."""
        result = await self.remove_unit_member(unit_name, member)
        await interaction.response.send_message(result, ephemeral=True)

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

    @app_commands.command(name="resendunitmessage", description="Sendet die Mitgliederliste der Einheit erneut.")
    async def resendunitmessage(self, interaction: discord.Interaction, unit_name: str):
        """Sendet die Mitgliederliste der Einheit erneut."""
        units = load_units()

        # Überprüfen, ob die Einheit existiert
        if unit_name not in units["units"]:
            await interaction.response.send_message(f"Die Einheit {unit_name} existiert nicht.", ephemeral=True)
            return
        
        unit = units["units"][unit_name]
        unit_members = unit["members"]
        
        # Embed-Nachricht erstellen
        embed = discord.Embed(title=f"Mitglieder der Einheit {unit_name}", color=discord.Color.blue())

        for member_data in unit_members:
            member = await self.bot.fetch_user(int(member_data["member_id"]))
            rank = discord.utils.get(self.bot.guilds[0].roles, id=member_data["rank"])
            embed.add_field(name=rank.name if rank else "Unbekannter Rang", value=member.mention, inline=False)
        
        embed.set_footer(text="U.S. ARMY Management", icon_url="https://oneautumnsheath.de/army.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnitManager(bot))
