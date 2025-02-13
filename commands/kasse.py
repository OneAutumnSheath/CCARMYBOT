import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from permissions_logic import check_permissions  # Import der Berechtigungsprüfung

KASSEN_CHANNEL_ID = 1339424277446787143  # ID des Channels für Transaktions-Logs

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

    async def log_transaction(self, interaction: discord.Interaction, embed: discord.Embed):
        """Sendet eine Transaktion in den Kassen-Channel."""
        channel = self.bot.get_channel(KASSEN_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)
        else:
            await interaction.followup.send("⚠️ Kassen-Log-Channel nicht gefunden!", ephemeral=True)

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
    @app_commands.describe(geld="Optional: Betrag in regulärem Geld", schwarzgeld="Optional: Betrag in Schwarzgeld")
    async def einzahlen(
        self, interaction: discord.Interaction,
        geld: int = 0, schwarzgeld: int = 0
    ):
        # **Berechtigungsprüfung**
        if not await self.is_allowed(interaction):
            await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
            return
        
        # Falls weder Geld noch Schwarzgeld angegeben wurde
        if geld == 0 and schwarzgeld == 0:
            await interaction.response.send_message("⚠️ Du musst mindestens einen Betrag angeben!", ephemeral=True)
            return
        
        # Kassenstand vor der Einzahlung abrufen (optional für Vergleich)
        old_geld, old_schwarzgeld = self.get_kassenstand()

        # Datenbank aktualisieren
        self.update_kassenstand(geld, schwarzgeld)

        # Neuen Kassenstand abrufen
        new_geld, new_schwarzgeld = self.get_kassenstand()

        # Dynamische Embed-Erstellung für den User
        if geld > 0 and schwarzgeld > 0:
            embed_user = discord.Embed(
                title="💵 Einzahlung",
                description=(
                    f"👤 **Von:** {interaction.user.mention}\n"
                    f"💰 **Geld:** +{geld}€\n"
                    f"🖤 **Schwarzgeld:** +{schwarzgeld}€\n"
                ),
                color=discord.Color.green()
            )
        elif geld > 0:
            embed_user = discord.Embed(
                title="💵 Einzahlung",
                description=(
                    f"👤 **Von:** {interaction.user.mention}\n"
                    f"💰 **Geld:** +{geld}€\n"
                ),
                color=discord.Color.green()
            )
        elif schwarzgeld > 0:
            embed_user = discord.Embed(
                title="💵 Einzahlung",
                description=(
                    f"👤 **Von:** {interaction.user.mention}\n"
                    f"🖤 **Schwarzgeld:** +{schwarzgeld}€\n"
                ),
                color=discord.Color.green()
            )

        # Kassenstand-Embed für den User
        embed_kassenstand = discord.Embed(
            title="📊 Neuer Kassenstand",
            description=(
                f"💰 **Geld:** {new_geld}€ (vorher: {old_geld}€)\n"
                f"🖤 **Schwarzgeld:** {new_schwarzgeld}€ (vorher: {old_schwarzgeld}€)"
            ),
            color=discord.Color.blue()
        )

        # Log-Embed für den Kassen-Channel
        embed_log = discord.Embed(
            title="📜 Kassen-Log: Einzahlung",
            description=(
                f"👤 **Von:** {interaction.user.mention}\n"
                f"{'💰 **Geld:** +' + str(geld) + '€' if geld > 0 else ''}"
                f"{'🖤 **Schwarzgeld:** +' + str(schwarzgeld) + '€' if schwarzgeld > 0 else ''}\n"
                f"📊 **Neuer Kassenstand:**\n"
                f"💰 {new_geld}€ | 🖤 {new_schwarzgeld}€"
            ),
            color=discord.Color.orange()
        )

        # Antwort an den Nutzer (ephemeral, beide Embeds in EINER Nachricht)
        await interaction.response.send_message(embeds=[embed_user, embed_kassenstand], ephemeral=True)

        # Transaktion im Log-Channel posten
        await self.log_transaction(interaction, embed_log)



    @app_commands.command(name="auszahlen", description="Zahlt Geld aus der Kasse aus.")
    @app_commands.describe(
        an_wen="Der Empfänger der Auszahlung",
        grund="Grund der Auszahlung",
        geld="Optional: Betrag in regulärem Geld",
        schwarzgeld="Optional: Betrag in Schwarzgeld"
    )
    async def auszahlen(
        self, interaction: discord.Interaction,
        an_wen: discord.Member, grund: str, geld: int = 0, schwarzgeld: int = 0
    ):
        # **Berechtigungsprüfung mit `check_permissions`**
        if not await self.is_allowed(interaction):
            return  # Falls keine Berechtigung, Abbruch

        # Überprüfung, ob sowohl Geld als auch Schwarzgeld angegeben wurden
        if geld > 0 and schwarzgeld > 0:
            await interaction.response.send_message(
                "❌ Du kannst nicht gleichzeitig Geld und Schwarzgeld auszahlen!", ephemeral=True
            )
            return

        # Kassenstand abrufen
        current_geld, current_schwarzgeld = self.get_kassenstand()

        # Falls keine Werte angegeben wurden
        if geld == 0 and schwarzgeld == 0:
            await interaction.response.send_message(
                "⚠️ Du musst entweder Geld oder Schwarzgeld angeben!", ephemeral=True
            )
            return

        # Falls nicht genug Geld oder Schwarzgeld in der Kasse ist
        if geld > current_geld:
            await interaction.response.send_message(
                f"❌ Nicht genug Geld in der Kasse! Verfügbar: {current_geld}€", ephemeral=True
            )
            return
        if schwarzgeld > current_schwarzgeld:
            await interaction.response.send_message(
                f"❌ Nicht genug Schwarzgeld in der Kasse! Verfügbar: {current_schwarzgeld}€", ephemeral=True
            )
            return

        # Kassenstand aktualisieren
        self.update_kassenstand(-geld, -schwarzgeld)

        # Kassenstand nach Auszahlung abrufen
        new_geld, new_schwarzgeld = self.get_kassenstand()

        # Dynamische Embed-Erstellung für den User
        if geld > 0:
            embed_user = discord.Embed(
                title="💸 Auszahlung",
                description=(
                    f"👤 **Von:** {interaction.user.mention}\n"
                    f"➡️ **An:** {an_wen.mention}\n"
                    f"💰 **Geld:** -{geld}€\n"
                    f"📌 **Grund:** {grund}"
                ),
                color=discord.Color.red()
            )
        elif schwarzgeld > 0:
            embed_user = discord.Embed(
                title="💸 Auszahlung",
                description=(
                    f"👤 **Von:** {interaction.user.mention}\n"
                    f"🖤 **Schwarzgeld:** -{schwarzgeld}€\n"
                    f"📌 **Grund:** {grund}"
                ),
                color=discord.Color.red()
            )

        # Kassenstand-Embed für den User
        embed_kassenstand = discord.Embed(
            title="📊 Neuer Kassenstand",
            description=(
                f"💰 **Geld:** {new_geld}€\n"
                f"🖤 **Schwarzgeld:** {new_schwarzgeld}€"
            ),
            color=discord.Color.blue()
        )

        # Log-Embed für den Kassen-Channel
        embed_log = discord.Embed(
            title="📜 Kassen-Log: Auszahlung",
            description=(
                f"👤 **Von:** {interaction.user.mention}\n"
                f"➡️ **An:** {an_wen.mention}\n"
                f"{'💰 **Geld:** -' + str(geld) + '€' if geld > 0 else ''}"
                f"{'🖤 **Schwarzgeld:** -' + str(schwarzgeld) + '€' if schwarzgeld > 0 else ''}\n"
                f"📌 **Grund:** {grund}\n\n"
                f"📊 **Neuer Kassenstand:**\n"
                f"💰 {new_geld}€ | 🖤 {new_schwarzgeld}€"
            ),
            color=discord.Color.orange()
        )

        # Antwort an den Nutzer (ephemeral)
        await interaction.response.send_message(embeds=[embed_user, embed_kassenstand], ephemeral=True)

        # Transaktion im Log-Channel posten
        await self.log_transaction(interaction, embed_log)

    @app_commands.command(name="send-kassenstand", description="Sendet den aktuellen Kassenstand in den Kassen-Channel.")
    async def send_kassenstand(self, interaction: discord.Interaction):
        # **Berechtigungsprüfung mit `check_permissions`**
        if not await self.is_allowed(interaction):
            await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
            return

        # Aktuellen Kassenstand abrufen
        geld, schwarzgeld = self.get_kassenstand()

        # Embed für den Kassenstand
        embed_kassenstand = discord.Embed(
            title="📊 Aktueller Kassenstand",
            description=(
                f"💰 **Geld:** {geld}€\n"
                f"🖤 **Schwarzgeld:** {schwarzgeld}€"
            ),
            color=discord.Color.blue()
        )

        # Kassen-Channel abrufen
        channel = self.bot.get_channel(1339424277446787143)

        # Falls der Channel existiert, Nachricht senden
        if channel:
            await channel.send(embed=embed_kassenstand)
            await interaction.response.send_message("✅ Kassenstand wurde erfolgreich gesendet!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Kassen-Channel nicht gefunden!", ephemeral=True)


# Setup-Funktion für das Cog
async def setup(bot):
    await bot.add_cog(KassenCog(bot))
