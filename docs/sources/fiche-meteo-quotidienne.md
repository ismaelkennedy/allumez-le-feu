# Fiche d'identité - Données climatologiques quotidiennes (Météo-France)

Rédigée par : Hoa Cong, 2026-11-17
Fichiers analysés : `Q_33_previous-1950-2024_RR-T-Vent.csv.gz`, `Q_33_latest-2025-2026_RR-T-Vent.csv.gz` et les deux fichiers `autres-parametres` des mêmes périodes, téléchargés le 17/11/2026 depuis le jeu « Données climatologiques de base - quotidiennes » sur data.gouv.fr (Gironde, analyse faite du 01/01/2016 au 15/11/2026)

## Identité

| Rubrique | Contenu |
|---|---|
| Propriétaire | Météo-France |
| Accès | Jeu « Données climatologiques de base - quotidiennes » sur data.gouv.fr. Un fichier par département, par période et par groupe de paramètres. Téléchargement libre, sans compte |
| Format | CSV compressé en gzip, séparateur `;`. Les noms de stations sont en majuscules sans accents. Deux groupes de fichiers : `RR-T-Vent` (pluie, température, vent, 60 colonnes) et `autres-parametres` (humidité, ensoleillement, orages, 88 colonnes). La description des colonnes est dans deux fichiers à part, `Q_descriptif_champs_*.csv` |
| Contenu | Les mesures de chaque station météo, jour par jour : pluie, températures, vent, humidité, ensoleillement, phénomènes observés (orage, brouillard, grêle) |
| Granularité | Une ligne = une station × un jour. Chaque station a ses coordonnées GPS et son altitude |
| Historique | Depuis 1950 dans le fichier « 1950-2024 » (155 stations en Gironde sur la période), plus un fichier « avant 1949 ». 38 stations ont mesuré au moins la pluie depuis 2016, 21 sont encore actives en 2026 |
| Fraîcheur | Dernier jour : 15/11/2026. Le fichier 2025-2026 est mis à jour chaque jour, le fichier 1950-2024 chaque mois |
| Clés | `NUM_POSTE` : ses 5 premiers chiffres donnent le code INSEE de la commune de la station (33281001 pour Mérignac, code 33281), à vérifier pour les communes fusionnées. `AAAAMMJJ` pour croiser avec la date d'alerte de la BDIFF et le jour de la Météo des forêts |
| Licence | Licence Ouverte / Open Licence 2.0 (indiquée sur data.gouv.fr) |
| Millésime | Fichiers téléchargés le 17/11/2026. Les valeurs récentes peuvent encore changer : chaque mesure a un code qualité (validée, douteuse, filtrée) |
| Données personnelles | Aucune : ce sont des mesures de stations météo |

## Chiffres clés de l'export

- Depuis 2016 : 111 233 lignes `RR-T-Vent` et 90 048 lignes `autres-parametres`, sur 38 stations
- 9 stations mesurent à la fois la température, la pluie, le vent et l'humidité sur tout l'été 2025 : Belin-Béliet, Cazats, Bordeaux-Mérignac, Pauillac, Saint-Émilion, Saint-Gervais, Saint-Sulpice-de-Pommiers, Cazaux et Vendays-Montalivet
- Température la plus haute depuis 2016 : 44,6 °C à Bordeaux-Paulin le 23/06/2026
- À Bordeaux-Mérignac, le nombre de jours à 30 °C ou plus va de 19 (2021) à 54 (2022) entre 2016 et 2025. En 2026, on en compte déjà 79 au 15 novembre
- Été 2024 à Mérignac (juin à septembre) : 274 mm de pluie et 20 jours à 30 °C ou plus, contre 168 mm et 54 jours en 2022. Cela appuie l'hypothèse d'un été humide pour expliquer les 98 feux de la BDIFF en 2024

## Schéma

Seules les colonnes utiles au projet sont listées. Le remplissage est calculé sur les lignes depuis 2016.

| Colonne | Type | Description | Exemple | Remplissage |
|---|---|---|---|---|
| NUM_POSTE | texte | Numéro de la station sur 8 chiffres | 33281001 | 100 % |
| NOM_USUEL | texte | Nom de la station | BORDEAUX-MERIGNAC | 100 % |
| LAT, LON | décimal | Coordonnées de la station, en degrés | 44.830667 ; -0.691333 | 100 % |
| ALTI | entier | Altitude de la station, en mètres | 47 | 100 % |
| AAAAMMJJ | texte | Date de la mesure | 20250715 | 100 % |
| RR | décimal | Pluie en mm, mesurée de 6 h UTC le jour J à 6 h UTC le lendemain et rattachée au jour J | 0.0 | 100 % |
| TN | décimal | Température minimale, en °C | 16.3 | 80 % |
| TX | décimal | Température maximale, en °C | 28.1 | 81 % |
| FFM | décimal | Vitesse moyenne du vent à 10 m, en m/s (multiplier par 3,6 pour des km/h) | 2.8 | 36 % |
| FXI | décimal | Rafale la plus forte de la journée à 10 m, en m/s | 11.3 | 36 % |
| DXI | entier | Direction de cette rafale, en degrés | 290 | 36 % |
| UN | entier | Humidité relative la plus basse de la journée, en % | 36 | 55 % |
| UM | entier | Humidité relative moyenne de la journée, en % | 68 | 55 % |
| DHUMI40 | entier | Durée pendant laquelle l'humidité est restée à 40 % ou moins, en minutes | 145 | 54 % |
| ETPMON | décimal | Évapotranspiration en mm, un indicateur de dessèchement | 5.6 | 32 % |
| ORAG | 0 ou 1 | Orage observé ce jour-là | 0 | 10 % |
| Q + nom de la mesure (QRR, QTX…) | entier | Code qualité : 0 protégée, 1 validée, 2 douteuse, 9 filtrée | 1 | Comme la mesure |

Les exemples viennent de Bordeaux-Mérignac le 15/07/2025, sauf `ORAG`.

## Limites repérées

- Peu de stations mesurent le vent (10) et l'humidité (12) en Gironde, alors que ce sont deux critères du danger de feu. Les 21 stations actives mesurent toutes la pluie et la température.
- Le réseau rétrécit : 38 stations mesuraient la pluie en 2016, il n'en reste que 21 depuis 2022. Une comparaison sur dix ans doit se limiter aux stations présentes sur toute la période.
- Les stations sont des points, alors que la BDIFF ne donne que la commune du feu. Il faudra rattacher chaque commune à la station la plus proche, avec les coordonnées des communes, qui viendront d'une autre source.
- L'Indice Forêt Météo n'est pas fourni. On peut l'approcher avec TX, UN, FFM et RR, mais le calcul officiel utilise les valeurs de midi, que ce fichier ne donne pas.
- Il faut assembler quatre fichiers : empiler les périodes 1950-2024 et 2025-2026, puis joindre `RR-T-Vent` et `autres-parametres` sur `NUM_POSTE` et `AAAAMMJJ`.
- Le vent est en m/s et les durées en minutes. Il faut convertir avant de présenter les chiffres à la direction.

## Questions servies

| Question | Ce que la météo quotidienne apporte |
|---|---|
| 1. Zones les plus touchées | En partie : on peut comparer les zones du département là où il y a une station |
| 2, 5, 6. Seuil de l'indice | Non : le niveau de l'indice est dans la Météo des forêts. Ce fichier aide à expliquer pourquoi un été a eu peu ou beaucoup de jours à risque |
| 3. Comparaison avec les autres départements | En partie : même format partout, mais un téléchargement par département |
| 4. Feux avec indice bas | Oui : le vent et l'humidité réels du jour du feu peuvent montrer ce que l'indice n'a pas vu |
| 7. Critères météo suffisants | Oui, c'est la donnée centrale : chaleur, pluie, vent et humidité au jour près depuis 2016, à croiser avec les feux de la BDIFF |
