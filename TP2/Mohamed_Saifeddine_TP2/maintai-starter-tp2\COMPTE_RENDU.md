# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** à renseigner · **Membre :** Mohamed Saifeddine · **Date :** 06/11/2026

## 1. Activité 1 : casser son API

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---:|---:|
| `POST /v1/predict` sans `load_pct` | champ manquant | 422 | 422 |
| `POST /v1/predict` avec `temperature_c: 600` | valeur absurde, supérieure à 150 °C | 422 | 422 |
| `POST /v1/predict` avec `temperature_c: "abc"` | texte au lieu d'un nombre | 422 | 422 |
| `POST /v1/predict` avec le champ `pression` | champ supplémentaire interdit | 422 | 422 |
| `POST /v1/predict2` | route inexistante | 404 | 404 |

Les codes prévus étaient corrects. Pour le troisième cas, j'ai mis du texte à la place de la température et j'ai obtenu 422.

Sortie actuelle du TP1 :

```text
======================== 19 passed, 1 warning in 0.93s =========================
```

J'ai 19 tests parce qu'il y a aussi un test sur la température à 500 °C.

`@pytest.mark.parametrize` permet de tester plusieurs cas avec la même fonction. Ici, Pytest compte cinq tests.

## 2. Ruff

```text
All checks passed!
```

Ruff vérifie la qualité et le style du code. Pytest exécute le code pour vérifier qu'il fonctionne correctement.

## 3. Mise en place du TP2

État initial du starter :

```text
============================= 2 failed, 16 passed =============================
```

Les deux tests qui échouent sont ceux de la clé absente et de la mauvaise clé. Ils reçoivent 200 au lieu de 401.

## 4. La clé API

Fonction `require_api_key()` :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
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

Routeur protégé :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Deux tests échouent encore, car la fonction de sécurité n'est pas encore utilisée par le routeur.

Résultat final :

```text
======================== 23 passed, 1 warning in 0.83s =========================
```

Le warning ne fait pas échouer les tests.

| Requête | Code | Corps JSON obtenu |
|---|---:|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, normal, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, normal, fausse clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, normal, bonne clé | 200 | `{"failure_probability":0.0027,"alert":false,"threshold":0.3,...}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | température inférieure ou égale à 150 attendue |

Sans clé, l'API vérifie d'abord la sécurité et renvoie 401. Avec la bonne clé, elle vérifie la température et renvoie 422.

Sans `--env-file .env`, le serveur renvoie :

```text
{"detail":"Clé API non configurée sur le serveur"}
HTTP 500
```

J'obtiens 500 parce que la clé du serveur n'a pas été chargée.

## 5. La page web

Gestionnaire du bouton :

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

| Essai sur `http://localhost:5500` | Affichage |
|---|---|
| relevé normal, bonne clé | `Probabilité de panne : 0.27 % - Alerte : non` |
| 500 °C, bonne clé | `Erreur 422`, avec le détail de validation |
| relevé normal, fausse clé | `Erreur 401 : "Clé API absente ou invalide"` |

Sur le port 5500, la page fonctionne et la requête CORS est acceptée.

Sur le port 5501, la page affiche `Failed to fetch` et la console indique une erreur CORS.

`curl` fonctionne parce que CORS concerne surtout les navigateurs.

## 6. Tests de l'activité 1 dans le TP2

Sans les headers, quatre tests reçoivent 401 et échouent. Le test de la mauvaise route passe quand même avec 404.

Avec `HEADERS = {"X-API-Key": "test-key"}` :

```text
======================== 23 passed, 1 warning in 0.83s =========================
```

## 7. Questions de compréhension

1. **401, 422 et 403 :** 401 concerne une clé absente ou fausse. 422 concerne des données invalides. 403 signifie que l'accès est interdit même si le client est identifié.
2. **Clé et Git :** la clé ne doit pas être visible sur Git. La vraie clé est dans `.env`, qui est ignoré. `.env.example` contient seulement un exemple et peut être commité.
3. **En-tête plutôt qu'URL :** la clé est mise dans un en-tête pour éviter qu'elle apparaisse dans l'historique ou les logs de l'URL.
4. **`secrets.compare_digest` :** il compare les clés de façon plus sûre que `==`.
5. **Origine :** une origine contient le protocole, le domaine et le port. Les ports 5500 et 8000 donnent donc deux origines différentes.

## 8. Le rendu Git

- Lien de la pull request : à renseigner après sa création.
- Tag `tp2` sur GitHub : non créé pour le moment ; il doit être créé après la fusion.
- `.env` apparaissait dans les fichiers suivis : non, il est ignoré par `.gitignore`.
- Relecteur et commentaire : à renseigner après la relecture de la pull request.

## 9. Ce qui reste flou

Pour le moment, tout est clair.
