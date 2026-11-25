# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** …  ·  **Membres :** Sara Hajdaoui  ·  **Date :** 25/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
5 failed, 27 passed
```

Quels tests échouent, et pourquoi ?

Les 5 tests de `tests/test_tracking.py` (`test_training_creates_a_run`, `test_run_records_metrics`, `test_run_records_data_version`, `test_run_stores_the_model`, `test_options_change_the_run`). `log_run` n'était pas encore écrite : elle renvoyait `""` sans rien enregistrer, donc MLflow ne contenait aucun run (ni paramètres, ni métriques, ni `data_md5`, ni modèle).

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avec l'environnement du TP4, `maintai` pointait vers le dossier `TP4` (installation éditable du TP4). Après `pip install -e .` dans le dossier du TP5, il pointe vers le code du TP5 (version 0.3.0) ; c'est ce que vérifie `test_installed_version_matches_the_code`. (Sur Mac, j'ai créé un nouvel environnement Python 3.12, car MLflow 3.18 ne fonctionne pas avec le Python 3.9 du système : avant `pip install -e .`, `maintai` n'y était donc pas installé du tout.)

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
    # Toutes les runs de MaintAI sont rangées sous la même expérience
    mlflow.set_experiment(EXPERIMENT)
    # Tout ce qui est enregistré dans le bloc with appartient à ce run
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        # Version des données : la même empreinte md5 que celle écrite par DVC dans le fichier .dvc
        mlflow.log_param("data_md5", file_md5(data_path))
        mlflow.log_metrics(metrics)
        # Le modèle, avec les versions exactes des bibliothèques (requirements.txt du run)
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES,
        )
    return run.info.run_id
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
32 passed, 4 warnings in 23.33s
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.750 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train --threshold 0.5` (mon essai) | 0.574 | 0.736 | 0.914 |

Tous ces runs ont été entraînés sur les mêmes données (v1, 5000 lignes, `data_md5` = `b7fec4274774842dc1f48202c6013490`) ; le baseline (toujours « pas de panne ») a un recall de 0.

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

La régression logistique avec `--threshold 0.2` (run `39ed092134a84869952ce2689e9b3c8c`). Elle a le meilleur recall (0.838) : elle manque le moins de pannes, ce qui est la priorité. En échange, la precision baisse (0.543) : il y a plus de fausses alertes, ce qui coûte moins cher qu'une panne manquée. L'accuracy baisse un peu (0.882), mais elle n'est pas le bon critère ici, car les pannes sont rares (le baseline atteint déjà 0.864 sans détecter aucune panne). La forêt aléatoire n'est pas meilleure : au même seuil (0.3), elle a un recall (0.728) et une precision (0.562) plus faibles que la régression logistique (0.750 et 0.622). Mon essai à 0.5 confirme le compromis dans l'autre sens : meilleure precision (0.736), mais recall de 0.574, donc trop de pannes manquées.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

`scikit-learn==1.8.0` (avec aussi `mlflow==3.18.0`, `numpy==2.4.4`, `pandas==3.0.2`, `skops==0.16.0`…). Au TP4, le modèle `.joblib` était livré sans les versions des bibliothèques : le recharger avec une autre version de scikit-learn pouvait donner un avertissement, une erreur ou des prédictions différentes. Maintenant, chaque modèle est livré avec la liste exacte des versions nécessaires pour le recharger à l'identique.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

Dans le dossier `TP5` : `mlflow.db` (base SQLite avec les runs, paramètres et métriques) et `mlruns/` (les artefacts, dont les modèles et leur `requirements.txt`). Ils ne vont pas dans Git (ils sont dans le `.gitignore`) : ce sont des fichiers générés, binaires et qui grossissent à chaque entraînement, et propres à chaque poste. Pour partager les runs dans une équipe, on utiliserait un serveur MLflow commun plutôt que Git.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
outs:
- md5: b7fec4274774842dc1f48202c6013490
  size: 121814
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

Les deux valeurs sont identiques (`b7fec4274774842dc1f48202c6013490`) : `file_md5` calcule la même empreinte que DVC. Le `data_md5` d'un run désigne donc exactement une version de données sous DVC : à partir d'un run MLflow, on retrouve le commit Git dont le reçu `.dvc` porte ce md5, puis on récupère le fichier avec `dvc checkout` (ou `dvc pull`).

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Le fichier de données peut être gros, et Git garderait chaque version pour toujours dans l'historique du dépôt. DVC le range dans son cache et dans le stockage, et Git ne garde que le reçu `.dvc` (4 lignes : md5, taille, chemin), petit et lisible. Le reçu suffit pour savoir quelle version des données va avec quel commit du code. `data/*.csv` est d'ailleurs dans le `.gitignore`.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data/sensors.csv.dvc:
	changed outs:
		modified:           data/sensors.csv
```

DVC détecte que le fichier ne correspond plus au reçu : son md5 a changé depuis le dernier `dvc add`.

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | `13c8d9f Données v1` | `b7fec427` | 5000 |
| v2 | `ebd5c73 Données v2` | `31ef5ebb` | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après `git checkout 13c8d9f -- data/sensors.csv.dvc` puis `dvc checkout` (`M data/sensors.csv`), le fichier contient **5000** lignes : DVC a remis la v1 depuis son cache. `git status` montre alors le `.dvc` modifié (c'est l'ancien reçu) : je ne l'ai pas commité. Retour à la v2 avec `git checkout HEAD -- data/sensors.csv.dvc` puis `dvc checkout` : **8000** lignes.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

```
A       data/sensors.csv
1 file fetched and 1 file added
```

DVC lit le reçu `data/sensors.csv.dvc`, télécharge la version correspondante depuis le stockage (`~/dvc-stockage`) dans le cache, puis remet `data/sensors.csv` (8000 lignes, la v2). C'est ce que ferait un coéquipier qui clone le dépôt : Git lui donne le reçu, `dvc pull` lui donne les données.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

Mêmes réglages pour les deux runs : `logreg`, `C = 1.0`, seuil 0.3.

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 (`f2e3b740…`) | `b7fec427` | 4000 | 0.750 | 0.622 |
| v2 (`0b39f2e8…`) | `31ef5ebb` | 6400 | 0.741 | 0.650 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non. Le run v2 a une meilleure precision (0.650 contre 0.622) mais un recall un peu plus faible (0.741 contre 0.750), et pour MaintAI c'est le recall qui compte. Surtout, les deux runs ne sont pas évalués sur le même jeu de test : la v2 a d'autres lignes (8000, graine 7, taux de panne 12,8 % contre 13,6 %), donc un autre test de 1600 lignes au lieu de 1000. Les écarts mesurés mélangent l'effet du modèle et celui des données de test, et sont de l'ordre du bruit. Pour comparer honnêtement, il faudrait évaluer les deux modèles sur un même jeu de test fixe. C'est justement le `data_md5` enregistré dans chaque run qui permet de voir que les données diffèrent.

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   **Git** versionne le code (et les petits fichiers texte comme le compte rendu ou l'ADR), ainsi que les reçus `.dvc` des données. **DVC** versionne les fichiers de données eux-mêmes : il les garde hors de Git, dans son cache et dans un stockage, et ne laisse dans Git qu'un reçu (md5, taille, chemin). **MLflow** garde la trace de chaque entraînement (un run) : les paramètres (`model`, `C`, `threshold`, `n_train`), l'empreinte des données (`data_md5`), les métriques (recall, precision, accuracy) et le modèle avec les versions exactes de ses bibliothèques. Git et DVC répondent à « quelle version du code et des données ? », MLflow à « quel réglage a donné quel résultat ? ».
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   Le stockage est un dossier de mon ordinateur (`~/dvc-stockage`) : ce chemin n'existe pas sur les postes des autres membres, il ne doit donc pas aller dans Git. Avec `--local`, il est écrit dans `.dvc/config.local`, qui est ignoré par Git. Pour partager les données, il faudrait un stockage accessible à tout le groupe (S3, Google Drive, un serveur SSH…), déclaré **sans** `--local` pour que la configuration soit dans `.dvc/config` et donc commitée. Chacun pourrait alors faire `git pull` puis `dvc pull` pour récupérer exactement les mêmes données.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   Le **code** (le package `maintai`) est dans Git, et dans le wheel construit au TP4. Les **données** d'entraînement sont sous DVC : le reçu `data/sensors.csv.dvc` est dans Git, le fichier lui-même est dans le stockage DVC. Le **modèle** est dans MLflow, sous forme d'un run identifié par son `run_id`, avec les **versions exactes** des bibliothèques dans son `requirements.txt`. Le `data_md5` du run fait le lien entre le modèle et ses données.

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp5` existe sur GitHub : oui / non
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? oui / non

## 8. Ce qui reste flou

…
