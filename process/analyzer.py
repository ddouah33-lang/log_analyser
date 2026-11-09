"""Module process : calcul des statistiques du dashboard."""
from src.log_config import get_logger

logger = get_logger("process")


def country_of(ip, ip_country):
    """Pays d'une IP : correspondance par prefixe le plus long."""
    best, best_len = "Inconnu", -1
    for prefix, country in ip_country.items():
        if ip.startswith(prefix) and len(prefix) > best_len:
            best, best_len = country, len(prefix)
    return best


def failed_by_country(events, ip_country):
    result = {}
    for e in events:
        if not e["success"]:
            country = country_of(e["ip"], ip_country)
            result[country] = result.get(country, 0) + 1
    return result


def success_by_user(events):
    result = {}
    for e in events:
        if e["success"]:
            result[e["user"]] = result.get(e["user"], 0) + 1
    return result


def failed_invalid_user(events):
    result = {}
    for e in events:
        if not e["success"] and e["invalid_user"]:
            result[e["user"]] = result.get(e["user"], 0) + 1
    return result


def analyze(events, ip_country):
    """Retourne les 3 statistiques demandees."""
    try:
        results = {
            "failed_by_country": failed_by_country(events, ip_country),
            "success_by_user": success_by_user(events),
            "failed_invalid_user": failed_invalid_user(events),
        }
        logger.info("Statistiques calculees")
        return results
    except Exception as e:
        logger.error("Erreur pendant le calcul des statistiques : %s", e)
        return {"failed_by_country": {}, "success_by_user": {}, "failed_invalid_user": {}}
