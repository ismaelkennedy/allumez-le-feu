# Fiche d'identité - Modèles de prévision AROME et ARPEGE (Météo-France)

Rédigée par : Hoa Cong, 2026-11-17
Fichiers analysés : métadonnées des jeux « Paquets Arome - Résolution 0,01° » et « Paquets Arpège - Résolution 0,1° » sur data.gouv.fr (runs du 17/11/2026 à 03 h et 06 h UTC), et les deux descriptifs techniques de Météo-France. Les fichiers GRIB2 n'ont pas été ouverts.

## Identité

| Rubrique | AROME | ARPEGE |
|---|---|---|
| Propriétaire | Météo-France | Météo-France |
| Accès | data.gouv.fr → « Paquets Arome - Résolution 0,01° ». Fichiers hébergés sur `meteofrance-pnt.s3.rbx.io.cloud.ovh.net`, téléchargement libre, sans compte | data.gouv.fr → « Paquets Arpège - Résolution 0,1° ». Même hébergement, même accès |
| Format | GRIB2 compressé, plusieurs paramètres par fichier. Il faut une bibliothèque spécialisée pour le lire (eccodes, cfgrib avec xarray) | Pareil |
| Contenu | Prévisions météo heure par heure sur une grille régulière, de 0 à 51 h après le lancement du calcul | Prévisions de 0 à 102 h : toutes les heures jusqu'à 48 h, puis toutes les 3 h |
| Granularité | Une valeur = un point de grille × une heure prévue. Pas de 0,01°, environ 1 km. Grille EURW1S100 : de 37,5° N à 55,4° N, de 12° O à 16° E | Pas de 0,1°, environ 10 km. Grille EURAT01 : de 20° N à 72° N, de 32° O à 42° E |
| Historique | **Environ deux semaines en ligne.** Le 17/11/2026, le plus ancien run encore disponible était celui du 03/11/2026 à 0 h UTC. Aucune archive des étés passés sur data.gouv.fr | Pareil : le 17/11/2026, le run du 05/11/2026 était disponible, ceux du 01/11/2026 et d'octobre ne l'étaient plus |
| Fraîcheur | 8 runs par jour, toutes les 3 h (d'après le descriptif technique) | 4 runs par jour : 0 h, 6 h, 12 h et 18 h UTC |
| Clés | Latitude, longitude, date du run et échéance. Pas de code commune ni de département | Pareil |
| Licence | Licence Ouverte / Open Licence 2.0 (indiquée sur data.gouv.fr) | Pareil |
| Millésime | Métadonnées lues le 17/11/2026. Descriptif technique AROME v4 du 01/04/2025 | Descriptif technique ARPEGE du 02/01/2024 |
| Données personnelles | Aucune | Aucune |

## Chiffres clés de l'export

- Points de grille dans la Gironde, calculés avec le contour du département fourni avec la Météo des forêts : 11 817 pour AROME 0,01°, 117 pour ARPEGE 0,1°
- AROME 0,01° : un run = 52 fichiers horaires par paquet (00H à 51H). Le paquet SP1 pèse environ 22 Mo par fichier, soit 1,2 Go par run. Le paquet HP1 pèse environ 70 Mo par fichier, soit 3,7 Go par run
- ARPEGE 0,1° : un run = 9 fichiers par paquet. 0,65 Go par run pour SP1, 14,4 Go pour les 8 paquets
- Les fichiers couvrent toute la grille. Pour la Gironde seule, il faut quand même télécharger l'Europe de l'Ouest
- Estimation : garder SP1 et SP2 d'AROME pour un run par jour pendant un été (122 jours) représente environ 280 Go

## Schéma

Paramètres utiles pour le risque de feu. Un fichier GRIB2 n'a pas de colonnes : chaque paramètre est une grille de valeurs.

| Paramètre | Unité (convention GRIB) | Description | AROME 0,01° | ARPEGE 0,1° |
|---|---|---|---|---|
| T(2m) | kelvin | Température à 2 m | SP1 | SP1 |
| HU(2m) | % | Humidité relative à 2 m | SP1 | SP1 |
| U(10m), V(10m) | m/s | Vent à 10 m, en deux composantes | SP1 | SP1 |
| FF(10m), DD(10m) | m/s, degrés | Vitesse et direction du vent à 10 m | absents, à calculer à partir de U et V | SP1 |
| U_RAF, V_RAF, FF_RAF | m/s | Rafales à 10 m | SP1 (U_RAF, V_RAF) | SP1 |
| PRECIP | kg/m² (= mm) | Précipitations | absent | SP1 |
| EAU, NEIGE, GRAUPEL | kg/m² (= mm) | Précipitations par type | SP2 | NEIGE seulement, dans SP1 |
| TMIN(2m), TMAX(2m) | kelvin | Températures minimale et maximale | absents | SP2 |
| TD(2m) | kelvin | Point de rosée à 2 m | absent | SP2 |
| NEBBAS, NEBMOY, NEBHAU | % | Nébulosité basse, moyenne, haute | SP2 | SP2 |
| ALTITUDE | m | Relief du point de grille | SP3 | SP2 |
| HU, U, V en altitude | %, m/s | Humidité et vent à 10, 20, 50 et 100 m | HP1 | HP1 (24 niveaux de 20 à 3000 m) |

## Limites repérées

- **Pas d'historique.** Environ deux semaines de runs sont en ligne. Pour étudier les feux 2016-2025 de la BDIFF ou les saisons 2024-2025 de la Météo des forêts, il aurait fallu télécharger les fichiers chaque jour depuis le début.
- **Ce sont des prévisions, pas des mesures.** Pour savoir quel temps il faisait le jour d'un feu, les relevés des stations Météo-France (données climatologiques quotidiennes) sont plus fiables et remontent à plusieurs décennies.
- **Volume énorme** : environ 1,2 Go par run pour le seul paquet SP1 d'AROME, et la grille couvre l'Europe de l'Ouest entière.
- **Format difficile** : GRIB2 multi-paramètres. Le descriptif d'AROME prévient que sa grille est trapézoïdale et contient des valeurs manquantes, qu'il faut repérer paramètre par paramètre. Ce n'est pas vérifié sur la Gironde.
- **Pas de lien direct avec la BDIFF** : il faut rattacher chaque point de grille à une commune avec les contours IGN, ou prendre le point le plus proche du centre de la commune.
- **ARPEGE est trop grossier pour la Gironde** : 117 points, environ 10 km entre deux points, alors qu'AROME couvre le même territoire à 1 km. Son seul avantage est l'échéance : jusqu'à 4 jours, contre 2 jours pour AROME et pour la Météo des forêts.
- **Pas de paramètre de sécheresse de la végétation** : le modèle donne la météo, pas l'état de la forêt que la Météo des forêts prend en compte.

## Questions servies

| Question | Ce que AROME et ARPEGE apportent |
|---|---|
| 1. Zones les plus touchées | En partie : AROME montre quelles zones de la Gironde sont les plus chaudes, sèches et ventées un jour donné, mais seulement pour les deux dernières semaines |
| 2. Seuil de l'indice | Non : pas d'historique à croiser avec les feux passés |
| 3. Comparaison avec les autres départements | Non, pour la même raison |
| 4. Feux avec indice bas | Non, pour la même raison |
| 5. Jours de suite en danger élevé | Non pour le passé. ARPEGE pourrait servir à l'été 2027 pour voir arriver une suite de jours chauds jusqu'à 4 jours à l'avance |
| 6. Jours de dispositif renforcé par été | Non : rien sur les étés passés |
| 7. Critères météo suffisants | Non pour le passé. Possible pour l'été 2027 si l'équipe archive un run par jour dès le début de la saison |
