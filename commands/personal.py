import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import check_permissions  # Berechtigungsprüfung

# ID für den Personal-Kanal
PERSONAL_CHANNEL = 1097625981671448698
MGMT_ID = 1097648080020574260  # Management ID für Ankündigungen

# Berechtigungsprüfung für den Befehl
async def is_allowed(interaction: discord.Interaction):
    permission_node = "personal"  # Berechtigungs-Node für den Personal-Befehl
    if check_permissions(permission_node, interaction.user.id, [role.id for role in interaction.user.roles]):
        return True
    await interaction.response.send_message(f"Du hast keine Berechtigung, diesem Befehl auszuführen.", ephemeral=True)
    return False

# Cog-Klasse für Personal-Operationen
class Personal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash-Befehl: einstellen
    @app_commands.command(name="einstellen", description="Stellt einen neuen Rekruten ein und fügt die entsprechenden Rollen hinzu.")
    async def einstellen(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        name: str,
        dn: str,
        dienstgrad: discord.Role,
        division: discord.Role,
        grund: str
    ):
        if not await is_allowed(interaction):  # Berechtigungsprüfung
            return

        # ID der festen Rollen
        MAIN_UNIT_ROLE_ID = 1134170231275782154
        INFANTRY_ROLE_ID = 1187756956425920645
        ARMY_ROLE_ID = 1097625926243733536

        # Feste Rollen basierend auf IDs abrufen
        main_unit_role = interaction.guild.get_role(MAIN_UNIT_ROLE_ID)
        infantry_role = interaction.guild.get_role(INFANTRY_ROLE_ID)
        army_role = interaction.guild.get_role(ARMY_ROLE_ID)

        # Benutzer umbenennen
        new_nickname = f"[USA-{dn}] {name}"
        try:
            await user.edit(nick=new_nickname, reason="Einstellung in die Army")
        except discord.Forbidden:
            await interaction.response.send_message(
                f"Der Benutzer konnte nicht umbenannt werden. Möglicherweise fehlen mir die Berechtigungen.", ephemeral=True
            )
            return
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Fehler beim Umbenennen: {e}", ephemeral=True)
            return

        # Erstelle den Embed
        embed = discord.Embed(
            title="Neueinstellung",
            description=(
                f"╔══════════════════════════════════════════════╗\n\n"
                f"Hiermit tritt {user.mention} der Army als {dienstgrad.mention} bei.\n\n"
                f"Grund: {grund}\n\n"
                f"Hochachtungsvoll,\n"
                f"<@&{MGMT_ID}>\n\n"
                f"╚══════════════════════════════════════════════╝"
            ),
            color=discord.Color.green()  # Farbcode: #00FF00
        )
        embed.set_footer(text="U.S. ARMY Management")

        # Sende die Ankündigung im festgelegten Kanal
        channel = self.bot.get_channel(PERSONAL_CHANNEL)
        if not channel:
            await interaction.response.send_message("Der Personal-Kanal wurde nicht gefunden!", ephemeral=True)
            return
        await channel.send(embed=embed)

        # Rollen hinzufügen
        try:
            roles_to_add = [dienstgrad, division, main_unit_role, infantry_role, army_role]
            for role in roles_to_add:
                if role:
                    await user.add_roles(role, reason=f"Einstellung: {grund}")
        except discord.DiscordException as e:
            await interaction.response.send_message(f"Fehler beim Hinzufügen der Rollen: {e}", ephemeral=True)
            return

        # Bestätigungsnachricht für den Ausführenden
        await interaction.response.send_message(
            f"{user.mention} wurde erfolgreich als {dienstgrad.mention} eingestellt, hat die entsprechenden Rollen erhalten und wurde umbenannt zu `{new_nickname}`.",
            ephemeral=True
        )

# Setup-Funktion, die den Cog dem Bot hinzufügt
async def setup(bot):
    await bot.add_cog(Personal(bot))
