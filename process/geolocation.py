"""Module process : geolocalisation des adresses IP (recherche du pays)."""
import re

from src.log_config import get_logger

logger = get_logger("geolocation")

IP_PATTERN = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
UNKNOWN = "Inconnu"
LOCAL = "Reseau local"


def is_valid_ip(ip):
    """Vrai si ip est une adresse IPv4 correcte (4 nombres entre 0 et 255)."""
    if not isinstance(ip, str) or not IP_PATTERN.match(ip):
        return False
    return all(0 <= int(part) <= 255 for part in ip.split("."))


def is_private_ip(ip):
    """Vrai si l'IP est privee ou locale (10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x)."""
    first, second = (int(part) for part in ip.split(".")[:2])
    return (
        first == 10
        or first == 127
        or (first == 172 and 16 <= second <= 31)
        or (first == 192 and second == 168)
        or (first == 169 and second == 254)
    )


def country_from_table(ip, ip_country):
    """Cherche le pays dans la table CSV : correspondance par prefixe le plus long."""
    best, best_len = UNKNOWN, -1
    for prefix, country in ip_country.items():
        if ip.startswith(prefix) and len(prefix) > best_len:
            best, best_len = country, len(prefix)
    return best


def get_country(ip, ip_country):
    """Retourne le pays d'une IP. Ne plante jamais : en cas de probleme, retourne 'Inconnu'.

    Ordre : 1) IP invalide -> erreur loggee  2) IP privee -> 'Reseau local'
            3) recherche dans la table CSV (solution de secours locale).
    """
    try:
        if not is_valid_ip(ip):
            logger.error("Adresse IP invalide : %s", ip)
            return UNKNOWN
        if is_private_ip(ip):
            logger.info("IP privee detectee : %s", ip)
            return LOCAL
        country = country_from_table(ip, ip_country)
        if country == UNKNOWN:
            logger.warning("Aucun pays trouve pour l'IP %s", ip)
        return country
    except Exception as e:  # securite : la geolocalisation ne doit jamais arreter le pipeline
        logger.error("Erreur inattendue en geolocalisant %s : %s", ip, e)
        return UNKNOWN
    