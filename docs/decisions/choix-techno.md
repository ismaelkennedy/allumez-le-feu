# Choix techniques du pipeline

> **Décision** : le pipeline est construit avec **Python** (extraction), **DuckDB** (base de données) et **dbt** (transformations, tests, documentation), en traitement par lots.
> Spark, Docker et les outils temps réel (Kafka, Flink) ne sont pas retenus pour l'instant.
> **Plan B** : PostgreSQL + PostGIS si la partie géographique devient trop lourde pour DuckDB.

| | |
|---|---|
| Date | 2026-11-20 |
| Rédigé par | Melissa Benbouabdellah (responsable pipeline et modèle) |
| Statut | Proposé, à valider par le groupe |

---

## 1. En une phrase

**Python télécharge, DuckDB stocke, dbt transforme et teste, Streamlit affiche.**

```
SOURCES              EXTRACTION            TRANSFORMATION                      UTILISATION
data.gouv, IGN, ──►  scripts Python   ──►  dbt + DuckDB                   ──►  KPIs, tableau de bord
Météo-France…        (data/raw/)           raw → staging → marts               (Pandas, Streamlit)
                                           (bronze → silver → gold)
```

## 2. Rôle de chaque outil

### Retenus

| Outil | À quoi il sert |
|---|---|
| **Python** | Scripts qui téléchargent chaque source et la déposent telle quelle dans `data/raw/`, avec un journal de chargement (date, URL, nombre de lignes) |
| **DuckDB** | La base de données. Elle stocke toutes les tables et exécute le SQL. Elle tient dans **un seul fichier**, sans serveur à installer. Elle lit directement les CSV, Parquet et GeoJSON, et son extension spatiale permet de relier une forêt à une commune |
| **dbt** | Organise les transformations SQL couche par couche, **teste** les données (doublons, valeurs vides, bornes) et **génère la documentation et le lineage**. Imposé par le cours |
| **SQL** | Nettoyer, relier les sources (jointures sur la date et le territoire), calculer |
| **Git / GitHub** | Versionne le **code**, pas les données |
| **Pandas / Streamlit** | Lire la couche finale (marts) et construire le tableau de bord |

### Écartés pour l'instant

| Outil | À quoi il sert | Pourquoi pas ici |
|---|---|---|
| **Spark** | Calcul distribué sur des volumes énormes (centaines de Go, To) | Nos données font au plus quelques Go. Sur ces volumes, Spark est plus lent et beaucoup plus lourd à installer que DuckDB |
| **Docker** | Faire tourner un logiciel lourd à l'identique sur toutes les machines | DuckDB et dbt s'installent avec `pip install`. Les versions sont fixées dans `requirements.txt` |
| **Kafka, Flink** | Recevoir et traiter des flux continus (temps réel) | Aucune de nos sources n'est un flux : BDIFF est mise à jour une fois par an, la Météo des forêts une fois par jour |

## 3. Pourquoi DuckDB

1. **Les volumes sont faibles.** Même en intégrant toutes les sources envisagées, on reste entre quelques centaines de Mo et quelques Go après filtrage sur notre zone. DuckDB traite des dizaines de Go sur un ordinateur portable.

   | Source | Volume estimé après filtrage |
   |---|---|
   | BDIFF (feux) | quelques dizaines de milliers de lignes |
   | Météo des forêts (France entière, pour le benchmark) | environ 100 000 lignes par an |
   | Météo quotidienne / horaire (stations) | de quelques centaines de milliers à quelques millions de lignes |
   | BD Forêt V2 (Gironde) | 53 151 polygones |
   | BD TOPO (routes, bâtiments, points d'eau) | jusqu'à environ 1 million d'objets |
   | INSEE, calendrier, budget, arrêtés | de quelques dizaines à quelques milliers de lignes |

2. **Cinq personnes, cinq ordinateurs.** `pip install -r requirements.txt` puis `dbt build`, et tout le monde a le même pipeline en quelques minutes. Personne ne se retrouve avec « chez moi ça ne marche pas ».
3. **Ce qui est noté, c'est le modèle**, pas la technique. Le cadrage le dit : « un modèle juste mais impossible à exécuter ne vaut rien ». On met notre temps sur le grain, les jointures et les tests.
4. **Il relie les sources facilement.** Les jointures SQL classiques et l'extension spatiale (pour la BD Forêt, qui n'a pas de code commune) suffisent pour construire le schéma en étoile.

### Limites connues

- **Une seule personne peut écrire dans le fichier à la fois.** Chacun reconstruit sa base en local avec `dbt build`, et le fichier `.duckdb` n'est jamais versionné.
- **Pas d'utilisateurs ni de droits** dans la base : quiconque a le fichier voit tout. C'est acceptable pour des données publiques.
- **La géographie avancée** (distances aux casernes, aux habitations, aux points d'eau) est moins complète que dans PostGIS. Si ça bloque, on passe au plan B : dbt fonctionne aussi avec PostgreSQL, et la plupart du SQL se réutilise.
- **Les données en grille** (AROME, ARPEGE, humidité des sols) ne se chargent pas telles quelles, quelle que soit la base. Il faut d'abord un script Python (`xarray`) pour découper la zone et garder les variables utiles.

## 4. RGPD et normes

**Un outil n'est pas « conforme RGPD » : c'est le traitement qui l'est.** DuckDB aide parce que tout reste en local.

| Point | Ce qu'on fait |
|---|---|
| Localisation | Les données restent sur nos ordinateurs : pas de cloud, pas de transfert hors UE. On n'utilise **pas MotherDuck** (la version cloud de DuckDB) |
| Minimisation | Dans les modèles dbt de staging, on ne garde que les colonnes qui servent une question (étape 5 du cadrage) |
| Pseudonymisation | Si nécessaire, en SQL dans le staging |
| Sécurité | Chiffrement du disque (FileVault, BitLocker), ou chiffrement du fichier DuckDB (possible depuis la version 1.4) |
| Ré-identification | Attention aux croisements : coordonnées précises d'un feu + cause (malveillance) peuvent renvoyer à une personne ou une propriété |
| **GitHub** | **On ne pousse jamais de données** : `data/` et `*.duckdb` sont dans le `.gitignore`. Chacun retélécharge avec les scripts. On vérifie la licence de chaque source |

- **ISO 27001** certifie une organisation, pas un logiciel.
- **ISO/IEC 25012** (qualité des données) se met en œuvre avec **les tests dbt** (complétude, exactitude, fraîcheur), pas par le choix de la base.

## 5. Préparer l'évolution sans la surconstruire

On ne met pas en place le temps réel maintenant, mais on construit le pipeline pour qu'il puisse évoluer :

| Bonne pratique dès maintenant | Ce qu'elle prépare |
|---|---|
| Un script d'extraction par source, **idempotent** (le relancer ne double rien) | Un planificateur pourra le relancer automatiquement |
| **Chargement incrémental** (seulement les nouvelles dates) | Le principe même d'un flux |
| Modèles dbt **incrémentaux** | Des mises à jour fréquentes sans tout recalculer |
| **SQL standard**, peu de fonctions propres à DuckDB | Changer de moteur en changeant l'adaptateur dbt |
| Colonne `_loaded_at` sur chaque ligne chargée | Le suivi de données qui arrivent en continu |

Le modèle en étoile, les tables de correspondance (communes ↔ zones de l'indice) et les tests sont écrits en SQL dans dbt : **ils se réutilisent quel que soit l'outil d'ingestion.**

## 6. Évolutions possibles (hors périmètre du projet)

| Besoin | Fréquence | Outils |
|---|---|---|
| Carte du danger et des feux mise à jour automatiquement | Quasi temps réel (de 15 min à 1 h) : satellites (NASA FIRMS, EFFIS), API Météo-France | **Dagster** ou **Airflow** pour relancer le pipeline, **PostgreSQL + PostGIS**, **Grafana** ou Streamlit avec carte |
| Alertes en direct (caméras de détection, foudre) | Temps réel (secondes) | **Kafka** (ou Redpanda) pour recevoir les événements, **Flink** ou Spark Structured Streaming pour les traiter, **PostGIS / TimescaleDB**, carte web, **Docker** pour déployer |

Le suivi des interventions en temps réel existe déjà côté pompiers (NexSIS, systèmes de gestion des SDIS). Une piste crédible serait de **l'enrichir** (couche danger + végétation + points d'eau), pas de le remplacer.

> **Ce qu'on dit au jury** : « Pour une décision stratégique, un traitement par lots suffit. L'évolution naturelle est un rafraîchissement horaire avec un planificateur et PostGIS. Kafka et Flink ne seraient utiles que pour des capteurs en temps réel, et ce serait un autre produit, opérationnel. »
