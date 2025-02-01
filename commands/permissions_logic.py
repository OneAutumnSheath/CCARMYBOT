import os
import yaml

# Verzeichnis für die Konfiguration
config_dir = './config'
config_file = f'{config_dir}/permissions.yaml'

# Laden der Berechtigungen aus der YAML-Datei
def load_permissions():
    if not os.path.exists(config_file):
        return {}
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

# Berechtigungen für einen Befehl überprüfen
def check_permissions(permission_node, user_id, role_ids):
    permissions = load_permissions()
    for role_id in role_ids:
        if str(role_id) in permissions.get("roles", {}):
            if permission_node in permissions["roles"][str(role_id)] or "*" in permissions["roles"][str(role_id)]:
                return True
    if str(user_id) in permissions.get("users", {}):
        if "*" in permissions["users"][str(user_id)]:
            return True
    return False

# Berechtigungen für eine Rolle setzen
def set_permissions(role_id, commands):
    permissions = load_permissions()
    if "roles" not in permissions:
        permissions["roles"] = {}
    if str(role_id) not in permissions["roles"]:
        permissions["roles"][str(role_id)] = []
    permissions["roles"][str(role_id)] += commands
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f, default_flow_style=False)

# Berechtigungen für eine Rolle oder einen Benutzer anzeigen
def view_permissions(user_id=None, role_id=None):
    permissions = load_permissions()
    permissions_info = []

    if user_id:  # Zeige Berechtigungen für einen Benutzer
        if str(user_id) in permissions.get("users", {}):
            permissions_info.append(f"Permissions for User {user_id}: {permissions['users'][str(user_id)]}")
        else:
            permissions_info.append(f"No permissions found for User {user_id}")
    
    if role_id:  # Zeige Berechtigungen für eine Rolle
        if str(role_id) in permissions.get("roles", {}):
            permissions_info.append(f"Permissions for Role {role_id}: {permissions['roles'][str(role_id)]}")
        else:
            permissions_info.append(f"No permissions found for Role {role_id}")

    return "\n".join(permissions_info) if permissions_info else "No permissions data found."

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    print("Permissions logic loaded")
