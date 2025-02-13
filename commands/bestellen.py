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
        # **GUILD-Check: Bestellen nur auf Guild 1097626402540499044 erlaubt**
        if interaction.guild_id != BESTELLEN_GUILD_ID:
            await interaction.response.send_message("❌ Dieser Befehl ist auf diesem Server nicht erlaubt!", ephemeral=True)
            return

        # **Berechtigungsprüfung**
        if not await self.is_allowed(interaction):
            return

        # Artikel speichern
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

        # Überprüfen, ob der Nutzer berechtigt ist, bestimmte Artikel zu bestellen
        gesperrte_artikel = []
        erlaubte_artikel = {}

        for artikel, menge in bestellte_artikel.items():
            if menge > 0:  # Nur prüfen, wenn der Artikel bestellt wurde
                if not check_permissions(f"bestellen.{artikel}", interaction.user.id, [role.id for role in interaction.user.roles]):
                    gesperrte_artikel.append(artikel)
                else:
                    erlaubte_artikel[artikel] = menge

        # Falls gesperrte Artikel enthalten sind → Fehler ausgeben
        if gesperrte_artikel:
            fehlermeldung = "\n".join([f"🚫 **{artikel.replace('_', ' ').title()}** ist für dich nicht verfügbar!" for artikel in gesperrte_artikel])
            await interaction.response.send_message(f"❌ Du darfst folgende Artikel nicht bestellen:\n{fehlermeldung}", ephemeral=True)
            return

        bestellnummer = self.generate_bestellnummer()

        # Berechnung des Gesamtpreises
        artikel_preise = self.get_artikel_preise()
        gesamtpreis = sum(artikel_preise[item] * menge for item, menge in erlaubte_artikel.items())

        # Bestellung in die Datenbank einfügen
        self.add_bestellung(fraktion.id, bestellnummer, gesamtpreis, **erlaubte_artikel)

        embed = discord.Embed(
            title="📦 Bestellung aufgegeben",
            description=f"**Fraktion:** {fraktion.mention}\n**Bestellnummer:** `{bestellnummer}`\n💰 **Gesamtpreis:** `{gesamtpreis}€`\n📌 **Status:** Offen",
            color=discord.Color.green()
        )

        bestellte_items = [f"🔹 **{name}:** `{menge}`" for name, menge in erlaubte_artikel.items()]
        embed.add_field(name="🛒 Bestellte Artikel", value="\n".join(bestellte_items), inline=False)

        await interaction.response.send_message(embed=embed)
