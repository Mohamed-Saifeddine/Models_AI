# ADR 004 : choix du modèle et du seuil de MaintAI

Date : 25/11/2026 · Auteurs : Sara Hajdaoui

## Contexte
MaintAI doit prédire les pannes de machines à partir des capteurs (température, vibration, charge, heures de fonctionnement). Une panne manquée coûte beaucoup plus cher qu'une fausse alerte : le critère principal est donc le **recall** (part des pannes détectées), et l'accuracy n'est pas un bon critère car les pannes sont rares (le baseline « jamais de panne » atteint 0.864 d'accuracy avec un recall de 0).

## Options étudiées
Tous les runs ci-dessous viennent de l'expérience MLflow `maintai`, entraînés sur les mêmes données (v1, 5000 lignes, `data_md5` = `b7fec4274774842dc1f48202c6013490`, 4000 lignes d'entraînement, 1000 de test).

| Run MLflow | Modèle | C | Seuil | recall | precision | accuracy |
|---|---|---|---|---|---|---|
| `f2e3b740b59443038b43ed96b7aca1b7` | logreg | 1.0 | 0.3 | 0.750 | 0.622 | 0.904 |
| `4297f771306049cd9770996cf6c1d761` | logreg | 0.01 | 0.3 | 0.691 | 0.653 | 0.908 |
| **`39ed092134a84869952ce2689e9b3c8c`** | **logreg** | **1.0** | **0.2** | **0.838** | **0.543** | **0.882** |
| `7516f20f08c648568d546b6fa4184e68` | forest | – | 0.3 | 0.728 | 0.562 | 0.886 |
| `0a33da5973a54be38557ffbf5d09d9e1` | logreg | 1.0 | 0.5 | 0.574 | 0.736 | 0.914 |

1. **Régression logistique, seuil 0.3 (réglage par défaut)** : bon équilibre recall / precision, mais environ une panne sur quatre est manquée.
2. **Régression logistique, C = 0.01** : régularisation plus forte, precision un peu meilleure mais recall plus faible : moins adapté.
3. **Régression logistique, seuil 0.2** : meilleur recall (0.838) ; en échange, precision plus faible (0.543), donc plus de fausses alertes.
4. **Forêt aléatoire, seuil 0.3** : plus lourde et moins lisible, et au même seuil elle fait moins bien que la régression logistique sur le recall et sur la precision.
5. **Régression logistique, seuil 0.5** : meilleure precision et accuracy, mais recall de 0.574 : beaucoup trop de pannes manquées.

## Décision
Nous retenons la **régression logistique (C = 1.0) avec un seuil de 0.2**, c'est-à-dire le run MLflow **`39ed092134a84869952ce2689e9b3c8c`**, entraîné sur les données de `data_md5` **`b7fec4274774842dc1f48202c6013490`** (v1, commit Git `13c8d9f Données v1`).

Raison principale : c'est le réglage qui manque le moins de pannes (recall 0.838), ce qui répond à la contrainte la plus forte du projet. La régression logistique reste aussi plus simple et plus légère que la forêt aléatoire, qui n'apporte aucun gain ici.

## Conséquences
- **Ce que nous acceptons :** plus de fausses alertes. Avec une precision de 0.543, presque une alerte sur deux est une fausse alerte ; les équipes de maintenance feront des contrôles inutiles, ce qui coûte moins cher qu'une panne non détectée.
- **Ce que cela facilite :** le modèle est traçable. Le run MLflow contient les paramètres, les métriques, le modèle et son `requirements.txt` (scikit-learn 1.8.0) ; le `data_md5` permet de retrouver exactement les données avec Git et DVC (`git checkout 13c8d9f -- data/sensors.csv.dvc` puis `dvc checkout`).
- **Ce qu'il faudra surveiller :** le taux de fausses alertes en production (si les techniciens finissent par ignorer les alertes, il faudra remonter le seuil), et la dérive des données : un run sur la v2 donne des chiffres proches mais différents (recall 0.741, precision 0.650 au seuil 0.3) ; il faudra ré-entraîner et comparer sur un même jeu de test quand les données changent.
