"""Tests de validation et de refus des requêtes invalides."""

import pytest

HEADERS = {"X-API-Key": "test-key"}

VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}

SANS_CHARGE = {k: v for k, v in VALID.items() if k != "load_pct"}

CAS_REFUSES = [
    (
        "champ_manquant",
        "/v1/predict",
        SANS_CHARGE,
        422,
    ),
    (
        "valeur_absurde",
        "/v1/predict",
        {**VALID, "temperature_c": 500},
        422,
    ),
    (
        "texte_au_lieu_nombre",
        "/v1/predict",
        {**VALID, "temperature_c": "chaud"},
        422,
    ),
    (
        "champ_supplementaire",
        "/v1/predict",
        {**VALID, "capteur_inconnu": 10},
        422,
    ),
    (
        "mauvaise_route",
        "/v1/predcit",
        VALID,
        404,
    ),
]


@pytest.mark.parametrize(
    "description, url, corps, attendu",
    CAS_REFUSES,
)
def test_requete_refusee(client, description, url, corps, attendu):
    response = client.post(
        url,
        json=corps,
        headers=HEADERS,
    )

    assert response.status_code == attendu, (
        f"{description} : attendu {attendu}, obtenu {response.status_code}"
    )
