# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI
**Nom:** Sara Hajdaoui
**Groupe :** 4 · **Membres :** Mohamed Saifeddine / Marwa Khabarate/ Sara hajdaoui / Ilyas edhoum  · **Date :** 04/11/2026


---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1 | Champ `load_pct` manquant | 422 | 422 (test automatisé TP2) |
| 2 | Valeur absurde : `temperature_c = 500` | 422 | 422 (test automatisé TP2) |
| 3 | Texte `"chaud"` au lieu d'un nombre | 422 | 422 (test automatisé TP2) |
| 4 | Champ supplémentaire `capteur_inconnu` | 422 | 422 (test automatisé TP2) |
| 5 | Mauvaise route `/v1/predcit` | 404 | 404 (test automatisé TP2) |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

Les cinq prévisions correspondent aux résultats des tests automatisés exécutés **dans le TP2**, avec une clé valide. Les quatre premières erreurs relèvent de la validation du corps JSON par Pydantic ; la cinquième correspond à une route inexistante. **À vérifier :** les résultats obtenus dans `/docs` et dans le dossier séparé `TP/TP1` n'ont pas été conservés dans les journaux.

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```text
================= 5 passed, 1 warning in 0.79s ==================
```

**Précision :** cette sortie provient de la commande `python -m pytest tests/test_casser.py -v` exécutée dans le TP2, et non d'une exécution attestée dans TP1.

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

`@pytest.mark.parametrize` permet d'exécuter une même fonction avec plusieurs ensembles de données. Ici, la fonction `test_requete_refusee` est exécutée cinq fois, une fois pour chaque cas de `CAS_REFUSES`. Pytest comptabilise donc **cinq tests**.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```text
All checks passed!
```

**Précision :** cette sortie a été obtenue dans le TP2. Un contrôle Ruff distinct dans `TP/TP1` reste **à vérifier**. Le terminal du TP2 confirme également :

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

**Deux tests sont censés continuer à échouer** : sans la dépendance `Depends(require_api_key)` ajoutée au routeur, FastAPI n'appelle pas la fonction de contrôle pour les requêtes `/v1`. Il s'agit du résultat attendu d'après le fonctionnement du code ; **l'exécution intermédiaire n'est pas documentée** dans les journaux fournis.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```text
[Sortie distincte à vérifier : la suite finale avec cinq tests supplémentaires donne 23 passed.]
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 (test automatisé) | `{"status":"ok","model_loaded":true}` si le modèle est chargé ; corps HTTP exact à vérifier |
| `POST /v1/predict`, relevé normal, sans clé | 401 (journal Uvicorn) | `{"detail":"Clé API absente ou invalide"}` selon le code |
| `POST /v1/predict`, relevé normal, fausse clé | 401 (tests et essais) | `{"detail":"Clé API absente ou invalide"}` selon le code |
| `POST /v1/predict`, relevé normal, bonne clé | 200 (journal Uvicorn) | Objet contenant `failure_probability` et `alert` ; valeurs exactes non relevées |
| `POST /v1/predict`, 500 °C, sans clé | **À vérifier** (401 attendu) | `{"detail":"Clé API absente ou invalide"}` attendu |
| `POST /v1/predict`, 500 °C, bonne clé | 422 (journal Uvicorn et tests) | Détail de validation Pydantic ; corps exact non relevé |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

La dépendance d'authentification intervient avant l'exécution de la route. Sans clé valide, l'API renvoie 401. Avec une clé valide, la requête atteint la validation Pydantic ; la température 500 °C dépasse le maximum autorisé de 150 °C et provoque un code 422.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

**À vérifier expérimentalement.** Si aucune variable `MAINTAI_API_KEY` n'est déjà définie dans l'environnement, le serveur renvoie **500**, car aucune clé attendue n'est configurée. C'est une erreur de configuration du serveur et non une erreur d'identification du client (401).

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
| relevé normal, bonne clé | Probabilité en % et message `Machine OK` ou `ALERTE` selon la prédiction (valeur chiffrée exacte non relevée) |
| 500 °C, bonne clé | `Erreur HTTP 422` avec le détail de validation |
| relevé normal, fausse clé | `Erreur HTTP 401 : "Clé API absente ou invalide"` |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

Le second terminal confirme que la page a été servie sur le port 5501. Les tests automatisés confirment que l'origine 5500 est autorisée et qu'une origine inconnue est refusée. **Le texte exact de la console du navigateur n'a pas été conservé.** Lorsque la politique CORS bloque l'appel depuis 5501, la page affiche un message du type `Impossible de contacter l'API : Failed to fetch` et la console signale le blocage CORS ou l'absence de `Access-Control-Allow-Origin`.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

CORS est une politique de sécurité appliquée par le navigateur. `curl` n'applique pas cette restriction et peut lire une réponse du serveur. Il reste cependant soumis à la vérification de la clé API pour les routes protégées.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

**Résultat attendu, à vérifier par exécution :** quatre tests sur `/v1/predict` échoueraient, car l'API renverrait **401** au lieu du **422** attendu. Le test de la route inexistante `/v1/predcit` devrait continuer à réussir avec **404**, car aucune route ne correspond à cette URL et la dépendance du routeur n'est pas exécutée.

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

- Lien de la pull request : **[à compléter après création]**
- Le tag `tp2` existe sur GitHub : **à vérifier**
- `git status` avant le commit : le fichier `.env` apparaissait-il ? **à vérifier** ; il ne doit pas être suivi par Git
- Qui a relu la pull request, et quel commentaire a-t-il laissé ? **[à compléter après relecture]**

## 9. Ce qui reste flou

Cette séance m'a permis de mieux comprendre comment sécuriser une API avec une clé, valider les données envoyées par un client web et automatiser les tests. La principale difficulté technique a été la version initiale de Python 3.9.6, incompatible avec `numpy==2.4.4` ; l'installation de Python 3.12.16 a permis de poursuivre le TP. Je souhaite encore approfondir la distinction entre l'authentification et CORS, ainsi que la gestion des secrets dans un environnement de production. Avant le rendu, il reste à vérifier les manipulations non consignées et les informations de la pull request GitHub.
