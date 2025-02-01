from discord.ext import commands
import discord

class Aufstellung(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="aufstellung", description="Erstellt eine Aufstellung für einen Benutzer und sendet sie im Aufstellungs-Kanal.")
    async def aufstellung(self, ctx, user: discord.Member, wann: str, uhrzeit: str, position: discord.Role):
        # Rollenabfrage: Der Befehl darf nur von bestimmten Rollen ausgeführt werden
        allowed_roles = {1196072112977358968, 1331306902897823745, 1097648080020574260}
        if not any(role.id in allowed_roles for role in ctx.author.roles):
            await ctx.respond("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return

        # Erstelle die Nachricht im gewünschten Format
        message = (
            f"<@&1097625926243733536>\n\n"
            f"Hiermit wird eine Aufstellung angekündigt.\n\n"
            f"**Wann?**: {wann} um {uhrzeit} Uhr\n\n"
            f"Hochachtungsvoll,\n"
            f"{user.mention}\n"
            f"{position.mention}"
        )

        # Sende die Nachricht im Aufstellungs-Kanal
        channel = self.bot.get_channel(1136004218436722688)  # ID des Aufstellungs-Kanals
        if not channel:
            await ctx.send("Der Aufstellungs-Kanal konnte nicht gefunden werden.", ephemeral=True)
            return

        await channel.send(message)

        # Bestätigung für den ausführenden Benutzer
        await ctx.respond(
            f"Die Aufstellung für {user.mention} wurde erfolgreich erstellt und im Aufstellungs-Kanal gesendet.",
            ephemeral=True
        )

# Cog in den Bot laden
async def setup(bot):
    await bot.add_cog(Aufstellung(bot))
