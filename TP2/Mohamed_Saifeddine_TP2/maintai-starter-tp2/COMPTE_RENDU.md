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

Les prévisions de codes étaient correctes. Lors du premier essai du cas « texte au lieu d'un nombre », un JSON mal formé pouvait produire un message de décodage JSON. Le test final envoie bien un JSON valide contenant une chaîne, ce qui vérifie la validation de type et renvoie 422.

Dernière ligne de `python -m pytest` dans le TP1 actuel :

```text
======================== 19 passed, 1 warning in 0.93s =========================
```

Le TP1 contient les cinq cas paramétrés ainsi qu'un test supplémentaire sur 500 °C, ce qui explique que son total actuel soit supérieur aux 18 tests annoncés dans le sujet.

`@pytest.mark.parametrize` exécute la même fonction de test avec plusieurs jeux de paramètres. La liste contient cinq lignes : Pytest compte donc cinq tests distincts et indique le cas concerné dans son rapport.

## 2. Ruff

Sortie de `ruff check .` dans le TP1 :

```text
All checks passed!
```

`ruff check .` effectue une analyse statique : imports inutiles, organisation des imports et règles de qualité ou de style. `python -m pytest` exécute le programme et vérifie son comportement avec des assertions. Un code peut donc être fonctionnel mais mal écrit, ou être bien formaté tout en produisant un résultat faux.

## 3. Mise en place du TP2

État initial attendu avec le starter, avant la sécurité :

```text
============================= 2 failed, 16 passed =============================
```

Les deux tests en échec sont `test_missing_key_is_rejected` et `test_wrong_key_is_rejected`. Ils attendent 401, mais reçoivent 200 parce que la fonction de sécurité n'est pas encore appelée par le routeur.

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

Après avoir écrit uniquement `security.py`, deux tests échouent encore. La fonction existe, mais FastAPI ne l'exécute pas tant qu'elle n'est pas ajoutée comme dépendance du routeur `/v1`.

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

500 °C sans clé donne 401, tandis que 500 °C avec la bonne clé donne 422. FastAPI exécute d'abord la dépendance de sécurité du routeur, puis valide le corps de la requête seulement si l'authentification réussit.

Sans `--env-file .env`, une requête avec la clé renvoie :

```text
{"detail":"Clé API non configurée sur le serveur"}
HTTP 500
```

Ce n'est pas 401, car le problème ne vient pas du client : le serveur ne possède aucune clé de référence et ne peut pas authentifier les requêtes.

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

`curl` reçoit quand même une réponse parce que CORS est une règle de sécurité appliquée par les navigateurs. `curl` n'applique pas cette politique.

## 6. Les tests de l'activité 1 dans le TP2

Sans `headers=HEADERS`, quatre cas qui attendent 422 reçoivent 401 et échouent. Le cas « mauvaise route » passe quand même avec 404 : aucune route ne correspond à l'URL, donc FastAPI renvoie 404 sans exécuter la dépendance du routeur.

Avec `HEADERS = {"X-API-Key": "test-key"}` :

```text
======================== 23 passed, 1 warning in 0.86s =========================
```

## 7. Questions de compréhension

1. **Différence entre 401, 422 et 403.** 401 indique que l'authentification est absente ou invalide. 422 indique que la requête a été comprise, mais que ses données ne respectent pas le schéma attendu. 403 indique que l'identité est connue mais qu'elle n'a pas l'autorisation d'effectuer l'action.
2. **Stockage de la clé.** Une clé placée dans le code ou Git reste visible dans l'historique et doit être remplacée si elle fuit. `.env` contient la vraie clé locale et n'est pas commité. `.env.example` décrit les variables avec une fausse valeur et peut être commité.
3. **En-tête plutôt qu'URL.** Les URL sont souvent enregistrées dans l'historique, les journaux des serveurs, les outils de suivi et certains intermédiaires. Un en-tête évite cette exposition et sépare l'authentification des données métier.
4. **Rôle de `secrets.compare_digest`.** Il compare les valeurs avec une durée moins dépendante de la position du premier caractère différent, ce qui réduit les informations exploitables par une attaque temporelle.
5. **Origine.** Une origine est la combinaison du protocole, du nom d'hôte et du port. `http://localhost:5500` et `http://localhost:8000` sont deux origines différentes, car leurs ports diffèrent.

## 8. Le rendu Git

- Lien de la pull request : à compléter après la création de la pull request.
- Le tag `tp2` existe localement : non, à créer après la fusion.
- `.env` apparaissait-il dans les fichiers suivis par Git ? non, il est ignoré par `.gitignore`.
- Relecteur et commentaire : à compléter après la relecture de la pull request.

## 9. Ce qui reste flou

La partie technique est terminée. Il reste uniquement les informations externes qui ne peuvent être connues avant le rendu : numéro du groupe, lien de la pull request, nom du relecteur, commentaire de relecture et création du tag `tp2` après fusion.
