"""Point d'entree du pipeline : ingestion -> process -> storage -> serving."""
from ingestion.reader import read_lines, load_ip_country
from process.parser import parse_lines
from process.analyzer import analyze
from storage.store import save_results, load_results
from serving.dashboard import print_dashboard, generate_html

LOG_FILE = "data/auth.log"
IP_FILE = "data/ip_country.csv"
RESULT_FILE = "data/results.json"


def main():
    lines = read_lines(LOG_FILE)                 # 1. ingestion
    ip_country = load_ip_country(IP_FILE)
    events = parse_lines(lines)                  # 2. process
    results = analyze(events, ip_country)
    save_results(results, RESULT_FILE)           # 3. storage
    results = load_results(RESULT_FILE)
    print_dashboard(results)                     # 4. serving
    generate_html(results)


if __name__ == "__main__":
    main()
