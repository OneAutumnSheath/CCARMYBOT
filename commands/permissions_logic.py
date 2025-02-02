import logging
from permissions import load_permissions, save_permissions

# Logging konfigurieren
logger = logging.getLogger(__name__)

class PermissionsLogic:
    def __init__(self):
        load_permissions()  # Berechtigungen beim Start des Cogs laden

    def set_permissions(self, user_id, permission_node, value):
        try:
            if permission_node not in permissions["users"].get(str(user_id), {}):
                permissions["users"][str(user_id)] = {}

            permissions["users"][str(user_id)][permission_node] = value
            save_permissions()
            logger.info(f"Berechtigung {permission_node} für Benutzer {user_id} auf {value} gesetzt.")
        except Exception as e:
            logger.error(f"Fehler beim Setzen der Berechtigung {permission_node} für Benutzer {user_id}: {e}")

    def unset_permissions(self, user_id, permission_node):
        try:
            if str(user_id) in permissions["users"] and permission_node in permissions["users"][str(user_id)]:
                del permissions["users"][str(user_id)][permission_node]
                save_permissions()
                logger.info(f"Berechtigung {permission_node} für Benutzer {user_id} entfernt.")
        except Exception as e:
            logger.error(f"Fehler beim Entfernen der Berechtigung {permission_node} für Benutzer {user_id}: {e}")

    def view_permissions(self, user_id):
        try:
            user_permissions = permissions["users"].get(str(user_id), {})
            if not user_permissions:
                logger.info(f"Benutzer {user_id} hat keine Berechtigungen.")
                return f"Benutzer {user_id} hat keine Berechtigungen."
            
            perms_message = f"Berechtigungen für Benutzer {user_id}:\n"
            for permission_node, value in user_permissions.items():
                perms_message += f"- {permission_node}: {value}\n"
            logger.info(f"Angeforderte Berechtigungen für Benutzer {user_id} angezeigt.")
            return perms_message
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Berechtigungen für Benutzer {user_id}: {e}")
            return f"Fehler beim Abrufen der Berechtigungen für Benutzer {user_id}."

# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    print("Permissions logic loaded")
