"""
FastAPI application for serving the zoologist model.

The model is loaded once at startup: from GCS if MODEL_LOCATION=gcs.
"""
import pandas as pd
from fastapi import FastAPI

from zoologist.predict import predict
from zoologist.registry import load_model

app = FastAPI()
app.state.model = load_model()


@app.get("/")
def root():
    """Root endpoint returning a greeting."""
    return {"greeting": "hello"}


@app.get("/predict")
def predict_species(
    island: str,
    bill_length_mm: float,
    bill_depth_mm: float,
    flipper_length_mm: float,
    body_mass_g: float,
    sex: str,
):
    """Predict the species of one penguin."""
    X = pd.DataFrame([locals()])
    return {"species": str(predict(app.state.model, X)[0])}
