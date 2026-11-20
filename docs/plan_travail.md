# Plan de travail


Remplacez la légende par : CP chef de projet · DA data analyst · DQ data quality · BD gestionnaire de la base · DE data engineer. Puis ajustez :


## 1. Tâches à faire

### Organisation (CP)
-  Créer le dépôt `feux-de-foret-nouvelle-aquitaine` et ajouter les collaborateurs
-  Compléter le README (équipe, branches, où trouver quoi, état d'avancement)
-  Créer une issue par livrable ci-dessous, avec responsable et date
-  Créer `docs/decisions/journal.md` et y consigner la répartition des rôles
-  Organiser un checkpoint avant le 22 novembre
-  Vérifier avant rendu : historique des commits, PR fusionnées, contributions de chacun visibles

### Analyses individuelles (tous)
-  Un fichier `docs/analyse/commande-prenom-nom.md` par personne, avec commit individuel
-  Les 4 sections complétées (questions, termes inconnus, besoins, données)
-  Chaque question passe le test « si X alors A, si Y alors B, avec A ≠ B »

### Questions analytiques et glossaire (DA, validé par CP)
-  Fusionner les analyses individuelles en une liste de questions analytiques du groupe
-  Construire le glossaire à partir des termes inconnus de chacun, avec les définitions vérifiées et leur source

### Sources (DA)
-  Inventaire des sources candidates (nom, propriétaire, lien, licence, format)
-  Une fiche descriptive par source retenue (identité, colonnes retenues, limites, couverture des questions)
-  Matrice questions × sources

### Qualité et conformité (DQ)
-  Vérifier la licence et les données personnelles de chaque source
-  Rédiger les règles de qualité (complétude, formats, doublons, valeurs aberrantes)
-  Lister les tests à automatiser

### Modèle cible (BD, avec DQ et DA)
-  Partie 1 : diagramme de la structure, avec une notation normalisée (par exemple diagramme de classes UML)
-  Partie 2 : tableau de data lineage, une ligne par donnée, avec :
  - nom de la donnée
  - source d'origine
  - transformations
  - problèmes d'alignement (par exemple nom de commune d'un côté, géolocalisation de l'autre)
  - données concurrentes (pourquoi choisir telle version en cas de doublon)
-  Partie 3 : annexe listant les sources, avec renvoi vers leurs fiches
-  Facultatif : représentation en graphe avec Protégé



## 2. Rappel des bonnes pratiques

### Git
- Une branche par sujet
- Un changement logique par commit, message `type: action` (docs, feat, fix)
- Pas de commit direct sur `main` ; une PR par branche
- Pas de réécriture de l'historique poussé (pas de `push --force`)
- Supprimer la branche après fusion
- Les dates de commit font foi : ne pas attendre le dernier moment pour pousser

### Relectures
- Le relecteur est le responsable du domaine touché, jamais l'auteur
- Une PR courte, avec une description
- On ne fusionne pas sa propre PR


### Données
- Ne jamais modifier un fichier source d'origine : travailler sur une copie
- Vérifier l'encodage, les séparateurs et les codes (département sur 2 caractères) avant de croiser des sources
- Distinguer ce qui est vérifié de ce qui est supposé (« à vérifier »)
- Ne pas déposer de données volumineuses ou personnelles dans le dépôt