# ADR 003 — Sécurisation de l'API MaintAI

## Contexte

Dans le cadre du TP2, notre API MaintAI permet de prédire les risques de panne d'une machine à partir de quatre mesures de capteurs.

Nous devons protéger les routes de prédiction contre les accès non autorisés, sans bloquer la route publique `/health`. Nous devons également contrôler les origines web autorisées à appeler notre API.

## Décision 1 — Authentification par clé API

Nous avons choisi de transmettre la clé API dans l'en-tête HTTP `X-API-Key`.

La fonction `require_api_key()` récupère la clé reçue, puis la compare à celle configurée sur le serveur avec `secrets.compare_digest()`.

Les réponses prévues sont :

- **200** : clé correcte et requête valide.
- **401** : clé absente ou incorrecte.
- **500** : aucune clé configurée sur le serveur.

Nous avons utilisé `Depends(require_api_key)` dans le routeur `/v1` pour appliquer automatiquement cette vérification aux routes protégées.

La route `/health` reste accessible sans authentification.

### Alternatives écartées

Nous n'avons pas choisi de transmettre la clé dans l'URL, car elle pourrait apparaître dans l'historique du navigateur ou les journaux du serveur.

Nous avons également écarté sa transmission dans le corps JSON, car cela mélangerait les données métier et les informations d'authentification.

## Décision 2 — Gestion des secrets

La clé API est définie dans un fichier `.env`, chargé au démarrage du serveur.

Ce fichier est exclu de Git grâce au `.gitignore`.

Le fichier `.env.example` peut être partagé pour indiquer les paramètres nécessaires sans dévoiler la véritable clé.

Stocker directement la clé dans le code exposerait le secret dans le dépôt Git et son historique.

## Décision 3 — Politique CORS

Nous avons choisi d'autoriser explicitement `http://localhost:5500` comme origine du client web.

Les origines autorisées sont configurées dans les paramètres de MaintAI, à partir des variables d'environnement, puis transmises au middleware CORS de FastAPI.

Nous n'utilisons pas `*`, car cela autoriserait les réponses CORS à être accessibles depuis toutes les origines, contrairement à notre objectif de restriction.

Une page provenant de `http://localhost:5501` ne doit donc pas pouvoir lire la réponse de l'API depuis le navigateur.

CORS constitue une protection appliquée par le navigateur et ne remplace pas l'authentification. Un programme comme curl peut envoyer une requête sans être soumis à cette restriction.

## Validation

Les vérifications réalisées ont permis de confirmer :

- Les requêtes sans clé valide sont refusées avec HTTP 401.
- Les requêtes authentifiées et valides obtiennent HTTP 200.
- Les entrées invalides sont refusées avec HTTP 422.
- La route `/health` reste publique.
- Les tests automatisés sont réussis : **23 passed**.
- L'analyse statique de Ruff retourne `All checks passed!`.
- Le contrôle de formatage Ruff indique 19 fichiers conformes.

## Conséquences

Cette solution est simple à mettre en place et adaptée au périmètre pédagogique de MaintAI.

Pour une utilisation en production, il faudrait également prévoir HTTPS, une gestion centralisée des secrets, la rotation des clés et éventuellement une authentification plus avancée.