"""Module storage : sauvegarde et chargement des resultats (JSON)."""
import json
import os

from src.log_config import get_logger

logger = get_logger("storage")


def save_results(results, path):
    try:
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info("Resultats sauvegardes dans %s", path)
        return True
    except PermissionError:
        logger.error("Permission refusee pour ecrire : %s", path)
    except TypeError as e:
        logger.error("Donnees non serialisables en JSON : %s", e)
    except OSError as e:
        logger.error("Erreur systeme en ecrivant %s : %s", path, e)
    return False


def load_results(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Fichier de resultats introuvable : %s", path)
    except json.JSONDecodeError as e:
        logger.error("JSON invalide dans %s : %s", path, e)
    except OSError as e:
        logger.error("Erreur systeme en lisant %s : %s", path, e)
    return {}
