# Pipeline Log Analyser

Projet Python Avancé – 3ème année (ESISA)
Auteur : SAD DOUAH

## Objectif

Ce projet analyse un fichier de logs SSH (`auth.log`) et produit un dashboard
qui répond à trois questions :

1. Combien de tentatives de connexion **échouées par pays** ?
2. Combien de tentatives **réussies par utilisateur** ?
3. Quelles sont les tentatives **échouées avec « invalid user »** ?

Le projet respecte les consignes du cours : uniquement la bibliothèque standard
de Python (`logging`, `re`, `csv`, `json`, `unittest`), aucun package externe.

## Architecture du pipeline

```
data/auth.log ──► ingestion ──► process ──► storage ──► serving
                  (lecture)    (parsing +   (JSON)      (dashboard
                               statistiques)             console + HTML)
```

| Dossier | Rôle |
|---|---|
| `ingestion/` | Lecture du fichier de logs et de la table IP → pays (`data/ip_country.csv`) |
| `process/` | `parser.py` : analyse de chaque ligne avec un regex ; `analyzer.py` : calcul des 3 statistiques |
| `storage/` | Sauvegarde et rechargement des résultats dans `data/results.json` |
| `serving/` | Affichage du dashboard dans la console et génération de `dashboard.html` |
| `src/` | Configuration des logs (`log_config.py`) |
| `tests/` | Tests unitaires (`unittest`) |
| `data/` | Fichier de logs et table IP → pays |

## Gestion des logs de l'application

Chaque module écrit ses propres logs dans le dossier `logs/` :
`ingestion.log`, `process.log`, `storage.log`, `serving.log`.
Le fichier est géré avec `RotatingFileHandler` (rotation à 100 Ko, 3 sauvegardes).

Erreurs enregistrées par module :

- **ingestion** : fichier introuvable, permission refusée, erreur d'encodage, fichier vide, ligne invalide dans le CSV des pays
- **process** : ligne non reconnue, adresse IP invalide, erreur inattendue pendant le parsing ou le calcul
- **storage** : permission refusée, données non sérialisables, JSON invalide, fichier introuvable
- **serving** : aucun résultat à afficher, aucune donnée pour un indicateur, erreur d'écriture du HTML

## Installation et lancement

Prérequis : Python 3.10 ou plus récent. Aucune installation de package n'est nécessaire.

```
python main.py
```

Le programme affiche le dashboard dans la console et crée `dashboard.html`
(à ouvrir dans un navigateur).

## Tests

```
python -m unittest discover -s tests -v
```

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

- Le pays d'une IP est trouvé par préfixe (`data/ip_country.csv`) ; une IP absente de la table est comptée comme « Inconnu ».
- Les lignes de logs mal formées ou avec une IP invalide sont ignorées et enregistrées dans `logs/process.log`.
- Pour analyser un autre fichier de logs, modifier `LOG_FILE` dans `main.py` et adapter le regex `PATTERN` dans `process/parser.py` si le format est différent.
