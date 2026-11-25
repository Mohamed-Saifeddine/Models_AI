# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G1 · **Membre :** Ilyass Edhoum · **Date :** 11/11/2026

## 1. Mise en place

J’ai constaté que `requirements.txt` se trouve dans `maintai-starter-tp3`, et non dans le dossier parent `TP3`. Depuis `TP3`, je me place dans le projet avant d’installer les dépendances :

```powershell
cd .\maintai-starter-tp3
python -m pip install -r requirements.txt
```

Le message « Could not open requirements file » venait donc du mauvais dossier courant. L’avis de mise à jour de pip est indépendant et n’est pas une erreur.

Pour le starter non complété, le polycopié indique `5 failed, 18 passed`. Les échecs concernent `tests/test_client.py` (les trois tests rencontrent `NotImplementedError`) et `tests/test_ui.py` (les indicateurs et la prédiction sont encore remplacés par des messages provisoires). Après avoir complété le code, j’ai exécuté `python -m pytest -q` et obtenu :

```
23 passed, 1 warning in 14.56s
```

L’avertissement concerne la dépréciation de l’intégration entre `httpx` et `starlette.testclient` ; il n’empêche pas les tests de réussir. `python -m pip check` ne signale aucune dépendance cassée.

## 2. Lancer Streamlit

J’ai vérifié le lancement direct depuis le dossier du projet avec `streamlit run ui/app.py`. Dans le navigateur, j’obtiens `ModuleNotFoundError: No module named 'maintai'`. Avec `python -m streamlit run ui/app.py`, Streamlit est lancé comme module depuis le dossier du projet et Python peut résoudre l’import `maintai` ; l’interface s’affiche.

## 3. Sprint 1 : l’onglet « Données »

Voici le code que j’ai ajouté dans l’onglet :

```python
c1, c2, c3 = st.columns(3)
c1.metric("Relevés", len(df))
c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

variable = st.selectbox("Variable", FEATURES)
tranches = pd.cut(df[variable], bins=10)
taux_par_tranche = df.groupby(tranches, observed=True).failure.mean()
taux_par_tranche.index = [round(interval.mid, 2) for interval in taux_par_tranche.index]
st.bar_chart(taux_par_tranche)

nuage = df.assign(panne=df.failure.map({0: "Non", 1: "Oui"}))
st.scatter_chart(nuage, x="temperature_c", y="vibration_mm_s", color="panne")
```

Après avoir généré le jeu synthétique par défaut (`n=5000`, `seed=42`), j’obtiens :

| Indicateur | Valeur affichée |
|---|---:|
| Relevés | 5000 |
| Taux de panne | 13,6 % |
| Température moyenne | 59,8 °C |

Quand je choisis `vibration_mm_s`, le taux de panne augmente nettement dans l’ensemble lorsque la vibration augmente. Sur ce jeu synthétique, cette hausse est plus marquée que celle liée à la température.

Si j’ajoute `print("relance")` en haut du script puis déplace un curseur, Streamlit réexécute le script et le message réapparaît dans le terminal. `@st.cache_data` conserve le résultat du chargement CSV et évite de relire le fichier à chaque relance.

## 4. Sprint 2 : l’onglet « Prédiction »

Voici ma méthode `predict` dans `maintai/client.py` :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
    headers = {"X-API-Key": self.api_key} if self.api_key is not None else {}
    response = self.http.post("/v1/predict", json=reading, headers=headers)
    if response.status_code != 200:
        raise APIError(response.status_code, response.json().get("detail"))
    return response.json()
```

À la fin du sprint 2, j’ai vérifié que les 23 tests passent avec `python -m pytest -q`. J’ai aussi testé l’application réelle avec l’API FastAPI lancée : la vérification `/health` renvoie `status: ok` et `model_loaded: true`.

| Essai | Ce que j’obtiens dans Streamlit |
|---|---|
| Valeurs par défaut (`72 °C`, `6 mm/s`, `85 %`, `15 000 h`), bonne clé | L’interface affiche `95 %` et « ALERTE de panne (seuil : 30 %) ». L’API renvoie une probabilité de `0.9475`. |
| Valeurs par défaut, fausse clé | L’interface affiche « Erreur API (401) : Clé API absente ou invalide ». |
| API arrêtée | L’interface affiche « API injoignable » avec le détail de l’erreur de connexion. |

Je n’ai pas besoin d’ajouter le port 8501 à `MAINTAI_CORS_ORIGINS`, car ce n’est pas le navigateur qui appelle l’API : le code Python exécuté par Streamlit envoie la requête côté serveur. CORS s’applique aux requêtes inter-origines effectuées par les navigateurs.

## 5. Questions de compréhension

1. Dans la page web du TP2, le JavaScript du navigateur envoie la requête à l’API. Dans Streamlit, c’est le code Python du serveur Streamlit qui l’envoie.
2. Les tests de `test_client.py` passent un `TestClient` à `MaintaiClient`. La requête va directement à l’application FastAPI en mémoire ; je n’ai donc pas besoin de lancer uvicorn.
3. Pour une démonstration rapide à un client, je choisirais Streamlit, car je peux construire l’interface rapidement en Python. Pour une application durable destinée aux techniciens, je choisirais une interface web dédiée pour mieux contrôler l’ergonomie, le déploiement et l’usage mobile. Streamlit reste adapté à un outil interne ou à un prototype.

## 6. Le rendu Git

- **Lien de ma pull request :** pas encore créée ; le dossier qui m’a été fourni ne contient pas de dépôt Git (`.git`).
- **Le tag `tp3` existe sur GitHub :** je ne peux pas le créer ni le vérifier tant que le dépôt Git distant n’est pas disponible.
- **`git status` avant le commit :** non disponible pour la même raison. J’ai vérifié que `.env` est absent et que `data/sensors.csv` ainsi que `models/` sont exclus par `.gitignore`.

## 7. Ce qui reste flou

À ce stade, je n’ai pas identifié de point technique bloquant. Si une notion ou une étape de rendu me reste floue, je la noterai ici avant de rendre le TP.
