"""
Save and load trained models, locally or in Google Cloud Storage.
"""
import time
from pathlib import Path

import joblib

from zoologist.params import (
    BUCKET_NAME,
    GCS_MODELS_PREFIX,
    LOCAL_REGISTRY_PATH,
    MODEL_LOCATION,
)


def save_model(model, name: str = "pipeline_logreg") -> Path:
    """Save the model locally, then also upload it to GCS if MODEL_LOCATION=gcs.

    Every training gets a timestamped file, so older models are never overwritten.
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{name}_{timestamp}.joblib"

    # 1. Always save locally first
    LOCAL_REGISTRY_PATH.mkdir(exist_ok=True)
    local_path = LOCAL_REGISTRY_PATH / filename
    joblib.dump(model, local_path)
    print(f"✅ Model saved locally: {local_path}")

    # 2. Then upload the same file to the bucket
    if MODEL_LOCATION == "gcs":
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{GCS_MODELS_PREFIX}{filename}")
        blob.upload_from_filename(local_path)
        print(f"✅ Model uploaded to gs://{BUCKET_NAME}/{blob.name}")

    return local_path


def load_model():
    """Load the most recent model, from GCS if MODEL_LOCATION=gcs, otherwise locally."""
    if MODEL_LOCATION == "gcs":
        from google.cloud import storage

        client = storage.Client()
        blobs = list(client.list_blobs(BUCKET_NAME, prefix=GCS_MODELS_PREFIX))
        blobs = [b for b in blobs if b.name.endswith(".joblib")]
        if not blobs:
            raise FileNotFoundError(f"No model found in gs://{BUCKET_NAME}/{GCS_MODELS_PREFIX}")

        latest = max(blobs, key=lambda b: b.updated)
        LOCAL_REGISTRY_PATH.mkdir(exist_ok=True)
        local_path = LOCAL_REGISTRY_PATH / Path(latest.name).name
        latest.download_to_filename(local_path)
        print(f"✅ Model downloaded from gs://{BUCKET_NAME}/{latest.name}")
    else:
        local_models = sorted(LOCAL_REGISTRY_PATH.glob("*.joblib"))
        if not local_models:
            raise FileNotFoundError(f"No model found in {LOCAL_REGISTRY_PATH}")
        local_path = local_models[-1]  # timestamps sort chronologically
        print(f"✅ Model loaded locally: {local_path}")

    return joblib.load(local_path)
