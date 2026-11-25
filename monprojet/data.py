"""Chargement et découpage des données.

À vous d'écrire load_data() et split().
Les tests de tests/test_data.py disent ce qui est attendu.
"""

import pandas as pd
from sklearn.model_selection import train_test_split

from monprojet import config


def load_data(path=None) -> pd.DataFrame:
    """Charge les données depuis un fichier CSV."""

    if path is None:
        path = config.DATA_PATH

    df = pd.read_csv(path)

    if config.TARGET not in df.columns:
        raise ValueError(
            f"La colonne cible '{config.TARGET}' est absente du fichier CSV."
        )

    df = df.dropna(subset=[config.TARGET])

    return df


def feature_columns(df: pd.DataFrame) -> list:
    """Renvoie les colonnes d'entrée, sauf la cible et la date."""

    if config.FEATURES is not None:
        return list(config.FEATURES)

    excluded = {config.TARGET, config.TIME_COLUMN}

    return [c for c in df.columns if c not in excluded]


def split(df: pd.DataFrame):
    """Sépare les données en entraînement et test."""

    X = df[feature_columns(df)]
    y = df[config.TARGET]

    if config.SPLIT == "random":

        stratify = y if config.TASK == "classification" else None

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=config.TEST_SIZE,
            random_state=config.SEED,
            stratify=stratify
        )

    elif config.SPLIT == "chronologique":

        ordre = pd.to_datetime(df[config.TIME_COLUMN]).argsort()

        X = X.iloc[ordre]
        y = y.iloc[ordre]

        n_test = max(1, int(len(df) * config.TEST_SIZE))

        X_train = X.iloc[:-n_test]
        X_test = X.iloc[-n_test:]

        y_train = y.iloc[:-n_test]
        y_test = y.iloc[-n_test:]

    else:
        raise ValueError(
            f"Type de découpage inconnu : {config.SPLIT}"
        )

    return X_train, X_test, y_train, y_test