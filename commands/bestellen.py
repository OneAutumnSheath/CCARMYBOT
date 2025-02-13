import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from permissions_logic import check_permissions  # Import der Berechtigungsprüfung

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
                    kampfPDW INTEGER DEFAULT 0,
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
                    kampfSMG INTEGER DEFAULT 0,
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
                INSERT INTO bestellungen (bestellnummer, fraktion_id, gefechtspistole, kampfPDW, smg, schlagstock, tazer, 
                taschenlampe, fallschirm, schutzweste, magazin, erweitertes_magazin, waffengriff, schalldaempfer, 
                taschenlampe_aufsatz, zielfernrohr, kampfSMG, schwerer_revolver, preis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (bestellnummer, fraktion_id, *items.values()))
            conn.commit()

    @app_commands.command(name="bestellen", description="Erstellt eine neue Waffenbestellung.")
    async def bestellen(
        self, interaction: discord.Interaction, 
        fraktion: discord.Role, bestellnummer: int, preis: int,
        gefechtspistole: int = 0, kampfPDW: int = 0, smg: int = 0, schlagstock: int = 0,
        tazer: int = 0, taschenlampe: int = 0, fallschirm: int = 0, schutzweste: int = 0,
        magazin: int = 0, erweitertes_magazin: int = 0, waffengriff: int = 0,
        schalldaempfer: int = 0, taschenlampe_aufsatz: int = 0, zielfernrohr: int = 0,
        kampfSMG: int = 0, schwerer_revolver: int = 0
    ):
        # **Berechtigungsprüfung**
        if not await self.is_allowed(interaction):
            await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
            return

        # Artikel mit Berechtigungsprüfung definieren
        artikel_mit_rechten = {
            "gefechtspistole": gefechtspistole,
            "kampfPDW": kampfPDW,
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
            "kampfSMG": kampfSMG,
            "schwerer_revolver": schwerer_revolver
        }

        # Liste gesperrter Artikel für den User
        gesperrte_artikel = []
        
        for artikel, menge in artikel_mit_rechten.items():
            if menge > 0:  # Nur prüfen, wenn das Item bestellt wurde
                if not check_permissions(f"bestellen.{artikel}", interaction.user.id, [role.id for role in interaction.user.roles]):
                    gesperrte_artikel.append(artikel)

        # Falls gesperrte Artikel enthalten sind → Fehler ausgeben
        if gesperrte_artikel:
            fehlermeldung = "\n".join([f"🚫 **{artikel.replace('_', ' ').title()}** ist für dich nicht verfügbar!" for artikel in gesperrte_artikel])
            await interaction.response.send_message(f"❌ Du darfst folgende Artikel nicht bestellen:\n{fehlermeldung}", ephemeral=True)
            return

        # Bestellung in die Datenbank einfügen
        self.add_bestellung(bestellnummer, fraktion.id, **artikel_mit_rechten)

        # Erstelle das Embed für die Bestätigung
        embed = discord.Embed(
            title="📦 Bestellung aufgegeben",
            description=(
                f"**Fraktion:** {fraktion.mention}\n"
                f"**Bestellnummer:** `{bestellnummer}`\n"
                f"💰 **Preis:** `{preis}€`\n"
                f"📌 **Status:** Offen"
            ),
            color=discord.Color.green()
        )

        # Liste der bestellten Gegenstände hinzufügen
        bestellte_items = [f"🔹 **{name.replace('_', ' ').title()}:** `{menge}`" for name, menge in artikel_mit_rechten.items() if menge > 0]

        if bestellte_items:
            embed.add_field(name="🛒 Bestellte Artikel", value="\n".join(bestellte_items), inline=False)
        else:
            embed.add_field(name="⚠️ Hinweis", value="Keine Gegenstände wurden angegeben.", inline=False)

        await interaction.response.send_message(embed=embed)

    async def is_allowed(self, interaction):
        """Überprüft, ob der Benutzer berechtigt ist, den Befehl auszuführen."""
        if not check_permissions("bestellen", interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
            return False
        return True

async def setup(bot):
    await bot.add_cog(BestellenCog(bot))
