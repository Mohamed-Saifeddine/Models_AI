"""Chargement et découpage des données.

À vous d'écrire load_data() et split(). Les tests de tests/test_data.py disent ce qui est attendu.
"""
from os import path

import pandas as pd
from sklearn.model_selection import train_test_split  # noqa: F401  (utile pour split)

from monprojet import config


def load_data(path=None) -> pd.DataFrame:
    """Lit le fichier CSV et renvoie un DataFrame.

    Attendu :
    - lire config.DATA_PATH (ou `path` s'il est donné) ;
    - si la colonne config.TARGET n'existe pas, lever une ValueError avec un message clair ;
    - retirer les lignes où la cible est manquante.

    Pistes : pd.read_csv, df.columns, df.dropna(subset=[...]).
    """
    csv_path = path if path is not None else config.DATA_PATH
    df = pd.read_csv(csv_path)

    if config.TARGET not in df.columns:
        raise ValueError(
            f"La colonne cible '{config.TARGET}' est absente du fichier CSV."
        )

    return df.dropna(subset=[config.TARGET])

def feature_columns(df: pd.DataFrame) -> list:
    """Les colonnes d'entrée : celles de config.FEATURES, ou toutes sauf la cible et la date. (Fournie.)"""
    if config.FEATURES is not None:
        return list(config.FEATURES)
    excluded = {config.TARGET, config.TIME_COLUMN}
    return [c for c in df.columns if c not in excluded]


def split(df: pd.DataFrame):
    """Renvoie X_train, X_test, y_train, y_test."""
    columns = feature_columns(df)

    if config.SPLIT == "random":
        X = df[columns]
        y = df[config.TARGET]

        stratify = y if config.TASK == "classification" else None

        return train_test_split(
            X,
            y,
            test_size=config.TEST_SIZE,
            random_state=config.SEED,
            stratify=stratify,
        )

    if config.SPLIT == "chronologique":
        if config.TIME_COLUMN is None:
            raise ValueError(
                "TIME_COLUMN doit être défini pour un découpage chronologique."
            )

        if config.TIME_COLUMN not in df.columns:
            raise ValueError(
                f"La colonne temporelle '{config.TIME_COLUMN}' est absente."
            )

        ordre = pd.to_datetime(df[config.TIME_COLUMN]).argsort()
        df_trie = df.iloc[ordre]

        nombre_test = max(1, round(len(df_trie) * config.TEST_SIZE))
        limite = len(df_trie) - nombre_test

        train = df_trie.iloc[:limite]
        test = df_trie.iloc[limite:]

        X_train = train[columns]
        X_test = test[columns]
        y_train = train[config.TARGET]
        y_test = test[config.TARGET]

        return X_train, X_test, y_train, y_test

    raise ValueError(
        f"Type de découpage inconnu : {config.SPLIT}"
    )
