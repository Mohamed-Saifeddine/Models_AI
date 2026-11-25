# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI
**Nom:** Sara Hajdaoui
**Groupe :** 4 · **Membres :** Mohamed Saifeddine / Marwa Khabarate/ Sara hajdaoui / Ilyas edhoum  · **Date :** 04/11/2026


---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | Champ `load_pct` manquant | 422 | 422 |
| 2 | Valeur absurde : `temperature_c = 500` | 422 | 422 |
| 3 | Texte `"chaud"` au lieu d'un nombre | 422 | 422 |
| 4 | Champ supplémentaire `capteur_inconnu` | 422 | 422 |
| 5 | Mauvaise route `/v1/predcit` | 404 | 404 |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

Non, les cinq prévisions étaient justes. Les quatre premières requêtes sont refusées par la validation Pydantic du corps JSON (champ obligatoire absent, borne maximale de 150 °C dépassée, type incorrect, champ non prévu par le schéma), d'où le code 422. La cinquième vise une route qui n'existe pas : FastAPI répond 404 avant toute validation. Aucune correction des bornes dans `schemas.py` n'a donc été nécessaire.

Dernière ligne de `python -m pytest` avec les tests de l'activité 1 (dans `TP/TP1`) :

```text
19 passed, 1 warning in 1.19s
```

Les 13 tests fournis, les 5 cas de l'activité 1 et le test d'exemple « 500 °C donne 422 » passent tous.

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

`@pytest.mark.parametrize` permet d'exécuter une même fonction avec plusieurs ensembles de données. Ici, la fonction `test_requete_refusee` est exécutée cinq fois, une fois pour chaque cas de `CAS_REFUSES`. Pytest comptabilise donc **cinq tests**.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```text
All checks passed!
```

Le même résultat est obtenu dans `TP/TP2` une fois le sprint 1 terminé. Après `ruff format .`, le terminal indiquait :

```text
12 files reformatted, 7 files left unchanged
19 files already formatted
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

`ruff check .` analyse statiquement le code : organisation des imports, variables non définies, imports inutilisés et règles de qualité. Il a notamment détecté des imports à corriger dans `maintai/api/main.py` et l'utilisation de `timezone.utc` dans `maintai/train.py`. `python -m pytest` **exécute** les tests pour vérifier le comportement du programme, comme les codes 200, 401, 404 ou 422 renvoyés par l'API.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```text
======== 2 failed, 16 passed, 1 warning in 1.23s ========
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

Les tests `test_missing_key_is_rejected` et `test_wrong_key_is_rejected` échouaient. Tous deux recevaient **200 OK** au lieu de **401 Unauthorized**, parce que l'authentification n'était pas encore appliquée au routeur `/v1`.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou incorrecte."""
    expected_key = get_settings().api_key

    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )

    if not secrets.compare_digest(x_api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(
    prefix="/v1",
    dependencies=[Depends(require_api_key)],
)
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

Toujours **2 tests échouent** (`2 failed, 16 passed`) : `test_missing_key_is_rejected` et `test_wrong_key_is_rejected` reçoivent encore 200. La fonction `require_api_key()` existe, mais rien ne l'appelle : tant qu'elle n'est pas déclarée comme dépendance du routeur, FastAPI ne l'exécute pas avant les routes `/v1`.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```text
18 passed, 1 warning in 1.23s
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability":0.0027,"alert":false,"threshold":0.3,"model_version":"..."}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | `{"detail":[{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150","input":500,"ctx":{"le":150.0}}]}` |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

La dépendance d'authentification intervient avant l'exécution de la route. Sans clé valide, l'API renvoie 401. Avec une clé valide, la requête atteint la validation Pydantic ; la température 500 °C dépasse le maximum autorisé de 150 °C et provoque un code 422.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

On obtient **500**, avec `{"detail":"Clé API non configurée sur le serveur"}`. Sans `--env-file .env`, la variable `MAINTAI_API_KEY` n'est pas chargée : le serveur n'a aucune clé à laquelle comparer celle du client. Ce n'est pas le client qui se trompe (401), c'est le serveur qui est mal configuré, d'où une erreur 5xx.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
document.getElementById("go").addEventListener("click", async () => {
  const reading = Object.fromEntries(
    FEATURES.map(f => [f, Number(document.getElementById(f).value)])
  );

  const url = document.getElementById("url").value.trim().replace(/\/+$/, "");
  const cle = document.getElementById("key").value.trim();

  try {
    const resp = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": cle
      },
      body: JSON.stringify(reading)
    });

    const data = await resp.json();
    if (!resp.ok) {
      show("err", `Erreur HTTP ${resp.status} : ${JSON.stringify(data.detail)}`);
      return;
    }

    const probabilite = (data.failure_probability * 100).toFixed(2);
    if (data.alert) {
      show("alert", `ALERTE : risque de panne de ${probabilite} %`);
    } else {
      show("ok", `Machine OK : risque de panne de ${probabilite} %`);
    }
  } catch (e) {
    show("err", `Impossible de contacter l'API : ${e.message}`);
  }
});
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | `Machine OK : risque de panne de 0.27 %` |
| 500 °C, bonne clé | `Erreur HTTP 422 : [{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150",...}]` |
| relevé normal, fausse clé | `Erreur HTTP 401 : "Clé API absente ou invalide"` |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

La page affiche `Impossible de contacter l'API : Failed to fetch`. La console indique :

```text
Access to fetch at 'http://localhost:8000/v1/predict' from origin 'http://localhost:5501'
has been blocked by CORS policy: Response to preflight request doesn't pass access control
check: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

La requête préalable `OPTIONS` envoyée par le navigateur reçoit `400 Bad Request` (« Disallowed CORS origin »), sans en-tête `Access-Control-Allow-Origin`, parce que `http://localhost:5501` ne figure pas dans `MAINTAI_CORS_ORIGINS`. Depuis le port 5500, la même requête préalable reçoit `200` avec `access-control-allow-origin: http://localhost:5500`. Le navigateur n'envoie donc jamais le `POST`.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

CORS est une politique de sécurité appliquée par le navigateur. `curl` n'applique pas cette restriction et peut lire une réponse du serveur. Il reste cependant soumis à la vérification de la clé API pour les routes protégées.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

Sans `headers=HEADERS`, on obtient `4 failed, 1 passed`. Les quatre cas sur `/v1/predict` reçoivent **401** au lieu du 422 attendu : la clé est vérifiée avant la validation des données. Le cas de la mauvaise route `/v1/predcit` passe quand même avec **404**, car aucune route ne correspond à cette URL : la dépendance du routeur n'est jamais exécutée.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```text
================= 23 passed, 1 warning in 0.90s =================
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?

   **401** : authentification absente ou incorrecte. **422** : données de la requête invalides au regard du schéma. **403** : l'accès à la ressource est interdit, même si le client peut être identifié.

2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?

   Une clé publiée dans Git peut être récupérée et reste dans l'historique des commits. `.env` contient la véritable configuration locale, notamment le secret, et ne doit pas être commité. `.env.example` donne des valeurs fictives et la liste des variables attendues ; il peut être commité.

3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?

   Une clé dans l'URL risque de se retrouver dans les historiques de navigation, les journaux et les systèmes de suivi. L'en-tête `X-API-Key` sépare le secret des paramètres de l'URL. En réseau, HTTPS reste nécessaire.

4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?

   Cette fonction réduit les variations de durée liées au contenu des secrets comparés et limite ainsi les risques d'attaques temporelles.

5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?

   Une origine combine protocole, hôte et port. Les deux adresses ont des **ports différents** (5500 et 8000) et sont donc deux origines différentes.

## 8. Le rendu Git

- Lien de la pull request : https://github.com/unknownxowker/Models_AI/pull/4
- Le tag `tp2` existe sur GitHub : OUI
- `git status` avant le commit : le fichier `.env` apparaissait-il ? NON 
- Qui a relu la pull request, et quel commentaire a-t-il laissé ? **[à compléter après relecture]**

## 9. Ce qui reste flou

Cette séance m'a permis de mieux comprendre comment sécuriser une API avec une clé, valider les données envoyées par un client web et automatiser les tests. La principale difficulté technique a été la version initiale de Python 3.9.6, incompatible avec `numpy==2.4.4` ; l'installation de Python 3.12.16 a permis de poursuivre le TP. Je souhaite encore approfondir la distinction entre l'authentification et CORS, ainsi que la gestion des secrets dans un environnement de production.