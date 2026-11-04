# TP0 : MaintAI

**Nom :** Mohamed Saifeddine  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate

## Le problème

Prédire une panne à partir de quatre capteurs : la température, les vibrations, la charge et le nombre d'heures de fonctionnement. Une panne non détectée peut arrêter une ligne de production ; il est donc important de maximiser le rappel afin de limiter les faux négatifs.

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|---|---:|---:|---:|
| Baseline | 0,824 | 0,000 | 0,000 |
| Régression logistique | 0,889 | 0,574 | 0,737 |
| Arbre de décision | 0,839 | 0,597 | 0,538 |
| Forêt aléatoire | 0,873 | 0,545 | 0,671 |

Les tests automatisés du projet sont tous validés : **8 tests réussis sur 8**.

## Mon choix, et pourquoi

Je retiens l'arbre de décision, car le rappel est la métrique principale du projet et ce modèle obtient le meilleur rappel (`0,597`). Il détecte donc davantage de pannes réelles que les autres modèles testés. Il améliore le rappel de `0,597` par rapport à la baseline, dont le rappel est nul. Même si la régression logistique obtient une meilleure accuracy (`0,889`) et une meilleure précision (`0,737`), ces métriques sont secondaires ici, car manquer une panne est plus coûteux qu'une fausse alerte.

## Le critère (rappel >= 0,75) est-il atteint ?

Non. Le meilleur rappel obtenu est de `0,597`, soit un écart de `0,153` en dessous du seuil attendu de `0,75`. Le modèle n'est donc pas encore assez fiable pour satisfaire le critère d'acceptation.

## Ce qui reste flou

- Les données semblent être un jeu d'exemple ; leur représentativité par rapport à des machines réelles reste à confirmer.
- Les résultats reposent sur un seul découpage aléatoire entraînement/test et devraient être confirmés par validation croisée.
- Le comportement du modèle sur de nouveaux types de machines, de capteurs ou de conditions de production n'est pas connu.
- Le seuil de décision pourrait être ajusté pour augmenter le rappel, au prix d'un plus grand nombre de fausses alertes.
- Il faudrait analyser les faux négatifs et recueillir davantage d'exemples de pannes avant une utilisation en production.

---

# TP0 : Cantine AI

**Nom :** Mohamed Saifeddine  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate

## Le problème

Prédire le nombre de repas qui seront servis chaque jour à la cantine afin d'adapter les quantités préparées. La prédiction utilise notamment le jour, le nombre d'inscrits, le menu, la météo, les examens, les sorties scolaires, la veille des vacances et le nombre de repas servis la semaine précédente. Une mauvaise estimation peut provoquer du gaspillage alimentaire ou un manque de repas.

## Résultats sur le jeu de test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Baseline | 70,271 | 88,416 | -0,151 |
| Régression linéaire | 22,239 | 28,170 | 0,883 |
| Arbre de décision | 46,000 | 59,710 | 0,475 |
| Forêt aléatoire | 31,845 | 41,540 | 0,746 |

Les tests automatisés du projet sont tous validés : **8 tests réussis sur 8**.

## Mon choix, et pourquoi

Je retiens la **régression linéaire**, car la MAE est la métrique principale du projet et ce modèle obtient la valeur la plus faible (`22,239`). Ses prévisions s'écartent donc en moyenne d'environ 22 repas de la valeur réelle. Il réduit la MAE de `48,032` repas par rapport à la baseline, soit une amélioration d'environ `68,35 %`. Il obtient également le meilleur RMSE (`28,170`) et le meilleur coefficient R² (`0,883`) parmi les modèles testés.

## Le critère d'acceptation est-il atteint ?

Aucun seuil numérique d'acceptation n'est précisé dans les informations fournies. Il n'est donc pas possible de répondre définitivement. Le modèle améliore toutefois nettement la baseline : sa MAE passe de `70,271` à `22,239` repas. Si le critère retenu est une **MAE inférieure ou égale à 30 repas**, alors il est atteint.

## Ce qui reste flou

- Le seuil maximal de MAE acceptable pour une utilisation réelle n'est pas défini.
- Le jeu contient seulement 340 journées ; il faudrait vérifier les performances sur une période plus longue et sur plusieurs années scolaires.
- Les événements exceptionnels, les changements de menu et les variations soudaines du nombre d'inscrits peuvent être mal représentés.
- Les conséquences d'une surestimation et d'une sous-estimation ne sont pas nécessairement équivalentes et devraient être évaluées séparément.
- Les résultats reposent sur un seul découpage chronologique ; les performances devraient être confirmées sur d'autres périodes.
