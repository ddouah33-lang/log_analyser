"""Module ingestion : lecture du fichier de logs et de la table IP -> pays."""
import csv

from src.log_config import get_logger

logger = get_logger("ingestion")


def read_lines(path):
    """Lit le fichier de logs et retourne la liste des lignes non vides."""
    lines = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    lines.append(line)
    except FileNotFoundError:
        logger.error("Fichier de logs introuvable : %s", path)
        return []
    except PermissionError:
        logger.error("Permission refusee pour lire : %s", path)
        return []
    except UnicodeDecodeError as e:
        logger.error("Erreur d'encodage dans %s : %s", path, e)
        return []
    except OSError as e:
        logger.error("Erreur systeme en lisant %s : %s", path, e)
        return []

    if not lines:
        logger.warning("Le fichier %s est vide", path)
    else:
        logger.info("%d lignes lues depuis %s", len(lines), path)
    return lines


def load_ip_country(path):
    """Charge le CSV 'prefixe_ip,pays' dans un dictionnaire."""
    table = {}
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for num, row in enumerate(reader, 1):
                if len(row) != 2:
                    logger.warning("%s ligne %d ignoree (format invalide) : %s", path, num, row)
                    continue
                table[row[0].strip()] = row[1].strip()
    except FileNotFoundError:
        logger.error("Table IP/pays introuvable : %s", path)
    except PermissionError:
        logger.error("Permission refusee pour lire : %s", path)
    except OSError as e:
        logger.error("Erreur systeme en lisant %s : %s", path, e)
    logger.info("%d prefixes IP charges", len(table))
    return table
