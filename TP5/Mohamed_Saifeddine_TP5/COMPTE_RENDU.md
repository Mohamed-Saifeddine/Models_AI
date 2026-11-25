# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** G1 · **Membre :** Mohamed Saifeddine · **Date :** 25/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
32 passed, 5 warnings in 76.49s
```

Quels tests échouent, et pourquoi ?

Avant l'installation des dépendances, aucun test lié à MLflow ne pouvait être exécuté : `test_tracking.py` échouait à la collecte avec `ModuleNotFoundError: No module named 'mlflow'`. Après `pip install -r requirements.txt`, les 32 tests passent.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Après `pip install -e .`, le package `maintai==0.3.0` pointe vers `C:\Users\user\Downloads\TP5\TP5` en mode éditable.

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
mlflow.set_experiment(EXPERIMENT)
with mlflow.start_run() as run:
    mlflow.log_params(params)
    mlflow.log_param("data_md5", file_md5(data_path))
    mlflow.log_metrics(metrics)
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
32 passed, 5 warnings in 76.49s
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.750 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| (v2, seuil 0.3) | 0.741 | 0.650 | 0.916 |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Je choisirais la régression logistique avec le seuil `0.2`, car elle obtient le meilleur recall (`0.838`) parmi les essais. En contrepartie, sa précision passe à `0.543`, donc davantage de fausses alertes. La forêt n'obtient pas un meilleur rappel (`0.728`).

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

La version de scikit-learn indiquée est `1.8.0`. Cela rend l'environnement du modèle reproductible : on connaît exactement la bibliothèque utilisée pour l'entraînement. Le TP4 avait ce problème de reproductibilité avec des modèles potentiellement entraînés sous des versions différentes.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

Les runs sont enregistrés dans `mlflow.db` et les artefacts dans `mlruns/` à la racine de TP5. Ces fichiers sont ignorés par Git grâce à `.gitignore`, car ils sont locaux et volumineux ; seul le code pertinent est partagé dans Git.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

Les valeurs concordent exactement : le `.dvc` de la v1 porte `73e0b7cb3c6f795c70c3ddf970b99c15`, la même empreinte que `data_md5` des runs v1.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

`data/sensors.csv` contient le fichier volumineux complet et doit rester hors de Git. `data/sensors.csv.dvc` contient seulement l'empreinte MD5, la taille et le chemin : ce petit fichier peut être suivi par Git comme reçu de version.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:
	changed outs:
		modified:           data/sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | `5558e1a` | `73e0b7cb` | 5000 |
| v2 | `d29e49c` | `93fdeef2` | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Le retour à la v1 donne exactement `5000` lignes. Le retour à la v2 puis `dvc checkout` donne `8000` lignes.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

Après suppression de `data/sensors.csv` et de `.dvc/cache`, `dvc pull` récupère la v2 : `1 file fetched and 1 file added`. La lecture donne `8000` lignes.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | `73e0b7cb` | 4000 | 0.750 | 0.622 |
| v2 | `93fdeef2` | 6400 | 0.741 | 0.650 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Le recall baisse légèrement sur la v2 (`0.741` contre `0.750`) alors que la précision augmente (`0.650` contre `0.622`). On ne peut pas conclure que le modèle v2 est meilleur : les jeux de données, leur taille et leurs séparations train/test diffèrent. Une comparaison fiable demanderait les mêmes données de validation ou une validation stable.

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

L'ADR 004 a été créé. Modèle retenu provisoirement : régression logistique, seuil `0.2`, sur les données v1. Run : `a06f8078361e481aa92706bc51054d60`, `data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15`.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   Git versionne le code et les petits fichiers reçus DVC. DVC versionne les contenus de données volumineux via son cache, son stockage et les fichiers `.dvc`. MLflow garde les runs : paramètres, métriques, modèles/artefacts et versions de bibliothèques.
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   `--local` utilise un dossier local qui ne doit pas être partagé par chemin absolu ni écrit dans Git. Pour partager les données, il faudrait configurer un stockage distant accessible à toute l'équipe (S3, Google Drive, serveur), puis pousser/puller avec DVC.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   Il faut livrer le code (Git/wheel), les données (stockage DVC, reçu dans Git) et le modèle (artefact lié à un run MLflow). Les versions exactes des bibliothèques sont dans le `requirements.txt` du modèle enregistré par MLflow.

## 7. Le rendu Git


## 8. Ce qui reste flou
