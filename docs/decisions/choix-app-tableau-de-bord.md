# Choix de l'app : carte et tableau de bord décisionnel

> **Décision** : une app **Streamlit** à deux vues, une **carte** des feux de Nouvelle-Aquitaine jour par jour et un **tableau de bord décisionnel** construit d'après les fiches KPI (`KPI_fiches.docx`).
> Le seuil actuel de la **Météo des forêts n'est plus utilisé** : il est jugé obsolète, et le tableau de bord aide à le **redéfinir** à partir de la température et de l'humidité.
> Les indicateurs sans donnée publique (délai d'intervention, couverture en eau DFCI) sont remplacés par des **proxys déclarés**, en attendant les données du SDIS et de la DFCI.
> **C'est un prototype** : l'app lit pour l'instant les fichiers téléchargés directement avec pandas, pour prévisualiser et analyser. À terme, elle lira les tables finales du pipeline décrit dans `choix-techno.md` (Python → DuckDB → dbt).

| | |
|---|---|
| Date | 2026-11-20 |
| Rédigé par | Hoa Cong |
| Statut | Proposé, à valider par le groupe |

---

## 1. En une phrase

**Les scripts de `sources/` téléchargent, `main/donnees.py` charge, la carte montre où et quand, le tableau de bord dit quoi décider.**

```
sources/*.py  ──►  data/ (hors Git)  ──►  main/donnees.py  ──►  main/app.py (carte)
                   main/geo/ (suivi)                        └►  main/tableau_de_bord.py (KPI)
```

## 2. Périmètre

| Décision | Pourquoi |
|---|---|
| **Nouvelle-Aquitaine** (12 départements), avec un filtre par département dans le tableau de bord | La Gironde seule ne permet pas de comparer ; la question porte sur les pompiers de la région |
| **Année 2025** uniquement pour l'instant | C'est la seule année de l'export BDIFF ouvert. Il faut exporter les autres années pour comparer et caler un seuil sur plusieurs étés |
| Données de **Nouvelle-Aquitaine seulement** dans le tableau de bord | Le décideur agit sur sa région ; le reste de la France sert au benchmark, pas au pilotage |

## 3. Carte

| Décision | Pourquoi |
|---|---|
| Chaque feu est placé **au centre de sa commune** | La BDIFF ne donne pas de coordonnées, seulement le code INSEE |
| **Taille** du point = surface brûlée (aire proportionnelle) ; **couleur** = jour du mois, de l'orange clair au rouge sombre | Voir à la fois l'ampleur et l'évolution dans le temps |
| **Curseurs mois et jour** : les feux s'ajoutent jour après jour, ceux du jour choisi sont pleins, les précédents estompés | La BDIFF ne donne pas l'évolution de chaque feu (ni contour, ni durée) : on montre l'évolution des départs |
| **Flèches de vent retirées** | Trop grosses, et la direction du vent n'apportait pas d'information utile à la décision |
| **Zones par département** : température maximale ou humidité minimale du jour, « Aucune » par défaut | Lire la météo du jour par territoire ; une seule teinte bleue, avec la valeur écrite sur chaque département |
| **Végétation** : BD Forêt V2 de l'IGN, regroupée en 3 niveaux (résineux et landes, forêts mélangées, feuillus) | Les résineux et les landes brûlent plus facilement que les feuillus. 32 types illisibles à l'échelle de la région |
| **Casernes** et **points d'eau des massifs** (citernes, réserves, points d'aspiration) | Voir où sont les moyens par rapport aux feux. Les 30 000 poteaux incendie des bourgs sont exclus de la carte : illisibles à cette échelle |
| **Infobulle** d'un feu : commune, date, surface, temps de trajet depuis la caserne la plus proche | En texte simple : les retours à la ligne passent et aucun nom venu d'un fichier n'est lu comme du HTML |
| Couleurs : **rouge réservé aux feux**, vert pin pour l'interface, bleu pour les zones | La couleur est le canal qui ressort le plus vite (cours de dataviz) : on la garde pour l'information clé |

## 4. Tableau de bord décisionnel

Organisé selon l'arbre de KPIs de `KPI_fiches.docx` : un KPI de décision, des KPIs de pilotage (Q1, Q2), puis l'impact et le seuil.

| Décision | Pourquoi |
|---|---|
| **KPI de décision (fiche 1) présenté brut** : surface brûlée, part due aux feux de plus de 10 ha, plus grand feu | La fiche 1 rapporte la surface aux jours de danger élevé de la Météo des forêts, dont le seuil est à redéfinir |
| **Q1, taux d'échappement (fiche 2)** : part des feux de plus de 10 ha, publiée avec le nombre de feux | Définition de la fiche 2, sans changement |
| **Q1, délai d'intervention → temps de trajet par la route** depuis la caserne la plus proche (OSRM) | Les heures d'alerte, de départ et d'arrivée sont chez le SDIS, pas en open data. Proxy déclaré, sans le temps d'alerte ni de départ |
| **Q2, couverture en eau (fiche 3) → part des départs de feu à moins de 2 km d'un point d'eau** (OpenStreetMap), avec et sans les poteaux incendie | La fiche 3 demande la part de la forêt couverte, avec la BD Forêt et les points d'eau DFCI de PIGMA, pas encore accessibles |
| **Tableau des communes où créer des points d'eau** : départs de feu à 2 km ou plus d'un point d'eau de massif, les feux les plus étendus d'abord | Traduire l'option « création de points d'eau » en liste d'actions |
| **Dégâts aux habitations** depuis la BDIFF (bâtiments détruits, décès) | Le critère de la fiche (« à moins de 200 m d'une maison ») demande les contours des feux, qu'on n'a pas |
| **Végétation brûlée** depuis la BDIFF (forêt, agricole, espaces naturels) | Le type d'arbres touchés n'est pas renseigné dans la BDIFF ; la carte montre où sont les résineux |
| **Section « Redéfinir le seuil »** : départs de feu et hectares brûlés par jour, selon la température maximale et l'humidité minimale du jour | C'est la matière pour fixer le nouveau seuil de renforcement (option « prévisions ») |
| **Titres qui portent le message**, calculés à partir des données (« À 20 min ou plus de la caserne, 43 % des feux dépassent 1 ha… ») | Principe de Minto (cours de dataviz). Calculés, pour ne jamais affirmer ce que les données d'un département ne montrent pas |
| **Garde-fous** : alerte sous 30 feux ; cases de la grille météo vides sous 10 jours | Petits effectifs : un pourcentage ou un taux sur trop peu de cas est trompeur |

## 5. Données et code

| Décision | Pourquoi |
|---|---|
| **Un script par source** dans `sources/`, avec un module commun (téléchargement avec nouvel essai si le serveur est surchargé) | Chacun retélécharge les données chez lui ; voir `sources/README.md` et `SOURCES.md` |
| **`data/` hors Git** ; seuls les petits fichiers géographiques de référence (contours, centres des communes) sont suivis dans `main/geo/` | On ne pousse pas de données (voir `choix-techno.md`) |
| **La BDIFF s'exporte à la main** dans `data/Incendies.csv` | Le site passe par un formulaire, sans lien direct. Les 2 lignes de métadonnées en tête sont sautées à la lecture |
| La **végétation** est une **image** du flux WMS de l'IGN, pas les polygones de la BD Forêt | Les polygones pèsent plusieurs centaines de Mo pour la région ; l'image suffit pour la carte régionale (environ 300 m par pixel) |
| Le **thème** est dans `main/.streamlit/config.toml`, à côté de l'app | Il s'applique quel que soit le dossier depuis lequel on lance `streamlit run` |

## 6. Limites connues

- **Une seule année** : le nouveau seuil et les comparaisons doivent être confirmés sur plusieurs étés.
- **Lieu du feu approché** par le centre de la commune ; la météo est la moyenne des stations du département.
- **Surfaces surtout estimées** dans la BDIFF : un feu de 9 ou 11 ha peut changer de côté du seuil de 10 ha.
- **OpenStreetMap est incomplet** en forêt ; un point d'eau peut être à sec en été.
- **Temps de trajet** calculé en voiture : un camion roule moins vite sur les pistes forestières.
- **Corrélation n'est pas causalité** : un lien entre distance à la caserne et taille du feu ne prouve pas l'effet d'une option.

## 7. À faire ou à décider

| Sujet | Action |
|---|---|
| Données du SDIS (heures d'alerte, de départ, d'arrivée ; moyens engagés) | Les demander, pour remplacer le temps de trajet par le vrai délai d'intervention |
| Points d'eau DFCI et BD Forêt en polygones | Vérifier l'accès sur PIGMA, pour calculer la couverture en eau de la forêt (fiche 3) |
| Autres années de la BDIFF | Les exporter, pour caler le seuil et suivre les KPIs dans le temps |
| Passage au pipeline (`choix-techno.md`) | Aujourd'hui, les scripts écrivent dans `data/<source>/` et l'app lit les fichiers avec pandas (prototype). Ensuite : scripts → `data/raw/`, transformations et tests dans dbt + DuckDB, et `main/donnees.py` lit les tables finales (marts) au lieu des fichiers. La carte et le tableau de bord ne changent pas : seul `donnees.py` change de source |
| Nouveau seuil de renforcement | Le fixer à partir de la grille température × humidité, puis le comparer à l'ancien (archives Météo des forêts gardées pour ça) |
