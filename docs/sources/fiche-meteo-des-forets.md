# Fiche d'identité - Météo des forêts (Météo-France)

Rédigée par : Hoa Cong, 2026-11-17
Fichiers analysés : `mdf_2024.csv.gz`, `mdf_2025.csv.gz` et `mdf_2026.csv.gz`, téléchargés le 17/11/2026 depuis le jeu « Archives de la Météo des forêts » sur data.gouv.fr (tous les départements de l'Hexagone et de la Corse)

## Identité

| Rubrique | Contenu |
|---|---|
| Propriétaire | Météo-France, dans le cadre de la stratégie nationale de prévention des feux pilotée par la DGPR et la DGSCGC |
| Accès | Jeu « Archives de la Météo des forêts » sur data.gouv.fr : un fichier `mdf_AAAA.csv.gz` par saison, hébergé chez Météo-France. Téléchargement libre, sans compte. Le jeu contient aussi un PDF de présentation, un GeoJSON des départements et un ZIP d'échantillons |
| Format | CSV compressé en gzip, encodage UTF-8. Séparateur `,` en 2024 et 2025, `;` en 2026 |
| Contenu | Le niveau de danger de feu prévu pour chaque département, pour le lendemain (J+1) et le surlendemain (J+2), sur une échelle de 1 (faible) à 4 (très élevé) |
| Granularité | Une ligne = un département × un bulletin quotidien. 96 départements, sans l'outre-mer |
| Historique | Depuis le 3 juin 2024. L'indice existe depuis 2023, mais la saison 2023 n'est pas dans les archives. Uniquement l'été : du 3 juin au 30 septembre en 2024 et 2025, du 28 mai au 5 octobre en 2026 |
| Fraîcheur | Dernier bulletin : 05/10/2026. La saison 2026 est complète. Aucune donnée d'octobre à fin mai |
| Clés | `num_dep` pour croiser avec le `Département` de la BDIFF. `date` pour croiser avec la `Date de première alerte`, en ajoutant un jour pour `niveau_j1` et deux jours pour `niveau_j2` |
| Licence | Licence Ouverte / Open Licence 2.0 (indiquée sur data.gouv.fr) |
| Millésime | Fichiers téléchargés le 17/11/2026, dernière mise à jour du fichier 2026 le 05/10/2026 |
| Données personnelles | Aucune : un niveau par département et par jour |

## Chiffres clés de l'export

- 35 616 lignes en tout (11 520 en 2024, 11 520 en 2025, 12 576 en 2026), 5 colonnes
- 371 bulletins, sans jour manquant ni doublon département × jour
- En Gironde, le niveau 4 (très élevé) n'a jamais été prévu. Le niveau 3 (élevé) l'a été 1 jour en 2024, 4 jours en 2025 et 14 jours en 2026
- En Gironde, le niveau 2 ou plus a été prévu 14 jours sur 120 en 2024, 41 sur 120 en 2025 et 75 sur 131 en 2026
- Dans toute la France, le niveau 4 a été prévu 1 fois en 2024, 29 fois en 2025 et 99 fois en 2026 (en jours × départements)

## Schéma

| Colonne | Type | Description | Exemple | Remplissage |
|---|---|---|---|---|
| date | date et heure (UTC) | Moment où le bulletin est émis, vers 17 h heure de Paris. Ce n'est pas le jour auquel s'applique le niveau | 2025-06-03T14:50:06Z | 100 % |
| num_dep | texte | Code du département. Sans le 0 du début en 2024 et 2025 (`1`), avec en 2026 (`01`). La Corse est en `2A` et `2B` | 33 | 100 % |
| niveau_j1 | entier | Niveau de danger prévu pour le lendemain : 1 faible, 2 modéré, 3 élevé, 4 très élevé | 2 | 100 % |
| niveau_j2 | entier | Niveau prévu pour le surlendemain, même échelle | 1 | 100 % |
| nom_dep | texte | Nom du département. La colonne s'appelle `dep_nom` en 2025 | Gironde | 100 % |

## Limites repérées

- Les archives commencent en juin 2024. Comme la BDIFF s'arrête fin 2025, on ne peut croiser les feux et l'indice que sur deux étés, 2024 et 2025, et 2024 est l'année où la BDIFF ne compte que 98 feux.
- Rien hors saison : les feux de printemps de la BDIFF (mars, avril) n'auront pas de niveau.
- C'est une prévision émise la veille. Le niveau `niveau_j1` du bulletin du 3 juin s'applique au 4 juin : il faut décaler d'un jour avant de comparer avec la date d'un feu.
- Un seul niveau pour toute la Gironde. On ne peut pas comparer le Médoc, le bassin d'Arcachon et le sud du département avec ce fichier.
- Quatre niveaux seulement, et la Gironde n'a jamais dépassé le niveau 3. Un seuil de déclenchement ne peut donc être que 2 ou 3, on ne peut pas tester de seuil intermédiaire.
- Le format change chaque année (séparateur, nom de la dernière colonne, code département avec ou sans 0). Il faut harmoniser les trois fichiers avant de les fusionner.
- Le niveau publié n'est pas une mesure météo brute. D'après la présentation de Météo-France, il combine l'Indice Forêt Météo, la sécheresse de la végétation et la surface de forêt du département, puis il est revu par un prévisionniste.

## Questions servies

| Question | Ce que la Météo des forêts apporte |
|---|---|
| 1. Zones les plus touchées | Non : un seul niveau pour tout le département |
| 2. Seuil de l'indice | Oui, c'est la donnée centrale, mais le croisement avec les feux ne porte que sur les étés 2024 et 2025 |
| 3. Comparaison avec les autres départements | Oui : les 96 départements sont dans le même fichier |
| 4. Feux avec indice bas | Oui, après décalage d'un jour, et seulement pour les feux de juin à septembre |
| 5. Un jour à niveau élevé ou plusieurs de suite | Oui : un bulletin par jour, sans trou |
| 6. Jours de dispositif renforcé selon le seuil | Oui : en Gironde, un seuil au niveau 2 aurait déclenché 14, 41 puis 75 jours de 2024 à 2026, et un seuil au niveau 3, 1, 4 puis 14 jours |
| 7. Critères météo suffisants | Non : le fichier ne donne que le niveau final, pas la chaleur, le vent ou l'humidité qui l'expliquent |
