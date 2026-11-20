# allumez-le-feu

## Lancer le pipeline

Prérequis : Python 3.10 à 3.13.

```bash
# 1. Créer l'environnement (une seule fois)
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt

# 2. Vérifier la connexion à la base
dbt debug

# 3. Construire et tester toutes les couches
dbt build
```

Toutes les commandes `dbt` se lancent **depuis la racine du dépôt** (c'est là que se trouve `profiles.yml`).

## Organisation

| Dossier | Contenu |
|---|---|
| `extract/` | Scripts Python qui téléchargent les sources vers `data/raw/` |
| `data/raw/` | Fichiers sources tels quels (**non versionnés**) |
| `data/warehouse/` | Base DuckDB `feux.duckdb` (**non versionnée**) |
| `models/staging/` | Une vue par source : typée, renommée, colonnes utiles seulement |
| `models/intermediate/` | Consolidation : tables de correspondance, rejets |
| `models/marts/` | Schéma en étoile : faits et dimensions |
| `seeds/` | Petits référentiels saisis à la main (CSV versionnés) |
| `snapshots/` | Dimensions historisées (SCD2) |
| `docs/` | Analyses, fiches sources, journal des décisions |

Les choix techniques sont expliqués dans [docs/decisions/choix-techno.md](docs/decisions/choix-techno.md) (branche `docs/choix-techno`).

**Règle :** aucune donnée ni fichier `.duckdb` n'est poussé sur GitHub.
