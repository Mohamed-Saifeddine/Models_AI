import pytest

VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}
CAS_REFUSES = [
    ("champ manquant", "/v1/predict", {**VALID, "load_pct": None}, 422),
    ("valeur absurde", "/v1/predict", {**VALID, "temperature_c": 600}, 422),
    (
        "texte au lieu d'un nombre",
        "/v1/predict",
        {**VALID, "temperature_c": "abc"},
        422,
    ),
    (
        "champ en trop",
        "/v1/predict",
        {**VALID, "temperature_c": 50, "pression": 1},
        422,
    ),
    ("mauvaise route", "/v1/predict2", VALID, 404),
]


@pytest.mark.parametrize("description, url, corps, attendu", CAS_REFUSES)
def test_requete_refusee(client, description, url, corps, attendu):
    assert client.post(url, json=corps).status_code == attendu
