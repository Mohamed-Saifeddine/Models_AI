import pytest

HEADERS = {"X-API-Key": "test-key"}
VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}
MISSING_LOAD = {key: value for key, value in VALID.items() if key != "load_pct"}

CAS_REFUSES = [
    ("champ manquant", "/v1/predict", MISSING_LOAD, 422),
    ("valeur absurde", "/v1/predict", {**VALID, "temperature_c": 500}, 422),
    (
        "texte au lieu d'un nombre",
        "/v1/predict",
        {**VALID, "temperature_c": "chaud"},
        422,
    ),
    ("champ supplémentaire", "/v1/predict", {**VALID, "debug": True}, 422),
    ("mauvaise route", "/v1/predicte", VALID, 404),
]


@pytest.mark.parametrize("description,url,body,expected", CAS_REFUSES)
def test_requete_refusee(client, description, url, body, expected):
    response = client.post(url, json=body, headers=HEADERS)
    assert response.status_code == expected, description
