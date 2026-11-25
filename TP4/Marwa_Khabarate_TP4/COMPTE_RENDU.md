# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** G1  ·  **Membre :** Marwa Khabarate  ·  **Date :** 12/11/2026

> Les commandes ont été exécutées sous Windows avec Python 3.14.3 dans le `.venv` du projet.

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
2 failed, 25 passed, 1 warning in 74.96s
```

Les deux tests qui échouent sont `test_installed_version_matches_the_code` et `test_command_is_declared`, dans `tests/test_package.py`. MaintAI n'est pas encore installé comme distribution : ses métadonnées et le point d'entrée `maintai-predict` n'existent donc pas encore.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "numpy>=2.4",
    "pandas>=3.0",
    "scikit-learn>=1.8",
    "joblib>=1.5",
    "httpx>=0.28",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

`pytest` est un outil de développement et `fastapi` est dans le groupe optionnel `api` ; ils ne sont pas nécessaires aux dépendances de base du package. `streamlit` est dans le groupe optionnel `ui`.

Quatre premières lignes de `pip show maintai` :

```
Name: maintai
Version: 0.2.0
Summary: Prédiction de panne à partir de relevés de capteurs
Home-page:
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
27 passed, 1 warning in 28.01s
```

Depuis un autre dossier, `maintai-predict 72 6 85 15000` affiche `Probabilité de panne : 95 % (ALERTE)`. `python -c "import maintai; print(maintai.__file__)"` pointe vers le dossier `maintai` du projet : l'installation éditable référence le code source du projet.

Avec `pip install -e .`, une modification de `maintai/cli.py` est visible sans réinstallation : la commande utilise le code source, et non une copie statique.

La commande `streamlit run ui/app.py` lance également l'interface depuis la racine du projet ; son endpoint de santé a répondu `ok`.

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` :

```
maintai-0.2.0-py3-none-any.whl  11619 octets
maintai-0.2.0.tar.gz            12265 octets
```

Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`) :

```
maintai/__init__.py
maintai/cli.py
maintai/client.py
maintai/config.py
maintai/data.py
maintai/dataset.py
maintai/predict.py
maintai/train.py
maintai/api/__init__.py
maintai/api/main.py
maintai/api/schemas.py
maintai/api/security.py
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL
maintai-0.2.0.dist-info/entry_points.txt
maintai-0.2.0.dist-info/top_level.txt
maintai-0.2.0.dist-info/RECORD
```

Le wheel contient le package `maintai`, mais pas le modèle, les tests ni `ui/`. Seul le package `maintai*` est configuré pour être distribué.

Essais dans un environnement neuf avec le wheel :

| Étape | Ce qui s'affiche |
|---|---|
| Sans `MAINTAI_MODELS_DIR` | `Modèle introuvable` sous `.venv\Lib\site-packages\models\model.joblib`, puis un conseil pour entraîner le modèle ou renseigner la variable d'environnement. |
| Avec `MAINTAI_MODELS_DIR` vers le dossier `models` du projet | Prédiction à 95 % (`ALERTE`). Des `InconsistentVersionWarning` signalent que le modèle a été entraîné avec scikit-learn 1.8.0 alors que l'environnement neuf a installé 1.9.1. |
| Après `pip install scikit-learn==1.8.0` | Prédiction à 95 % (`ALERTE`), sans avertissement de version. |

La ligne `"sklearn_version": "1.8.0"` de `models/model_info.json` donne la version utilisée pour entraîner le modèle. La différence avec scikit-learn 1.9.1 explique les avertissements.

## 4. Questions de compréhension

1. `requirements.txt` fige les versions exactes de l'environnement du projet, notamment pour relire le modèle. Les `dependencies` de `pyproject.toml` déclarent les dépendances minimales nécessaires à l'installation du package.
2. `pip install -e .` installe le package en mode éditable et pointe vers le code source du projet. `pip install dist\maintai-0.2.0-py3-none-any.whl` installe une distribution construite, indépendante du dossier source.
3. `[project.scripts]` associe une commande à une fonction Python. pip crée l'exécutable `maintai-predict.exe` dans le dossier `Scripts` de l'environnement Python où le package est installé.

## 5. Le rendu Git

- Lien de la pull request : non créé ; ce dossier n'est pas un dépôt Git.
- Le tag `tp4` existe sur GitHub : non vérifiable depuis ce dossier sans dépôt ni remote Git.
- `dist/`, `build/` et `maintai.egg-info/` sont exclus par `.gitignore`. Aucun `git status` n'est disponible ici, car le dossier ne contient pas de dépôt Git.

## 6. Ce qui reste flou

Aucun point technique du packaging n'est resté non résolu. Il reste à créer la pull request ainsi que le tag depuis le dépôt Git.
