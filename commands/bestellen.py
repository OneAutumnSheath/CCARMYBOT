import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from permissions_logic import check_permissions  # Import der Berechtigungsprüfung

# GUILD-IDs für Befehle
BESTELLEN_GUILD_ID = 1097626402540499044
LAGER_GUILD_ID = 1097625621875675188

class BestellenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "lager.db"
        self.init_database()

    def init_database(self):
        """Erstellt die Datenbank für Bestellungen, falls sie nicht existiert."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bestellungen (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bestellnummer INTEGER UNIQUE,
                    fraktion_id INTEGER,
                    gefechtspistole INTEGER DEFAULT 0,
                    kampf_pdw INTEGER DEFAULT 0,
                    smg INTEGER DEFAULT 0,
                    schlagstock INTEGER DEFAULT 0,
                    tazer INTEGER DEFAULT 0,
                    taschenlampe INTEGER DEFAULT 0,
                    fallschirm INTEGER DEFAULT 0,
                    schutzweste INTEGER DEFAULT 0,
                    magazin INTEGER DEFAULT 0,
                    erweitertes_magazin INTEGER DEFAULT 0,
                    waffengriff INTEGER DEFAULT 0,
                    schalldaempfer INTEGER DEFAULT 0,
                    taschenlampe_aufsatz INTEGER DEFAULT 0,
                    zielfernrohr INTEGER DEFAULT 0,
                    kampf_smg INTEGER DEFAULT 0,
                    schwerer_revolver INTEGER DEFAULT 0,
                    preis INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'Offen'
                )
            """)
            conn.commit()

    def add_bestellung(self, bestellnummer, fraktion_id, **items):
        """Fügt eine neue Bestellung in die Datenbank ein."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bestellungen (bestellnummer, fraktion_id, gefechtspistole, kampf_pdw, smg, schlagstock, tazer, 
                taschenlampe, fallschirm, schutzweste, magazin, erweitertes_magazin, waffengriff, schalldaempfer, 
                taschenlampe_aufsatz, zielfernrohr, kampf_smg, schwerer_revolver, preis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (bestellnummer, fraktion_id, *items.values()))
            conn.commit()

    @app_commands.command(name="bestellen", description="Erstellt eine neue Waffenbestellung.")
    async def bestellen(
        self, interaction: discord.Interaction, 
        fraktion: discord.Role, bestellnummer: int, preis: int,
        gefechtspistole: int = 0, kampf_pdw: int = 0, smg: int = 0, schlagstock: int = 0,
        tazer: int = 0, taschenlampe: int = 0, fallschirm: int = 0, schutzweste: int = 0,
        magazin: int = 0, erweitertes_magazin: int = 0, waffengriff: int = 0,
        schalldaempfer: int = 0, taschenlampe_aufsatz: int = 0, zielfernrohr: int = 0,
        kampf_smg: int = 0, schwerer_revolver: int = 0
    ):
        # **GUILD-Check: Bestellen nur auf Guild 1097626402540499044 erlaubt**
        if interaction.guild_id != BESTELLEN_GUILD_ID:
            await interaction.response.send_message("❌ Dieser Befehl ist auf diesem Server nicht erlaubt!", ephemeral=True)
            return

        # **Berechtigungsprüfung**
        if not await self.is_allowed(interaction):
            await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
            return

        # Bestellung in die Datenbank einfügen
        self.add_bestellung(
            bestellnummer, fraktion.id,
            gefechtspistole=gefechtspistole, kampf_pdw=kampf_pdw, smg=smg, schlagstock=schlagstock,
            tazer=tazer, taschenlampe=taschenlampe, fallschirm=fallschirm, schutzweste=schutzweste,
            magazin=magazin, erweitertes_magazin=erweitertes_magazin, waffengriff=waffengriff,
            schalldaempfer=schalldaempfer, taschenlampe_aufsatz=taschenlampe_aufsatz, zielfernrohr=zielfernrohr,
            kampf_smg=kampf_smg, schwerer_revolver=schwerer_revolver, preis=preis
        )

        embed = discord.Embed(
            title="📦 Bestellung aufgegeben",
            description=f"**Fraktion:** {fraktion.mention}\n**Bestellnummer:** `{bestellnummer}`\n💰 **Preis:** `{preis}€`\n📌 **Status:** Offen",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ausgeliefert", description="Markiert eine Bestellung als ausgeliefert.")
    async def ausgeliefert(self, interaction: discord.Interaction, bestellnummer: int):
        # **GUILD-Check: Nur auf Guild 1097625621875675188 erlaubt**
        if interaction.guild_id != LAGER_GUILD_ID:
            await interaction.response.send_message("❌ Dieser Befehl ist auf diesem Server nicht erlaubt!", ephemeral=True)
            return

        # **Berechtigungsprüfung**
        if not await self.is_allowed(interaction):
            await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE bestellungen SET status = 'Ausgeliefert' WHERE bestellnummer = ?", (bestellnummer,))
            conn.commit()

        await interaction.response.send_message(f"✅ Bestellung `{bestellnummer}` wurde als **ausgeliefert** markiert!", ephemeral=True)

    @app_commands.command(name="wochenbericht", description="Zeigt alle offenen Bestellungen.")
    async def wochenbericht(self, interaction: discord.Interaction):
        # **GUILD-Check: Nur auf Guild 1097625621875675188 erlaubt**
        if interaction.guild_id != LAGER_GUILD_ID:
            await interaction.response.send_message("❌ Dieser Befehl ist auf diesem Server nicht erlaubt!", ephemeral=True)
            return

        # **Berechtigungsprüfung**
        if not await self.is_allowed(interaction):
            await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bestellungen WHERE status = 'Offen'")
            bestellungen = cursor.fetchall()

        if not bestellungen:
            await interaction.response.send_message("📭 Keine offenen Bestellungen!", ephemeral=True)
            return

        bericht = "\n".join([f"📦 **Bestellnummer:** {b[1]}, 💰 **Preis:** {b[-2]}€, 📌 **Status:** {b[-1]}" for b in bestellungen])
        embed = discord.Embed(title="📋 Offene Bestellungen", description=bericht, color=discord.Color.orange())

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(BestellenCog(bot))
