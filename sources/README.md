# Récupérer les données

Les données téléchargées vont dans `data/`, qui est ignoré par Git : chacun lance les scripts chez lui. Seuls les contours et les centres des communes (`main/geo/`) sont suivis par Git.

Depuis la racine du projet, avec l'environnement Python activé :

```
python sources/telecharger_geo.py
python sources/telecharger_meteo.py
python sources/telecharger_meteo_des_forets.py
python sources/telecharger_osm.py
python sources/telecharger_firms.py
python sources/calculer_temps_trajet.py
python sources/telecharger_foret.py
```

Les scripts qui dépendent d'une année prennent 2025 par défaut. Pour une autre année : `python sources/telecharger_meteo.py 2024`.

| Script | Source | Fichiers produits | Utilisé par |
|---|---|---|---|
| `telecharger_geo.py` | france-geojson, geo.api.gouv.fr | `main/geo/` : contours de la région et des départements, centre des communes | Carte, tableau de bord |
| `telecharger_meteo.py` | Météo-France, données quotidiennes (data.gouv.fr) | `data/meteo/` : température (RR-T-Vent) et humidité (autres-parametres) par station et par jour, 12 départements | Carte (zones), tableau de bord (redéfinir le seuil) |
| `telecharger_meteo_des_forets.py` | Météo-France, archives de la Météo des forêts (data.gouv.fr) | `data/meteo_des_forets/` : niveau de danger par département et par jour, de juin à septembre, depuis 2024 | Tableau de bord (seuil actuel, dans « Redéfinir le seuil ») |
| `telecharger_osm.py` | OpenStreetMap (API Overpass) | `data/osm/` : casernes et points d'eau incendie (citernes, bassins, points d'aspiration, poteaux incendie) | Tableau de bord (KPI de pilotage) |
| `calculer_temps_trajet.py` | OSRM (itinéraires sur OpenStreetMap) | `data/osrm/` : temps de trajet par la route depuis la caserne la plus proche, pour chaque commune touchée par un feu | Carte (infobulle des feux), tableau de bord (Q1) |
| `telecharger_foret.py` | IGN, BD Forêt V2 (image WMS de la Géoplateforme) | `data/ign/` : végétation de la région en 3 niveaux d'inflammabilité (résineux et landes, forêts mélangées, feuillus), environ 300 m par pixel | Carte (végétation) |
| `telecharger_firms.py` | NASA FIRMS, satellite VIIRS | `data/firms/` : points chauds détectés par satellite en France, avec date et heure | Pas encore : sert à suivre l'avancée des grands feux |

`commun.py` contient ce que les scripts partagent : téléchargement avec nouvel essai quand le serveur est surchargé, chemins du projet, liste des départements.

## La BDIFF se télécharge à la main

Le site de la BDIFF passe par un formulaire, sans lien de téléchargement direct :

1. Ouvrir bdiff.agriculture.gouv.fr, partie « Incendies ».
2. Choisir la période (dates de première alerte), « France entière » et le type de feu.
3. Exporter en CSV.
4. Enregistrer le fichier sous `data/Incendies.csv`.

Le fichier commence par 2 lignes de métadonnées (nombre de feux, critères) avant les titres de colonnes : l'app et le notebook les sautent.
