"""Les modèles à comparer.

À vous d'écrire candidates(). Les tests de tests/test_models.py disent ce qui est attendu.
"""
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from monprojet import config


def candidates() -> dict:
    """Renvoie un dictionnaire {nom: modèle scikit-learn non entraîné}.

    Attendu :
    - le PREMIER modèle est la baseline : le modèle le plus simple possible
      (DummyClassifier pour une classification, DummyRegressor pour une régression) ;
    - au moins trois vrais modèles ensuite, adaptés à config.TASK ;
    - random_state=config.SEED pour les modèles qui ont du hasard.

    Pistes : sklearn.dummy, sklearn.linear_model, sklearn.ensemble, sklearn.neighbors, sklearn.tree.
    """
    if config.TASK == "classification":
        return {
            "baseline": DummyClassifier(strategy="most_frequent"),
            "regression_logistique": LogisticRegression(
                max_iter=1000,
                random_state=config.SEED,
            ),
            "arbre_decision": DecisionTreeClassifier(random_state=config.SEED),
            "foret_aleatoire": RandomForestClassifier(
                n_estimators=100,
                random_state=config.SEED,
            ),
        }

    if config.TASK == "regression":
        return {
            "baseline": DummyRegressor(strategy="mean"),
            "regression_lineaire": LinearRegression(),
            "arbre_decision": DecisionTreeRegressor(random_state=config.SEED),
            "foret_aleatoire": RandomForestRegressor(
                n_estimators=100,
                random_state=config.SEED,
            ),
        }

    raise ValueError(f"Type de tâche inconnu : {config.TASK}")
