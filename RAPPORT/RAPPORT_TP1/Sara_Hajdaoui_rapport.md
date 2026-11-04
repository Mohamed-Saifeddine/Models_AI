# Compte rendu · TP1 : validation d'une API MaintAI

**Nom :** Sara Hajdaoui  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate · **Date :** 29/10/2026

> Ce rapport suit la progression du projet depuis les TODO initiaux jusqu'à la validation finale de l'API. Les valeurs HTTP proviennent du modèle entraîné présent dans le projet.

---

## 1. Mise en place

La commande `python -m pytest` collecte 13 tests. Avant de compléter les deux TODO, le bilan obtenu est :

```text
3 failed, 10 passed, 1 warning in 1.37s
```

Dans `tests/test_api.py`, quatre tests passent :

- `test_health` ;
- `test_out_of_range_value_is_rejected` ;
- `test_missing_field_is_rejected` ;
- `test_openapi_documents_predict`.

Les deux tests de validation qui attendent un code 422 donnent une impression trompeuse de réussite. `SensorReading` ne contient encore aucun attribut et sa configuration `extra="forbid"` considère donc chaque mesure reçue comme un champ interdit. FastAPI répond bien 422, mais sans avoir réellement contrôlé la température maximale ni la présence de `load_pct`.

## 2. Le contrat d'entrée (`maintai/api/schemas.py`)

Les contraintes suivantes décrivent les valeurs physiquement acceptables par l'API :

| Mesure | Type | Borne basse | Borne haute | Raisonnement |
|---|---:|---:|---:|---|
| `temperature_c` | `float` | -40 °C | 150 °C | La plage couvre le froid industriel et une forte surchauffe sans accepter une valeur irréaliste. |
| `vibration_mm_s` | `float` | 0 mm/s | 100 mm/s | Une amplitude négative n'a pas de sens et 100 mm/s représente déjà une vibration très sévère. |
| `load_pct` | `float` | 0 % | 100 % | Cette variable exprime la part utilisée de la capacité nominale. |
| `runtime_hours` | `float` | 0 h | 100 000 h | Le compteur commence à zéro et la limite haute autorise plusieurs années d'exploitation. |

Implémentation retenue :

```python
temperature_c: float = Field(ge=-40, le=150, description="Température en °C")
vibration_mm_s: float = Field(ge=0, le=100, description="Vibration en mm/s")
load_pct: float = Field(ge=0, le=100, description="Charge en pourcentage")
runtime_hours: float = Field(ge=0, le=100_000, description="Durée de fonctionnement en heures")
```

Si seul ce schéma est ajouté, les requêtes valides franchiront la validation mais rencontreront ensuite `NotImplementedError` dans `predict()`. Le maintien de trois échecs à cette étape est donc logique : le point de blocage se sera déplacé de la validation vers le traitement métier.

## 3. Traitement d'une prédiction (`maintai/api/main.py`)

Le corps implémenté dans la route est :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(
        status_code=503,
        detail="Modèle de prédiction indisponible.",
    )
return PredictionOut(**predictor.predict(reading.model_dump()))
```

La logique suit trois étapes : récupérer le prédicteur partagé, vérifier sa disponibilité, puis convertir le relevé Pydantic en dictionnaire avant l'appel au modèle.

Le code **503** indique que le serveur répond, mais que la dépendance nécessaire à la prédiction est momentanément absente. Le code 500 serait moins précis, car il signalerait une erreur interne inattendue.

Le chargement est réalisé dans `lifespan` au lancement de FastAPI. Le fichier `model.joblib` n'est donc lu qu'une fois, ce qui évite un accès disque et une désérialisation à chaque requête.

## 4. Lecture des tests

Après l'ajout du contrat d'entrée et du traitement de prédiction, la suite complète termine par :

```text
13 passed, 1 warning in 4.45s
```

Les sept scénarios API sont alors couverts : état de santé, prédiction normale, alerte sur un risque élevé, valeur hors limites, champ absent, modèle indisponible et présence de la route dans OpenAPI. Les trois tests de données et les trois tests d'entraînement complètent ce contrôle.

Le passage de `3 failed, 10 passed` à 13 réussites confirme deux corrections distinctes : Pydantic accepte désormais un relevé valide tout en rejetant précisément les entrées incorrectes, puis `predict()` renvoie soit la sortie du modèle, soit le statut 503 attendu.

L'unique avertissement est un `StarletteDeprecationWarning` relatif à l'utilisation de `httpx` dans `starlette.testclient`. Il ne remet pas en cause le résultat fonctionnel des tests.

## 5. Comportement HTTP observé

| Appel | Code final | Corps de la réponse |
|---|---:|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | 200 | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-10-28T17:40:31Z"}` |
| `POST /v1/predict` avec `temperature_c=500` | 422 | Erreur `less_than_equal` indiquant que la valeur doit être inférieure ou égale à 150. |
| `POST /v1/predicte` | 404 | `{"detail":"Not Found"}` |

La probabilité `0,9553` dépasse largement le seuil `0,3`, ce qui explique la valeur `alert=true`. Cette sortie dépend toutefois du modèle sauvegardé et peut changer après un nouvel entraînement.

Dans `/docs`, les quatre propriétés de `SensorReading` apparaissent avec leur type, leur description et leurs limites. Cette documentation est issue du même contrat Pydantic que celui utilisé pour valider les requêtes, ce qui réduit le risque de décalage entre documentation et comportement réel.

## 6. Questions de compréhension

1. **Quelle différence entre REST et FastAPI ?**  
   REST décrit une manière d'organiser une interface HTTP. FastAPI est l'outil Python utilisé ici pour programmer cette interface, valider ses messages et produire sa documentation.

2. **Quels sont les trois rôles de Pydantic ?**  
   Il contrôle les données reçues, effectue les conversions de types autorisées et fournit à OpenAPI la description des objets échangés.

3. **Que signifie `http://localhost:8000/v1/predict` ?**  
   `localhost` est l'ordinateur qui exécute l'application, `8000` est le port d'écoute et `/v1/predict` identifie la première version de la route de prédiction.

4. **Pourquoi versionner avec `/v1` ?**  
   Ce préfixe permet de créer plus tard une `/v2` incompatible tout en laissant les clients existants utiliser la première version.

5. **Comment lire `uvicorn maintai.api.main:app` ?**  
   Uvicorn importe le module Python `maintai.api.main`, puis récupère dans ce module la variable `app` contenant l'instance FastAPI.

## 7. Rendu Git

- Lien de la pull request : [à compléter]
- Présence du tag `tp1` sur GitHub : [à vérifier]
- Relecteur et commentaire : [à compléter après la revue]

## 8. Bilan personnel

Le principal apprentissage est qu'un code HTTP correct ne suffit pas à prouver qu'une validation est correcte : au début, deux tests 422 passaient uniquement parce que tous les champs étaient refusés. La progression des tests a permis de distinguer la validation du JSON, l'appel au modèle et la gestion de son indisponibilité. Après les corrections, la chaîne complète est validée par 13 tests et par les essais dans `/docs`. Il reste seulement à renseigner les éléments liés à la pull request, au tag et à la relecture.
