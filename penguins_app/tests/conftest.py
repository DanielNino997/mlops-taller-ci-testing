"""Fixtures compartidas. pytest carga este archivo automáticamente."""

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_model


class FakeModel:
    """Modelo falso: siempre responde 'Adelie' y guarda lo que recibió."""

    def __init__(self):
        self.received = None

    def predict(self, rows):
        self.received = rows
        return ["Adelie" for _ in rows]


@pytest.fixture
def valid_penguin():
    """Un registro válido (pingüino Adelie real del dataset)."""
    return {
        "island": "Torgersen",
        "sex": "male",
        "bill_length_mm": 39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181.0,
        "body_mass_g": 3750.0,
    }


@pytest.fixture
def fake_model():
    return FakeModel()


@pytest.fixture
def client(fake_model):
    """Cliente de la API con el modelo real reemplazado por el falso."""
    app.dependency_overrides[get_model] = lambda: fake_model
    yield TestClient(app)
    app.dependency_overrides.clear()
