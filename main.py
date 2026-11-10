"""Point d'entree du pipeline : ingestion -> process -> storage -> serving."""
from ingestion.reader import read_lines, load_ip_country
from process.parser import parse_lines
from process.analyzer import analyze
from storage.store import save_results, load_results
from serving.dashboard import print_dashboard, generate_html
from src.log_config import get_logger

try:
    from storage.database import save_events, get_stats
except ImportError:  # psycopg2 non installe : le pipeline continue avec le JSON
    save_events = None
    get_stats = None

logger = get_logger("main")

LOG_FILE = "data/auth.log"
IP_FILE = "data/ip_country.csv"
RESULT_FILE = "data/results.json"


def stats_from_database(events, ip_country):
    """Enregistre les tentatives dans PostgreSQL puis lit les statistiques en SQL.

    Retourne {} si PostgreSQL est inutilisable (le programme utilise alors le JSON).
    """
    if save_events is None:
        logger.warning("psycopg2 absent : PostgreSQL ignore, utilisation du JSON")
        return {}
    if not save_events(events, ip_country):
        logger.warning("PostgreSQL indisponible : utilisation du JSON")
        return {}
    return get_stats()


def main():
    lines = read_lines(LOG_FILE)                 # 1. ingestion
    ip_country = load_ip_country(IP_FILE)
    events = parse_lines(lines)                  # 2. process
    results = analyze(events, ip_country)
    save_results(results, RESULT_FILE)           # 3. storage : JSON (solution de secours)
    results = load_results(RESULT_FILE)
    db_results = stats_from_database(events, ip_country)   # 3. storage : PostgreSQL
    if db_results:
        results = db_results                     # statistiques calculees en SQL
    print_dashboard(results)                     # 4. serving
    generate_html(results)


if __name__ == "__main__":
    main()