"""Entraîne chaque modèle candidat, l'évalue sur le jeu de test et les compare.

Usage, depuis la racine du projet : python -m monprojet.train
"""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error, mean_squared_error,
                             precision_score, r2_score, recall_score)
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from monprojet import config
from monprojet.data import load_data, split
from monprojet.models import candidates

HIGHER_IS_BETTER = {"accuracy": True, "recall": True, "precision": True, "f1": True,
                    "mae": False, "rmse": False, "r2": True}


def build_preprocessing(X: pd.DataFrame) -> ColumnTransformer:
    """Prépare les colonnes : nombres mis à l'échelle, catégories encodées, texte vectorisé. (Fournie.)"""
    text = [config.TEXT_COLUMN] if config.TEXT_COLUMN else []
    numeric = [c for c in X.columns if c not in text and pd.api.types.is_numeric_dtype(X[c])]
    categorical = [c for c in X.columns if c not in text and c not in numeric]
    steps = []
    if numeric:
        steps.append(("nombres", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric))
    if categorical:
        steps.append(("categories", make_pipeline(SimpleImputer(strategy="most_frequent"),
                                                  OneHotEncoder(handle_unknown="ignore")), categorical))
    if text:
        steps.append(("texte", TfidfVectorizer(), config.TEXT_COLUMN))
    return ColumnTransformer(steps, sparse_threshold=0)


def evaluate(model, X_test, y_test) -> dict:
    """Prédit sur le jeu de test et renvoie un dictionnaire {nom de la métrique: valeur}.

    Attendu :
    - classification : "accuracy", "recall", "precision", "f1"
      (average="binary" s'il y a deux classes, "macro" sinon ; zero_division=0) ;
    - régression : "mae", "rmse", "r2" ;
    - des float, arrondis à 3 décimales.

    Pistes : model.predict(X_test) ; les fonctions importées en haut du fichier ; np.sqrt.
    """
    predictions = model.predict(X_test)

    if config.TASK == "classification":
        average = "binary" if y_test.nunique() == 2 else "macro"
        return {
            "accuracy": round(float(accuracy_score(y_test, predictions)), 3),
            "recall": round(float(recall_score(
                y_test, predictions, average=average, zero_division=0
            )), 3),
            "precision": round(float(precision_score(
                y_test, predictions, average=average, zero_division=0
            )), 3),
            "f1": round(float(f1_score(
                y_test, predictions, average=average, zero_division=0
            )), 3),
        }

    if config.TASK == "regression":
        mse = mean_squared_error(y_test, predictions)
        return {
            "mae": round(float(mean_absolute_error(y_test, predictions)), 3),
            "rmse": round(float(np.sqrt(mse)), 3),
            "r2": round(float(r2_score(y_test, predictions)), 3),
        }

    raise ValueError(f"Type de tâche inconnu : {config.TASK}")


def main() -> None:
    """Entraîne chaque candidat, l'évalue, compare, et sauvegarde.

    Plan :
    1. charger les données (load_data) et les découper (split) ;
    2. pour chaque (nom, estimateur) de candidates() :
       model = Pipeline([("preparation", build_preprocessing(X_train)), ("modele", estimateur)]),
       l'entraîner sur X_train, y_train, puis l'évaluer avec evaluate() ;
    3. afficher un tableau de comparaison (pd.DataFrame(resultats).T), trié selon config.MAIN_METRIC ;
    4. trouver le meilleur modèle selon config.MAIN_METRIC (HIGHER_IS_BETTER dit dans quel sens) ;
    5. créer config.MODELS_DIR, y sauvegarder le meilleur modèle (joblib.dump) dans model.joblib,
       et écrire metrics.json : {"main_metric": ..., "best": nom du meilleur, "results": {nom: scores}}.
    """
    df = load_data()
    X_train, X_test, y_train, y_test = split(df)

    resultats = {}
    modeles_entraines = {}

    for nom, estimateur in candidates().items():
        model = Pipeline([
            ("preparation", build_preprocessing(X_train)),
            ("modele", estimateur),
        ])
        model.fit(X_train, y_train)
        resultats[nom] = evaluate(model, X_test, y_test)
        modeles_entraines[nom] = model

    if config.MAIN_METRIC not in HIGHER_IS_BETTER:
        raise ValueError(f"Métrique principale inconnue : {config.MAIN_METRIC}")

    higher_is_better = HIGHER_IS_BETTER[config.MAIN_METRIC]
    tableau = pd.DataFrame(resultats).T.sort_values(
        by=config.MAIN_METRIC,
        ascending=not higher_is_better,
    )
    print(tableau)

    selection = max if higher_is_better else min
    meilleur_nom = selection(
        resultats,
        key=lambda nom: resultats[nom][config.MAIN_METRIC],
    )

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(modeles_entraines[meilleur_nom], config.MODELS_DIR / "model.joblib")

    rapport = {
        "main_metric": config.MAIN_METRIC,
        "best": meilleur_nom,
        "results": resultats,
    }
    (config.MODELS_DIR / "metrics.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
