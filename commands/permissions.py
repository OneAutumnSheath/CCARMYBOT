import logging
import yaml
from collections import defaultdict

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

permissions = defaultdict(dict)  # {user_id: {permission_node: bool}}
class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_permissions(file_path="permissions.yaml"):
        try:
            with open(file_path, "r") as file:
                permissions_data = yaml.safe_load(file)
                if permissions_data:
                    global permissions
                    permissions = permissions_data
                    logger.info(f"Berechtigungen erfolgreich aus {file_path} geladen.")
                else:
                    logger.warning(f"Die Datei {file_path} ist leer.")
        except FileNotFoundError:
           logger.error(f"Die Datei {file_path} wurde nicht gefunden.")
        except yaml.YAMLError as e:
           logger.error(f"Fehler beim Laden der YAML-Datei {file_path}: {e}")
        except Exception as e:
           logger.error(f"Unbekannter Fehler beim Laden der Berechtigungen: {e}")

    def save_permissions(file_path="permissions.yaml"):
        try:
            with open(file_path, "w") as file:
                yaml.dump(permissions, file)
                logger.info(f"Berechtigungen erfolgreich in {file_path} gespeichert.")
        except IOError as e:
            logger.error(f"Fehler beim Speichern der Berechtigungen in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unbekannter Fehler beim Speichern der Berechtigungen: {e}")

    def check_permissions(permission_node, user_id, role_ids):
        try:
            # Prüfe Benutzer-spezifische Berechtigungen
            if str(user_id) in permissions.get("users", {}):
                user_perms = permissions["users"][str(user_id)]
                if "*" in user_perms or permission_node in user_perms:
                    return True

            # Prüfe Rollen-spezifische Berechtigungen
            for role_id in role_ids:
                if str(role_id) in permissions.get("roles", {}):
                    role_perms = permissions["roles"][str(role_id)]
                    if "*" in role_perms or permission_node in role_perms:
                        return True

            logger.info(f"Berechtigung {permission_node} für Benutzer {user_id} oder eine Rolle nicht gefunden.")
            return False
        except Exception as e:
            logger.error(f"Fehler bei der Berechtigungsprüfung für Benutzer {user_id} und Node {permission_node}: {e}")
            return False
# Setup-Funktion zum Hinzufügen des Cogs
async def setup(bot):
    await bot.add_cog(Permissions(bot))  # Hier wird der Permissions-Cog dem Bot hinzugefügt
