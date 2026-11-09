"""Module serving : dashboard (console + page HTML sans package externe)."""
import html
import os

from src.log_config import get_logger

logger = get_logger("serving")

TITLES = {
    "failed_by_country": "Tentatives echouees par pays",
    "success_by_user": "Tentatives reussies par utilisateur",
    "failed_invalid_user": "Tentatives echouees avec 'invalid user'",
}


def _sorted(data):
    return sorted(data.items(), key=lambda item: item[1], reverse=True)


def print_dashboard(results):
    """Affiche le dashboard dans la console."""
    if not results:
        logger.error("Aucun resultat a afficher")
        print("Aucun resultat a afficher.")
        return
    for key, title in TITLES.items():
        data = results.get(key, {})
        print(f"\n=== {title} ===")
        if not data:
            print("  (aucune donnee)")
            logger.warning("Aucune donnee pour : %s", key)
            continue
        biggest = max(data.values())
        for name, count in _sorted(data):
            bar = "#" * max(1, round(30 * count / biggest))
            print(f"  {name:<20} {count:>4} {bar}")


def generate_html(results, path="dashboard.html"):
    """Genere une page HTML avec des barres (CSS pur)."""
    try:
        sections = []
        for key, title in TITLES.items():
            data = results.get(key, {})
            rows = ""
            if data:
                biggest = max(data.values())
                for name, count in _sorted(data):
                    width = round(100 * count / biggest)
                    rows += (
                        f"<div class='row'><span class='lbl'>{html.escape(str(name))}</span>"
                        f"<div class='bar' style='width:{width}%'></div>"
                        f"<span class='val'>{count}</span></div>"
                    )
            else:
                rows = "<p>Aucune donnee</p>"
            sections.append(f"<section><h2>{title}</h2>{rows}</section>")

        page = (
            "<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
            "<title>Dashboard Log Analyser</title><style>"
            "body{font-family:Arial,sans-serif;background:#0f172a;color:#e2e8f0;max-width:800px;margin:auto;padding:20px}"
            "section{background:#1e293b;border-radius:10px;padding:16px;margin-bottom:20px}"
            "h2{margin-top:0;color:#38bdf8}.row{display:flex;align-items:center;gap:10px;margin:6px 0}"
            ".lbl{width:140px}.bar{height:16px;background:#38bdf8;border-radius:4px}.val{font-weight:bold}"
            "</style></head><body><h1>Dashboard - Log Analyser</h1>"
            + "".join(sections)
            + "</body></html>"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        logger.info("Dashboard HTML genere : %s", os.path.abspath(path))
        return True
    except OSError as e:
        logger.error("Impossible d'ecrire %s : %s", path, e)
        return False
