# Choix du modèle — Prévision des repas servis à la cantine

Date : 28/10/2026 · Groupe : Mohamed Saifeddine / Sara Hajdaoui / Marwa Khabarate / Ilyass Edhoum

## Contexte
Le projet cherche à prévoir le nombre de repas servis à la cantine afin d'aider à planifier les quantités. La métrique principale est la MAE (erreur absolue moyenne), car elle exprime l'écart moyen directement en nombre de repas.

## Données et découpage
Le fichier `data/cantine_repas.csv` contient 340 observations quotidiennes. Les variables utilisées sont `jour`, `inscrits`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances` et `repas_semaine_precedente`. La colonne `date` sert au découpage chronologique et n'est pas utilisée comme variable d'entrée. Les 272 premières observations servent à l'entraînement et les 68 dates les plus récentes au test.

## Résultats sur le jeu de test

| Modèle | MAE (repas) | RMSE (repas) | R² |
|---|---:|---:|---:|
| Baseline (prédiction de la moyenne) | 70,271 | 88,416 | -0,151 |
| Régression linéaire | 22,239 | 28,170 | 0,883 |
| Forêt aléatoire | 31,845 | 41,540 | 0,746 |
| Gradient boosting | 39,015 | 51,049 | 0,616 |

## Décision
Le modèle retenu est la régression linéaire, qui obtient la MAE la plus faible. Par rapport à la baseline, sa MAE diminue de 48,032 repas, soit environ 68,4 %. Il bat donc la baseline sur le jeu de test. Aucun seuil numérique d'acceptation n'ayant été fixé dans la section 5 avant l'entraînement, il n'est pas possible de conclure qu'un critère d'acceptation préalable est atteint.

## Limites
Le jeu de test comprend 68 jours consécutifs d'une seule période ; les résultats peuvent varier sur une autre période ou avec d'autres habitudes de fréquentation. Les valeurs manquantes des variables d'entrée sont imputées par le pipeline. La source et la licence d'origine du fichier CSV restent à confirmer par le groupe. L'entraînement affiche des avertissements numériques scikit-learn concernant la régression linéaire ; les scores indiqués sont ceux produits, mais ces avertissements méritent une vérification avant toute utilisation réelle.
