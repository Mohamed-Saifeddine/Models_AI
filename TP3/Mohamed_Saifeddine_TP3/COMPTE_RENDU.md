# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** Mohamed Saifeddine  ·  **Membre :** Mohamed Saifeddine  ·  **Date :** 11 novembre 2026

---

## 1. Mise en place (dans `TP3/Mohamed_Saifeddine_TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```text
5 failed, 18 passed, 1 warning in 1.85s
```

Les trois tests de `tests/test_client.py` échouaient avec `NotImplementedError`, car
`MaintaiClient.predict` n'était pas encore écrit. Les deux tests de `tests/test_ui.py`
échouaient avec `IndexError`, car l'interface ne contenait encore aucune métrique.

## 2. Lancer Streamlit

Avec `streamlit run ui/app.py`, l'application peut ne pas trouver le package local :

```text
ModuleNotFoundError: No module named 'maintai'
```

Avec `python -m streamlit run ui/app.py`, Streamlit est lancé comme un module du même
interpréteur Python. Le dossier courant du projet reste dans le chemin de recherche des
modules, donc `maintai` est importable. L'application s'ouvre sur
`http://localhost:8501`.

## 3. Sprint 1 : l'onglet « Données »

Code de l'onglet « Données » :

```python
c1, c2, c3 = st.columns(3)
c1.metric("Relevés", len(df))
c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

variable = st.selectbox("Variable", FEATURES)
tranches = pd.cut(df[variable], bins=10)
taux_par_tranche = df.groupby(tranches, observed=True).failure.mean()
taux_par_tranche.index = [round(intervalle.mid, 2) for intervalle in taux_par_tranche.index]
st.subheader(f"Taux de panne par tranche de {variable}")
st.bar_chart(taux_par_tranche)

donnees_nuage = df.copy()
donnees_nuage["panne"] = donnees_nuage.failure.map({0: "non", 1: "oui"})
st.subheader("Température et vibration selon la panne")
st.scatter_chart(
    donnees_nuage,
    x="temperature_c",
    y="vibration_mm_s",
    color="panne",
)
```

| Indicateur | Valeur affichée |
|---|---:|
| Relevés | 5000 |
| Taux de panne | 13,6 % |
| Température moyenne | 59,8 °C |

Avec `vibration_mm_s`, le taux de panne augmente nettement avec la vibration : il est
proche de 2 % dans la première tranche, dépasse 32 % entre environ 4,5 et 6,7 mm/s,
puis dépasse 66 % dans la tranche suivante. Parmi les variables étudiées, la vibration
est celle qui est le plus fortement associée à la panne.

Un widget ordinaire, comme la liste déroulante, relance le script du début à la fin et
le message `relance` réapparaît dans le terminal. Les curseurs placés dans
`st.form("releve")` constituent l'exception : leur déplacement seul ne relance pas le
script ; la relance se produit lorsque l'utilisateur clique sur « Prédire ».

`@st.cache_data` mémorise le résultat de `charger`. Ainsi, le CSV n'est pas relu sur le
disque à chaque relance du script tant que le chemin et le fichier ne changent pas.

## 4. Sprint 2 : l'onglet « Prédiction »

Méthode `predict` de `maintai/client.py` :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
    headers = {"X-API-Key": self.api_key} if self.api_key else {}
    response = self.http.post("/v1/predict", json=reading, headers=headers)
    if response.status_code != 200:
        raise APIError(response.status_code, response.json().get("detail"))
    return response.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```text
23 passed, 1 warning in 2.30s
```

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | Probabilité de panne : 95 % ; « ALERTE : risque de panne détecté » |
| valeurs par défaut, fausse clé | « Erreur 401 : Clé API absente ou invalide » |
| API arrêtée | « API injoignable » suivi du message de connexion |

Le port 8501 n'a pas besoin d'être ajouté à `MAINTAI_CORS_ORIGINS`. Avec la page HTML
du TP2, le navigateur envoyait directement la requête à l'API : la politique CORS du
navigateur s'appliquait. Avec Streamlit, le navigateur communique avec Streamlit sur
8501, puis le processus Python Streamlit appelle l'API sur 8000. CORS ne s'applique pas
aux communications serveur-à-serveur.

## 5. Questions de compréhension

1. Dans le TP2, le code JavaScript exécuté par le navigateur envoie la requête à l'API.
   Dans le TP3, le processus Python Streamlit l'envoie grâce à `MaintaiClient`.
2. `tests/test_client.py` fournit à `MaintaiClient` le `TestClient` FastAPI avec le
   paramètre `http=client`. Les requêtes sont envoyées directement à l'application en
   mémoire ; aucun serveur Uvicorn ni port réseau n'est nécessaire.
3. Pour une démonstration rapide à un client, je choisirais Streamlit, car il permet de
   construire rapidement une interface de données en Python. Pour une application de
   production destinée quotidiennement aux techniciens, je choisirais plutôt une
   interface HTML/JavaScript dédiée : elle offre davantage de contrôle sur l'ergonomie,
   le design, les performances et l'intégration au système d'information.

## 6. Le rendu Git

- Lien de la pull request : à ajouter après la création de la pull request.
- Le tag `tp3` existe sur GitHub : non, à créer après la fusion.
- `git status` avant le commit : `.env`, `data/*.csv` et `models/` n'apparaissent pas,
  car ils sont correctement ignorés par `.gitignore`.

## 7. Ce qui reste flou

Les différences entre un appel HTTP effectué par le navigateur et un appel effectué par
le serveur Streamlit sont maintenant comprises, notamment leur conséquence sur CORS.
Le travail restant concerne uniquement le rendu Git : commit, pull request, fusion et tag.
