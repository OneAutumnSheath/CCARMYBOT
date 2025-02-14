import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector

class BestellenNeu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_config = {
            "host": "localhost",
            "user": "weaplog_dev",
            "password": "weaplog_dev",
            "database": "weaplog_dev"
        }
        self.init_databases()

    def init_databases(self):
        """Verbindet sich mit der MySQL/MariaDB und erstellt die benötigten Tabellen."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sortiment (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE,
                preis INT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bestellungen (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fraktion BIGINT,
                message_id BIGINT,
                waffe1 INT DEFAULT 0,
                waffe2 INT DEFAULT 0,
                waffe3 INT DEFAULT 0,
                waffe4 INT DEFAULT 0,
                waffe5 INT DEFAULT 0,
                waffe6 INT DEFAULT 0,
                waffe7 INT DEFAULT 0,
                waffe8 INT DEFAULT 0,
                waffe9 INT DEFAULT 0,
                waffe10 INT DEFAULT 0,
                waffe11 INT DEFAULT 0,
                waffe12 INT DEFAULT 0,
                waffe13 INT DEFAULT 0,
                waffe14 INT DEFAULT 0,
                waffe15 INT DEFAULT 0, 
                waffe16 INT DEFAULT 0,
                messageid BIGINT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bestellpermission (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fraktion BIGINT UNIQUE,
                waffe1 BOOLEAN DEFAULT 1,
                waffe2 BOOLEAN DEFAULT 1,
                waffe3 BOOLEAN DEFAULT 1,
                waffe4 BOOLEAN DEFAULT 1,
                waffe5 BOOLEAN DEFAULT 1,
                waffe6 BOOLEAN DEFAULT 1,
                waffe7 BOOLEAN DEFAULT 1,
                waffe8 BOOLEAN DEFAULT 1,
                waffe9 BOOLEAN DEFAULT 1,
                waffe10 BOOLEAN DEFAULT 1,
                waffe11 BOOLEAN DEFAULT 1,
                waffe12 BOOLEAN DEFAULT 1,
                waffe13 BOOLEAN DEFAULT 1,
                waffe14 BOOLEAN DEFAULT 1,
                waffe15 BOOLEAN DEFAULT 1,
                waffe16 BOOLEAN DEFAULT 1
            )
        """)
        conn.commit()
        
        cursor.close()
        conn.close()

    @app_commands.command(name="bestellen", description="Erstellt eine neue Bestellung.")
    async def bestellen(
        self, interaction: discord.Interaction, fraktion: discord.Role,
        gefechtspistole: int = 0, kampfpdw: int = 0, smg: int = 0, schlagstock: int = 0,
        tazer: int = 0, taschenlampe: int = 0, fallschirm: int = 0, schutzweste: int = 0,
        magazin: int = 0, erweitertes_magazin: int = 0, waffengriff: int = 0,
        schalldaempfer: int = 0, taschenlampe_aufsatz: int = 0, zielfernrohr: int = 0,
        kampf_smg: int = 0, schwerer_revolver: int = 0
    ):
        await interaction.response.defer()
        
        artikel_dict = {
            "waffe1": gefechtspistole, "waffe2": kampfpdw, "waffe3": smg, "waffe4": schlagstock,
            "waffe5": tazer, "waffe6": taschenlampe, "waffe7": fallschirm, "waffe8": schutzweste,
            "waffe9": magazin, "waffe10": erweitertes_magazin, "waffe11": waffengriff, "waffe12": schalldaempfer,
            "waffe13": taschenlampe_aufsatz, "waffe14": zielfernrohr, "waffe15": kampf_smg, "waffe16": schwerer_revolver
        }
        
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        # Bestellung in DB anlegen und Bestellnummer abrufen
        cursor.execute("INSERT INTO bestellungen (fraktion) VALUES (%s)", (fraktion.id,))
        conn.commit()
        bestellnummer = cursor.lastrowid

        gesamtpreis = 0
        bestellte_items = []

        for artikel, menge in artikel_dict.items():
            if menge > 0:
                cursor.execute("SELECT name, preis FROM sortiment WHERE id = %s", (artikel.replace("waffe", ""),))
                artikel_info = cursor.fetchone()
                artikel_name, artikel_preis = artikel_info if artikel_info else (artikel.replace('_', ' ').title(), 0)
                gesamtpreis += artikel_preis * menge
                bestellte_items.append(f"🔹 **{artikel_name}:** `{menge}`")

        embed = discord.Embed(
            title="📦 Bestellung aufgegeben",
            description=f"**Fraktion:** {fraktion.mention}\n**Bestellnummer:** `{bestellnummer}`\n💰 **Gesamtpreis:** `{gesamtpreis}€`\n📌 **Status:** Offen",
            color=discord.Color.green()
        )
        embed.add_field(name="🛒 Bestellte Artikel", value="\n".join(bestellte_items), inline=False)
        
        message = await interaction.followup.send(embed=embed)
        
        # Speichern der message_id für spätere Bearbeitung
        cursor.execute("UPDATE bestellungen SET message_id = %s WHERE id = %s", (message.id, bestellnummer))
        conn.commit()
        
        cursor.close()
        conn.close()

async def setup(bot):
    await bot.add_cog(BestellenNeu(bot))
