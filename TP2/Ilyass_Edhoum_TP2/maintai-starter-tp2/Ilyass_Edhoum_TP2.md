# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :*G1* … · **Membres :*ILYASS EDHOUM* … · **Date :*4/11/2026* …

> Les réponses techniques ci-dessous ont été vérifiées sur le TP1/TP2 local. Le
> groupe doit encore renseigner les informations propres à la remise GitHub.

## 1. Activité 1 : casser son API (dans TP1)

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---:|---:|
| 1 | Champ manquant | 422 | 422 |
| 2 | Température absurde (500 °C) | 422 | 422 |
| 3 | Texte au lieu d'un nombre | 422 | 422 |
| 4 | Champ supplémentaire | 422 | 422 |
| 5 | Route `/v1/predicte` inexistante | 404 | 404 |

La suite TP1, avec les cinq cas paramétrés, donne :

```text
19 passed, 1 warning in 0.65s
```

`@pytest.mark.parametrize` réutilise la même fonction de test avec plusieurs
jeux de paramètres. Ici, pytest compte cinq cas pour la fonction, un par requête.

## 2. Ruff

Résultat de la vérification de disponibilité dans l'environnement TP1 :

```text
All checks passed!
```

Ruff fait une analyse statique du code et détecte notamment des problèmes de
style et certaines erreurs probables. `python3 -m pytest` exécute les tests et vérifie le comportement. Une fois Ruff
installé, `ruff check .` a terminé avec `All checks passed!`.

## 3. Mise en place du TP2

Résultat initial, avant de brancher l'authentification :

```text
2 failed, 16 passed
```

Les deux tests en échec sont `test_missing_key_is_rejected` et
`test_wrong_key_is_rejected`. L'API répond 200 alors que chacun attend 401.

## 4. La clé API (sprint 1)

Corps de `require_api_key()` :

```python
expected_api_key = get_settings().api_key
if expected_api_key is None:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Clé API non configurée sur le serveur.",
    )
if x_api_key is None or not secrets.compare_digest(x_api_key, expected_api_key):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Clé API absente ou invalide.",
    )
```

Router protégé :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Écrire seulement `security.py` ne change pas les requêtes : les deux tests
d'authentification échouent encore tant que le router n'appelle pas cette
dépendance. Une fois le router protégé :

```text
18 passed, 1 warning in 0.58s
```

L'API sécurisée a été démarrée sur le port 8001 (le port 8000 était déjà occupé).
Résultats des requêtes :

| Requête | Code | Réponse |
|---|---:|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API absente ou invalide."}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API absente ou invalide."}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-11-04T16:16:07Z"}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API absente ou invalide."}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | Erreur Pydantic : température supérieure à la limite 150 °C |

La vérification de la clé intervient avant la prédiction : sans clé, la requête
est arrêtée avec 401. Avec une clé correcte, le contenu est validé, et 500 °C
est rejeté avec 422.

Sans `--env-file .env`, le serveur n'a pas de clé configurée et une requête
authentifiée reçoit 500 : c'est une erreur de configuration du serveur, et non
une erreur de clé client.

## 5. La page web (sprint 2)

La page envoie le relevé en JSON et la clé dans l'en-tête :

```javascript
const response = await fetch(`${apiUrl}/v1/predict`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": apiKey,
  },
  body: JSON.stringify(reading),
});
const data = await response.json();
if (!response.ok) {
  show("err", `Erreur HTTP ${response.status}`);
} else {
  show(
    data.alert ? "alert" : "ok",
    `Risque estimé : ${new Intl.NumberFormat("fr-FR", {
      style: "percent",
      maximumFractionDigits: 1,
    }).format(data.failure_probability)}`,
  );
}
```

Observations dans le navigateur, page servie sur le port 5500 :

| Essai | Affichage |
|---|---|
| Relevé normal, bonne clé | `Alerte : risque estimé de 94,8 % (seuil : 30 %).` |
| 500 °C, bonne clé | `Erreur HTTP 422 : body.temperature_c : Input should be less than or equal to 150` |
| Relevé normal, fausse clé | `Erreur HTTP 401 : Clé API absente ou invalide.` |

Sur le port 5501, la page affiche `API inaccessible ou requête bloquée par
CORS : Failed to fetch`. La console explique que la requête preflight ne reçoit
pas d'en-tête `Access-Control-Allow-Origin`. L'origine permise sur le port 5500
a reçu 200 à la preflight; celle du port 5501 a reçu 400 sans cet en-tête.

`curl` n'applique pas la politique CORS des navigateurs. La restriction est
imposée par le navigateur aux requêtes initiées par une page web; un client HTTP
en ligne de commande peut joindre directement l'API.

## 6. Tests de l'activité 1 dans TP2

Sans `headers=HEADERS`, les quatre requêtes invalides vers `/v1/predict`
reçoivent 401 et échouent par rapport au 422 attendu. La faute de frappe de route
reste en 404 : aucune route correspondante n'est trouvée, donc sa dépendance ne
s'exécute pas.

Avec l'en-tête d'authentification :

```text
23 passed, 1 warning
```

## 7. Questions de compréhension

1. **401 vs 422, et 401 vs 403 ?**  
   401 indique une authentification absente ou invalide; 422 indique que les
données ne respectent pas le schéma; 403 signifie que le client authentifié
n'est pas autorisé à effectuer l'action.
2. **Pourquoi ne pas mettre la clé dans le code ou Git ? Que contiennent les
   fichiers `.env` et `.env.example` ?**  
   Une clé commitée serait accessible aux personnes ayant accès au dépôt.
   `.env` contient la clé locale et est ignoré par Git. `.env.example` décrit
   les variables à configurer et peut être commité, jamais avec une vraie clé.
3. **Pourquoi mettre la clé dans un en-tête plutôt que dans l'URL ?**  
   Les URL peuvent être enregistrées dans l'historique, les journaux ou les
   outils d'analyse; l'en-tête évite d'exposer la clé dans ces endroits courants.
4. **Que fait `secrets.compare_digest` de plus que `==` ?**  
   Il effectue une comparaison conçue pour limiter les fuites d'information par
   le temps d'exécution sur le préfixe correct de la clé.
5. **Qu'est-ce qu'une origine ? Les ports 5500 et 8000 sont-ils la même origine ?**  
   Une origine est le triplet schéma, hôte et port. Non : les ports diffèrent.

## 8. Rendu Git

- Pull request : à créer par le groupe après avoir poussé la branche `tp2`.
- Tag `tp2` : à créer après la fusion de la pull request.
- `.env` avant commit : ignoré par la règle `.env` de `.gitignore`.
- Relecture et commentaire : à renseigner par le groupe après revue.
