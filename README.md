# Pipeline Log Analyser

Projet Python Avancé – 3ème année (ESISA)
Auteur : SAD DOUAH

## Objectif

Ce projet analyse un fichier de logs SSH (`auth.log`) et produit un dashboard
qui répond à trois questions :

1. Combien de tentatives de connexion **échouées par pays** ?
2. Combien de tentatives **réussies par utilisateur** ?
3. Quelles sont les tentatives **échouées avec « invalid user »** ?

Le projet utilise la bibliothèque standard de Python (`logging`, `re`, `csv`,
`json`, `unittest`). Le seul package externe est `psycopg2-binary`, qui sert à
connecter Python à PostgreSQL.

## Architecture du pipeline

```
data/auth.log ──► ingestion ──► process ──► storage ──────────► serving
                  (lecture)    (parsing,    (PostgreSQL         (dashboard
                               géolocalisation, + JSON de       console + HTML)
                               statistiques)    secours)
```

| Dossier | Rôle |
|---|---|
| `ingestion/` | Lecture du fichier de logs et de la table IP → pays (`data/ip_country.csv`) |
| `process/` | `parser.py` : analyse de chaque ligne avec un regex ; `geolocation.py` : recherche du pays d'une IP ; `analyzer.py` : calcul des 3 statistiques |
| `storage/` | `database.py` : enregistrement et statistiques SQL dans PostgreSQL ; `store.py` : sauvegarde JSON (`data/results.json`) |
| `serving/` | Affichage du dashboard dans la console et génération de `dashboard.html` |
| `src/` | Configuration des logs (`log_config.py`) |
| `tests/` | Tests unitaires (`unittest`) |
| `data/` | Fichier de logs et table IP → pays |

## Géolocalisation des adresses IP

Le module `process/geolocation.py` donne le pays de chaque adresse IP :

1. Une **IP invalide** (par exemple `999.1.1.1`) donne « Inconnu » et une erreur est enregistrée dans les logs.
2. Une **IP privée** (`10.x`, `172.16-31.x`, `192.168.x`, `127.x`, `169.254.x`) donne « Reseau local ».
3. Sinon, le pays est cherché dans `data/ip_country.csv` par préfixe le plus long. Si rien n'est trouvé, le résultat est « Inconnu » (avertissement dans les logs).

La fonction ne plante jamais : en cas d'erreur inattendue, elle renvoie « Inconnu » et enregistre l'erreur.

## Stockage des données

Le stockage se fait de deux façons :

- **PostgreSQL** (stockage principal) : base `log_analyser`, table `login_attempts`.
  Chaque tentative de connexion y est enregistrée (date du log, utilisateur, adresse IP, pays,
  succès ou échec, « invalid user »). Les 3 statistiques du dashboard sont calculées par des requêtes SQL
  (`COUNT` et `GROUP BY`).
  La table est vidée avant chaque enregistrement, dans une seule transaction : relancer le
  programme ne crée donc pas de doublons.
- **JSON** (solution de secours) : `data/results.json`. Si PostgreSQL est inaccessible
  (serveur arrêté, mot de passe absent, `psycopg2` non installé), le programme continue avec les
  statistiques du JSON et enregistre un avertissement dans les logs.

## Gestion des logs de l'application

Chaque module écrit ses propres logs dans le dossier `logs/` :
`ingestion.log`, `process.log`, `geolocation.log`, `storage.log`, `serving.log`, `main.log`.
Le fichier est géré avec `RotatingFileHandler` (rotation à 100 Ko, 3 sauvegardes).

Erreurs enregistrées par module :

- **ingestion** : fichier introuvable, permission refusée, erreur d'encodage, fichier vide, ligne invalide dans le CSV des pays
- **process** : ligne non reconnue, adresse IP invalide, erreur inattendue pendant le parsing ou le calcul
- **geolocation** : adresse IP invalide, aucun pays trouvé, erreur inattendue
- **storage** : permission refusée, données non sérialisables, JSON invalide, fichier introuvable, mot de passe `DB_PASSWORD` absent, connexion PostgreSQL impossible, erreur SQL, événement mal formé
- **serving** : aucun résultat à afficher, aucune donnée pour un indicateur, erreur d'écriture du HTML
- **main** : PostgreSQL indisponible ou `psycopg2` absent (le programme utilise alors le JSON)

## Installation et lancement

Prérequis : Python 3.10 ou plus récent, et PostgreSQL (avec pgAdmin).

1. Installer le connecteur PostgreSQL :

```
pip install psycopg2-binary
```

2. Dans pgAdmin, créer la base `log_analyser`, puis exécuter dans le Query Tool :

```sql
CREATE TABLE login_attempts (
    id SERIAL PRIMARY KEY,
    log_date VARCHAR(20) NOT NULL,
    username VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    country VARCHAR(100),
    success BOOLEAN NOT NULL,
    invalid_user BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

3. Donner le mot de passe de l'utilisateur `postgres` au programme avec une variable
   d'environnement (PowerShell). Le mot de passe n'est jamais écrit dans le code :

```
$env:DB_PASSWORD = "votre_mot_de_passe"
```

Par défaut, la connexion utilise `localhost`, le port `5432`, la base `log_analyser` et
l'utilisateur `postgres`. On peut les changer avec `DB_HOST`, `DB_PORT`, `DB_NAME` et `DB_USER`.

4. Lancer le programme :

```
python main.py
```

Le programme affiche le dashboard dans la console et crée `dashboard.html`
(à ouvrir dans un navigateur).

## Tests

```
python -m unittest discover -s tests -v
```

Les 17 tests couvrent le parsing, les statistiques, la géolocalisation et la gestion des
erreurs de connexion à la base (ils n'ont pas besoin d'une vraie base PostgreSQL).

## Exemple de résultat

```
=== Tentatives echouees par pays ===
  Russie                  4 ##############################
  Chine                   2 ###############
  Etats-Unis              2 ###############
  Maroc                   1 ########
  Inconnu                 1 ########

=== Tentatives reussies par utilisateur ===
  saad                    2 ##############################
  alice                   2 ##############################
  bob                     1 ###############

=== Tentatives echouees avec 'invalid user' ===
  admin                   3 ##############################
  test                    1 ##########
  oracle                  1 ##########
  ubuntu                  1 ##########
  guest                   1 ##########
```

## Remarques

- Le pays d'une IP est trouvé par préfixe (`data/ip_country.csv`) ; une IP absente de la table est comptée comme « Inconnu », une IP privée comme « Reseau local ».
- Les lignes de logs mal formées ou avec une IP invalide sont ignorées et enregistrées dans `logs/process.log`.
- La date des logs n'a pas d'année (`Nov  9 08:01:10`) : elle est donc stockée en texte dans `login_attempts`.
- Pour analyser un autre fichier de logs, modifier `LOG_FILE` dans `main.py` et adapter le regex `PATTERN` dans `process/parser.py` si le format est différent.