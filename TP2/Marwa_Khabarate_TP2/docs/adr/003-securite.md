# ADR 003 : Clé API et origines CORS

Date : 04/11/2026 · Auteurs : à compléter

## Contexte

L'API MaintAI doit réserver les routes de prédiction aux clients qui possèdent une clé, tout en permettant au client web local de l'appeler. La clé ne doit pas être exposée dans le code source, l'historique du navigateur ou Git.

## Options étudiées

1. **Transmettre la clé dans l'en-tête `X-API-Key`** : l'en-tête ne fait pas partie de l'URL copiée ou enregistrée dans l'historique. Il faut néanmoins utiliser HTTPS en production et garder la clé secrète côté client.
2. **Transmettre la clé dans l'URL ou le corps JSON** : une clé dans l'URL risque d'être conservée dans les journaux, l'historique et les liens partagés. Une clé dans le corps imposerait un format de requête différent aux clients et ne la rendrait pas plus sûre qu'un en-tête.
3. **Autoriser toutes les origines avec `*`** : cela simplifierait le développement, mais permettrait à n'importe quelle origine d'effectuer des appels navigateur vers l'API.
4. **Configurer une liste d'origines autorisées** : la liste est explicite et peut être adaptée sans modifier le code, mais chaque nouvelle origine doit être ajoutée à la configuration et nécessite un redémarrage de l'API.

## Décision

Les clients transmettent la clé dans l'en-tête `X-API-Key`. Le serveur lit la clé attendue depuis `MAINTAI_API_KEY`; le fichier local `.env` est ignoré par Git et `.env.example` documente la configuration sans contenir de secret utilisable.

CORS autorise uniquement les origines configurées dans `MAINTAI_CORS_ORIGINS`, par défaut `http://localhost:5500` et `http://127.0.0.1:5500`. La configuration ne doit pas utiliser `*` pour cette application.

## Conséquences

Les routes `/v1` valident la clé avant de traiter la prédiction, tandis que `/health` reste publique. Un navigateur exécutant le client depuis une origine non listée ne peut pas lire la réponse; les outils tels que `curl` ne sont pas soumis à la politique CORS du navigateur. Les nouvelles origines doivent être inscrites dans l'environnement avant de redémarrer l'API. En production, la clé doit être distribuée et stockée de façon sécurisée, et les communications doivent utiliser HTTPS.
