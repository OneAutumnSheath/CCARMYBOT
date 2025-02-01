import discord
from discord.ext import commands
from discord import app_commands
import yaml
import os

# Pfad zur Config
config_file = './config/permissions.yaml'

# Berechtigungsprüfung laden
def load_permissions():
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found at {config_file}")

    with open(config_file, 'r') as f:
        permissions = yaml.safe_load(f)

    return permissions

# Setzen von Berechtigungen für Benutzer oder Rollen
@commands.hybrid_command(name="setpermissions", description="Setze Berechtigungen für eine Rolle oder einen Benutzer")
async def set_permissions(ctx, user: discord.User = None, role: discord.Role = None, permission_node: str = None):
    """Setzt Berechtigungen für einen Benutzer oder eine Rolle."""
    
    if not user and not role:
        await ctx.send("Gebe entweder einen Benutzer oder eine Rolle an, dem die Berechtigung gesetzt werden soll.", ephemeral=True)
        return

    if not permission_node:
        await ctx.send("Gebe eine Berechtigung (Node) an, die gesetzt werden soll.", ephemeral=True)
        return
    
    # Berechtigungen laden
    permissions = load_permissions()

    # Berechtigung einer Rolle zuweisen
    if role:
        if permission_node not in permissions.get('roles', {}):
            permissions['roles'][str(role.id)] = []
        permissions['roles'][str(role.id)].append(permission_node)
        await ctx.send(f"Die Berechtigung `{permission_node}` wurde der Rolle `{role.name}` zugewiesen.", ephemeral=True)
    
    # Berechtigung einem Benutzer zuweisen
    if user:
        if permission_node not in permissions.get('users', {}):
            permissions['users'][str(user.id)] = []
        permissions['users'][str(user.id)].append(permission_node)
        await ctx.send(f"Die Berechtigung `{permission_node}` wurde dem Benutzer `{user.name}` zugewiesen.", ephemeral=True)
    
    # Berechtigungen in der Datei speichern
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f)

# Unsetzen von Berechtigungen für Benutzer oder Rollen
@commands.hybrid_command(name="unsetpermission", description="Entferne eine Berechtigung von einer Rolle oder einem Benutzer")
async def unset_permission(ctx, user: discord.User = None, role: discord.Role = None, permission_node: str = None):
    """Entfernt eine Berechtigung von einem Benutzer oder einer Rolle."""
    
    if not permission_node:
        await ctx.send("Bitte gib eine Berechtigung an, die entfernt werden soll.", ephemeral=True)
        return
    
    if not user and not role:
        await ctx.send("Gebe entweder einen Benutzer oder eine Rolle an, von dem die Berechtigung entfernt werden soll.", ephemeral=True)
        return
    
    permissions = load_permissions()
    
    # Berechtigung von einer Rolle entfernen
    if role:
        if str(role.id) in permissions.get('roles', {}) and permission_node in permissions['roles'][str(role.id)]:
            permissions['roles'][str(role.id)].remove(permission_node)
            await ctx.send(f"Die Berechtigung `{permission_node}` wurde der Rolle `{role.name}` entfernt.", ephemeral=True)
        else:
            await ctx.send(f"Die Berechtigung `{permission_node}` ist der Rolle `{role.name}` nicht zugewiesen.", ephemeral=True)

    # Berechtigung von einem Benutzer entfernen
    if user:
        if str(user.id) in permissions.get('users', {}) and permission_node in permissions['users'][str(user.id)]:
            permissions['users'][str(user.id)].remove(permission_node)
            await ctx.send(f"Die Berechtigung `{permission_node}` wurde dem Benutzer `{user.name}` entfernt.", ephemeral=True)
        else:
            await ctx.send(f"Die Berechtigung `{permission_node}` ist dem Benutzer `{user.name}` nicht zugewiesen.", ephemeral=True)

    # Berechtigungen in der Datei speichern
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f)

# Slash-Befehl: delpermission
@commands.hybrid_command(name="delpermission", description="Löscht eine Berechtigung vollständig von einem Benutzer oder einer Rolle")
async def delpermission(ctx, user: discord.User = None, role: discord.Role = None, permission_node: str = None):
    """Löscht eine Berechtigung vollständig von einem Benutzer oder einer Rolle."""
    
    if not permission_node:
        await ctx.send("Bitte gib eine Berechtigung an, die gelöscht werden soll.", ephemeral=True)
        return
    
    if not user and not role:
        await ctx.send("Gebe entweder einen Benutzer oder eine Rolle an, von dem die Berechtigung gelöscht werden soll.", ephemeral=True)
        return
    
    permissions = load_permissions()
    
    # Berechtigung vollständig von einer Rolle löschen
    if role:
        if str(role.id) in permissions.get('roles', {}) and permission_node in permissions['roles'][str(role.id)]:
            del permissions['roles'][str(role.id)]
            await ctx.send(f"Die Berechtigung `{permission_node}` wurde vollständig von der Rolle `{role.name}` gelöscht.", ephemeral=True)
        else:
            await ctx.send(f"Die Berechtigung `{permission_node}` ist der Rolle `{role.name}` nicht zugewiesen.", ephemeral=True)

    # Berechtigung vollständig von einem Benutzer löschen
    if user:
        if str(user.id) in permissions.get('users', {}) and permission_node in permissions['users'][str(user.id)]:
            del permissions['users'][str(user.id)]
            await ctx.send(f"Die Berechtigung `{permission_node}` wurde vollständig vom Benutzer `{user.name}` gelöscht.", ephemeral=True)
        else:
            await ctx.send(f"Die Berechtigung `{permission_node}` ist dem Benutzer `{user.name}` nicht zugewiesen.", ephemeral=True)

    # Berechtigungen in der Datei speichern
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f)

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(Permissions(bot))  # Hier wird der Cog korrekt hinzugefügt
