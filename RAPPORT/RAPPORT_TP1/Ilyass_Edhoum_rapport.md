# Compte rendu · TP1 : exposition du modèle MaintAI par API

**Nom :** Ilyass Edhoum  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate · **Date :** 29/10/2026

> L'analyse ci-dessous sépare les fonctions déjà opérationnelles des deux éléments encore incomplets : le modèle `SensorReading` et le point d'entrée `predict()`.

---

## 1. État initial du projet

L'environnement utilise Python 3.14.4 et pytest 9.1.1. La suite automatisée découvre 13 tests et termine actuellement par :

```text
3 failed, 10 passed, 1 warning in 1.37s
```

Les tests de chargement des données et d'entraînement sont tous validés. Côté API, `test_health` et `test_openapi_documents_predict` réussissent normalement. Deux autres tests, consacrés à une température excessive et à un champ manquant, réussissent accidentellement.

La cause se trouve dans `SensorReading` : la classe est vide alors que `extra="forbid"` est activé. Tous les champs du JSON sont alors vus comme étrangers. Le serveur renvoie 422 quelle que soit la qualité du relevé, ce qui masque l'absence des véritables règles de validation.

## 2. Définition de `SensorReading`

Le contrat choisi impose quatre nombres flottants :

| Champ | Intervalle accepté | Motif du choix |
|---|---:|---|
| `temperature_c` | de -40 à 150 | Inclure les conditions froides et les cas de surchauffe tout en bloquant les températures absurdes. |
| `vibration_mm_s` | de 0 à 100 | Une vibration est positive ou nulle ; la borne haute couvre un défaut mécanique majeur. |
| `load_pct` | de 0 à 100 | Un pourcentage de charge reste compris entre l'arrêt et la pleine capacité. |
| `runtime_hours` | de 0 à 100 000 | Les heures cumulées ne diminuent pas et peuvent couvrir une très longue exploitation. |

Déclaration correspondante :

```python
temperature_c: float = Field(ge=-40, le=150, description="Température de fonctionnement en °C")
vibration_mm_s: float = Field(ge=0, le=100, description="Vitesse vibratoire en mm/s")
load_pct: float = Field(ge=0, le=100, description="Taux de charge de la machine")
runtime_hours: float = Field(ge=0, le=100_000, description="Compteur d'utilisation en heures")
```

Une fois ce contrat écrit, une requête correcte n'est plus arrêtée par FastAPI et entre dans `predict()`. Comme cette fonction contient encore `raise NotImplementedError`, les trois scénarios de prédiction restent en échec. Ce changement de message d'erreur prouve néanmoins que la première couche, la validation, fonctionne.

## 3. Disponibilité du modèle et fonction `predict()`

La fonction doit utiliser l'objet stocké dans le dictionnaire partagé `state` :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(status_code=503, detail="Modèle de prédiction indisponible.")

result = predictor.predict(reading.model_dump())
return PredictionOut(**result)
```

Le statut **503 Service Unavailable** correspond au cas où le processus web est actif mais ne peut pas rendre le service de prédiction. Cette réponse permet aussi à un client de distinguer une indisponibilité temporaire d'un défaut imprévu du serveur, qui relèverait plutôt d'un code 500.

Le gestionnaire `lifespan` tente de charger le modèle avant d'accepter les requêtes. Cette architecture présente deux avantages : la présence du modèle est connue dès le démarrage et son coût de chargement n'est payé qu'une fois. Lors de l'arrêt de l'application, `state.clear()` libère la référence partagée.

## 4. Analyse de la couverture automatisée

| Test API | Attendu | État constaté | Cause |
|---|---:|---:|---|
| Santé du service | 200 | 200 | Route indépendante du schéma d'entrée |
| Prédiction normale | 200 | 422 | Les mesures sont considérées supplémentaires |
| Relevé à haut risque | `alert=true` | Pas de champ `alert` | La réponse est une erreur de validation |
| Température à 500 °C | 422 | 422 | Bon statut, mais mauvaise règle déclenchée |
| Champ `load_pct` absent | 422 | 422 | Bon statut, mais schéma encore vide |
| Modèle introuvable | 503 | 422 | La validation intervient avant le contrôle du modèle |
| Présence dans OpenAPI | Route présente | Route présente | Le routeur est déjà enregistré |

Les six tests non liés directement à l'API passent également : trois pour les données et trois pour l'entraînement. L'avertissement `StarletteDeprecationWarning` concerne l'outil de test et n'affecte pas les assertions.

Après correction des deux TODO, le critère de fin est l'obtention de :

```text
13 passed, 1 warning
```

## 5. Vérification des routes

Les observations actuelles sont les suivantes :

| Méthode et chemin | Entrée | Code observé | Corps ou effet principal |
|---|---|---:|---|
| `GET /health` | aucune | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` | relevé normal | 422 | Quatre erreurs `extra_forbidden` |
| `POST /v1/predict` | température égale à 500 | 422 | Rejet avant application d'une borne physique |
| `POST /v1/predicte` | relevé normal | 404 | `{"detail":"Not Found"}` |

Une fois l'implémentation terminée, la deuxième ligne devra produire un objet contenant `failure_probability`, `alert`, `threshold` et `model_version`. La troisième devra toujours produire 422, mais cette fois avec une erreur `less_than_equal` associée à la limite de 150 °C.

Les contraintes Pydantic seront aussi répercutées dans `/docs`. OpenAPI affichera alors chaque propriété de `SensorReading`, son type, son caractère obligatoire, sa description et ses bornes.

## 6. Notions retenues

1. **REST et FastAPI**  
   REST fournit des conventions de conception pour les services HTTP ; FastAPI fournit les classes et les décorateurs Python qui servent à les implémenter.

2. **Utilité de Pydantic**  
   Le modèle Pydantic protège la frontière de l'application : il valide le JSON, convertit les valeurs compatibles et alimente la documentation OpenAPI.

3. **Composition de l'URL**  
   Dans `http://localhost:8000/v1/predict`, l'hôte est `localhost`, le port TCP est `8000` et `/v1/predict` est le chemin de la ressource appelée.

4. **Rôle de la version**  
   Le segment `/v1` rend possible le maintien d'un contrat stable pendant la préparation d'une future version différente.

5. **Point d'entrée Uvicorn**  
   Dans `maintai.api.main:app`, la partie gauche localise le module importable et la partie droite donne le nom de l'application ASGI à servir.

## 7. Suivi Git

- Pull request du TP1 : [à compléter]
- Tag `tp1` publié : [à contrôler]
- Nom du relecteur et retour donné : [à compléter]

## 8. Points à finaliser

Le modèle entraîné et l'endpoint de santé sont disponibles, mais une réponse 422 est actuellement émise trop tôt dans le traitement. Il reste à définir les quatre champs, à remplacer `NotImplementedError` par l'appel au prédicteur et à vérifier le passage des 13 tests. Une vérification manuelle depuis Swagger complétera les tests en confirmant le contenu précis des réponses 200, 422, 503 et 404.
