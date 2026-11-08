"""API de inferencia de especies de pingüinos."""

import os
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from app.preprocessing import FEATURE_NAMES, transform_features

MODEL_PATH = os.getenv("MODEL_PATH", "model/model.joblib")

app = FastAPI(title="Penguins API")


class PenguinIn(BaseModel):
    island: str
    sex: str
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float


@lru_cache
def get_model():
    """Carga el modelo real si existe; si no, devuelve None."""
    if not os.path.exists(MODEL_PATH):
        return None
    import joblib
    return joblib.load(MODEL_PATH)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(data: PenguinIn, model=Depends(get_model)):
    if model is None:
        raise HTTPException(status_code=503, detail="modelo no disponible")

    try:
        features = transform_features(data.model_dump())
    except (ValueError, TypeError) as error:
        raise HTTPException(status_code=422, detail=str(error))

    species = model.predict([features])[0]
    return {"species": str(species), "features": dict(zip(FEATURE_NAMES, features))}
