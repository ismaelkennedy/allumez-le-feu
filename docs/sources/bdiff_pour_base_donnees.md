# BDIFF – Ce qu'il faut savoir pour l'intégrer dans la base

Rédigée par : Rim Zougarh, 2026-11-20
Fiche source complète : `docs/sources/fiche-bdiff.md` (branche `docs/analyse`)
Exploration détaillée : `notebooks/exploration_bdiff.ipynb` (branche `explo/bdiff`)

## À quoi sert cette source dans le projet

Objectif du projet : **réduire les surfaces brûlées en Gironde à l'été 2027**, en choisissant où concentrer les moyens du SDIS 33 et à partir de quel niveau de la Météo des forêts déclencher le dispositif renforcé.

BDIFF est **la liste des feux** : c'est la table centrale à laquelle on raccroche les autres sources (Météo des forêts, météo, BD Forêt, interventions SDIS).

En Gironde, 2016-2025 : 1 380 feux, 31 793 ha brûlés. Les 4 plus grands feux (2022) font 89 % de la surface.

## Le fichier

| | |
|---|---|
| Fichier | `Incendies.csv` (dans le ZIP téléchargé depuis https://bdiff.agriculture.gouv.fr) |
| Emplacement local | `data/raw/Incendies.csv` – le dossier `data/` est dans le `.gitignore`, **le CSV n'est pas sur GitHub** : chacun le télécharge |
| Filtres de l'export | Nouvelle-Aquitaine, type de feu « F » (forêt), du 01/01/2016 au 31/12/2025 |
| Taille | 4 003 feux, 24 colonnes, 12 départements (Gironde : 1 380) |
| Format | CSV, séparateur `;`, encodage UTF-8 |
| Licence | Licence Ouverte 2.0 – citer « bdiff.agriculture.gouv.fr » |

## Comment le lire

1. **Sauter les 3 premières lignes** : ce sont des informations sur l'export, la ligne des titres de colonnes est la 4ᵉ.
2. **Lire `Département` et `Code INSEE` en texte**, jamais en nombre (sinon on perd les zéros du début dans d'autres régions, et la Corse a des codes `2A` / `2B`).
3. Convertir `Date de première alerte` en date et heure. Certaines dates ont des secondes (`10:49:58`), d'autres non (`14:42:00`).

```python
import pandas as pd

df = pd.read_csv(
    "data/raw/Incendies.csv",
    sep=";",
    skiprows=3,
    encoding="utf-8",
    dtype={"Département": str, "Code INSEE": str},
)
df["Date de première alerte"] = pd.to_datetime(df["Date de première alerte"])
```

## Clés

| Usage | Colonne(s) | Remarque |
|---|---|---|
| Identifiant d'un feu | `Année` + `Numéro` + `Département` | Unique (vérifié : aucun doublon). Le `Numéro` seul **n'est pas** unique |
| Lien avec une commune / une carte | `Code INSEE` | Toujours utiliser le code, **pas le nom** : 8 codes ont deux noms différents (fusions de communes, fautes de saisie) |
| Lien avec la Météo des forêts, la météo | `Date de première alerte` (partie date) + `Code INSEE` ou `Département` | Il faudra une table de correspondance commune → zone de l'indice |
| Lien avec la BD Forêt | `Code INSEE` | **Pas de coordonnées GPS** dans BDIFF : on ne peut localiser un feu qu'à la commune |

## Colonnes

Les surfaces sont en **m²** (1 ha = 10 000 m²).

| Colonne | Type | Remplissage | À garder ? |
|---|---|---|---|
| Année | entier | 100 % | Oui |
| Numéro | entier | 100 % | Oui (clé) |
| Département | texte | 100 % | Oui |
| Code INSEE | texte (5 caractères) | 100 % | Oui (clé) |
| Nom de la commune | texte | 100 % | Oui, pour l'affichage seulement |
| Date de première alerte | date et heure | 100 % | Oui |
| Surface parcourue (m2) | entier | 100 % | Oui – **c'est la mesure principale** |
| Surface forêt (m2) | décimal | 99,6 % | Oui |
| Autres surfaces naturelles hors forêt (m2) | décimal | 95,6 % | Oui |
| Surfaces agricoles (m2) | décimal | 26 % | Format depuis 2023 uniquement |
| Autres surfaces (m2) | décimal | 26 % | Format depuis 2023 uniquement |
| Surface autres terres boisées (m2) | décimal | 71,5 % | Format avant 2023 uniquement |
| Surfaces non boisées (m2) | décimal | 68,8 % | Format avant 2023 uniquement |
| Surfaces non boisées naturelles (m2) | décimal | 19,4 % | Format avant 2023 uniquement |
| Surfaces non boisées artificialisées (m2) | décimal | 19,4 % | Format avant 2023 uniquement |
| Surface maquis garrigues (m2) | – | **0 %** | Vide : zone méditerranéenne seulement |
| Type de peuplement | – | **0 %** | Vide : zone méditerranéenne seulement |
| Précision des surfaces | texte : `Estimées` / `Mesurées` | 58,6 % | Oui (bien rempli depuis 2022) |
| Nature | texte : cause du feu | **37,5 %** | Oui (voir points d'attention) |
| Décès ou bâtiments touchés | texte : `Oui` / `Non` | 44,1 % | Oui (rempli depuis 2022) |
| Nombre de décès | décimal | 16,8 % | Oui (rempli depuis 2022) |
| Nombre de bâtiments totalement détruits | décimal | 16,8 % | Oui (rempli depuis 2022) |
| Nombre de bâtiments partiellement détruits | décimal | 16,8 % | Oui (rempli depuis 2022) |
| Précision de la donnée | texte | 0,3 % | Oui : 13 feux marqués « Données partielles ou non valides » |

Valeurs de `Nature` : `Naturelle`, `Accidentelle`, `Involontaire (particulier)`, `Involontaire (travaux)`, `Malveillance`, ou vide.

## Points d'attention

**Aucune donnée n'a été supprimée ni corrigée.** Les points ci-dessous sont en cours de décision avec le groupe : merci de charger le fichier tel quel.

1. **2024 : 98 feux** (29 en Gironde) contre 250 à 650 les autres années – année humide ou données incomplètes, à vérifier.
2. **Cause inconnue pour 62 % des feux** (colonne `Nature` vide).
3. **Changement de format en 2023** : les colonnes de détail des surfaces ne sont pas les mêmes avant et après. Seules `Surface parcourue` et `Surface forêt` sont comparables sur toute la période.
4. Avant 2023, 51 feux où la somme des sous-surfaces ≠ surface totale.
5. 79 feux à 1 m², 346 à 10 m² ou moins (vraie surface ou valeur par défaut ?).
6. Beaucoup de surfaces rondes (100, 500, 1 000, 10 000 m²) : ce sont des estimations.
7. 13 feux « Données partielles ou non valides » (10 en Gironde en 2017).
8. 2 alertes à 00:00 pile : heure peut-être inconnue.
9. Landiras apparaît deux fois en 2022 (juillet et août) : ce sont **deux feux différents**, pas un doublon.
10. **La saison 2026 n'est pas disponible** dans BDIFF (le portail publie jusqu'à l'année précédente).
11. Données personnelles : pas de nom ni d'adresse, mais les décès et bâtiments détruits croisés avec la commune et la date peuvent identifier une personne dans une petite commune.

## Ce que BDIFF ne contient pas

Ces informations viendront d'autres sources :

- Coordonnées GPS des départs de feu
- Délai d'intervention, moyens engagés (données SDIS)
- Niveau de la Météo des forêts du jour (Météo-France)
- Type de forêt (BD Forêt)
- Points d'eau, casernes, routes (BD TOPO)
