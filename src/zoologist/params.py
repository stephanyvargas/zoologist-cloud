"""
Project configuration, read from environment variables (see .env).

Code and configuration are kept separate: the same code saves the model
locally or to Google Cloud Storage depending on MODEL_LOCATION.
"""
import os
from pathlib import Path

# Where to save / load models: "local" or "gcs"
MODEL_LOCATION = os.environ.get("MODEL_LOCATION", "local")

# Google Cloud
GCP_PROJECT = os.environ.get("GCP_PROJECT")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

# Local folder where models are saved (project_root/models)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_REGISTRY_PATH = PROJECT_ROOT / "models"

# Blob "folder" in the bucket (buckets have no real folders, only name prefixes)
GCS_MODELS_PREFIX = "models/"

# Training data (the same penguins dataset the notebook loads with seaborn)
DATA_URL = os.environ.get(
    "DATA_URL",
    "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",
)
