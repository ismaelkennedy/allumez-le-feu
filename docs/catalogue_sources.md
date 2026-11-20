# Sources : liens et licences

Mise à jour : 2026-11-20

## 1. Les sources

| Source | Lien d'accès | Licence |
|---|---|---|
| BDIFF (Base de données sur les incendies de forêts en France) | https://bdiff.agriculture.gouv.fr/ | Licence Ouverte 2.0 – citer bdiff.agriculture.gouv.fr |
| Interventions des SDIS | https://www.data.gouv.fr/datasets/interventions-realisees-par-les-services-d-incendie-et-de-secours | Licence Ouverte 1.0 |
| Statistiques nationales des SDIS | https://www.interieur.gouv.fr/documentation/etudes-et-statistiques/statistiques-2024-dgscgc.html | **Non trouvée** (voir tableau 2) |
| BD Forêt V2 | https://www.data.gouv.fr/datasets/bd-foret-r (flux WMS : https://data.geopf.fr/wms-r) | Licence Ouverte 2.0 |
| AROME | https://www.data.gouv.fr/datasets/?q=paquets%20arome | Licence Ouverte 2.0 |
| ARPEGE | https://www.data.gouv.fr/datasets/?q=paquets%20arpege | Licence Ouverte 2.0 |
| Archives de la Météo des forêts | https://www.data.gouv.fr/datasets/archives-de-la-meteo-des-forets | Licence Ouverte 2.0 |
| Données climatologiques de base, quotidiennes | https://www.data.gouv.fr/datasets/donnees-climatologiques-de-base-quotidiennes | Licence Ouverte 2.0 |
| OpenStreetMap | https://overpass-api.de (licence : https://www.openstreetmap.org/copyright) | ODbL – citer « © contributeurs OpenStreetMap » |
| OSRM (temps de trajet) | https://router.project-osrm.org | Données OpenStreetMap (ODbL). Serveur de démonstration : usage non commercial, 1 requête par seconde maximum |
| API Découpage administratif | https://geo.api.gouv.fr/communes | **À vérifier** : la page ne l'indique pas, voir https://geo.api.gouv.fr/cgu |
| france-geojson | https://github.com/gregoiredavid/france-geojson | **Aucune licence sur le dépôt**. Les données viennent d'IGN Admin Express (Licence Ouverte), édition 2018 |
| Fond de carte Positron (CARTO) | https://carto.com/basemaps | Gratuit pour un usage non commercial (jusqu'à 5 millions de requêtes par mois). Afficher « © OpenStreetMap contributors, © CARTO » sur la carte |
| FIRMS (satellite VIIRS S-NPP) | https://firms.modaps.eosdis.nasa.gov/ | Aucune restriction (données NASA), citation demandée : FIRMS, LANCE, ESDIS |

## 2. Sources payantes, limitées ou pas en open data : axes d'amélioration

| Source | Le problème | Axe d'amélioration |
|---|---|---|
| Statistiques nationales des SDIS | Licence introuvable, données en PDF | Utiliser le CSV « Interventions des SDIS » (Licence Ouverte, mêmes chiffres par département et par an, 2008-2024) |
| france-geojson | Pas de licence sur le dépôt, contours de 2018 | Prendre les contours directement dans IGN Admin Express (Licence Ouverte, à jour) : https://geoservices.ign.fr/adminexpress |
| Fond de carte Positron (CARTO) | Gratuit seulement en non commercial ; au-delà, payant (à partir de 500 $ par mois) | Rester en usage non commercial (projet d'école), ou passer au fond « Plan IGN » de la Géoplateforme (Licence Ouverte, gratuit) |
| OSRM (serveur de démonstration) | Non commercial, 1 requête par seconde, aucune garantie de disponibilité | Garder des calculs peu nombreux et les enregistrer une fois ; sinon installer son propre serveur OSRM, ou utiliser openrouteservice (clé gratuite) |
| Foudre (Météorage) | Payant, pas d'open data | Pas d'alternative gratuite précise. Utiliser la cause « Naturelle » de BDIFF pour repérer les feux de foudre |
| Heures d'alerte, de départ et d'arrivée des pompiers | Pas en open data | À demander au SDIS 33 (données du CODIS) |
| Jours où le dispositif renforcé a été déclenché | Pas en open data | À demander au SDIS 33 ou à la préfecture |
| Points d'eau DFCI, avec leur état | Pas en open data complet | Demander à la DFCI / GIP ATGeRi (PIGMA : https://www.pigma.org). En attendant : points d'eau incendie d'OpenStreetMap |
| Contours des feux | Pas en open data pour les petits feux | Grands feux : EFFIS (https://forest-fire.emergency.copernicus.eu). Autres : à demander au SDIS 33 |
