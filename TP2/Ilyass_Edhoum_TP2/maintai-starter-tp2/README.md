# MaintAI

Application de prédiction de panne à partir de relevés de capteurs, construite pas à pas pendant le cours « Développement et déploiement d'applications intelligentes ».

Les données fournies sont synthétiques : `python3 -m maintai.dataset` les génère. Elles se remplacent par des données réelles qui gardent les mêmes colonnes.

## Installation

```bash
python3 -m venv .venv
# Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Linux / macOS :
source .venv/bin/activate

python3 -m pip install -r requirements.txt
```

## Données et entraînement

```bash
python3 -m maintai.dataset     # écrit data/sensors.csv
python3 -m maintai.train       # écrit models/model.joblib, model_info.json, metrics.json
python3 -m pytest              # lance tous les tests
```

## Lancer l'API

```bash
uvicorn maintai.api.main:app --reload
```

Documentation interactive : http://localhost:8001/docs

## Clé API et client web

```bash
cp .env.example .env            # puis changez MAINTAI_API_KEY
uvicorn maintai.api.main:app --reload --port 8001 --env-file .env
python3 -m http.server 5500 -d web  # dans un second terminal
```

Ouvrez http://localhost:5500 et saisissez la clé définie dans `.env`.
`/health` reste public; les routes sous `/v1` exigent l'en-tête `X-API-Key`.
Seules les origines définies par `MAINTAI_CORS_ORIGINS` sont autorisées à appeler
l'API depuis un navigateur. Avec la configuration d'exemple, le port 5501 n'est
pas autorisé.

## Structure

```
maintai/            code du projet
  config.py         chemins et paramètres
  dataset.py        génération des données synthétiques
  data.py           chargement et découpage
  train.py          entraînement, évaluation, sauvegarde
  predict.py        chargement du modèle et prédiction
  api/              API FastAPI (TP1, TP2)
  client.py         client HTTP de l'API (TP3)
web/                client web HTML/JS (TP2)
ui/                 interface Streamlit (TP3)
tests/              tests pytest
docs/adr/           décisions d'architecture
```
