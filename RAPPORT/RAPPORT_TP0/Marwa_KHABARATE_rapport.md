# TP0 : MaintAI

**Nom :** Marwa Khabarate  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate

## Le problème

MaintAI s'appuie sur les mesures de température, de vibrations, de charge et d'heures de fonctionnement pour estimer si une machine va tomber en panne. Comme une panne non signalée peut interrompre la production, le modèle doit avant tout repérer le plus grand nombre possible de pannes réelles.

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|---|---:|---:|---:|
| Baseline | 0,824 | 0,000 | 0,000 |
| Régression logistique | 0,889 | 0,574 | 0,737 |
| Arbre de décision | 0,839 | 0,597 | 0,538 |
| Forêt aléatoire | 0,873 | 0,545 | 0,671 |

Les tests automatisés du projet sont tous validés : **8 tests réussis sur 8**.

## Mon choix, et pourquoi

Parmi les modèles évalués, l'**arbre de décision** correspond le mieux à la priorité du projet : il obtient le rappel le plus élevé, `0,597`. Autrement dit, il retrouve davantage de pannes que la régression logistique ou la forêt aléatoire sur ce test. Son gain par rapport à la baseline est de `0,597`, puisque cette dernière ne détecte aucune panne. La régression logistique est plus précise (`0,737`) et obtient une meilleure accuracy (`0,889`), mais elle laisse passer davantage de pannes ; ici, éviter ces oublis est prioritaire.

## Le critère (rappel >= 0,75) est-il atteint ?

Pas encore : le rappel maximal mesuré est `0,597`, alors que l'objectif est `0,75`. Il manque donc `0,153` pour atteindre le seuil. L'arbre de décision est le meilleur des candidats testés, mais ce résultat ne satisfait pas le critère fixé.

## Ce qui reste flou

- Il reste à vérifier que ce jeu d'exemple représente bien les machines et les conditions réelles d'une usine.
- Les scores peuvent varier selon les observations retenues pour le test ; une validation croisée aiderait à mieux mesurer cette variabilité.
- Rien ne permet encore de savoir si les performances se maintiennent sur d'autres machines ou dans des conditions de fonctionnement différentes.
- Un réglage du seuil de décision pourrait améliorer la détection, mais pourrait aussi multiplier les alertes erronées.
- Il serait utile de revoir les pannes non détectées et de tester le modèle sur des données de maintenance réelles avant de l'utiliser sur le terrain.

---

# TP0 : Cantine AI

**Nom :** Mohamed Saifeddine  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate

## Le problème

Pour mieux préparer les repas, Cantine AI estime le nombre de convives attendus chaque jour. L'estimation tient compte du calendrier, des inscriptions, du menu, de la météo et des repas servis récemment ; une prévision trop haute ou trop basse peut respectivement créer du gaspillage ou des repas manquants.

## Résultats sur le jeu de test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Baseline | 70,271 | 88,416 | -0,151 |
| Ridge | 22,623 | 28,545 | 0,880 |
| Forêt aléatoire | 31,825 | 41,647 | 0,745 |
| Arbre de décision | 46,000 | 59,710 | 0,475 |

Les tests automatisés du projet sont tous validés : **8 tests réussis sur 8**.

## Mon choix, et pourquoi

Le modèle **Ridge** est le meilleur des candidats évalués pour cette tâche : sa MAE de `22,623` repas est la plus faible, ce qui signifie que ses estimations s'écartent en moyenne d'environ 23 repas des observations. Comparé à la baseline, il réduit la MAE de `47,648` repas, soit environ `67,8 %`. Il obtient aussi le RMSE le plus faible (`28,545`) et le meilleur R² (`0,880`).

## Le critère d'acceptation est-il atteint ?

Les informations du projet ne fixent pas de limite officielle pour la MAE, donc on ne peut pas conclure sur un seuil d'acceptation prédéfini. On peut toutefois constater que l'erreur diminue de `70,271` repas pour la baseline à `22,623` avec Ridge. Si la règle retenue était une **MAE de 30 repas maximum**, le résultat la respecterait.

## Ce qui reste flou

- La cantine doit encore décider quel écart de prévision est acceptable pour organiser les repas au quotidien.
- Les données couvrent 340 journées ; les tester sur plusieurs années scolaires permettrait de mieux évaluer la généralisation.
- Les journées atypiques, comme les événements exceptionnels ou les changements soudains d'effectifs, sont peut-être peu représentées.
- Un surplus et un manque de repas ont des conséquences différentes ; il serait utile de mesurer ces erreurs séparément.
- Le score vient d'une seule période de test chronologique. D'autres périodes de test aideraient à vérifier la stabilité des résultats.
