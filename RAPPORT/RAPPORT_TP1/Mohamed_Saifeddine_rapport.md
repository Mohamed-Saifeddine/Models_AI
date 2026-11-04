# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Nom :** Mohamed Saifeddine 
**Groupe :** Mohamed Saifeddine / Marwa Khabarate/ Sara hajdaoui / Ilyas edhoum              · **Date :** 28/10/2026

> Les résultats ci-dessous correspondent à l'état actuel du projet. Le modèle est entraîné, mais les deux TODO de `schemas.py` et `main.py` ne sont pas encore implémentés.

---

## 1. Mise en place

La génération des données a produit **5 000 relevés** avec un taux de panne de **13,6 %** :

```text
5000 relevés écrits dans /Users/omisse1/Downloads/S4_maintai-starter-tp1/data/sensors.csv (taux de panne : 13.6%)
```

L'entraînement a produit les résultats suivants :

```json
{
  "model": {
    "accuracy": 0.904,
    "recall": 0.75,
    "precision": 0.622,
    "threshold": 0.3
  },
  "baseline": {
    "accuracy": 0.864,
    "recall": 0.0
  },
  "n_train": 4000,
  "n_test": 1000
}
```

Le modèle a été correctement sauvegardé dans `models/model.joblib`.

Résultat initial avec les deux TODO non implémentés (`schemas.py` et `main.py`) :

```text
3 failed, 10 passed, 1 warning
```

Les quatre tests de `tests/test_api.py` qui passent déjà sont `test_health`, `test_out_of_range_value_is_rejected`, `test_missing_field_is_rejected` et `test_openapi_documents_predict`.

Les deux tests qui attendent un code 422 passent initialement pour une mauvaise raison : le schéma ne déclare pas encore les quatre champs d'entrée, mais `extra="forbid"` refuse tous les champs envoyés comme champs supplémentaires. La requête est donc rejetée, sans que la borne de température ni l'obligation de fournir `load_pct` soient réellement vérifiées.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

Les bornes physiques proposées pour compléter le schéma sont les suivantes :

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---:|---:|---:|---|
| `temperature_c` | `float` | -40 °C | 150 °C | Plage large couvrant les environnements froids et une température anormalement élevée de la machine. |
| `vibration_mm_s` | `float` | 0 mm/s | 100 mm/s | Une vibration ne peut pas être négative ; 100 mm/s représente un niveau extrême de défaut. |
| `load_pct` | `float` | 0 % | 100 % | La charge représente une proportion de la capacité nominale de la machine. |
| `runtime_hours` | `float` | 0 h | 100 000 h | Le compteur ne peut pas être négatif ; 100 000 h couvre une longue durée de service. |

Le code à ajouter dans `SensorReading` est :

```python
temperature_c: float = Field(
    ge=-40,
    le=150,
    description="Température de la machine en degrés Celsius",
)
vibration_mm_s: float = Field(
    ge=0,
    le=100,
    description="Niveau de vibration en millimètres par seconde",
)
load_pct: float = Field(
    ge=0,
    le=100,
    description="Charge de la machine en pourcentage",
)
runtime_hours: float = Field(
    ge=0,
    le=100_000,
    description="Nombre total d'heures de fonctionnement",
)
```

Après l'ajout de ces champs, mais avant l'implémentation de `predict()`, les trois tests de prédiction doivent encore échouer : les requêtes valides atteindront alors `raise NotImplementedError`. C'est un bon signe, car cela montrera que la validation Pydantic accepte enfin les relevés valides et que l'exécution atteint la fonction restant à implémenter.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Corps à ajouter dans la fonction :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(
        status_code=503,
        detail="Modèle de prédiction indisponible.",
    )
return PredictionOut(**predictor.predict(reading.model_dump()))
```

On répond **503 Service Unavailable** plutôt que 500, car l'API fonctionne mais ne peut pas traiter une prédiction tant que le modèle nécessaire n'est pas disponible. Un code 500 indiquerait plutôt une erreur interne inattendue.

Le modèle est chargé une seule fois dans le gestionnaire de cycle de vie (`lifespan`) au démarrage. Cela évite de relire le fichier du modèle à chaque requête, réduit la latence et permet de réutiliser le prédicteur déjà chargé.

## 4. Les tests

Dernière ligne obtenue avec `python -m pytest` dans l'état actuel :

```text
3 failed, 10 passed, 1 warning
```

Les trois tests en échec sont :

- `test_predict_returns_probability` : code 422 obtenu au lieu de 200 ;
- `test_high_risk_reading_raises_alert` : le champ `alert` est absent de la réponse d'erreur ;
- `test_503_when_model_missing` : code 422 obtenu au lieu de 503.

L'avertissement est une dépréciation de `starlette.testclient` concernant l'utilisation de `httpx`. Il n'est pas la cause des trois échecs.

Après l'implémentation du schéma et de la fonction `predict()`, le résultat final attendu est :

```text
13 passed, 1 warning
```

## 5. L'API en marche

Résultats vérifiés dans l'état actuel du projet, avec le modèle disponible :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---:|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | 422 | Les quatre champs sont signalés comme `extra_forbidden`. |
| `POST /v1/predict` avec une température de 500 | 422 | Les quatre champs sont aussi signalés comme `extra_forbidden`. La borne de 150 °C n'est pas encore appliquée. |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail":"Not Found"}` |

La requête valide retourne actuellement 422 parce que `SensorReading` ne contient encore aucun champ. Une fois le schéma et `predict()` implémentés, elle devra retourner 200 avec `failure_probability`, `alert`, `threshold` et `model_version`.

Dans `/docs`, les bornes n'apparaissent pas encore. Après l'ajout des contraintes `Field(ge=..., le=...)`, elles seront visibles dans le schéma de la requête `POST /v1/predict`, dans la description des champs et dans le schéma `SensorReading`.

## 6. Questions de compréhension

1. **REST et FastAPI : quelle est la différence ?**  
   REST est un style d'architecture pour concevoir des interfaces HTTP autour de ressources, de routes et de méthodes comme GET ou POST. FastAPI est un framework Python qui permet de construire des API web, notamment des API suivant les principes REST.

2. **Le schéma Pydantic sert à trois choses. Lesquelles ?**  
   Il valide les données entrantes, convertit les types compatibles et décrit les formats de requête et de réponse dans le schéma OpenAPI utilisé par `/docs`.

3. **Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?**  
   `localhost` désigne la machine locale, `8000` le port sur lequel le serveur écoute et `/v1/predict` le chemin de la route de prédiction versionnée.

4. **Pourquoi `/v1` dans l'adresse ?**  
   Pour identifier la version de l'API. Une évolution incompatible pourra être publiée sous une autre version, par exemple `/v2`, sans casser immédiatement les clients existants.

5. **Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?**  
   `maintai.api.main` est le chemin d'import Python vers le module `main.py`, et `app` est l'objet FastAPI défini dans ce module et servi par Uvicorn.

## 7. Le rendu Git

- Lien de la pull request : [à compléter]
- Le tag `tp1` existe sur GitHub : [à vérifier]
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?  
  [À compléter après la relecture.]

## 8. Ce qui reste flou

Les deux TODO de `schemas.py` et `main.py` restent à implémenter. Une fois ces modifications effectuées, il faudra relancer les 13 tests et vérifier les quatre requêtes depuis `/docs`. Les informations personnelles, le lien de la pull request, le tag et la relecture Git restent également à compléter.
