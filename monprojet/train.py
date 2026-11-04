
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
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score
)
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from monprojet import config
from monprojet.data import load_data, split
from monprojet.models import candidates


HIGHER_IS_BETTER = {
    "accuracy": True,
    "recall": True,
    "precision": True,
    "f1": True,
    "mae": False,
    "rmse": False,
    "r2": True
}


def build_preprocessing(X: pd.DataFrame) -> ColumnTransformer:
    """Prépare les colonnes : nombres, catégories et texte."""

    text = [config.TEXT_COLUMN] if config.TEXT_COLUMN else []

    numeric = [
        c for c in X.columns
        if c not in text and pd.api.types.is_numeric_dtype(X[c])
    ]

    categorical = [
        c for c in X.columns
        if c not in text and c not in numeric
    ]

    steps = []

    if numeric:
        steps.append((
            "nombres",
            make_pipeline(
                SimpleImputer(strategy="median"),
                StandardScaler()
            ),
            numeric
        ))

    if categorical:
        steps.append((
            "categories",
            make_pipeline(
                SimpleImputer(strategy="most_frequent"),
                OneHotEncoder(handle_unknown="ignore")
            ),
            categorical
        ))

    if text:
        steps.append((
            "texte",
            TfidfVectorizer(),
            config.TEXT_COLUMN
        ))

    return ColumnTransformer(steps, sparse_threshold=0)


def evaluate(model, X_test, y_test) -> dict:
    """Évalue le modèle sur le jeu de test."""

    y_pred = model.predict(X_test)

    if config.TASK == "classification":

        # Choisir la méthode selon le nombre de classes
        average = "binary" if len(np.unique(y_test)) == 2 else "macro"

        scores = {
            "accuracy": float(round(
                accuracy_score(y_test, y_pred), 3
            )),

            "recall": float(round(
                recall_score(
                    y_test,
                    y_pred,
                    average=average,
                    zero_division=0
                ), 3
            )),

            "precision": float(round(
                precision_score(
                    y_test,
                    y_pred,
                    average=average,
                    zero_division=0
                ), 3
            )),

            "f1": float(round(
                f1_score(
                    y_test,
                    y_pred,
                    average=average,
                    zero_division=0
                ), 3
            ))
        }

    elif config.TASK == "regression":

        scores = {
            "mae": float(round(
                mean_absolute_error(y_test, y_pred), 3
            )),

            "rmse": float(round(
                np.sqrt(mean_squared_error(y_test, y_pred)), 3
            )),

            "r2": float(round(
                r2_score(y_test, y_pred), 3
            ))
        }

    else:
        raise ValueError(
            f"Type de tâche inconnu : {config.TASK}"
        )

    return scores


def main() -> None:
    """Entraîne, évalue, compare et sauvegarde les modèles."""

    # 1. Charger et découper les données
    df = load_data()

    X_train, X_test, y_train, y_test = split(df)

    print("Données chargées avec succès.")
    print(f"Entraînement : {len(X_train)} lignes")
    print(f"Test : {len(X_test)} lignes")

    # 2. Entraîner et évaluer chaque modèle
    resultats = {}
    modeles_entraines = {}

    for nom, estimateur in candidates().items():

        print(f"\nEntraînement du modèle : {nom}")

        model = Pipeline([
            ("preparation", build_preprocessing(X_train)),
            ("modele", estimateur)
        ])

        model.fit(X_train, y_train)

        scores = evaluate(model, X_test, y_test)

        resultats[nom] = scores
        modeles_entraines[nom] = model

    # 3. Afficher le tableau comparatif
    tableau = pd.DataFrame(resultats).T

    metrique = config.MAIN_METRIC

    if metrique not in HIGHER_IS_BETTER:
        raise ValueError(f"Métrique inconnue : {metrique}")

    ordre_decroissant = HIGHER_IS_BETTER[metrique]

    tableau = tableau.sort_values(
        by=metrique,
        ascending=not ordre_decroissant
    )

    print("\n===== COMPARAISON DES MODÈLES =====")
    print(tableau.to_string())

    # 4. Sélectionner le meilleur modèle
    if ordre_decroissant:
        meilleur_nom = tableau[metrique].idxmax()
    else:
        meilleur_nom = tableau[metrique].idxmin()

    meilleur_modele = modeles_entraines[meilleur_nom]

    print(f"\nMeilleur modèle : {meilleur_nom}")
    print(f"Meilleur score ({metrique}) : "
          f"{resultats[meilleur_nom][metrique]}")

    # 5. Sauvegarder le modèle et les métriques
    config.MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    chemin_modele = config.MODELS_DIR / "model.joblib"

    joblib.dump(
        meilleur_modele,
        chemin_modele
    )

    contenu_metrics = {
        "main_metric": metrique,
        "best": meilleur_nom,
        "results": resultats
    }

    chemin_metrics = config.MODELS_DIR / "metrics.json"

    chemin_metrics.write_text(
        json.dumps(
            contenu_metrics,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("\nModèle sauvegardé :", chemin_modele)
    print("Métriques sauvegardées :", chemin_metrics)


if __name__ == "__main__":
    main()
