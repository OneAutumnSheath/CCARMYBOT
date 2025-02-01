import discord
from discord.ext import commands
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
@commands.command(name="setpermissions")
async def set_permissions(ctx, user: discord.Member = None, role: discord.Role = None, permission_node: str = None):
    # Überprüfen, ob entweder ein Benutzer oder eine Rolle angegeben wurde
    if not user and not role:
        await ctx.send("Gebe Rolle oder User an, dem die Berechtigung gesetzt werden soll.", ephemeral=True)
        return

    if not permission_node:
        await ctx.send("Gebe eine Berechtigung (Node) an, die gesetzt werden soll.", ephemeral=True)
        return
    
    # Berechtigungen laden
    permissions = load_permissions()

    # Wenn eine Rolle angegeben wurde, setzen der Berechtigungen
    if role:
        # Berechtigungs-Logik für die Rolle
        if permission_node not in permissions.get('roles', {}):
            permissions['roles'][str(role.id)] = []
        permissions['roles'][str(role.id)].append(permission_node)
        await ctx.send(f"Die Berechtigung `{permission_node}` wurde der Rolle `{role.name}` zugewiesen.", ephemeral=True)
    
    # Wenn ein Benutzer angegeben wurde, setzen der Berechtigungen
    if user:
        # Berechtigungs-Logik für den Benutzer
        if permission_node not in permissions.get('users', {}):
            permissions['users'][str(user.id)] = []
        permissions['users'][str(user.id)].append(permission_node)
        await ctx.send(f"Die Berechtigung `{permission_node}` wurde dem Benutzer `{user.name}` zugewiesen.", ephemeral=True)
    
    # Berechtigungen in der Datei speichern
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f)

# Unsetzen von Berechtigungen für Benutzer oder Rollen
@commands.command(name="unsetpermission")
async def unset_permission(ctx, user: discord.Member = None, role: discord.Role = None, permission_node: str = None):
    # Überprüfen, ob entweder ein Benutzer oder eine Rolle angegeben wurde
    if not user and not role:
        await ctx.send("Gebe Rolle oder User an, von dem die Berechtigung entfernt werden soll.", ephemeral=True)
        return

    if not permission_node:
        await ctx.send("Gebe eine Berechtigung (Node) an, die entfernt werden soll.", ephemeral=True)
        return
    
    # Berechtigungen laden
    permissions = load_permissions()

    # Berechtigungen von der Rolle entfernen
    if role:
        if str(role.id) in permissions.get('roles', {}) and permission_node in permissions['roles'][str(role.id)]:
            permissions['roles'][str(role.id)].remove(permission_node)
            await ctx.send(f"Die Berechtigung `{permission_node}` wurde der Rolle `{role.name}` entfernt.", ephemeral=True)
        else:
            await ctx.send(f"Die Berechtigung `{permission_node}` ist nicht der Rolle `{role.name}` zugewiesen.", ephemeral=True)

    # Berechtigungen vom Benutzer entfernen
    if user:
        if str(user.id) in permissions.get('users', {}) and permission_node in permissions['users'][str(user.id)]:
            permissions['users'][str(user.id)].remove(permission_node)
            await ctx.send(f"Die Berechtigung `{permission_node}` wurde dem Benutzer `{user.name}` entfernt.", ephemeral=True)
        else:
            await ctx.send(f"Die Berechtigung `{permission_node}` ist dem Benutzer `{user.name}` nicht zugewiesen.", ephemeral=True)

    # Berechtigungen in der Datei speichern
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f)

# Zurücksetzen von Berechtigungen für Benutzer oder Rollen
@commands.command(name="resetpermissions")
async def reset_permissions(ctx, user: discord.Member = None, role: discord.Role = None):
    # Überprüfen, ob entweder ein Benutzer oder eine Rolle angegeben wurde
    if not user and not role:
        await ctx.send("Gebe Rolle oder User an, dessen Berechtigungen zurückgesetzt werden sollen.", ephemeral=True)
        return
    
    # Berechtigungen laden
    permissions = load_permissions()

    # Berechtigungen von der Rolle zurücksetzen
    if role:
        if str(role.id) in permissions.get('roles', {}):
            permissions['roles'][str(role.id)] = []
            await ctx.send(f"Alle Berechtigungen der Rolle `{role.name}` wurden zurückgesetzt.", ephemeral=True)
        else:
            await ctx.send(f"Die Rolle `{role.name}` hat keine zugewiesenen Berechtigungen.", ephemeral=True)

    # Berechtigungen vom Benutzer zurücksetzen
    if user:
        if str(user.id) in permissions.get('users', {}):
            permissions['users'][str(user.id)] = []
            await ctx.send(f"Alle Berechtigungen des Benutzers `{user.name}` wurden zurückgesetzt.", ephemeral=True)
        else:
            await ctx.send(f"Der Benutzer `{user.name}` hat keine zugewiesenen Berechtigungen.", ephemeral=True)

    # Berechtigungen in der Datei speichern
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f)

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(Permissions(bot))
