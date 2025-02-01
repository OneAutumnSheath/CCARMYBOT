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
    permissions = load_permissions()  # Lädt die Berechtigungen aus der YAML-Datei

    # Zuerst prüfen, ob der Benutzer "*" hat (für alle Berechtigungen)
    if str(user_id) in permissions.get("users", {}):
        if "*" in permissions["users"][str(user_id)]:
            return True
        if permission_node in permissions["roles"][str(role_id)]:
                return True

    # Prüfe die Berechtigungen für jede Rolle des Benutzers
    for role_id in role_ids:
        if str(role_id) in permissions.get("roles", {}):
            # Zuerst prüfen, ob die Rolle "*" hat (für alle Berechtigungen)
            if "*" in permissions["roles"][str(role_id)]:
                return True
            # Dann prüfe die spezifische Berechtigung
            if permission_node in permissions["roles"][str(role_id)]:
                return True

    # Wenn keine "*" und keine spezifische Berechtigung gefunden, zurückgeben False
    return False


# Berechtigungen für eine Rolle oder einen Benutzer setzen
def set_permissions(identifier, commands, is_user=False):
    permissions = load_permissions()
    
    if is_user:  # Falls ein Benutzer und nicht eine Rolle
        if "users" not in permissions:
            permissions["users"] = {}
        if str(identifier) not in permissions["users"]:
            permissions["users"][str(identifier)] = []
        permissions["users"][str(identifier)].extend(commands)
    else:  # Für eine Rolle
        if "roles" not in permissions:
            permissions["roles"] = {}
        if str(identifier) not in permissions["roles"]:
            permissions["roles"][str(identifier)] = []
        permissions["roles"][str(identifier)].extend(commands)
    
    # Berechtigungen in der Datei speichern
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
def unset_permissions(user_or_role_id, command_names):
    """Entfernt Berechtigungen für einen Benutzer oder eine Rolle."""
    permissions = load_permissions()
    
    # Entferne die Berechtigungen für die angegebene ID (Rolle oder Benutzer)
    if str(user_or_role_id) in permissions.get("roles", {}):
        for command in command_names:
            if command in permissions["roles"][str(user_or_role_id)]:
                permissions["roles"][str(user_or_role_id)].remove(command)

    # Speichere die Änderungen zurück in die Datei
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f, default_flow_style=False)
def reset_permissions(user_or_role_id):
    """Setzt alle Berechtigungen für einen Benutzer oder eine Rolle zurück."""
    permissions = load_permissions()

    # Lösche alle Berechtigungen für den angegebenen Benutzer oder die Rolle
    if str(user_or_role_id) in permissions.get("roles", {}):
        permissions["roles"][str(user_or_role_id)] = []

    # Speichere die Änderungen zurück in die Datei
    with open(config_file, 'w') as f:
        yaml.dump(permissions, f, default_flow_style=False)

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    print("Permissions logic loaded")
