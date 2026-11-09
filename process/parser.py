"""Module process : analyse (parsing) des lignes de logs SSH."""
import re

from src.log_config import get_logger

logger = get_logger("process")

PATTERN = re.compile(
    r"^(?P<date>\w{3}\s+\d+\s[\d:]{8})\s+(?P<host>\S+)\s+sshd\[(?P<pid>\d+)\]:\s+"
    r"(?P<status>Failed|Accepted)\s+\w+\s+for\s+(?P<invalid>invalid user\s+)?"
    r"(?P<user>\S+)\s+from\s+(?P<ip>\d{1,3}(?:\.\d{1,3}){3})"
)


def valid_ip(ip):
    """Verifie que chaque octet de l'IP est entre 0 et 255."""
    return all(0 <= int(part) <= 255 for part in ip.split("."))


def parse_line(line):
    """Transforme une ligne de log en dictionnaire, ou None si non exploitable."""
    try:
        match = PATTERN.match(line)
        if not match:
            logger.warning("Ligne non reconnue : %s", line)
            return None
        data = match.groupdict()
        if not valid_ip(data["ip"]):
            logger.error("Adresse IP invalide (%s) dans la ligne : %s", data["ip"], line)
            return None
        return {
            "date": data["date"],
            "user": data["user"],
            "ip": data["ip"],
            "success": data["status"] == "Accepted",
            "invalid_user": data["invalid"] is not None,
        }
    except Exception as e:  # securite : une ligne ne doit jamais arreter le pipeline
        logger.error("Erreur inattendue en parsant '%s' : %s", line, e)
        return None


def parse_lines(lines):
    """Parse toutes les lignes et retourne la liste des evenements valides."""
    events = []
    for line in lines:
        event = parse_line(line)
        if event:
            events.append(event)
    logger.info("%d evenements valides sur %d lignes", len(events), len(lines))
    return events
