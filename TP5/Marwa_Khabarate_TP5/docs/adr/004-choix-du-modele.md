# ADR 004 : choix du modèle MaintAI

Date : 25/11/2026

## Contexte

MaintAI doit détecter les pannes tout en limitant les fausses alertes. Une panne manquée coûte généralement plus cher qu'une fausse alerte.

## Options étudiées

1. Régression logistique avec seuil `0.3` : rappel `0.750`, précision `0.622`, accuracy `0.904`.
2. Régression logistique avec `C=0.01`, seuil `0.3` : rappel `0.691`, précision `0.653`, accuracy `0.908`.
3. Régression logistique avec seuil `0.2` : rappel `0.838`, précision `0.543`, accuracy `0.882`.
4. Forêt aléatoire avec seuil `0.3` : rappel `0.728`, précision `0.562`, accuracy `0.886`.

## Décision

Retenir provisoirement la régression logistique avec le seuil `0.2`.

Ce choix privilégie le rappel, car une panne non détectée peut coûter plus cher qu'une alerte supplémentaire. Le run MLflow retenu est `a06f8078361e481aa92706bc51054d60`. Il a été entraîné avec les données v1 dont `data_md5` vaut `73e0b7cb3c6f795c70c3ddf970b99c15` (`5000` lignes).

## Conséquences

Cette décision augmente les fausses alertes : la précision passe à `0.543`. Elle facilite la détection des pannes, mais exige un suivi du taux d'alertes et une confirmation en conditions réelles. Une validation finale devra utiliser les mêmes données de validation pour comparer les seuils et surveiller la dérive des données.
