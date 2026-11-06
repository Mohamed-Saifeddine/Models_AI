import pytest

HEADERS = {"X-API-Key": "test-key"}
VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}
SANS_CHARGE = {key: value for key, value in VALID.items() if key != "load_pct"}

CAS_REFUSES = [
    ("champ manquant", "/v1/predict", SANS_CHARGE, 422),
    ("valeur absurde", "/v1/predict", {**VALID, "temperature_c": 600}, 422),
    ("texte au lieu d'un nombre", "/v1/predict", {**VALID, "temperature_c": "chaud"}, 422),
    ("champ en trop", "/v1/predict", {**VALID, "pression_bar": 3.2}, 422),
    ("mauvaise route", "/v1/predire", VALID, 404),
]


@pytest.mark.parametrize("description,url,corps,attendu", CAS_REFUSES)
def test_requete_refusee(client, description, url, corps, attendu):
    response = client.post(url, json=corps, headers=HEADERS)
    assert response.status_code == attendu, description
