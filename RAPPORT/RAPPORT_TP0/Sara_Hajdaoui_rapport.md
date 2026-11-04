# TP0 : MaintAI

**Nom :** Sara Hajdaoui  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate

## Le problème à résoudre

Le projet utilise quatre informations fournies par les capteurs — température, vibration, charge et durée de fonctionnement — pour repérer les machines susceptibles de tomber en panne. Une alerte manquée peut provoquer un arrêt de production. Je privilégie donc la capacité à retrouver les pannes, mesurée par le rappel, plutôt que le seul pourcentage global de bonnes réponses.

## Comparaison des modèles

| Modèle | Accuracy | Rappel | Précision |
|---|---:|---:|---:|
| Baseline | 0,824 | 0,000 | 0,000 |
| Régression logistique | 0,889 | 0,574 | 0,737 |
| Arbre de décision | 0,839 | 0,597 | 0,538 |
| Forêt aléatoire | 0,873 | 0,545 | 0,671 |

Le contrôle automatisé ne détecte aucune régression : **les 8 tests passent**.

## Décision argumentée

L'**arbre de décision** est mon choix, car son rappel de `0,597` est le maximum obtenu. Sur 100 pannes réelles, ce score correspond à environ 60 pannes détectées. La régression logistique produit moins de fausses alertes grâce à une précision de `0,737`, contre `0,538` pour l'arbre, mais elle retrouve légèrement moins de pannes. Pour MaintAI, ce supplément de détection est plus important que le confort d'avoir moins d'alertes à vérifier.

L'accuracy élevée de la baseline (`0,824`) est trompeuse : son rappel de `0,000` montre qu'elle choisit la classe majoritaire sans identifier les cas critiques.

## Respect du critère métier

L'objectif fixé est `rappel >= 0,75`. Le score retenu est `0,597`; il manque donc `0,153`. Le critère n'est pas atteint et le modèle ne devrait pas encore être présenté comme suffisamment sûr pour un usage réel sans surveillance.

## Incertitudes

- Le jeu de test ne garantit pas que tous les types de machines et toutes les conditions de production sont représentés.
- La stabilité du rappel doit être mesurée sur plusieurs découpages ou par validation croisée.
- Il faut examiner les faux négatifs pour comprendre quels profils de panne restent difficiles à détecter.
- La qualité et la fréquence d'étalonnage des capteurs peuvent modifier les performances en production.
- Le seuil de décision pourrait être abaissé pour capter plus de pannes, mais le volume d'interventions inutiles augmenterait probablement.

---

# TP0 : Cantine AI

**Nom :** Sara Hajdaoui  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate

## Le problème à résoudre

L'objectif est d'estimer chaque jour le nombre de repas à préparer à partir des inscriptions, du calendrier, du menu, de la météo et de l'historique récent. Une bonne prévision aide la cantine à limiter simultanément les surplus jetés et les ruptures de repas. La MAE est la métrique principale puisqu'elle traduit l'écart moyen dans l'unité directement utile : le repas.

## Comparaison des modèles

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Baseline | 70,271 | 88,416 | -0,151 |
| Régression linéaire | 22,239 | 28,170 | 0,883 |
| Arbre de décision | 46,000 | 59,710 | 0,475 |
| Forêt aléatoire | 31,845 | 41,540 | 0,746 |

La suite de tests est verte : **8 tests réussis sur 8**.

## Décision argumentée

Je sélectionne la **régression linéaire**. Elle obtient la plus petite MAE (`22,239`) et le plus petit RMSE (`28,170`), tout en présentant le meilleur R² (`0,883`). Son erreur moyenne est réduite de `48,032` repas par rapport à la baseline, soit une amélioration d'environ `68,35 %`. La cohérence des trois indicateurs rend ce choix plus solide qu'une décision fondée sur la MAE seule.

## Respect du critère métier

Le projet ne fournit pas de seuil d'acceptation chiffré. On peut mesurer l'amélioration, mais pas déclarer formellement le modèle acceptable. Si l'équipe de la cantine décidait qu'une MAE inférieure ou égale à **30 repas** est suffisante, la régression linéaire respecterait cette règle avec `22,239`.

## Incertitudes

- Les 340 journées disponibles représentent une période limitée et peuvent ne pas couvrir toutes les habitudes annuelles.
- Le découpage chronologique devrait être répété sur d'autres fenêtres pour vérifier la stabilité du modèle.
- Les événements rares, tels qu'une sortie exceptionnelle ou un changement de menu tardif, peuvent produire des erreurs plus fortes.
- Il serait utile de distinguer les sous-prévisions des sur-prévisions, car leurs coûts métier ne sont pas identiques.
- La cantine doit encore transformer l'erreur moyenne en une règle de décision opérationnelle pour les quantités à préparer.
