"""Module storage : sauvegarde et lecture des tentatives de connexion dans PostgreSQL."""
import os

import psycopg2

from process.geolocation import get_country
from src.log_config import get_logger

logger = get_logger("storage")

INSERT_SQL = (
    "INSERT INTO login_attempts (log_date, username, ip_address, country, success, invalid_user) "
    "VALUES (%s, %s, %s, %s, %s, %s)"
)

# Les 3 statistiques du dashboard, calculees directement en SQL.
STATS_QUERIES = {
    "failed_by_country": (
        "SELECT country, COUNT(*) FROM login_attempts "
        "WHERE success = FALSE GROUP BY country ORDER BY COUNT(*) DESC, country"
    ),
    "success_by_user": (
        "SELECT username, COUNT(*) FROM login_attempts "
        "WHERE success = TRUE GROUP BY username ORDER BY COUNT(*) DESC, username"
    ),
    "failed_invalid_user": (
        "SELECT username, COUNT(*) FROM login_attempts "
        "WHERE success = FALSE AND invalid_user = TRUE "
        "GROUP BY username ORDER BY COUNT(*) DESC, username"
    ),
}


def get_connection():
    """Ouvre la connexion PostgreSQL. Retourne None si elle est impossible.

    Le mot de passe est lu dans la variable d'environnement DB_PASSWORD
    (il ne doit jamais etre ecrit dans le code ni envoye sur GitHub).
    """
    password = os.environ.get("DB_PASSWORD")
    if not password:
        logger.error("Variable d'environnement DB_PASSWORD absente : connexion impossible")
        return None
    try:
        return psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", "5432")),
            dbname=os.environ.get("DB_NAME", "log_analyser"),
            user=os.environ.get("DB_USER", "postgres"),
            password=password,
        )
    except psycopg2.OperationalError as e:
        logger.error("Connexion PostgreSQL impossible : %s", e)
    except ValueError as e:
        logger.error("Port PostgreSQL invalide dans DB_PORT : %s", e)
    return None


def save_events(events, ip_country):
    """Remplace le contenu de login_attempts par les evenements du fichier de logs.

    On vide la table avant d'inserer : relancer le programme ne cree donc pas de doublons.
    Tout se fait dans une seule transaction (si une erreur arrive, rien n'est modifie).
    Retourne True si tout s'est bien passe, False sinon.
    """
    conn = get_connection()
    if conn is None:
        return False
    try:
        rows = [
            (
                e["date"],
                e["user"],
                e["ip"],
                get_country(e["ip"], ip_country),
                e["success"],
                e["invalid_user"],
            )
            for e in events
        ]
        with conn:  # valide (commit) la transaction, ou l'annule (rollback) en cas d'erreur
            with conn.cursor() as cur:
                cur.execute("DELETE FROM login_attempts")
                cur.executemany(INSERT_SQL, rows)
        logger.info("%d tentatives enregistrees dans PostgreSQL", len(rows))
        return True
    except psycopg2.Error as e:
        logger.error("Erreur SQL pendant l'enregistrement : %s", e)
    except (KeyError, TypeError) as e:
        logger.error("Evenement mal forme, enregistrement annule : %s", e)
    finally:
        conn.close()
    return False


def get_stats():
    """Calcule les 3 statistiques avec des requetes SQL.

    Retourne le meme format que process.analyzer.analyze(), ou {} si la base est inaccessible.
    """
    conn = get_connection()
    if conn is None:
        return {}
    try:
        results = {}
        with conn.cursor() as cur:
            for key, query in STATS_QUERIES.items():
                cur.execute(query)
                results[key] = {name: count for name, count in cur.fetchall()}
        logger.info("Statistiques lues depuis PostgreSQL")
        return results
    except psycopg2.Error as e:
        logger.error("Erreur SQL pendant le calcul des statistiques : %s", e)
        return {}
    finally:
        conn.close()