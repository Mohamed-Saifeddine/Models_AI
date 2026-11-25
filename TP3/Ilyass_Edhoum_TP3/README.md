# MaintAI

Application de prédiction de panne à partir de relevés de capteurs, construite pas à pas pendant le cours « Développement et déploiement d'applications intelligentes ».

Les données fournies sont synthétiques : `python -m maintai.dataset` les génère. Elles se remplacent par des données réelles qui gardent les mêmes colonnes.

## Installation

Toutes les commandes ci-dessous sont à lancer depuis `maintai-starter-tp3`, le dossier qui contient `requirements.txt`. Depuis le dossier parent `TP3`, placez-vous d'abord dans le projet :

```powershell
cd .\maintai-starter-tp3
```

```bash
python -m venv .venv
# Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Linux / macOS :
source .venv/bin/activate

python -m pip install -r requirements.txt
```

## Données et entraînement

```bash
python -m maintai.dataset      # écrit data/sensors.csv
python -m maintai.train        # écrit models/model.joblib, model_info.json, metrics.json
pytest                          # lance tous les tests
```

## Lancer l'API

```bash
uvicorn maintai.api.main:app --reload
```

Documentation interactive : http://localhost:8000/docs

## Clé API et client web

```bash
cp .env.example .env            # puis changez MAINTAI_API_KEY
uvicorn maintai.api.main:app --reload --env-file .env
python -m http.server 5500 -d web   # dans un second terminal
```

Ouvrez http://localhost:5500 et saisissez la clé définie dans `.env`.

## Interface Streamlit (TP3)

```bash
uvicorn maintai.api.main:app --reload --env-file .env   # terminal 1
python -m streamlit run ui/app.py                        # terminal 2
```

Ouvrez http://localhost:8501, saisissez l'URL de l'API et la clé dans la barre latérale.
Onglet « Données » : le jeu de données ; onglet « Prédiction » : un relevé envoyé à l'API.

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
