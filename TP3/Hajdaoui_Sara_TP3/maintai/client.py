"""Client Python de l'API MaintAI : ce que fetch faisait dans la page web (TP2), en Python.

Usage :
    from maintai.client import MaintaiClient
    api = MaintaiClient("http://localhost:8000", api_key="demo123")
    api.predict({"temperature_c": 72, "vibration_mm_s": 6, "load_pct": 85, "runtime_hours": 15000})
"""
import httpx


class APIError(Exception):
    """L'API a répondu, mais pas 200 : on garde le code et le message."""

    def __init__(self, status_code: int, detail):
        super().__init__(f"Erreur {status_code} : {detail}")
        self.status_code = status_code
        self.detail = detail


class MaintaiClient:
    def __init__(self, url: str = "http://localhost:8000", api_key: str | None = None,
                 http: httpx.Client | None = None):
        # Les tests passent leur TestClient dans http : même code, sans serveur
        self.http = http or httpx.Client(base_url=url, timeout=5.0)
        self.api_key = api_key

    def health(self) -> dict:
        r = self.http.get("/health")
        r.raise_for_status()
        return r.json()

    
    def predict(self, reading: dict) -> dict:
        """Envoie un relevé à l'API et retourne la prédiction."""

        # 1. Préparer les en-têtes HTTP
        headers = {}

        if self.api_key:
            headers["X-API-Key"] = self.api_key

        # 2. Envoyer la requête POST à l'API
        r = self.http.post(
            "/v1/predict",
            json=reading,
            headers=headers
        )

        # 3. Vérifier la réponse de l'API
        if r.status_code != 200:
            try:
                detail = r.json().get("detail")
            except ValueError:
                detail = r.text

            raise APIError(r.status_code, detail)

        # 4. Retourner le résultat au format dictionnaire
        return r.json()

