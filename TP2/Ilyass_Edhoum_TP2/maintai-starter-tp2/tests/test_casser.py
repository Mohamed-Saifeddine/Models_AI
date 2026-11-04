import pytest

HEADERS = {"X-API-Key": "test-key"}
VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}


@pytest.mark.parametrize(
    ("path", "reading", "expected_status"),
    [
        (
            "/v1/predict",
            {key: value for key, value in VALID.items() if key != "load_pct"},
            422,
        ),
        (
            "/v1/predict",
            {**VALID, "temperature_c": 500},
            422,
        ),
        (
            "/v1/predict",
            {**VALID, "temperature_c": "chaud"},
            422,
        ),
        (
            "/v1/predict",
            {**VALID, "unknown_sensor": 1},
            422,
        ),
        (
            "/v1/predicte",
            VALID,
            404,
        ),
    ],
)
def test_invalid_requests_are_rejected(client, path, reading, expected_status):
    response = client.post(path, json=reading, headers=HEADERS)
    assert response.status_code == expected_status
