# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G4  ·  **Membres :** Mohamed Saifeddine, Sara Hajdaoui, Ilyass Edhoum, Marwa Khabarate  ·  **Auteur :** Sara Hajdaoui  ·  **Date :** 25 novembre 2026

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
5 failed, 18 passed
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

- `tests/test_client.py` (3 tests) : `NotImplementedError`, car la méthode `MaintaiClient.predict` n'est pas encore écrite.
- `tests/test_ui.py` (2 tests) : la page ne contient pas encore les indicateurs ni le résultat de la prédiction (`IndexError: list index out of range` sur `at.metric[0]`), car les TODO de `ui/app.py` ne sont pas remplis.

## 2. Lancer Streamlit

`streamlit run ui/app.py` affiche dans le navigateur :

```
ModuleNotFoundError: No module named 'maintai'
Traceback:
File "ui/app.py", line 7, in <module>
    from maintai.client import APIError, MaintaiClient
```

`python -m streamlit run ui/app.py` fonctionne. Avec `python -m`, Python ajoute le **dossier courant** (`TP3/`, qui contient `maintai/`) à la liste des dossiers où il cherche les modules (`sys.path`). Avec la commande `streamlit` seule, il ajoute seulement le dossier du script (`ui/`), où `maintai` n'existe pas. Le TP4 règle le problème pour de bon en installant `maintai` comme package (`pip install -e .`).

## 3. Sprint 1 : l'onglet « Données »

Code de l'onglet « Données » :

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Nombre de relevés",
        f"{nombre_releves}"
    )

with col2:
    st.metric(
        "Taux de panne",
        f"{taux_panne:.1f} %"
    )

with col3:
    st.metric(
        "Température moyenne",
        f"{temperature_moyenne:.1f} °C"
    )

st.divider()

# ----------------------------------------------
# 4.2 Choix de la variable à analyser
# ----------------------------------------------

st.subheader("Analyse du taux de panne")

variable = st.selectbox(
    "Choisir une variable :",
    FEATURES
)

# ----------------------------------------------
# 4.3 Découpage en tranches avec pd.cut
# ----------------------------------------------

donnees_tranches = df.copy()

donnees_tranches["tranche"] = pd.cut(
    donnees_tranches[variable],
    bins=10
)

taux_par_tranche = (
    donnees_tranches
    .groupby("tranche", observed=True)["failure"]
    .mean()
    .mul(100)
    .to_frame()
)

# Étiquette = milieu de la tranche (un nombre, pas du texte)
taux_par_tranche.index = [
    round(i.mid, 1) for i in taux_par_tranche.index
]

# ----------------------------------------------
# 4.4 Affichage du graphique en barres
# ----------------------------------------------

st.caption(
    f"Taux de panne selon les différentes tranches de {variable}"
)

st.bar_chart(
    taux_par_tranche,
    y="failure",
    y_label="Taux de panne (%)"
)

st.divider()

# ----------------------------------------------
# 4.5 Nuage de points température / vibration
# ----------------------------------------------

st.subheader("Relation température / vibration")

donnees_scatter = df[
    ["temperature_c", "vibration_mm_s", "failure"]
].copy()

donnees_scatter["État"] = donnees_scatter["failure"].map(
    {0: "Normal", 1: "Panne"}
)

st.scatter_chart(
    donnees_scatter,
    x="temperature_c",
    y="vibration_mm_s",
    color="État",
    x_label="Température (°C)",
    y_label="Vibration (mm/s)"
)
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5000 |
| Taux de panne | 13.6 % |
| Température moyenne | 59.8 °C |

**Taux de panne selon `vibration_mm_s`** (milieu de tranche → taux de panne) : 1,1 mm/s → 2 % ; 3,4 → 10 % ; 5,6 → 32 % ; 7,8 → 66 % ; 10,0 → 84 % ; au-delà de 12 mm/s → 100 %. Le taux de panne augmente très fortement avec la vibration : au-dessus de 12 mm/s, toutes les machines du jeu de données sont en panne. Pour la température, il monte plus doucement (0 % vers 27 °C, environ 37 % vers 84-91 °C). **La vibration est la variable qui compte le plus.** Le nuage de points le confirme : les points « Panne » se regroupent en haut (forte vibration), quelle que soit la température.

**`print("relance")` en haut de `ui/app.py`** : à chaque déplacement d'un curseur ou changement de la liste déroulante, `relance` s'affiche à nouveau dans le terminal. Streamlit ré-exécute **tout le script**, de la première à la dernière ligne, à chaque interaction, puis renvoie la nouvelle page. Les curseurs placés dans `st.form` ne relancent rien : seul le bouton « Prédire » le fait.

**À quoi sert `@st.cache_data` ?** Comme le script est relancé à chaque clic, `charger()` relirait le CSV à chaque fois. Avec `@st.cache_data`, le résultat est gardé en mémoire : le CSV n'est lu qu'une fois (tant que le chemin ne change pas).

## 4. Sprint 2 : l'onglet « Prédiction »

Méthode `predict` (`maintai/client.py`) :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé à l'API et retourne la prédiction."""
    headers = {}
    if self.api_key:
        headers["X-API-Key"] = self.api_key

    r = self.http.post("/v1/predict", json=reading, headers=headers)

    if r.status_code != 200:
        try:
            detail = r.json().get("detail")
        except ValueError:
            detail = r.text
        raise APIError(r.status_code, detail)

    return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
23 passed, 1 warning in 2.21s
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) et `python -m streamlit run ui/app.py`, relevé par défaut (60 °C, 6 mm/s, 85 %, 10 000 h) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | Probabilité de panne **65 %** et message rouge « 🚨 ALERTE : risque élevé de panne ! » (seuil 0.3) |
| valeurs par défaut, fausse clé | Message jaune « Erreur API 401 : Clé API absente ou invalide » |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | Message rouge « API injoignable : impossible de contacter le serveur. [Errno 61] Connection refused » |

**Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?** CORS est une règle **du navigateur** : il bloque le JavaScript d'une page qui appelle un autre domaine ou port non autorisé. En TP2, c'était le navigateur (page du port 5501) qui envoyait la requête. Avec Streamlit, c'est le **serveur Python** (`httpx` dans `MaintaiClient`) qui appelle l'API, et pas le navigateur : CORS ne s'applique pas. Le navigateur ne parle qu'au serveur Streamlit (port 8501). La clé API, elle, protège toujours l'API.

## 5. Questions de compréhension

1. **Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?**
   En TP2, le navigateur de l'utilisateur (le `fetch` en JavaScript). Dans Streamlit, le programme Python qui tourne sur le serveur Streamlit (`MaintaiClient`, avec `httpx`) ; le navigateur ne fait qu'afficher la page.
2. **Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?**
   On donne à `MaintaiClient` le `TestClient` de FastAPI par le paramètre `http=`. Les requêtes vont directement à l'objet `app` en mémoire, sans réseau ni serveur. C'est le même code de client que celui qui parle à uvicorn.
3. **HTML + JavaScript (TP2) ou Streamlit (TP3) ?**
   Pour une **démonstration à un client**, Streamlit : en quelques lignes de Python on montre les données, des graphiques et la prédiction, sans écrire de HTML ni de JavaScript. Pour **l'application d'un technicien**, une page HTML + JavaScript (ou une application dédiée) : elle est plus légère, se personnalise entièrement (mobile, ergonomie), ne relance pas tout un script à chaque clic et ne demande pas un serveur Python par utilisateur. Streamlit reste possible pour un outil interne simple.

## 6. Le rendu Git

- Lien de la pull request : *voir la PR « TP3 : Hajdaoui Sara » sur Mohamed-Saifeddine/Models_AI*
- Le tag `tp3` existe sur GitHub : non (à créer après la fusion : `git tag tp3`, `git push --tags`)
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? **non** (exclus par `.gitignore`)

## 7. Ce qui reste flou

Comment déployer l'interface Streamlit et l'API sur un vrai serveur pour qu'un technicien y accède depuis l'atelier, et comment gérer la clé API pour plusieurs utilisateurs sans la saisir à chaque fois.
