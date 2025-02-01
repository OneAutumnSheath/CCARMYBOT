import discord
from discord.ext import commands
from discord import app_commands
from permissions_logic import check_permissions, set_permissions, view_permissions  # Import aus der permissions_logic.py

class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash-Befehl: setpermissions
    @app_commands.command(name="setpermissions", description="Setze Berechtigungen für eine Rolle oder einen Benutzer")
    async def setpermissions(self, interaction: discord.Interaction, user: discord.User = None, role: discord.Role = None, permission_node: str = None):
        """Setzt Berechtigungen für eine Rolle oder einen Benutzer."""
        
        if not user and not role:
            await interaction.response.send_message("Gebe entweder einen Benutzer oder eine Rolle an, dem die Berechtigung gesetzt werden soll.", ephemeral=True)
            return

        if not permission_node:
            await interaction.response.send_message("Gebe eine Berechtigung (Node) an, die gesetzt werden soll.", ephemeral=True)
            return
        
        # Berechtigungen setzen
        if role:
            set_permissions(role.id, [permission_node])  # Berechtigungen für eine Rolle setzen
            await interaction.response.send_message(f"Die Berechtigung `{permission_node}` wurde der Rolle `{role.name}` zugewiesen.", ephemeral=True)
        
        if user:
            set_permissions(user.id, [permission_node], is_user=True)  # Berechtigungen für einen Benutzer setzen
            await interaction.response.send_message(f"Die Berechtigung `{permission_node}` wurde dem Benutzer `{user.name}` zugewiesen.", ephemeral=True)

    # Slash-Befehl: unsetpermission
    @app_commands.command(name="unsetpermission", description="Entferne eine Berechtigung von einer Rolle oder einem Benutzer")
    async def unsetpermission(self, interaction: discord.Interaction, user: discord.User = None, role: discord.Role = None, permission_node: str = None):
        """Entfernt eine Berechtigung von einem Benutzer oder einer Rolle."""
        
        if not permission_node:
            await interaction.response.send_message("Bitte gib eine Berechtigung an, die entfernt werden soll.", ephemeral=True)
            return
        
        if not user and not role:
            await interaction.response.send_message("Gebe entweder einen Benutzer oder eine Rolle an, von dem die Berechtigung entfernt werden soll.", ephemeral=True)
            return
        
        permissions = load_permissions()
        
        # Berechtigung von einer Rolle entfernen
        if role:
            if str(role.id) in permissions.get('roles', {}) and permission_node in permissions['roles'][str(role.id)]:
                permissions['roles'][str(role.id)].remove(permission_node)
                await interaction.response.send_message(f"Die Berechtigung `{permission_node}` wurde der Rolle `{role.name}` entfernt.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Die Berechtigung `{permission_node}` ist der Rolle `{role.name}` nicht zugewiesen.", ephemeral=True)

        # Berechtigung von einem Benutzer entfernen
        if user:
            if str(user.id) in permissions.get('users', {}) and permission_node in permissions['users'][str(user.id)]:
                permissions['users'][str(user.id)].remove(permission_node)
                await interaction.response.send_message(f"Die Berechtigung `{permission_node}` wurde dem Benutzer `{user.name}` entfernt.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Die Berechtigung `{permission_node}` ist dem Benutzer `{user.name}` nicht zugewiesen.", ephemeral=True)

        # Berechtigungen in der Datei speichern
        with open(config_file, 'w') as f:
            yaml.dump(permissions, f)

    # Slash-Befehl: delpermission
    @app_commands.command(name="delpermission", description="Löscht eine Berechtigung vollständig von einem Benutzer oder einer Rolle")
    async def delpermission(self, interaction: discord.Interaction, user: discord.User = None, role: discord.Role = None, permission_node: str = None):
        """Löscht eine Berechtigung vollständig von einem Benutzer oder einer Rolle."""
        
        if not permission_node:
            await interaction.response.send_message("Bitte gib eine Berechtigung an, die gelöscht werden soll.", ephemeral=True)
            return
        
        if not user and not role:
            await interaction.response.send_message("Gebe entweder einen Benutzer oder eine Rolle an, von dem die Berechtigung gelöscht werden soll.", ephemeral=True)
            return
        
        permissions = load_permissions()
        
        # Berechtigung vollständig von einer Rolle löschen
        if role:
            if str(role.id) in permissions.get('roles', {}) and permission_node in permissions['roles'][str(role.id)]:
                del permissions['roles'][str(role.id)]
                await interaction.response.send_message(f"Die Berechtigung `{permission_node}` wurde vollständig von der Rolle `{role.name}` gelöscht.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Die Berechtigung `{permission_node}` ist der Rolle `{role.name}` nicht zugewiesen.", ephemeral=True)

        # Berechtigung vollständig von einem Benutzer löschen
        if user:
            if str(user.id) in permissions.get('users', {}) and permission_node in permissions['users'][str(user.id)]:
                del permissions['users'][str(user.id)]
                await interaction.response.send_message(f"Die Berechtigung `{permission_node}` wurde vollständig vom Benutzer `{user.name}` gelöscht.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Die Berechtigung `{permission_node}` ist dem Benutzer `{user.name}` nicht zugewiesen.", ephemeral=True)

        # Berechtigungen in der Datei speichern
        with open(config_file, 'w') as f:
            yaml.dump(permissions, f)

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(Permissions(bot))  # Hier wird der Cog korrekt hinzugefügt
