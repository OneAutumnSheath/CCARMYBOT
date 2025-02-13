import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from permissions_logic import check_permissions  # Import der Berechtigungsprüfung

class KassenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "kasse.db"
        self.init_database()

    def init_database(self):
        """Erstellt die Datenbank und die Tabelle, falls sie nicht existiert."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kasse (
                    id INTEGER PRIMARY KEY,
                    geld INTEGER DEFAULT 0,
                    schwarzgeld INTEGER DEFAULT 0
                )
            """)
            cursor.execute("SELECT COUNT(*) FROM kasse")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO kasse (geld, schwarzgeld) VALUES (0, 0)")
            conn.commit()

    def get_kassenstand(self):
        """Holt den aktuellen Kassenstand aus der Datenbank."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT geld, schwarzgeld FROM kasse")
            return cursor.fetchone()  # Gibt (geld, schwarzgeld) zurück

    def update_kassenstand(self, geld_diff: int, schwarzgeld_diff: int):
        """Ändert den Kassenstand in der Datenbank."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE kasse 
                SET geld = geld + ?, schwarzgeld = schwarzgeld + ?
            """, (geld_diff, schwarzgeld_diff))
            conn.commit()

    async def is_allowed(self, interaction):
        """Überprüft, ob der Benutzer berechtigt ist, den Befehl auszuführen."""
        if not check_permissions("kasse", interaction.user.id, [role.id for role in interaction.user.roles]):
            await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
            return False
        return True

    @app_commands.command(name="kassenstand", description="Zeigt den aktuellen Stand der Kasse.")
    async def kassenstand(self, interaction: discord.Interaction):
        geld, schwarzgeld = self.get_kassenstand()
        embed = discord.Embed(
            title="📊 Kassenstand",
            description=f"💰 **Geld:** {geld}€\n🖤 **Schwarzgeld:** {schwarzgeld}€",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="einzahlen", description="Zahlt Geld in die Kasse ein.")
    async def einzahlen(
        self, interaction: discord.Interaction,
        schwarzgeld: int, geld: int, an_wen: discord.Member, warum: str
    ):
        self.update_kassenstand(geld, schwarzgeld)

        embed = discord.Embed(
            title="💵 Einzahlung",
            description=(
                f"👤 **Von:** {interaction.user.mention}\n"
                f"➡️ **An:** {an_wen.mention}\n"
                f"💰 **Geld:** +{geld}€\n"
                f"🖤 **Schwarzgeld:** +{schwarzgeld}€\n"
                f"📌 **Grund:** {warum}"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="auszahlen", description="Zahlt Geld aus der Kasse aus.")
    async def auszahlen(
        self, interaction: discord.Interaction,
        schwarzgeld: int, geld: int, an_wen: discord.Member, warum: str
    ):
        # **Berechtigungsprüfung mit `check_permissions`**
        if not await self.is_allowed(interaction):
            return  # Falls keine Berechtigung, Abbruch

        current_geld, current_schwarzgeld = self.get_kassenstand()

        if geld > current_geld or schwarzgeld > current_schwarzgeld:
            await interaction.response.send_message("❌ Nicht genug Geld in der Kasse!", ephemeral=True)
            return

        self.update_kassenstand(-geld, -schwarzgeld)

        embed = discord.Embed(
            title="💸 Auszahlung",
            description=(
                f"👤 **Von:** {interaction.user.mention}\n"
                f"➡️ **An:** {an_wen.mention}\n"
                f"💰 **Geld:** -{geld}€\n"
                f"🖤 **Schwarzgeld:** -{schwarzgeld}€\n"
                f"📌 **Grund:** {warum}"
            ),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# Setup-Funktion für das Cog
async def setup(bot):
    await bot.add_cog(KassenCog(bot))
