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


# Textes et couleurs utilises seulement par la page HTML (la console garde TITLES).
HTML_TITLES = {
    "failed_by_country": "Tentatives échouées par pays",
    "success_by_user": "Tentatives réussies par utilisateur",
    "failed_invalid_user": "Tentatives échouées avec « invalid user »",
}
SUMMARY_LABELS = {
    "failed_by_country": "tentatives échouées",
    "success_by_user": "connexions réussies",
    "failed_invalid_user": "échecs « invalid user »",
}
ACCENTS = {
    "failed_by_country": "#f87171",
    "success_by_user": "#4ade80",
    "failed_invalid_user": "#fbbf24",
}

STYLE = (
    ":root{--card:#162033;--text:#e2e8f0;--muted:#94a3b8}"
    "*{box-sizing:border-box}"
    "body{margin:0;font-family:'Segoe UI',Arial,sans-serif;color:var(--text);min-height:100vh;"
    "background:linear-gradient(160deg,#0b1120,#111c33)}"
    ".wrap{max-width:900px;margin:auto;padding:32px 20px}"
    "header h1{margin:0;font-size:2rem}"
    "header p{color:var(--muted);margin:6px 0 24px}"
    ".summary{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:24px}"
    ".kpi{flex:1;min-width:200px;background:var(--card);border-radius:14px;padding:16px 18px;"
    "border-top:4px solid var(--accent)}"
    ".num{font-size:2.2rem;font-weight:700;color:var(--accent)}"
    ".txt{color:var(--muted);font-size:.9rem}"
    "section{background:var(--card);border-radius:14px;padding:20px 22px;margin-bottom:20px;"
    "box-shadow:0 6px 18px rgba(0,0,0,.35);border-left:5px solid var(--accent)}"
    "h2{margin:0 0 14px;font-size:1.15rem;color:var(--accent)}"
    ".row{display:grid;grid-template-columns:130px 1fr 80px;align-items:center;gap:12px;margin:9px 0}"
    ".lbl{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}"
    ".track{background:#0f172a;border-radius:999px;height:14px;overflow:hidden}"
    ".bar{height:100%;border-radius:999px;background-color:var(--accent);"
    "background-image:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.28))}"
    ".val{text-align:right;font-weight:700}"
    ".pct{color:var(--muted);font-weight:400;font-size:.8rem;margin-left:5px}"
    ".empty{color:var(--muted)}"
    "footer{text-align:center;color:var(--muted);font-size:.8rem;margin-top:8px}"
    "@media(max-width:560px){.row{grid-template-columns:90px 1fr 70px}}"
)


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


def _summary_html(results):
    """Les 3 cartes de chiffres en haut de la page."""
    cards = ""
    for key, label in SUMMARY_LABELS.items():
        total = sum(results.get(key, {}).values())
        cards += (
            f"<div class='kpi' style='--accent:{ACCENTS[key]}'>"
            f"<div class='num'>{total}</div><div class='txt'>{label}</div></div>"
        )
    return f"<div class='summary'>{cards}</div>"


def _section_html(key, data):
    """Une section du dashboard : un titre et une barre par ligne."""
    if data:
        total = sum(data.values())
        biggest = max(data.values())
        rows = ""
        for name, count in _sorted(data):
            width = round(100 * count / biggest)
            percent = round(100 * count / total)
            rows += (
                f"<div class='row'><span class='lbl'>{html.escape(str(name))}</span>"
                f"<div class='track'><div class='bar' style='width:{width}%'></div></div>"
                f"<span class='val'>{count}<span class='pct'>{percent}%</span></span></div>"
            )
    else:
        rows = "<p class='empty'>Aucune donnée</p>"
    return f"<section style='--accent:{ACCENTS[key]}'><h2>{HTML_TITLES[key]}</h2>{rows}</section>"


def generate_html(results, path="dashboard.html"):
    """Genere la page HTML du dashboard (CSS pur, aucun package externe)."""
    try:
        sections = "".join(_section_html(key, results.get(key, {})) for key in TITLES)
        page = (
            "<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>Dashboard Log Analyser</title><style>" + STYLE + "</style></head><body>"
            "<div class='wrap'><header><h1>Dashboard - Log Analyser</h1>"
            "<p>Analyse des tentatives de connexion SSH</p></header>"
            + _summary_html(results)
            + sections
            + "<footer>Pipeline Log Analyser</footer></div></body></html>"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        logger.info("Dashboard HTML genere : %s", os.path.abspath(path))
        return True
    except OSError as e:
        logger.error("Impossible d'ecrire %s : %s", path, e)
    except (AttributeError, TypeError) as e:
        logger.error("Resultats invalides, page HTML non generee : %s", e)
    return False