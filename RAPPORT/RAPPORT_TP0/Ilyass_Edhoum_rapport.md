# TP0 : MaintAI

**Nom :** Ilyass Edhoum  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate

## Compréhension du besoin

MaintAI doit anticiper les pannes d'une machine à partir de sa température, de ses vibrations, de son niveau de charge et de son nombre d'heures d'utilisation. Dans ce cas, le risque principal est de classer une future panne comme un fonctionnement normal. Le rappel est donc la mesure prioritaire, car il indique la part des pannes réellement retrouvées par le modèle.

## Mesures obtenues sur le test

| Modèle | Accuracy | Rappel | Précision |
|---|---:|---:|---:|
| Baseline | 0,824 | 0,000 | 0,000 |
| Régression logistique | 0,889 | 0,574 | 0,737 |
| Arbre de décision | 0,839 | 0,597 | 0,538 |
| Forêt aléatoire | 0,873 | 0,545 | 0,671 |

La suite automatisée confirme le bon fonctionnement du projet : **8 tests sur 8 réussissent**.

## Modèle retenu

Je choisis l'**arbre de décision**. Son rappel de `0,597` est le plus élevé du tableau : il détecte environ 59,7 % des pannes présentes dans le jeu de test. La régression logistique est meilleure en accuracy et en précision, mais son rappel est inférieur de `0,023`. Cette différence signifie que l'arbre retrouve un peu plus de pannes, en acceptant davantage de fausses alertes. Ce compromis correspond à la priorité de maintenance préventive.

La baseline illustre pourquoi l'accuracy ne suffit pas : elle atteint `0,824` tout en ayant un rappel nul. Elle peut donc sembler correcte globalement alors qu'elle ne signale aucune panne.

## Vérification du seuil demandé

Le critère exige un rappel d'au moins `0,75`. Avec `0,597`, l'arbre de décision reste inférieur de `0,153`, soit **15,3 points de pourcentage**. Le meilleur modèle testé ne valide donc pas encore le seuil d'acceptation.

## Limites et prochaines vérifications

- Il faudrait observer le nombre exact de faux négatifs et étudier les machines concernées.
- Une validation croisée permettrait de vérifier que l'avantage de l'arbre ne dépend pas d'un seul découpage des données.
- Les coûts d'une fausse alerte et d'une panne manquée devraient être chiffrés par le service de maintenance.
- Un ajustement du seuil de classification pourrait augmenter le rappel, avec le risque d'envoyer davantage d'alertes inutiles.
- Les performances doivent être confirmées sur des mesures issues de machines réelles et sur plusieurs périodes.

---

# TP0 : Cantine AI

**Nom :** Ilyass Edhoum  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate

## Compréhension du besoin

Cantine AI cherche à prévoir le nombre de repas servis afin de préparer une quantité plus proche de la demande. Une sous-estimation peut laisser des usagers sans repas, tandis qu'une surestimation augmente le gaspillage. La MAE est particulièrement lisible ici, car elle exprime directement l'écart moyen en nombre de repas.

## Mesures obtenues sur le test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Baseline | 70,271 | 88,416 | -0,151 |
| Ridge | 22,623 | 28,545 | 0,880 |
| Forêt aléatoire | 31,825 | 41,647 | 0,745 |
| Arbre de décision | 46,000 | 59,710 | 0,475 |

Les tests automatisés sont entièrement validés : **8 réussites sur 8**.

## Modèle retenu

Je retiens **Ridge**, car ses trois indicateurs sont les meilleurs. Sa MAE de `22,623` signifie que l'erreur absolue est d'environ 23 repas en moyenne. Elle est réduite de `47,648` repas par rapport à la baseline, ce qui représente une baisse d'environ `67,8 %`. Son RMSE de `28,545` montre aussi que ses erreurs importantes sont moins fortes que celles des autres modèles, et son R² de `0,880` indique qu'il explique une grande partie de la variation observée.

## Acceptation du résultat

Aucune valeur limite de MAE n'a été fixée avant l'évaluation. Il est donc impossible d'affirmer que le modèle respecte une règle officielle, même s'il améliore clairement la baseline. Avec une règle métier hypothétique de **30 repas d'erreur moyenne au maximum**, Ridge serait accepté puisque sa MAE vaut `22,623`.

## Limites et prochaines vérifications

- La cantine doit définir le nombre d'erreurs qu'elle peut réellement absorber sans manque ni gaspillage excessif.
- Une erreur positive et une erreur négative n'ont pas les mêmes conséquences et devraient être analysées séparément.
- Les périodes d'examens, sorties et veilles de vacances méritent une évaluation spécifique.
- Les résultats devraient être reproduits sur plusieurs périodes scolaires pour détecter une éventuelle saisonnalité.
- Avant le déploiement, il serait utile de comparer l'économie réalisée au coût de collecte et de maintenance des données.
