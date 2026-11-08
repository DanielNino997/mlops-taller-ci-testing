from fastapi.testclient import TestClient

from app.main import app, get_model


def test_health_responde_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_payload_valido_retorna_especie(client, valid_penguin):
    response = client.post("/predict", json=valid_penguin)

    assert response.status_code == 200
    assert response.json()["species"] == "Adelie"


def test_predict_envia_features_preprocesadas_al_modelo(client, fake_model, valid_penguin):
    client.post("/predict", json=valid_penguin)

    # 4 medidas + one-hot isla (Torgersen) + sexo male + bill_ratio
    assert fake_model.received == [[39.1, 18.7, 181.0, 3750.0, 0.0, 0.0, 1.0, 1.0, 2.0909]]


def test_predict_payload_incompleto_retorna_422(client, valid_penguin):
    del valid_penguin["island"]

    response = client.post("/predict", json=valid_penguin)

    assert response.status_code == 422


def test_predict_valor_fuera_de_rango_retorna_422(client, valid_penguin):
    valid_penguin["body_mass_g"] = 9000

    response = client.post("/predict", json=valid_penguin)

    assert response.status_code == 422
    assert "fuera de rango" in response.json()["detail"]


def test_predict_sin_modelo_retorna_503(valid_penguin):
    app.dependency_overrides[get_model] = lambda: None
    try:
        response = TestClient(app).post("/predict", json=valid_penguin)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["detail"] == "modelo no disponible"
