## Partie 1 : diagramme de la structure

![alt text](Gironde_Wildfire_Response_Data_Model-2026-11-22-141146.png)



MASSIF --o{ COMMUNE : "contient"
COMMUNE --o{ FEU : "lieu du feu"
JOUR --o{ FEU : "jour de l alerte"
FEU --o| INTERVENTION : "donne lieu a"
CASERNE --o{ INTERVENTION : "intervient"
CASERNE --o{ FEU : "la plus proche"
POINT_EAU --o{ FEU : "le plus proche"

COMMUNE }o--o{ NIVEAU_DANGER : "meme departement"
COMMUNE }o--o{ INDICE_FWI : "meme maille"
COMMUNE }o--o{ METEO : "meme station"
COMMUNE }o--o{ PROJECTION : "meme maille"
JOUR --o{ NIVEAU_DANGER : "date"
JOUR --o{ INDICE_FWI : "date"
JOUR --o{ METEO : "date"
DISPOSITIF_SDIS ||--o{ NIVEAU_DANGER : "dispositif prevu"

MASSIF["MASSIF (source : PIGMA + BD Foret V2)"] {
    string id_massif PK
    string nom
    float surface_foret_ha
    float part_pin_maritime
}
COMMUNE["COMMUNE (source : API Decoupage administratif + BD Foret V2 + INSEE   hebergements)"] {
    string code_insee PK
    string nom
    string code_dep
    string id_massif FK
    string id_maille
    string id_station
    float surface_foret_ha
    int capacite_hebergement
}
FEU["FEU (source : BDIFF + calculs OSM et OSRM)"] {
        string id_feu PK
        string code_insee FK
        date jour FK
        datetime date_alerte
        float latitude
        float longitude
        float surface_ha
        string cause
        boolean depasse_1ha
        string id_caserne FK
        float temps_trajet_min
        string id_point_eau FK
        float distance_eau_m
    }
    INTERVENTION["INTERVENTION (source : SDIS 33, a demander)"] {
        string id_intervention PK
        string id_feu FK
        string id_caserne FK
        datetime heure_alerte
        datetime heure_arrivee
        int nb_engins
    }
    CASERNE["CASERNE (source : OpenStreetMap Overpass, ou liste SDIS 33)"] {
        string id_caserne PK
        string nom
        float latitude
        float longitude
    }
    POINT_EAU["POINT_EAU (source : OpenStreetMap Overpass ou PIGMA)"] {
        string id_point_eau PK
        string type
        float latitude
        float longitude
    }
    JOUR["JOUR (source : calendrier calcule + arretes prefectoraux saisis a la main)"] {
        date jour PK
        string jour_semaine
        boolean est_weekend
        boolean est_ferie
        boolean vacances_scolaires
        int vigilance_prefecture
    }
    NIVEAU_DANGER["NIVEAU_DANGER (source : Archives de la Meteo des forets)"] {
        string code_dep PK
        date jour PK
        int niveau FK
    }
    DISPOSITIF_SDIS["DISPOSITIF_SDIS (source : OODFF 2020, saisie a la main)"] {
        int niveau PK
        string moyens_prevus
        string patrouille_guet
    }
    INDICE_FWI["INDICE_FWI (source : Copernicus CEMS Fire danger indices)"] {
        string id_maille PK
        date jour PK
        float fwi
    }
METEO["METEO (source : Donnees climatologiques de base quotidiennes)"] {
        string id_station PK
        date jour PK
        float temperature_max
        float humidite_min
        float vent_max
        float pluie
    }
    PROJECTION["PROJECTION (source : Copernicus CDS, projections indice feu)"] {
        string id_maille PK
        int annee PK
        string scenario PK
        int nb_jours_danger_eleve
    }

## Partie 2 : traitements appliqués (data lineage)

| Donnée | Source | Transformations | Problèmes d'alignement | Données concurrentes | 
|---|---|---|---|---|
| Départs de feu (date, commune, surface, cause, coordonnées) | BDIFF | Filtre sur les 12 départements de Nouvelle-Aquitaine ; conversion des dates ; surface en hectares ; indicateur « dépasse 1 ha » ; normalisation du code commune ; déduplication | Code commune à rapprocher du référentiel des communes ; si la commune manque, retrouvée par les coordonnées (jointure spatiale) ; millésime des codes commune | Comptages des interventions SDIS (autre définition) : BDIFF pour l'événement, SDIS en contrôle de volume | 
| Indice Météo des forêts (valeur, niveau) | Archives de la Météo des forêts | Lecture de l'historique ; agrégation à la maille retenue ; classement en niveaux de danger | Maille de l'indice ≠ commune ni département : table de correspondance à construire | Indice recalculé depuis la météo brute : on retient l'indice officiel | 
| Météo quotidienne (température max, humidité min, vent, pluie) | Données climatologiques de base quotidiennes | Sélection des stations de Nouvelle-Aquitaine ; conversion d'unités ; gestion des valeurs manquantes ; agrégation jour × département pour les croisements | Station → commune ou département : station la plus proche (jointure spatiale) | Plusieurs stations par zone : la plus proche ayant la mesure | 
| Interventions des SDIS (feux de végétation par département) | Interventions des SDIS (CSV) | Lecture en Windows-1252 ; suppression des « ? » dans les nombres ; conversion en entiers ; code département sur 2 caractères ; filtre sur les 12 services du Sud-ouest | Nom de département → code département | Départs de feu de la BDIFF : voir ligne 1 |  (fiche de la source) |
| Statistiques nationales SDIS (historique) | Statistiques nationales des SDIS (PDF) | Extraction des tableaux du PDF ; normalisation des codes | L'année affichée est peut-être celle de l'édition, pas des données | Interventions des SDIS (CSV) : le CSV est retenu pour 2024, le PDF pour l'historique | 
| Surface boisée par commune | BD Forêt V2 | Intersection des polygones de forêt avec les communes ; somme des surfaces | Projection commune aux deux couches (jointure spatiale) | Aucune identifiée | 
| Casernes et points d'eau (coordonnées, type) | OpenStreetMap (Overpass) | Sélection par balises OSM ; rattachement à la commune par jointure spatiale | Balises hétérogènes selon les contributeurs ; coordonnées → commune | Liste officielle des casernes du SDIS, si obtenue : elle fait foi | 
| Temps de trajet feu → caserne la plus proche | OSRM, casernes OSM, feux BDIFF | Requête par feu vers la caserne la plus proche ; conversion en minutes ; classes (moins de 10 min, 10 à 20 min, 20 min ou plus) | Point de départ du feu non routable : projection sur la route la plus proche ; serveur de démonstration limité à 1 requête par seconde | Distance à vol d'oiseau : écartée, le temps de trajet est plus proche de l'intervention | 
| Distance feu → point d'eau le plus proche | Points d'eau OSM, feux BDIFF | Distance au point d'eau le plus proche ; classes (moins de 2 km, 2 à 5 km, 5 km ou plus) | Définition de « point d'eau de massif » à fixer | Aucune identifiée | 
| Communes et départements (codes, noms, géométries) | API Découpage administratif, ou france-geojson | Chargement des codes et géométries ; code département sur 2 caractères ; surface calculée | Un seul millésime de codes commune pour toutes les sources ; france-geojson date de 2018 | API vs france-geojson : on retient l'API (plus récente), sous réserve de sa licence | 
| Calendrier (jour, mois, week-end, jour férié) | Calcul | Génération du calendrier ; jours fériés ; indicateur été | Aucun | Aucune |

### Alignements les plus délicats

1. **Feu → commune** : code commune de la BDIFF vs référentiel retenu, sinon jointure spatiale.
2. **Indice → commune ou département** : la maille réelle de l'indice conditionne le grain des analyses.
3. **Station météo → zone** : seuil de distance maximal à fixer.
4. **Feu → caserne** : feu non routable, temps de trajet via OSRM.

### Règles de choix en cas de doublon

- Source officielle plutôt que valeur recalculée.
- Source au grain le plus fin pour les événements (BDIFF), source agrégée pour les contrôles (statistiques SDIS).
- Source fournie par le SDIS plutôt que source publique, quand les deux existent.

## Partie 3 : annexe, sources utilisées

| Source | Utilisée pour | Licence | 
|---|---|---|
| BDIFF | Départs de feu | Licence Ouverte 2.0 | 
| Archives de la Météo des forêts | Indice Météo des forêts | Licence Ouverte 2.0 | 
| Données climatologiques de base quotidiennes | Météo quotidienne | Licence Ouverte 2.0 | 
| Interventions des SDIS | Contexte départemental, contrôle de volume | Licence Ouverte 1.0 | 
| BD Forêt V2 | Surface boisée par commune | Licence Ouverte 2.0 | 
| OpenStreetMap (Overpass) | Casernes, points d'eau | ODbL, attribution « © contributeurs OpenStreetMap » | 
| OSRM | Temps de trajet | Données OSM (ODbL), serveur de démonstration : usage non commercial | 
| france-geojson | Géométries des communes | Aucune licence sur le dépôt, données IGN 2018 | 
