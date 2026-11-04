
"""Les modèles à comparer.

À vous d'écrire candidates().
Les tests de tests/test_models.py disent ce qui est attendu.
"""

from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor
)

from monprojet import config


def candidates() -> dict:
    """Renvoie un dictionnaire de modèles scikit-learn non entraînés."""

    if config.TASK == "classification":
        return {
            "baseline": DummyClassifier(
                strategy="most_frequent"
            ),

            "regression_logistique": LogisticRegression(
                max_iter=1000,
                random_state=config.SEED
            ),

            "random_forest": RandomForestClassifier(
                n_estimators=100,
                random_state=config.SEED
            ),

            "gradient_boosting": HistGradientBoostingClassifier(
                random_state=config.SEED
            )
        }

    elif config.TASK == "regression":
        return {
            "baseline": DummyRegressor(
                strategy="mean"
            ),

            "regression_lineaire": LinearRegression(),

            "random_forest": RandomForestRegressor(
                n_estimators=100,
                random_state=config.SEED
            ),

            "gradient_boosting": HistGradientBoostingRegressor(
                random_state=config.SEED
            )
        }

    else:
        raise ValueError(
            f"Type de tâche inconnu : {config.TASK}"
        )
