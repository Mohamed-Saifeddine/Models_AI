 # Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** à compléter  ·  **Membres :** Marwa Khabarate  ·  **Date :** 04/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

----

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---:|---:|
| `POST /v1/predict` sans `load_pct` | Champ obligatoire manquant | 422 | 422 |
| `POST /v1/predict` avec `temperature_c: 500` | Température hors de la plage autorisée (maximum 150 °C) | 422 | 422 |
| `POST /v1/predict` avec `temperature_c: "chaud"` | Texte non convertible en nombre | 422 | 422 |
| `POST /v1/predict` avec un champ supplémentaire, par exemple `debug: true` | Champ inconnu refusé par le schéma | 422 | 422 |
| `POST /v1/predicte` | Route inexistante (faute de frappe) | 404 | 404 |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

Non : les quatre requêtes invalides sont rejetées avec le code 422 par la validation FastAPI/Pydantic, et la route inexistante renvoie 404.

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
5 passed in 19.29s
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

`@pytest.mark.parametrize` exécute la même fonction de test une fois pour chaque ligne de `CAS_REFUSES`. Pytest compte donc cinq tests, un par cas, et affiche leur description dans le rapport détaillé (`pytest -v`).

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
ruff check
UP017 : utilisation de `timezone.utc` au lieu de l'alias `datetime.UTC` dans `maintai/train.py`.
Found 1 error. 1 fixable with the `--fix` option.

ruff check--fix
error: unrecognized subcommand 'check--fix' (il manquait un espace).

ruff check --fix
Found 3 errors (3 fixed, 0 remaining).

ruff format
12 files reformatted, 8 files left unchanged

ruff check --fix
All checks passed!

python -m pytest
19 passed, 1 warning in 8.38s
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

`ruff check .` analyse statiquement le code pour détecter des erreurs et des problèmes de style, sans exécuter les tests. `python -m pytest` exécute les tests pour vérifier le comportement du projet. Après les corrections et le formatage avec Ruff, toutes les vérifications Ruff passent et les 19 tests passent ; pytest signale toutefois un avertissement de dépréciation lié à `starlette.testclient` et `httpx`.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Résultat attendu du starter indiqué dans le polycopié : `2 failed, 16 passed`. Cet état n'a pas été rejoué, car le dossier reçu contient déjà la sécurité implémentée.

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

`test_missing_key_is_rejected` et `test_wrong_key_is_rejected` échouent : avant l'implémentation de la sécurité, le starter renvoie 200 au lieu de 401. Cet état initial n'a pas été rejoué dans le dossier actuel, où la sécurité est déjà implémentée.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
api_key = get_settings().api_key
if api_key is None:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Clé API non configurée sur le serveur",
    )
if x_api_key is None or not secrets.compare_digest(x_api_key, api_key):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Clé API absente ou invalide",
    )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

Dans l'état du dossier actuel, aucun : `main.py` contient déjà `Depends(require_api_key)` sur le router `/v1`. Si cette dépendance n'était pas présente, écrire la fonction seule ne protégerait aucune route. L'étape intermédiaire avec `security.py` seul n'a pas été rejouée.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
24 passed in 27.13s
```

Le polycopié annonce 23 tests; cette copie en compte 24 car elle conserve aussi le test supplémentaire `test_unconfigured_server_key_returns_500`.

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` quand le modèle est chargé |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | Objet JSON contenant `failure_probability`, `alert`, `threshold` et `model_version` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | Détail Pydantic indiquant que la température dépasse la limite autorisée |

Ces réponses sont déduites du code et vérifiées en partie par les tests automatisés; les six requêtes n'ont pas été envoyées manuellement à un serveur uvicorn dans cette session.

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

L'authentification est une dépendance du router `/v1` : sans clé valide, la requête est refusée en 401. Avec la bonne clé, la validation du relevé s'effectue et refuse 500 °C en 422.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

Si aucune variable `MAINTAI_API_KEY` n'est configurée dans l'environnement, le serveur répond 500 : il n'a pas de clé de référence configurée pour comparer celle reçue. Le test `test_unconfigured_server_key_returns_500` couvre ce comportement.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
document.getElementById("go").addEventListener("click", async () => {
  const reading = Object.fromEntries(FEATURES.map(f => [f, Number(document.getElementById(f).value)]));
  const url = document.getElementById("url").value.trim().replace(/\/+$/, "");
  const key = document.getElementById("key").value;

  try {
    const response = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": key
      },
      body: JSON.stringify(reading)
    });
    const result = await response.json();
    if (!response.ok) {
      const detail = typeof result.detail === "string" ? result.detail : JSON.stringify(result);
      throw new Error(`${response.status} — ${detail}`);
    }

    show(result.alert ? "alert" : "ok",
      `${result.alert ? "Alerte panne" : "Aucun risque élevé"} — probabilité : ${(result.failure_probability * 100).toFixed(2)} %`);
  } catch (error) {
    show("err", error instanceof Error ? error.message : "Erreur inattendue");
  }
});
```

Ce qu'affiche la page (servie sur le port 5500) :

L'utilisateur confirme que l'interface fonctionne. Les résultats ci-dessous décrivent le comportement attendu du code; les essais individuels n'ont pas tous été consignés séparément.

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | Affiche la probabilité et le résultat : alerte ou aucun risque élevé |
| 500 °C, bonne clé | Affiche l'erreur 422 de validation |
| relevé normal, fausse clé | Affiche l'erreur 401 : clé absente ou invalide |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

Une page servie sur `http://localhost:5501` a une origine différente de celles autorisées (`localhost:5500` et `127.0.0.1:5500`). Le navigateur bloque la réponse avec une erreur CORS et la page affiche son message d'erreur réseau. Le refus de l'origine non autorisée est vérifié par `test_cors_refuses_unknown_origin`; l'essai réel dans le navigateur reste à faire.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

`curl.exe` n'applique pas la politique CORS du navigateur. CORS est une protection appliquée par les navigateurs aux requêtes initiées par des pages web.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

Sans `headers=HEADERS`, quatre cas correspondant à une route existante échouent en recevant 401 au lieu de 422. Le cas de mauvaise route passe quand même : aucune route `/v1/predicte` ne correspond, donc la dépendance du router n'est pas exécutée et l'API renvoie 404.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
24 passed in 27.13s
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   401 indique que l'authentification est absente ou invalide ; 422 indique que les données ne respectent pas le schéma attendu. 403 signifie que le serveur comprend la requête, mais refuse l'autorisation d'accès.
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   `.env` contient la clé locale et ne doit pas être commité. `.env.example` est un modèle sans secret réel, destiné à être copié en `.env` ; c'est ce modèle qui peut être commité.
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   Un en-tête évite d'exposer la clé dans l'URL, où elle pourrait être conservée dans l'historique, les journaux ou les liens partagés. La connexion doit aussi être protégée par HTTPS en production.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   `secrets.compare_digest` compare les clés en temps constant, ce qui réduit les fuites d'information par mesure du temps de comparaison.
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine est définie par le schéma, l'hôte et le port. `http://localhost:5500` et `http://localhost:8000` sont donc deux origines différentes.

## 8. Le rendu Git

- Lien de la pull request : https://github.com/unknownxowker/Models_AI/pull/5
- Le tag `tp2` existe sur GitHub : non, aucune référence `refs/tags/tp2` n'est publiée pour le moment.
- `git status` avant le commit : non consigné sur le poste d'origine; `.env` est ignoré et ne figure pas parmi les 26 fichiers de la PR.
- Relecteur et commentaire : à renseigner après la revue de la pull request.

Vérification Ruff de la version actuelle : le lint ciblé des fichiers Python modifiés passe après formatage. `ruff check .` signale encore `UP017` dans `maintai/train.py` (code préexistant, hors périmètre de ce TP); le formatage global du projet n'a pas été appliqué pour éviter de modifier des fichiers sans rapport.

## 9. Ce qui reste flou

Le contenu technique du TP est documenté et l'utilisateur confirme que l'interface fonctionne. La PR personnelle est ouverte; il reste à tester l'origine CORS sur le port 5501, obtenir une relecture, puis publier le tag `tp2` après le merge.
