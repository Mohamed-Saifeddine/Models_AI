# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** à compléter · **Membre :** Mohamed Saifeddine · **Date :** 06/11/2026

## 1. Activité 1 : casser son API (dans `TP1`)

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---:|---:|
| `POST /v1/predict` sans valeur exploitable pour `load_pct` | champ manquant ou nul | 422 | 422 |
| `POST /v1/predict` avec `temperature_c: 600` | valeur hors de la borne maximale de 150 °C | 422 | 422 |
| `POST /v1/predict` avec `temperature_c: "abc"` | texte au lieu d'un nombre | 422 | 422 |
| `POST /v1/predict` avec le champ supplémentaire `pression` | champ non autorisé | 422 | 422 |
| `POST /v1/predict2` | route inexistante | 404 | 404 |

Les codes prévus étaient corrects. Pour le cas du texte, j'ai remplacé la température par une chaîne et j'ai obtenu 422.

Dernière ligne de `python -m pytest` dans le TP1 actuel :

```text
======================== 19 passed, 1 warning in 0.93s =========================
```

Le TP1 contient les cinq cas paramétrés ainsi qu'un test supplémentaire sur 500 °C, ce qui explique que son total actuel soit supérieur aux 18 tests annoncés dans le sujet.

`@pytest.mark.parametrize` permet de tester plusieurs cas avec la même fonction. Ici, Pytest compte cinq tests.

## 2. Ruff

Sortie de `ruff check .` dans le TP1 :

```text
All checks passed!
```

Ruff vérifie la qualité et le style du code. Pytest exécute le code pour vérifier qu'il fonctionne correctement.

## 3. Mise en place du TP2

État initial attendu avec le starter, avant la sécurité :

```text
============================= 2 failed, 16 passed =============================
```

Les deux tests en échec sont ceux de la clé absente et de la mauvaise clé. Ils reçoivent 200 au lieu de 401.

## 4. La clé API (sprint 1)

Fonction `require_api_key()` :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou fausse."""
    expected_key = get_settings().api_key
    if expected_key is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
        )

    if x_api_key is None or not secrets.compare_digest(x_api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
```

Ligne du routeur dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Deux tests échouent encore, car la fonction de sécurité n'est pas encore utilisée par le routeur.

Dernière ligne de Pytest à la fin du TP2, avec les cinq tests de l'activité 1 :

```text
======================== 23 passed, 1 warning in 0.86s =========================
```

Le warning vient de la compatibilité entre `fastapi.testclient`, Starlette et la future bibliothèque `httpx2`; il ne correspond pas à un échec du TP.

Résultats observés avec `uvicorn maintai.api.main:app --reload --env-file .env` :

| Requête | Code obtenu | Réponse JSON |
|---|---:|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability":0.0027,"alert":false,"threshold":0.3,...}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | erreur de validation : température inférieure ou égale à 150 attendue |

Sans clé, l'API renvoie d'abord 401. Avec la bonne clé, elle vérifie la température et renvoie 422.

Sans `--env-file .env`, une requête avec la clé renvoie :

```text
{"detail":"Clé API non configurée sur le serveur"}
HTTP 500
```

J'obtiens 500 parce que la clé du serveur n'a pas été chargée.

## 5. La page web (sprint 2)

Code du gestionnaire du bouton :

```javascript
document.getElementById("go").addEventListener("click", async () => {
  const reading = Object.fromEntries(FEATURES.map(f => [f, Number(document.getElementById(f).value)]));
  const url = document.getElementById("url").value.replace(/\/$/, "");
  const key = document.getElementById("key").value;

  try {
    const response = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": key,
      },
      body: JSON.stringify(reading),
    });
    const data = await response.json();

    if (!response.ok) {
      const message = data.detail ?? "Erreur inconnue";
      show("err", `Erreur ${response.status} : ${JSON.stringify(message)}`);
      return;
    }

    const probability = (data.failure_probability * 100).toFixed(2);
    const message = `Probabilité de panne : ${probability} % - Alerte : ${data.alert ? "oui" : "non"}`;
    show(data.alert ? "alert" : "ok", message);
  } catch (error) {
    show("err", `API injoignable ou requête bloquée par CORS : ${error.message}`);
  }
});
```

| Essai sur le port 5500 | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | `Probabilité de panne : 0.27 % - Alerte : non` |
| 500 °C, bonne clé | `Erreur 422`, suivie du détail de validation de la température |
| relevé normal, fausse clé | `Erreur 401 : "Clé API absente ou invalide"` |

### Expérience CORS

La prérequête `OPTIONS` envoyée depuis `http://localhost:5500` reçoit 200 et l'en-tête :

```text
access-control-allow-origin: http://localhost:5500
```

Depuis `http://localhost:5501`, la prérequête reçoit 400 et ne contient aucun en-tête `access-control-allow-origin`. Dans un navigateur, la page affiche donc normalement :

```text
API injoignable ou requête bloquée par CORS : Failed to fetch
```

La console indique que l'accès à `http://localhost:8000/v1/predict` depuis l'origine `http://localhost:5501` a été bloqué par la politique CORS, car aucun en-tête `Access-Control-Allow-Origin` valide n'est présent.

`curl` fonctionne parce que CORS concerne surtout les navigateurs.

## 6. Les tests de l'activité 1 dans le TP2

Sans les headers, quatre tests reçoivent 401 et échouent. Le test de la mauvaise route passe quand même avec 404.

Avec `HEADERS = {"X-API-Key": "test-key"}` :

```text
======================== 23 passed, 1 warning in 0.86s =========================
```

## 7. Questions de compréhension

1. **401, 422 et 403 :** 401 concerne une clé absente ou fausse. 422 concerne des données invalides. 403 signifie que l'accès est interdit même si le client est identifié.
2. **Clé et Git :** la clé ne doit pas être visible sur Git. La vraie clé est dans `.env`, qui est ignoré. `.env.example` contient seulement un exemple.
3. **En-tête plutôt qu'URL :** cela évite que la clé apparaisse dans l'historique ou les logs de l'URL.
4. **`secrets.compare_digest` :** il compare les clés de façon plus sûre que `==`.
5. **Origine :** une origine contient le protocole, le domaine et le port. Les ports 5500 et 8000 donnent donc deux origines différentes.

## 8. Le rendu Git

- Lien de la pull request : à compléter après la création de la pull request.
- Le tag `tp2` existe localement : non, à créer après la fusion.
- `.env` apparaissait-il dans les fichiers suivis par Git ? non, il est ignoré par `.gitignore`.
- Relecteur et commentaire : à compléter après la relecture de la pull request.

## 9. Ce qui reste flou

Pour le moment, tout est clair.
