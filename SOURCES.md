# Sources de données

Les sources utilisées par l'app (carte et tableau de bord). Les scripts de téléchargement sont décrits dans `sources/README.md`. « À vérifier » : la licence n'a pas été relue sur la page de la source.

## Utilisées par l'app

| Source | Producteur | Ce qu'on en tire | Accès | Licence | Script | Utilisée dans |
|---|---|---|---|---|---|---|
| BDIFF (Base de données sur les incendies de forêts en France) | Ministère chargé de l'agriculture, application gérée par l'IGN | Départs de feu : commune, date et heure de l'alerte, surface brûlée par type (forêt, agricole, autres espaces naturels), cause, bâtiments détruits, décès | https://bdiff.agriculture.gouv.fr/ (export CSV par formulaire) | Mentions légales jointes à l'export, à vérifier | Aucun : export à la main dans `data/Incendies.csv` | Carte, tableau de bord |
| Données climatologiques de base, quotidiennes | Météo-France | Température maximale (`TX`) et humidité minimale (`UN`) par station et par jour | https://www.data.gouv.fr/datasets/donnees-climatologiques-de-base-quotidiennes | Licence Ouverte 2.0 | `telecharger_meteo.py` | Carte (zones), tableau de bord (redéfinir le seuil) |
| BD Forêt V2 | IGN | Végétation de la région, regroupée en 3 niveaux d'inflammabilité (résineux et landes, forêts mélangées, feuillus) | Image du flux WMS `LANDCOVER.FORESTINVENTORY.V2` de la Géoplateforme (https://data.geopf.fr/wms-r) | Licence Ouverte 2.0, à vérifier | `telecharger_foret.py` | Carte (végétation) |
| OpenStreetMap | Contributeurs OpenStreetMap | Casernes de pompiers ; points d'eau incendie (citernes, réserves, points d'aspiration, poteaux) | API Overpass (https://overpass-api.de) | ODbL | `telecharger_osm.py` | Carte, tableau de bord (Q1, Q2) |
| OSRM | Projet OSRM, sur les routes d'OpenStreetMap | Temps de trajet en voiture depuis la caserne la plus proche, pour chaque commune touchée par un feu | Serveur de démonstration https://router.project-osrm.org | Données ODbL ; serveur de démonstration à utiliser avec modération | `calculer_temps_trajet.py` | Carte (infobulle), tableau de bord (Q1) |
| API Découpage administratif | État (geo.api.gouv.fr), données INSEE et IGN | Centre de chaque commune de Nouvelle-Aquitaine, pour placer les feux | https://geo.api.gouv.fr/communes | Licence Ouverte, à vérifier | `telecharger_geo.py` | Carte, tableau de bord |
| france-geojson | Grégoire David, d'après les contours IGN | Contours de la région et des 12 départements | https://github.com/gregoiredavid/france-geojson | À vérifier sur le dépôt | `telecharger_geo.py` | Carte, tableau de bord |
| Fond de carte Positron | CARTO, données OpenStreetMap | Fond de carte clair | Chargé par la carte à l'affichage | © CARTO, © contributeurs OpenStreetMap | Aucun | Carte |

## Téléchargées mais pas encore utilisées

| Source | Producteur | Ce qu'on en tire | Accès | Licence | Script | Pourquoi |
|---|---|---|---|---|---|---|
| Archives de la Météo des forêts | Météo-France | Niveau de danger par département et par jour, de juin à septembre, depuis 2024 | https://www.data.gouv.fr/datasets/archives-de-la-meteo-des-forets | Licence Ouverte, à vérifier | `telecharger_meteo_des_forets.py` | Seuil actuel jugé obsolète ; gardé pour le comparer au nouveau seuil |
| FIRMS (satellite VIIRS S-NPP) | NASA | Points chauds détectés par satellite, avec date et heure | https://firms.modaps.eosdis.nasa.gov/ | Données NASA, libres d'utilisation, citation demandée | `telecharger_firms.py` | Pour suivre l'avancée des grands feux, une prochaine étape |

## Pas en open data, à demander

| Donnée | Qui la détient | Pour quel indicateur |
|---|---|---|
| Heures d'alerte, de départ et d'arrivée des pompiers | SDIS | Délai d'intervention réel (Q1) |
| Points d'eau DFCI, avec leur état | GIP ATGeRi (plateforme PIGMA), DFCI | Couverture en eau des massifs (fiche KPI 3) |
| Contours des feux | SDIS, DFCI ; satellite (EFFIS) pour les grands feux | Feux passés à moins de 200 m d'une maison |
