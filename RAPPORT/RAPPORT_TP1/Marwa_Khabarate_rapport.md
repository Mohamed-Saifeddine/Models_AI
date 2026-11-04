# Compte rendu · TP1 : une API de prédiction pour MaintAI

 **Nom :** Marwa Khabarate  
**Groupe :** G4 : Mohamed Saifeddine / Sara Hajdaoui / Ilyass Edhoum / Marwa Khabarate ·  **Date :** 28/10/2026

> Les sorties HTTP ci-dessous ont été vérifiées avec le modèle présent dans le projet. La réponse de prédiction peut varier si le modèle est réentraîné.

---

## 1. Mise en place

Résultat initial avec les deux TODO non implémentés (`schemas.py` et `main.py`) :

```
3 failed, 10 passed, 1 warning
```

Les quatre tests de `tests/test_api.py` qui passent déjà sont `test_health`, `test_out_of_range_value_is_rejected`, `test_missing_field_is_rejected` et `test_openapi_documents_predict`.

Les deux tests qui attendent un code 422 passent initialement pour une mauvaise raison : le schéma ne déclare pas encore les quatre champs d'entrée, mais `extra="forbid"` refuse tous les champs envoyés comme champs supplémentaires. La requête est donc rejetée, sans que la borne de température ni l'obligation de fournir `load_pct` soient réellement vérifiées.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---:|---:|---:|---|
| `temperature_c` | `float` | -40 °C | 150 °C | Plage large pour couvrir des environnements froids et des températures anormalement élevées d'une machine. |
| `vibration_mm_s` | `float` | 0 mm/s | 100 mm/s | Une vibration ne peut pas être négative ; 100 mm/s couvre un niveau extrême de défaut. |
| `load_pct` | `float` | 0 % | 100 % | La charge est une proportion de la capacité nominale. |
| `runtime_hours` | `float` | 0 h | 100 000 h | Le compteur ne peut pas être négatif ; 100 000 h couvre une longue durée de service. |

Après l'ajout des champs au schéma mais avant l'implémentation de `predict()`, les trois tests de prédiction échouent encore : les deux prédictions atteignent le `raise NotImplementedError`, et le test qui attend 503 ne reçoit donc pas la réponse attendue. Le résultat attendu reste `3 failed, 10 passed` ; le message lié aux requêtes valides est `NotImplementedError`. C'est un bon signe : la validation Pydantic laisse passer les relevés valides et l'exécution atteint bien la fonction qu'il reste à implémenter.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Corps de la fonction :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(status_code=503, detail="Modèle de prédiction indisponible.")
return PredictionOut(**predictor.predict(reading.model_dump()))
```

On répond **503 Service Unavailable** plutôt que 500, car l'API fonctionne mais ne peut pas traiter la prédiction tant que le modèle nécessaire n'est pas disponible. Un code 500 indiquerait plutôt une erreur interne inattendue.

Le modèle est chargé une seule fois dans le gestionnaire de cycle de vie (`lifespan`) au démarrage. Cela évite de relire le fichier du modèle à chaque requête, réduit la latence et permet de réutiliser le prédicteur déjà chargé.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
13 passed, 1 warning in 4.45s
```

L'avertissement est une dépréciation de `starlette.testclient` concernant l'utilisation de `httpx`. Il n'empêche pas les tests de réussir.

## 5. L'API en marche

Résultats obtenus avec `uvicorn maintai.api.main:app --reload` et le modèle disponible :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---:|---|
| `GET /health` | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` avec `{"temperature_c":72.5,"vibration_mm_s":6.1,"load_pct":85,"runtime_hours":15000}` | 200 | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-10-28T17:40:31Z"}` |
| `POST /v1/predict` avec une température de 500 | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | 404 | `{"detail":"Not Found"}` |

Dans `/docs`, les bornes apparaissent dans le schéma de la requête `POST /v1/predict`, dans la description des champs et dans le schéma `SensorReading` accessible dans la section des schémas.

## 6. Questions de compréhension

1. **REST et FastAPI : quelle est la différence ?**  
   REST est un style d'architecture pour concevoir des interfaces HTTP autour de ressources, de routes et de méthodes comme GET ou POST. FastAPI est un framework Python qui permet de construire des API web, notamment des API suivant les principes REST.

2. **Le schéma Pydantic sert à trois choses. Lesquelles ?**  
   Il valide les données entrantes, convertit les types compatibles (par exemple un nombre reçu en valeur numérique) et décrit/documente les formats de requête et de réponse dans OpenAPI, utilisé par `/docs`.

3. **Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?**  
   `localhost` désigne la machine locale, `8000` le port sur lequel le serveur écoute et `/v1/predict` le chemin de la route de prédiction versionnée.

4. **Pourquoi `/v1` dans l'adresse ?**  
   Pour identifier la version de l'API. Une évolution incompatible peut être publiée sous une autre version, par exemple `/v2`, sans casser immédiatement les clients existants.

5. **Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?**  
   `maintai.api.main` est le chemin d'import Python vers le module `main.py`, et `app` est l'objet FastAPI défini dans ce module et servi par Uvicorn.

## 7. Le rendu Git

- Lien de la pull request : [à compléter]
- Le tag `tp1` existe sur GitHub : [à vérifier]
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?  
  [À compléter après la relecture.]

## 8. Ce qui reste flou

Pas de point technique bloquant après validation des 13 tests. Les informations de groupe, de pull request, de tag et de relecture restent à compléter selon le rendu Git réel.