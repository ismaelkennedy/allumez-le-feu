# Analyse de la commande - Ismaël Kennedy KANTE

## 1. Les questions

Quatre questions dont la réponse aiderait la direction à trancher.

> [!test] Test
> Le test : si la réponse est X, la direction fait A ; si elle est Y, elle fait B. Si A et B sont identiques, ce n'est pas une question analytique pertinente.

1. En Gironde, dans quelles communes les départs de feu sont concentrés ?

2. À partir de quelle niveau de la Météo, les départs de feu deviennent-ils plus fréquents en Gironde ?

3. Qu'elles sont les données(seuil, metéo, ...) dispos des années antérieures ?

4.  Où sont situés les départs des feu par rapport au premier secours ?

## 2. Les termes inconnus

Les mots de la commande que vous ne savez pas définir précisément, ou qui peuvent se comprendre de plusieurs façons.

| Terme | Ce que je crois qu'il veut dire | Ce qu'il faudrait vérifier |
|---|---|---|
| Météo des forêts (IFM) | Un indice de Météo-France qui estime le danger de feu à partir de la météo | Variables et formule, échelle (maille, zone, département), historique téléchargeable |
| Niveaux de danger | Des classes (faible ou elevé) définies par des seuils sur l'indice | Nombre de niveaux, valeurs de coupure, identiques partout en France ou non |
| Seuil actuel | Le niveau à partir duquel le SDIS renforce déjà son dispositif | Sa valeur et ce qui se passe quand il est franchi |
| Dispositif renforcé | Patrouilles, guet, moyens supplémentaires | Contenu précis, coût par jour, durée minimale d'activation |
| Départ de feu | Un début d'incendie, quelle que soit sa taille | Surface minimale éventuelle, différence avec « feu de forêt » |
| « Autres départements de la région » | Les départements de Nouvelle-Aquitaine | Que la région soit bien Nouvelle-Aquitaine et que ces départements soient comparables |
| « Autant de feux qu'en 2026, voire davantage » | Hypothèse que l'été 2027 pourrait ressembler à 2026 | Sur quoi elle repose, si 2026 est représentatif, et la tendance sur 10 ans |


## 3. Les besoins

La décision à éclairer, en une phrase :
Choisir où concentrer les moyens du SDIS 33 et à partir de quel niveau de l'indice déclencher le dispositif renforcé, avec un budget qui ne permet pas de couvrir tout le département tout l'été.

Ce qui manque dans la commande pour y répondre (une information, une précision, une hypothèse à confirmer) :

- Le budget disponible et le coût d'une journée de dispositif.
- Le critère de réussite : éviter des départs de feu ou limiter les surfaces brûlées ?
- Hypothèse à confirmer : les départs sont-ils liés à une forte température ?

## 4. Les données

Pour chaque question, la donnée qu'il vous faudrait idéalement pour répondre.

| Question | Donnée idéale | Grain (une ligne = ?) | Période | Fraîcheur | Emprise géographique |
|---|---|---|---|---|---|
| 1 | Commune, coordonnées et cause de chaque feu (BDIFF) + surface boisée par commune (BD Forêt) | Un départ de feu | 10 dernières années, étés inclus | Annuelle | Gironde, par commune |
| 2 | Indice forêt météo du jour (Météo-France) + nombre de départs de feu (BDIFF) | Un jour × une maille ou un département | 10 dernières années | Quotidienne | Gironde |
| 3 | Température, humidité, vent et pluie de chaque jour (Météo-France) + date des feux (BDIFF) | Un jour × une station météo | 10 dernières années | Quotidienne | Gironde, par station |
| 4 | Coordonnées des départs de feu (BDIFF) + localisation des casernes, temps de trajet par la route (BD TOPO) | Un départ de feu ; une caserne | 10 ans pour les feux, situation actuelle pour les casernes | Annuelle | Gironde |