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
        """Erstellt die Datenbank für Bestellungen und Preise, falls sie nicht existiert."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabelle für Bestellungen
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bestellungen (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

            # Tabelle für Artikelpreise
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preise (
                    artikel TEXT PRIMARY KEY,
                    preis INTEGER DEFAULT 1
                )
            """)

            # Standardpreise setzen, falls noch keine Einträge vorhanden sind
            default_preise = [
                ("gefechtspistole", 1), ("kampf_pdw", 1), ("smg", 1), ("schlagstock", 1), ("tazer", 1),
                ("taschenlampe", 1), ("fallschirm", 1), ("schutzweste", 1), ("magazin", 1), ("erweitertes_magazin", 1),
                ("waffengriff", 1), ("schalldaempfer", 1), ("taschenlampe_aufsatz", 1), ("zielfernrohr", 1),
                ("kampf_smg", 1), ("schwerer_revolver", 1)
            ]

            cursor.executemany(
                "INSERT OR IGNORE INTO preise (artikel, preis) VALUES (?, ?)",
                default_preise
            )

            conn.commit()
    
    async def is_allowed(self, interaction: discord.Interaction):
        """Überprüft, ob der Benutzer berechtigt ist, den Befehl auszuführen."""
        if not check_permissions("bestellen", interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
            return False
        return True

    @app_commands.command(name="bestellen", description="Erstellt eine neue Waffenbestellung.")
    async def bestellen(
        self, interaction: discord.Interaction, 
        fraktion: discord.Role,
        gefechtspistole: int = 0, kampf_pdw: int = 0, smg: int = 0, schlagstock: int = 0,
        tazer: int = 0, taschenlampe: int = 0, fallschirm: int = 0, schutzweste: int = 0,
        magazin: int = 0, erweitertes_magazin: int = 0, waffengriff: int = 0,
        schalldaempfer: int = 0, taschenlampe_aufsatz: int = 0, zielfernrohr: int = 0,
        kampf_smg: int = 0, schwerer_revolver: int = 0
    ):
        if interaction.guild_id != BESTELLEN_GUILD_ID:
            await interaction.response.send_message("❌ Dieser Befehl ist auf diesem Server nicht erlaubt!", ephemeral=True)
            return

        if not await self.is_allowed(interaction):
            return

        bestellte_artikel = {
            "gefechtspistole": gefechtspistole,
            "kampf_pdw": kampf_pdw,
            "smg": smg,
            "schlagstock": schlagstock,
            "tazer": tazer,
            "taschenlampe": taschenlampe,
            "fallschirm": fallschirm,
            "schutzweste": schutzweste,
            "magazin": magazin,
            "erweitertes_magazin": erweitertes_magazin,
            "waffengriff": waffengriff,
            "schalldaempfer": schalldaempfer,
            "taschenlampe_aufsatz": taschenlampe_aufsatz,
            "zielfernrohr": zielfernrohr,
            "kampf_smg": kampf_smg,
            "schwerer_revolver": schwerer_revolver
        }
        artikel_preise = self.get_artikel_preise()
        gesamtpreis = sum(artikel_preise[item] * menge for item, menge in bestellte_artikel.items() if menge > 0)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bestellungen (fraktion_id, preis) VALUES (?, ?)
            """, (fraktion.id, gesamtpreis))
            bestellnummer = cursor.lastrowid  # Die ID als Bestellnummer setzen
            conn.commit()

        bestellte_items = [f"🔹 **{name}:** `{menge}`" for name, menge in bestellte_artikel.items() if menge > 0]
        embed = discord.Embed(
            title="📦 Bestellung aufgegeben",
            description=f"**Fraktion:** {fraktion.mention}\n**Bestellnummer:** `{bestellnummer}`\n💰 **Gesamtpreis:** `{gesamtpreis}€`\n📌 **Status:** Offen",
            color=discord.Color.green()
        )
        embed.add_field(name="🛒 Bestellte Artikel", value="\n".join(bestellte_items), inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(BestellenCog(bot))
