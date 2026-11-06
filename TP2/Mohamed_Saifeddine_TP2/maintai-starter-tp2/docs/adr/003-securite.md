# ADR 003 : clé API et origines CORS autorisées

Date : 06/11/2026 · Auteur : Mohamed Saifeddine

## Contexte

Les routes `/v1` de MaintAI ne doivent répondre qu'aux clients qui connaissent la clé API. Le client web est servi sur le port 5500 et doit pouvoir appeler l'API, sans autoriser automatiquement toutes les autres origines.

## Options étudiées

### Transmission de la clé

1. En-tête `X-API-Key` : la clé ne se retrouve pas dans l'URL et le même contrat fonctionne pour le navigateur, `curl` et les tests.
2. Paramètre d'URL : simple à envoyer, mais la clé peut être conservée dans l'historique du navigateur, les journaux du serveur et les outils de suivi.
3. Corps JSON : évite l'URL, mais mélange l'authentification avec les données métier et ne convient pas à toutes les méthodes HTTP.

### Configuration CORS

1. Liste d'origines dans l'environnement : seules les pages explicitement autorisées peuvent lire les réponses de l'API.
2. Origine `*` : plus facile à configurer, mais autorise n'importe quel site à appeler l'API depuis un navigateur.

## Décision

La clé est transmise dans l'en-tête `X-API-Key` et comparée avec `secrets.compare_digest`. Elle est chargée depuis la variable `MAINTAI_API_KEY` et n'est jamais écrite dans le code.

Les origines CORS sont une liste définie par `MAINTAI_CORS_ORIGINS`. Pour le développement, seuls `http://localhost:5500` et `http://127.0.0.1:5500` sont autorisés. Le port 5501 reste volontairement refusé.

## Conséquences

Les clients doivent toujours ajouter l'en-tête `X-API-Key`. Une modification de la clé ou de la liste CORS nécessite de relancer l'API, car les variables sont lues au démarrage. Cette solution demande un peu de configuration, mais évite d'exposer la clé dans les URL et limite l'accès depuis les pages web inconnues.
