# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G1  ·  **Membre :** Mohamed Saifeddine  ·  **Date :** …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
(collez ici)
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

…

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | | | | |
| `vibration_mm_s` | | | | |
| `load_pct` | | | | |
| `runtime_hours` | | | | |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
(collez ici)
```

…

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
(collez ici le corps de predict())
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

…

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

…

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
(collez ici)
```

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | | |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | | |
| `POST /v1/predict` avec une température de 500 | | |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | | |

Dans `/docs`, où voit-on les bornes que vous avez choisies ?

…

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   …
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   …
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   …
4. Pourquoi `/v1` dans l'adresse ?
   …
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   …

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp1` existe sur GitHub : oui / non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 8. Ce qui reste flou

…
