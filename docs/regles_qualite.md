# Règles de qualité et conformité des données

Responsable : Rim Zougarh (data quality)
Mise à jour : 2026-11-20

## 1. Méthode

Le cadre utilisé est la norme **ISO/IEC 25012** (qualité des données). Elle définit 15 caractéristiques ; on n'en garde que les 6 utiles pour notre question : où concentrer les moyens du SDIS 33, et à partir de quel niveau de la Météo des forêts déclencher le dispositif renforcé, pour réduire les surfaces brûlées en Gironde à l'été 2027.

| Caractéristique | Question posée | Pourquoi c'est important pour nous |
|---|---|---|
| **Complétude** | Rien ne manque ? | Une colonne trop vide ne permet pas de conclure (ex. : les causes) |
| **Exactitude** | Les valeurs sont-elles justes et plausibles ? | Une surface fausse fausse le classement des zones |
| **Cohérence** | Pas de contradiction ni de doublon ? | Un feu compté deux fois gonfle une commune |
| **Actualité** | Les données sont-elles assez récentes ? | La décision porte sur l'été 2027 |
| **Précision** | Le niveau de détail suffit-il ? | Commune ou coordonnées, jour ou heure |
| **Conformité** | Licence et données personnelles OK ? | Obligation légale |

**Les responsables**

| Rôle ISO 25012 | Qui |
|---|---|
| Propriétaire de la décision | SDIS 33 (direction) |
| Chef de projet | Ismaël Kennedy Kante |
| Data quality (responsable de la qualité) | Rim Zougarh |
| Data analyst | Hoa Cong |
| Gestionnaire de la base de données | Elias Akoudad |
| Data engineer | Melissa Benbouabdellah |
| Producteurs des données | IGN et ministère de l'Agriculture (BDIFF, BD Forêt), Météo-France, ministère de l'Intérieur (Interventions des SDIS), contributeurs OpenStreetMap |

**Comment lire les tableaux**

- **Seuil** : la valeur à partir de laquelle la règle est respectée.
- **Résultat** : ce qui a été mesuré, sur la Gironde (33), et sur la Nouvelle-Aquitaine (NA) pour comparer.
- **Statut** : ✅ règle respectée · ⚠️ règle respectée en partie, utilisable avec une limite · ❌ règle non respectée.
- **Décision** : ce qu'on fait de la donnée. Les décisions marquées *proposée* sont à valider par le groupe.

**À quoi servent les seuils** : un seuil sert à **vérifier** la donnée, **pas à la supprimer**. Quand un résultat n'atteint pas le seuil (⚠️ ou ❌), on ne jette pas la donnée : c'est une alerte qui oblige à chercher la cause, puis à **décider** quoi faire (l'utiliser en annonçant la limite, la corriger sur une copie, la compléter avec une autre source, ou ne pas l'utiliser pour une analyse précise). Chaque décision est notée dans la colonne « Décision ».

**Règle générale** : on ne modifie jamais le fichier d'origine et on ne supprime aucune donnée. Les corrections se font sur une copie, et chaque décision est notée ici.

## 2. BDIFF – Incendies de forêt

Fichier : `Incendies.csv`, export du portail BDIFF du 17/11/2026 (Nouvelle-Aquitaine, feux de forêt, 2016-2025).
Mesures faites dans : `notebooks/exploration_bdiff.ipynb` (branche `explo/bdiff`).
Taille : 4 003 feux, dont 1 380 en Gironde.

### Complétude

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| C1 | Les colonnes clés (année, numéro, département, code INSEE, date d'alerte, surface totale) sont toujours remplies | 100 % | 100 % (33 et NA) | ✅ | Rien à faire |
| C2 | La surface forêt est remplie | 90 % | 33 : 100 % · NA : 99,6 % | ✅ | Rien à faire |
| C3 | La cause du feu (`Nature`) est remplie | 70 % | 33 : **38,1 %** · NA : 37,5 % | ❌ | *Proposée* : remplacer le vide par « Inconnue » sur la copie ; toute conclusion sur les causes sera présentée comme fragile |
| C4 | `Précision des surfaces` est remplie | 90 % | 33 : 49,9 % sur 2016-2025, **100 % depuis 2022** | ⚠️ | *Proposée* : n'utiliser cette colonne que depuis 2022 |
| C5 | `Décès ou bâtiments touchés` est remplie | 90 % | **100 % depuis 2022**, presque vide avant | ⚠️ | *Proposée* : n'utiliser ces colonnes que depuis 2022 |
| C6 | Chaque année a un nombre de feux plausible (au moins la moitié de la moyenne des autres années) | ≥ 50 % de la moyenne | 33 : **2024 = 29 feux** (19 % de la moyenne des autres années) et **2021 = 65 feux** (44 %) ; les autres années sont entre 73 % et 194 % · NA : 2024 = 98 pour 434. Recoupement avec les Interventions des SDIS (section 6) : les pompiers ont aussi peu de feux de végétation en Gironde en 2021 (275) et en 2024 (175) | ⚠️ | **Validée : garder 2021 et 2024 et les utiliser.** Ce sont surtout des années calmes (confirmé par une autre source). Pour 2024, la baisse est plus forte dans BDIFF, donc quelques feux manquent peut-être : le signaler dans les tendances |
| C7 | Les colonnes réservées à la zone méditerranéenne (`Surface maquis garrigues`, `Type de peuplement`) | – | 0 % remplies | – | *Proposée* : les ignorer, elles ne concernent pas la Gironde |

### Exactitude

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| E1 | La surface totale est strictement positive | 100 % | 100 % (aucune surface à 0 ni vide) | ✅ | Rien à faire |
| E2 | La surface forêt n'est pas plus grande que la surface totale | 100 % | 100 % | ✅ | Rien à faire |
| E3 | Les très petites surfaces (≤ 10 m²) sont rares | < 5 % | 33 : 92 feux (6,7 %), dont 10 à 1 m² · NA : 346 (8,6 %) | ⚠️ | *Proposée* : les garder, les compter à part dans les analyses de surface ; vérifier dans la documentation BDIFF si 1 m² est une valeur par défaut |
| E4 | Les surfaces sont mesurées plutôt qu'estimées | – | 33 : **96,8 % estimées** (sur les feux renseignés) | ⚠️ | À garder en tête : les surfaces sont des ordres de grandeur, pas des mesures exactes |
| E5 | Aucun feu n'est marqué « Données partielles ou non valides » | 0 | 33 : **10 feux** (tous en 2017) · NA : 13 | ⚠️ | *Proposée* : les garder et les marquer, les exclure seulement si un résultat en dépend |
| E6 | L'heure d'alerte est réelle (pas 00:00 pile par défaut) | 100 % | 33 : 100 % · NA : 2 alertes à 00:00 | ✅ | Rien à faire en Gironde |

### Cohérence

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| H1 | Pas de doublon sur l'identifiant `Année` + `Numéro` + `Département` | 0 doublon | 0 | ✅ | Rien à faire |
| H2 | L'année correspond à l'année de la date d'alerte | 100 % | 100 % | ✅ | Rien à faire |
| H3 | Le code INSEE a 5 caractères et commence par le code du département | 100 % | 100 % | ✅ | Rien à faire |
| H4 | Un code INSEE a un seul nom de commune | 100 % | 33 : **2 codes** avec deux noms (Margaux / Margaux-Cantenac, Sallebuf / Sallebœuf) · NA : 8 | ⚠️ | *Proposée* : toujours relier et regrouper par **code INSEE**, jamais par nom |
| H5 | Avant 2023, la somme des sous-surfaces = surface totale | 100 % | 33 : 100 % · NA : 51 écarts sur 3 068 | ✅ | Rien à faire en Gironde ; garder la surface totale comme référence |
| H6 | Le format des colonnes de surfaces est le même sur toute la période | – | Changement de format en 2023 | ⚠️ | *Proposée* : ne comparer dans le temps que `Surface parcourue` et `Surface forêt` |

### Actualité

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| A1 | La dernière saison complète disponible est la plus récente possible | Saison 2026 | **Dernière saison : 2025**. La saison 2026 n'est pas publiée (le portail publie jusqu'à l'année précédente) | ❌ | Chercher une autre source pour 2026 (SDIS 33, FIRMS, EFFIS), ou annoncer clairement que l'analyse s'arrête en 2025 |
| A2 | L'historique est assez long pour voir une tendance | 10 ans | 10 ans (2016-2025) ; la BDIFF remonte à 2006 | ✅ | Possible de réexporter depuis 2006 si besoin |

### Précision

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| P1 | Le feu est localisé assez finement pour choisir des zones | Coordonnées ou carreau DFCI | **Commune seulement** | ⚠️ | Travailler à l'échelle de la commune. Pour plus fin : demander les coordonnées au SDIS 33, ou utiliser FIRMS pour les grands feux |
| P2 | La date est au moins au jour, pour croiser avec la Météo des forêts | Jour | Date et heure à la minute | ✅ | Rien à faire |
| P3 | Les surfaces sont dans une unité exploitable | – | En **m²** | ✅ | Convertir en hectares sur la copie (÷ 10 000) |

### Conformité

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| L1 | La licence permet la réutilisation | Licence ouverte | **Licence Ouverte 2.0** | ✅ | Citer « Source : BDIFF, bdiff.agriculture.gouv.fr » avec la date de l'export |
| L2 | Aucune donnée ne permet d'identifier une personne | 0 | Pas de nom ni d'adresse. Les colonnes décès et bâtiments détruits, croisées avec la commune et la date, peuvent identifier une personne dans une petite commune. En Gironde : 0 feu avec décès ou bâtiment touché | ⚠️ | *Proposée* : ne pas afficher ces colonnes au niveau du feu ; seulement en total par département ou par année |
| L3 | Le fichier n'est pas déposé dans le dépôt GitHub | – | `data/` est dans le `.gitignore` | ✅ | Rien à faire |

### Bilan BDIFF

**Utilisable**, avec ces limites à annoncer dans le rendu :

1. La cause est inconnue pour 62 % des feux en Gironde.
2. L'année 2024 a très peu de feux (29 en Gironde) : c'est surtout une année calme (confirmé par les Interventions des SDIS), mais quelques feux manquent peut-être.
3. La saison 2026 n'est pas disponible.
4. Le feu est localisé à la commune, pas plus finement.
5. Les surfaces sont presque toutes estimées.

## 3. Météo des forêts

Fichiers : `mdf_2024.csv.gz`, `mdf_2025.csv.gz`, `mdf_2026.csv.gz`, jeu « Archives de la Météo des forêts » sur data.gouv.fr (mise à jour du 05/10/2026), plus le PDF de présentation de Météo-France.
Contenu : une ligne par département et par jour de publication, avec le niveau de danger prévu pour le lendemain (`niveau_j1`) et le surlendemain (`niveau_j2`).
Échelle : 4 niveaux – 1 faible (vert), 2 modéré (jaune), 3 élevé (orange), 4 très élevé (rouge).
Taille : 35 616 lignes (96 départements), dont 371 jours pour la Gironde.

### Complétude

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| C1 | Aucune valeur vide | 100 % | 100 % (aucune case vide) | ✅ | Rien à faire |
| C2 | Chaque jour de la saison a une ligne pour chaque département | 100 % | 100 % : aucun jour manquant, 96 départements chaque jour | ✅ | Rien à faire |
| C3 | L'historique est assez long pour fixer un seuil | Au moins 5 saisons | **3 saisons** (2024, 2025, 2026). La Météo des forêts existe depuis 2023, mais les archives commencent en 2024 | ❌ | *Proposée* : compléter avec un indice recalculé sur de longues années (IFM historique de Copernicus, ou à demander à Météo-France) ; sinon annoncer que le seuil repose sur peu d'années |
| C4 | Les saisons couvertes à la fois par la Météo des forêts et par BDIFF sont assez nombreuses | Au moins 5 saisons | **2 saisons** (2024 et 2025), dont 2024 qui paraît incomplète dans BDIFF (29 feux en Gironde). 2026 n'est pas dans BDIFF | ❌ | *Proposée* : demander les feux 2026 au SDIS 33 pour avoir 3 saisons ; présenter le croisement indice × feux comme une première indication, pas comme une preuve |
| C5 | La période couverte inclut tous les mois où les feux partent | Toute l'année à risque | Du **3 juin au 30 septembre** (2024, 2025), du 28 mai au 5 octobre (2026). Pas de printemps : or en Gironde, 51 feux en avril 2017 et 25 en avril 2021 (BDIFF) | ⚠️ | Le seuil ne vaudra que pour l'été. Le dire dans le rendu |

### Exactitude

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| E1 | Les niveaux sont entre 1 et 4 | 100 % | 100 % | ✅ | Rien à faire |
| E2 | La prévision du lendemain (`niveau_j1`) confirme celle faite la veille pour le surlendemain (`niveau_j2`) | – | Gironde : identiques dans **93,5 %** des cas | ✅ | Normal : la prévision est corrigée le lendemain. Utiliser `niveau_j1`, la plus récente |

### Cohérence

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| H1 | Pas de doublon département + jour | 0 doublon | 0 | ✅ | Rien à faire |
| H2 | Le format des fichiers est le même chaque année | Identique | **Change chaque année** : séparateur `,` (2024, 2025) puis `;` (2026) ; code département `1` puis `01` en 2026 ; colonne `nom_dep` (2024, 2026) puis `dep_nom` (2025) ; heure de publication 16:00 (2024) puis 14:50 UTC | ⚠️ | *Proposée* : au chargement, détecter le séparateur, renommer la colonne en `nom_dep`, écrire le code département sur 2 caractères (`01`), comme dans BDIFF |
| H3 | Le nom du département correspond au code | 100 % | Gironde : toujours « Gironde » pour le code 33 | ✅ | Rien à faire |

### Actualité

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| A1 | La dernière saison est disponible | Saison 2026 | **2026 disponible**, jusqu'au 05/10/2026 | ✅ | Rien à faire |

### Précision

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| P1 | Le niveau est donné à une échelle plus fine que le département, pour choisir des zones | Zone, massif ou commune | **Département seulement** : un seul niveau pour toute la Gironde | ⚠️ | On ne peut pas fixer un seuil différent par zone avec cette source. Si on en a besoin : indice plus fin à demander à Météo-France ou au SDIS 33 |
| P2 | La date de la ligne est la date du jour prévu | – | **Non** : `date` est le jour de **publication**. `niveau_j1` vaut pour le **lendemain** | ⚠️ | *Proposée* : pour croiser avec BDIFF, ajouter 1 jour à `date` pour `niveau_j1` (2 jours pour `niveau_j2`). Sans ça, chaque feu serait comparé au niveau de la veille |
| P3 | Tous les niveaux sont représentés en Gironde | Les 4 niveaux | Gironde, 371 jours : niveau 1 = 241 jours, niveau 2 = 111, **niveau 3 = 19, niveau 4 = 0** | ⚠️ | Très peu de jours « élevé » et aucun « très élevé » : on ne peut pas étudier le niveau 4 en Gironde. Comparer avec les autres départements de la région |

### Conformité

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| L1 | La licence permet la réutilisation | Licence ouverte | **Licence Ouverte 2.0** (vérifiée sur data.gouv.fr) | ✅ | Citer « Source : Météo-France – Météo des forêts » avec la date de mise à jour |
| L2 | Aucune donnée personnelle | 0 | Aucune : un niveau par département et par jour | ✅ | Rien à faire |

### Bilan Météo des forêts

**Données propres, mais historique trop court** pour fixer un seuil solide. Limites à annoncer dans le rendu :

1. Seulement 3 saisons d'archives, dont 2 seulement croisables avec BDIFF (et 2024 paraît incomplète dans BDIFF).
2. Un seul niveau pour toute la Gironde : pas de seuil par zone possible avec cette source.
3. Seulement 19 jours au niveau « élevé » en Gironde, et aucun au niveau « très élevé ».
4. Pas de données au printemps, alors que des feux partent en avril.
5. **Piège à éviter** : `niveau_j1` vaut pour le lendemain de `date`.

## 4. Données climatologiques quotidiennes

Fichiers : `Q_33_previous-1950-2024_*.csv.gz` et `Q_33_latest-2025-2026_*.csv.gz` (fichiers `RR-T-Vent` et `autres-parametres`), jeu « Données climatologiques de base - quotidiennes » sur data.gouv.fr, plus les fichiers de description des champs.
Contenu : une ligne par station météo et par jour. Colonnes utiles : `TX` (température max), `UN` (humidité min), `RR` (pluie), `FXI` (rafale max).
Période étudiée : 2016 à novembre 2026, pour être alignée sur BDIFF. Taille : 111 296 lignes, 38 stations en Gironde.
Chaque valeur a un **code qualité** de Météo-France : 0 = validée définitivement, 1 = validée, 9 = filtrée (premiers contrôles passés), 2 = douteuse.

### Complétude

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| C1 | Chaque jour d'été a des mesures en Gironde | 100 % des jours | 100 % : au moins 21 stations pour `TX` et 11 pour `UN` chaque jour d'été, 2016-2025 | ✅ | Rien à faire |
| C2 | Assez de stations complètes pour couvrir le département (≥ 95 % des jours d'été 2016-2025 remplis) | Au moins 10 stations | `TX` : 16 stations · `RR` : 20 · `UN` : **12** · `FXI` (vent) : **10** | ✅ | **Validée : garder toutes les stations.** Ajouter sur la copie une colonne « station complète : oui / non » (oui = mesures au moins 95 % des jours d'été). Pour relier une commune à une station, prendre en priorité la station complète la plus proche ; les stations incomplètes servent de secours les jours où elles ont une mesure |
| C3 | Les 4 variables utiles sont mesurées par les mêmes stations | – | Non : 38 stations mesurent la pluie, 29 la température, 14 l'humidité, 10 le vent | ⚠️ | Pour l'humidité et le vent, une station couvre une grande zone. Le dire si on calcule des zones |

### Exactitude

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| E1 | Aucune valeur marquée « douteuse » (code 2) | 0 | **0** | ✅ | Rien à faire |
| E2 | Les valeurs sont validées (code 0 ou 1) | 95 % | `TX` : 99,97 % · `RR` : 99,9 % · `UN` : 99,99 % · `FXI` : 99,99 % (le reste en code 9) | ✅ | Rien à faire |
| E3 | Les valeurs sont dans des plages plausibles | 100 % | `TX` de -1,3 à 44,6 °C · `UN` de 6 à 100 % · `RR` de 0 à 133 mm · `FXI` de 2,6 à 45,4 m/s | ✅ | Rien à faire |
| E4 | Une valeur extrême est confirmée par les stations voisines | – | Maximum de 44,6 °C à Bordeaux-Paulin le 23/06/2026 : le même jour, 21 stations ont en moyenne 42,4 °C. C'est une vraie canicule, pas une erreur | ✅ | Garder |

### Cohérence

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| H1 | Pas de doublon station + jour | 0 | 0 | ✅ | Rien à faire |
| H2 | La température max est ≥ la température min | 100 % | 100 % | ✅ | Rien à faire |
| H3 | Une station garde le même nom et les mêmes coordonnées | 100 % | 100 % | ✅ | Rien à faire |

### Actualité

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| A1 | La saison 2026 est disponible | Saison 2026 | **Données jusqu'au 18/11/2026**, mises à jour chaque jour | ✅ | Rien à faire |
| A2 | L'historique est long | 10 ans | Depuis 1950 (et avant pour certaines stations) | ✅ | Permet de recalculer un indice sur de nombreuses années si besoin |

### Précision

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| P1 | La mesure peut être reliée à une commune | – | **Stations** avec coordonnées, pas des communes | ⚠️ | *Proposée* : relier chaque commune à la station complète la plus proche (calcul de distance avec les coordonnées) |
| P2 | Le jour de la mesure correspond au jour du feu | – | `TX`, `UN`, `FXI` : jour J. **`RR` (pluie) : de 6 h le jour J à 6 h le lendemain**, notée au jour J | ⚠️ | Piège à connaître : la pluie notée au jour d'un feu inclut la nuit suivante. Pour « la pluie avant le feu », prendre `RR` de la veille |
| P3 | Le niveau de détail suffit | Jour | Valeur par jour (le max ou le min de la journée) | ✅ | Pour l'heure exacte d'un feu : données horaires de Météo-France |

### Conformité

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| L1 | La licence permet la réutilisation | Licence ouverte | **Licence Ouverte 2.0** (vérifiée sur data.gouv.fr) | ✅ | Citer « Source : Météo-France » avec la date de mise à jour |
| L2 | Aucune donnée personnelle | 0 | Aucune : des mesures de stations météo | ✅ | Rien à faire |

### Bilan météo quotidienne

**Très bonne qualité**, utilisable telle quelle. Points à connaître :

1. Peu de stations pour l'humidité (12) et le vent (10) : la couverture du département est plus large que fine.
2. Les mesures sont par station : il faut relier chaque commune à une station.
3. **Piège** : la pluie `RR` d'un jour inclut la nuit suivante.

## 5. BD Forêt V2

Fichier : `BDFORET_2-0__SHP_LAMB93_D033_2017-05-10.7z` (Gironde), téléchargé sur la Géoplateforme de l'IGN. Couche `FORMATION_VEGETALE` (shapefile, Lambert 93, UTF-8).
Contenu : un polygone par formation végétale de plus de 0,5 ha, avec son type (`CODE_TFV`, `TFV`), son groupe (`TFV_G11`) et son essence (`ESSENCE`).
Taille : 53 130 polygones, 549 745 ha.

### Complétude

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| C1 | Aucun attribut vide (`ID`, `CODE_TFV`, `TFV`, `TFV_G11`, `ESSENCE`) | 100 % | 100 % | ✅ | Rien à faire |
| C2 | Aucune géométrie vide | 0 | 0 | ✅ | Rien à faire |
| C3 | L'essence est connue (ni « NR » non renseigné, ni « NC » non concerné) | 90 % de la surface | **73,7 %** : « NR » = 22,4 % de la surface, « NC » = 3,9 % (landes) | ❌ | *Proposée* : traiter « NR » comme une catégorie à part (« forêt sans arbres visibles ») et non comme une erreur ; ne calculer l'inflammabilité par essence que sur la surface connue |

### Exactitude

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| E1 | Les surfaces sont positives | 100 % | 100 % | ✅ | Rien à faire |
| E2 | Les polygones respectent la taille minimum de la BD Forêt (0,5 ha) | 100 % | 42 polygones sous 0,5 ha (sur 53 130), le plus petit fait 0,014 ha | ✅ | Négligeable (moins de 0,1 %) : les garder |
| E3 | La surface totale est plausible pour la Gironde | – | 549 745 ha (forêts et landes), dont 222 194 ha de pin maritime pur | ✅ | Ordre de grandeur cohérent avec un département très boisé |
| E4 | Les formations correspondent à de vraies forêts aujourd'hui | – | **22,3 % de la surface (122 867 ha) en « Forêt fermée sans couvert arboré »** : parcelles coupées ou jeunes plantations, en grande partie après la tempête Klaus de 2009 | ⚠️ | Ces parcelles ont repoussé depuis. À garder en tête : la carte sous-estime la forêt de pins d'aujourd'hui |

### Cohérence

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| H1 | Pas de doublon d'identifiant | 0 | 0 | ✅ | Rien à faire |
| H2 | Un code `CODE_TFV` a un seul libellé `TFV` | 100 % | 100 % | ✅ | Rien à faire |
| H3 | Les libellés sont bien écrits | – | Apostrophes manquantes dans le fichier d'origine (« Forêt fermée dun autre feuillu pur ») | ⚠️ | Utiliser `CODE_TFV` pour les calculs, pas le libellé |

### Actualité

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| A1 | La carte décrit la forêt actuelle | Moins de 5 ans | **Forêt décrite entre 2010 et 2013**, d'après des photos aériennes de 2009 ; édition du 10/05/2017. C'est la seule version de la BD Forêt V2 pour la Gironde | ❌ | La carte ne montre **pas les 2022 : environ 30 000 ha brûlés** (Landiras, La Teste-de-Buch, Saumos) sont encore indiqués en forêt. *Proposée* : l'annoncer comme une limite majeure ; pour les zones brûlées, croiser avec les contours EFFIS des feux de 2022 |

### Précision

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| P1 | Le détail suffit pour calculer la forêt par commune | Polygones de 0,5 ha | Polygones de 0,5 ha minimum, échelle 1/25 000 | ✅ | Croiser avec les contours des communes (Admin Express) |
| P2 | Le système de coordonnées est connu | – | Lambert 93 (fichier `.prj`) | ✅ | Convertir en WGS84 pour l'app si besoin |

### Conformité

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| L1 | La licence permet la réutilisation | Licence ouverte | **Licence Ouverte 2.0** (vérifiée sur data.gouv.fr). Les métadonnées de 2017 citent encore les anciennes conditions IGN, remplacées depuis | ✅ | Citer « Source : IGN – BD Forêt V2 » |
| L2 | Aucune donnée personnelle | 0 | Aucune : ni propriétaire, ni parcelle cadastrale | ✅ | Rien à faire |

### Bilan BD Forêt

**Bonne qualité technique, mais carte ancienne.** Limites à annoncer :

1. **La forêt décrite est celle de 2010-2013** : les grands feux de 2022 n'y sont pas.
2. 22 % de la surface est « sans couvert arboré » (coupes et jeunes plantations après la tempête Klaus) : la carte sous-estime la forêt de pins actuelle.
3. L'essence n'est pas connue pour 26 % de la surface.

## 6. Interventions des SDIS

Fichiers : `interventions2016.csv` à `interventions2024.csv`, jeu « Interventions réalisées par les services d'incendie et de secours » sur data.gouv.fr (mise à jour du 02/07/2026).
Contenu : une ligne par service d'incendie et de secours et par an (un par département, plus la BSPP de Paris et le BMPM de Marseille), 71 colonnes. Colonne utile : `Feux de végétations`.
Taille : 99 lignes par an, 9 années étudiées (2016-2024).

### Complétude

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| C1 | `Feux de végétations` est remplie pour la Gironde et la Nouvelle-Aquitaine chaque année | 100 % | 100 % (9 années sur 9) | ✅ | Rien à faire |
| C2 | `Feux de végétations` est remplie pour tous les services | 100 % | 3 manques sur 891 lignes, tous en outre-mer : Martinique 2018 (« N.C. »), Mayotte 2019 et 2022 (vide) | ✅ | Hors de notre zone : rien à faire |

### Exactitude

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| E1 | Les chiffres sont des nombres entiers | 100 % | **2024 : 5 valeurs avec un séparateur de milliers illisible** (« 1 403 » pour Bouches-du-Rhône, Hérault, Pyrénées-Orientales, Guyane, Réunion) | ⚠️ | *Proposée* : lire la colonne en texte, retirer les espaces, puis convertir en nombre. Aucune valeur de Nouvelle-Aquitaine n'est touchée |
| E2 | Les chiffres de la Gironde évoluent comme ceux de BDIFF | Corrélation ≥ 0,7 | **Corrélation de 0,96** sur 2016-2024 : les deux sources montrent les mêmes bonnes et mauvaises années | ✅ | Les deux sources se confirment l'une l'autre |
| E3 | Pas de zéro suspect | – | Savoie 2024 : 0 feu de végétation | ⚠️ | Hors de notre zone : à signaler seulement |

### Cohérence

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| H1 | Pas de doublon de service dans une année | 0 | 0 | ✅ | Rien à faire |
| H2 | Le code département a le même format que BDIFF (2 caractères) | 100 % | **Non** : `1`, `2`… au lieu de `01`, `02` ; Corse en minuscules (`2a`, `2b`) ; lignes `BSPP` et `BMPM` qui ne sont pas des départements | ⚠️ | *Proposée* : écrire les codes sur 2 caractères en majuscules ; exclure BSPP et BMPM (hors de notre zone) |
| H3 | Le même format chaque année | Identique | Mêmes 71 colonnes, même séparateur `;`, même encodage chaque année | ✅ | Rien à faire |

### Actualité

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| A1 | La dernière année est récente | Année 2025 | **Dernière année : 2024** (publiée le 02/07/2026). Ni 2025 ni 2026 | ⚠️ | Utiliser pour comparer les années et les départements, pas pour 2025-2026 |

### Précision

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| P1 | Le détail suffit pour choisir des zones | Commune | **Département et année seulement** | ⚠️ | Sert à situer la Gironde dans la région, pas à choisir des zones |
| P2 | Les feux comptés sont les mêmes que dans BDIFF | Feux de forêt | **Non** : « feux de végétations » = tous les feux de végétation (forêt, champs, broussailles), environ 3 fois plus que BDIFF chaque année | ⚠️ | Ne jamais additionner ou comparer directement les chiffres des deux sources : comparer seulement les évolutions |

### Conformité

| # | Règle | Seuil | Résultat | Statut | Décision |
|---|---|---|---|---|---|
| L1 | La licence permet la réutilisation | Licence ouverte | **Licence Ouverte 1.0** (vérifiée sur data.gouv.fr) | ✅ | Citer « Source : Ministère de l'Intérieur – DGSCGC » avec la date de mise à jour |
| L2 | Aucune donnée personnelle | 0 | Aucune : des totaux par service | ✅ | Rien à faire |
| L3 | L'encodage est connu | – | **Windows-1252** (pas UTF-8, contrairement aux autres sources) | ⚠️ | Lire avec l'encodage `cp1252`, sinon les accents sont abîmés |

### Bilan Interventions des SDIS

**Bonne qualité, utile comme source de contrôle.** Elle confirme les tendances de BDIFF (corrélation 0,96) et montre que 2024 est surtout une année calme. Limites : département et année seulement, s'arrête en 2024, compte tous les feux de végétation.

## 7. OpenStreetMap (casernes et points d'eau)

Utilisée par l'app pour les casernes (`amenity=fire_station`) et les points d'eau incendie (`emergency=fire_hydrant`, `water_tank`, `suction_point`, `fire_water_pond`).

**Mesures pas encore faites** : le 20/11/2026, les serveurs publics d'OpenStreetMap (Overpass) étaient saturés. Les règles sont posées ci-dessous ; les résultats seront mesurés sur l'extraction faite par l'app.

| # | Caractéristique | Règle | Seuil | Résultat | Statut |
|---|---|---|---|---|---|
| C1 | Complétude | Le nombre de casernes est proche de la liste officielle du SDIS 33 | ≥ 95 % des casernes officielles | À mesurer : demander la liste officielle au SDIS 33 | – |
| C2 | Complétude | Chaque caserne a un nom | 100 % | À mesurer | – |
| C3 | Complétude | Les points d'eau ont une capacité (volume ou débit) | 50 % | À mesurer | – |
| E1 | Exactitude | Les casernes sont bien des casernes du SDIS (`operator`), pas des casernes privées ou militaires | 100 % | À mesurer | – |
| H1 | Cohérence | Pas de caserne en double (même nom à moins de 500 m) | 0 | À mesurer | – |
| A1 | Actualité | Les points d'eau ont une date de vérification récente (`check_date`, `survey:date`) | – | À mesurer | – |
| L1 | Conformité | Licence | – | **ODbL** : citer « © contributeurs OpenStreetMap » ; une base publiée qui contient ces données doit rester sous ODbL | ✅ |

**À savoir** : OpenStreetMap est rempli par des bénévoles. L'absence d'une caserne ou d'un point d'eau dans OSM ne veut pas dire qu'il n'existe pas. Pour les points d'eau DFCI, la source de référence est la DFCI (PIGMA), à demander.

## 8. Tests à automatiser

Contrôles à coder dans le pipeline de chargement, à relancer à chaque nouvel export. Un test qui échoue doit bloquer le chargement ou produire une alerte.

### BDIFF

| Test | Règle | Si le test échoue |
|---|---|---|
| Les 3 lignes d'en-tête sont présentes et la 4ᵉ ligne contient les titres attendus | Format | Bloquer : le format de l'export a changé |
| Les 24 colonnes attendues sont présentes, avec les mêmes noms | Format | Bloquer |
| `Département` et `Code INSEE` sont lus en texte ; le code INSEE a 5 caractères | H3 | Bloquer |
| Le code INSEE commence par le code du département | H3 | Alerte |
| Aucune valeur vide dans les colonnes clés | C1 | Bloquer |
| Aucun doublon sur `Année` + `Numéro` + `Département` | H1 | Bloquer |
| L'année = l'année de la date d'alerte | H2 | Alerte |
| Surface totale > 0 et surface forêt ≤ surface totale | E1, E2 | Alerte |
| Taux de remplissage de `Nature` (pour suivre son évolution) | C3 | Information |
| Nombre de feux par année comparé à la moyenne | C6 | Alerte si une année est sous 50 % de la moyenne |
| Nombre de feux marqués « Données partielles ou non valides » | E5 | Information |

### Météo des forêts

| Test | Règle | Si le test échoue |
|---|---|---|
| Le séparateur est détecté (`,` ou `;`) et les colonnes `date`, `num_dep`, `niveau_j1`, `niveau_j2` sont présentes | H2 | Bloquer : le format a changé |
| La colonne du nom de département est renommée en `nom_dep` | H2 | Bloquer |
| Le code département est écrit sur 2 caractères (`01`, `33`) | H2 | Bloquer |
| Aucune valeur vide | C1 | Bloquer |
| Les niveaux sont entre 1 et 4 | E1 | Bloquer |
| Pas de doublon département + jour | H1 | Bloquer |
| Chaque jour de la saison a 96 départements, sans jour manquant | C2 | Alerte |
| Le jour prévu = `date` + 1 jour pour `niveau_j1` (+ 2 jours pour `niveau_j2`) | P2 | Bloquer le croisement avec BDIFF si ce décalage n'est pas appliqué |

### Météo quotidienne

| Test | Règle | Si le test échoue |
|---|---|---|
| Les colonnes `NUM_POSTE`, `AAAAMMJJ`, `TX`, `RR`, `FXI` (et `UN` dans `autres-parametres`) sont présentes | Format | Bloquer |
| Pas de doublon station + jour | H1 | Bloquer |
| Aucune valeur avec le code qualité 2 (douteuse) | E1 | Alerte : exclure la valeur |
| `TX` entre -20 et 50 °C, `UN` entre 0 et 100 %, `RR` ≥ 0, `FXI` ≥ 0 | E3 | Alerte |
| `TX` ≥ `TN` | H2 | Alerte |
| Chaque jour d'été a au moins 10 stations avec `TX` et 5 avec `UN` | C1 | Alerte |
| Une station garde le même nom et les mêmes coordonnées | H3 | Alerte |

### BD Forêt

| Test | Règle | Si le test échoue |
|---|---|---|
| Les champs `ID`, `CODE_TFV`, `TFV`, `TFV_G11`, `ESSENCE` sont présents et remplis | C1 | Bloquer |
| Pas de géométrie vide, surface > 0 | C2, E1 | Bloquer |
| Pas de doublon d'`ID` | H1 | Bloquer |
| Un `CODE_TFV` a un seul libellé | H2 | Alerte |
| Le système de coordonnées est Lambert 93 | P2 | Bloquer : convertir avant tout croisement |

### Interventions des SDIS

| Test | Règle | Si le test échoue |
|---|---|---|
| Lecture en `cp1252`, séparateur `;`, 71 colonnes | L3, H3 | Bloquer |
| `Feux de végétations` convertie en nombre après retrait des espaces | E1 | Alerte : lister les valeurs non converties |
| Code département écrit sur 2 caractères, en majuscules | H2 | Bloquer |
| Une seule ligne par service et par an | H1 | Bloquer |
| Les 12 départements de Nouvelle-Aquitaine sont présents chaque année | C1 | Alerte |

## 9. Seuils à valider

Les seuils ci-dessous ont été validés par la data quality ; ils restent à présenter au groupe. Rappels :

- Un seuil se fixe d'après l'usage de la donnée, **avant** de regarder le résultat ; on ne le baisse pas pour qu'une donnée passe.
- Un seuil sert à **vérifier**, **jamais à supprimer** : une donnée sous le seuil est signalée, puis on décide quoi en faire.

| Type de règle | Seuil proposé | Pourquoi | Règles concernées |
|---|---|---|---|
| Colonnes clés (identifiant, code INSEE, date, surface, niveau) | **100 %**, 0 doublon ✅ validé | Sans elles, on ne peut ni compter, ni placer, ni relier un feu | BDIFF C1, H1-H3 · MDF C1, H1 · Météo H1 · BD Forêt C1, H1 · SDIS C1, H1 |
| Colonnes d'analyse importantes | **90 %** ✅ validé | Quelques vides ne changent pas la conclusion | BDIFF C2, C4, C5 · BD Forêt C3 |
| Colonnes d'analyse secondaires (ex. : la cause) | **70 %** ✅ validé | Au-dessous, la partie connue peut ne pas représenter le reste | BDIFF C3 |
| Valeurs bizarres tolérées | **moins de 5 %** ✅ validé | Une vraie base a toujours quelques valeurs étranges | BDIFF E3 · BD Forêt E2 |
| Valeurs validées par le producteur | **95 %** ✅ validé | Les codes qualité de Météo-France le permettent | Météo E2 |
| Historique pour fixer un seuil de l'indice | **au moins 5 saisons** ✅ validé | Avec moins, une seule saison exceptionnelle (comme 2022) pèse trop | MDF C3, C4 |
| Nombre de feux par année | **au moins 50 % de la moyenne** des autres années ✅ validé | Au-dessous, il faut vérifier si l'année est complète | BDIFF C6 |
| Couverture du département par les stations | **au moins 10 stations** complètes à 95 % ✅ validé (toutes les stations sont gardées) | Pour avoir plusieurs mesures dans chaque partie de la Gironde | Météo C2 |
| Âge de la carte de la forêt | **moins de 5 ans** ✅ validé | La forêt landaise change vite (coupes, tempêtes, feux) | BD Forêt A1 |
| Accord entre deux sources qui mesurent la même chose | **corrélation d'au moins 0,7** ✅ validé (pour l'instant) | En dessous, l'une des deux sources pose problème | SDIS E2 |
