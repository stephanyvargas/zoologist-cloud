# 🐧 Zoologist: saving models to Google Cloud Storage

Le Wagon ML Ops demo (07-Intro-to-ML-Ops / Cloud Storage).

We train a penguin species classifier (Adelie, Chinstrap or Gentoo) and save the trained model either **locally** or to a
**Google Cloud Storage bucket**. The prediction script and the API then load the latest model from the same place.
Switching between local and cloud is a **configuration change only** (`.env`); the code stays the same.

## Project structure

```
.
├── api/
│   └── fast.py              # FastAPI app: loads the latest model at startup, /predict endpoint
├── data/                    # sample input data (CSV files are gitignored)
├── models/                  # locally saved models (gitignored)
├── notebooks/
│   └── datascientist_deliverable.ipynb   # the original notebook from the data scientists
├── src/zoologist/
│   ├── params.py            # all configuration, read from environment variables
│   ├── data.py              # load and clean the training data
│   ├── model.py             # build the scikit-learn pipeline
│   ├── train.py             # train, evaluate and save the model
│   ├── registry.py          # save_model / load_model: local or Google Cloud Storage
│   └── predict.py           # load the latest model and predict
├── .env.sample              # template for your .env (copy it, never commit .env)
├── .envrc                   # tells direnv to load .env automatically
└── pyproject.toml
```

## Setup

You need [uv](https://docs.astral.sh/uv/) and, for the cloud part, the [gcloud CLI](https://cloud.google.com/sdk/docs/install).

```bash
gh repo clone stephanyvargas/zoologist-cloud
cd zoologist-cloud
uv sync
cp .env.sample .env
```

### Load the `.env` file

Pick **one** of these:

- **direnv** (recommended, the Le Wagon setup): run `direnv allow .` once. From then on `.env` loads automatically
  every time you `cd` into the project, and you can run the commands below as they are.
- **No direnv** (for example in Google Cloud Shell): add `--env-file .env` after `uv run`, for example
  `uv run --env-file .env python -m zoologist.train`.

> After editing `.env`, direnv reloads it automatically the next time you press Enter in the project folder.

## 1. Train and save locally

In `.env`:

```
MODEL_LOCATION=local
```

```bash
uv run python -m zoologist.train
ls models/
```

You should see `🎯 Test accuracy: …` and a new `models/pipeline_logreg_<timestamp>.joblib`.
Every training creates a new timestamped file, so older models are never overwritten.

## 2. Predict

Download the sample data once:

```bash
curl -O --output-dir data/ https://wagon-public-datasets.s3.amazonaws.com/07-Intro-to-ML-Ops/Penguins/sample_input.csv
```

```bash
uv run python -m zoologist.predict
```

Expected: `Predictions: ['Chinstrap' 'Gentoo' 'Adelie']`

## 3. Save the model to Google Cloud Storage

### 3.1 Authenticate (once per machine)

```bash
gcloud auth login                          # for the gcloud CLI
gcloud auth application-default login      # for Python code (google-cloud-storage)
gcloud config set project <your-project-id>
```

Not needed in Google Cloud Shell, or on a Compute Engine VM created with **Storage: Read Write** access.

### 3.2 Create a bucket

Bucket names are unique **worldwide** and use kebab-case.

```bash
BUCKET=zoologist-<your-name>
gcloud storage buckets create gs://$BUCKET --location europe-west1
```

### 3.3 Point the project to the bucket

In `.env`:

```
MODEL_LOCATION=gcs
GCP_PROJECT=<your-project-id>
BUCKET_NAME=zoologist-<your-name>
```

### 3.4 Train: the model is uploaded

```bash
uv run python -m zoologist.train
gcloud storage ls -r gs://$BUCKET
```

You'll see `✅ Model uploaded to gs://<bucket>/models/pipeline_logreg_<timestamp>.joblib`.
You can also check it in the [Cloud Storage console](https://console.cloud.google.com/storage/browser).

### 3.5 Predict: the model is downloaded

```bash
rm models/*.joblib                         # prove nothing is stored locally
uv run python -m zoologist.predict
```

The latest model is downloaded from the bucket, then used for the predictions.

## 4. Run the API

```bash
uv run uvicorn api.fast:app --reload
```

The API loads the latest model (from the bucket if `MODEL_LOCATION=gcs`) when it starts. Then open:

- http://localhost:8000/docs for the interactive docs
- http://localhost:8000/predict?island=Biscoe&bill_length_mm=49.1&bill_depth_mm=14.5&flipper_length_mm=212&body_mass_g=4625&sex=Female
  → `{"species": "Gentoo"}`

## 5. Train on a virtual machine

1. In the console, create a Compute Engine VM with **Ubuntu** and **Access scopes → Storage: Read Write**.
2. Connect: `gcloud compute ssh <vm-name> --zone <zone>`, or with VS Code Remote-SSH after `gcloud compute config-ssh`.
3. On the VM:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   sudo apt-get install -y direnv gh
   echo 'eval "$(direnv hook bash)"' >> ~/.bashrc && exec bash

   gh auth login
   gh repo clone stephanyvargas/zoologist-cloud && cd zoologist-cloud
   cp .env.sample .env && nano .env        # MODEL_LOCATION=gcs + your bucket
   direnv allow .
   uv run python -m zoologist.train
   ```

4. **Stop the VM when you're done** 💸: `gcloud compute instances stop <vm-name> --zone <zone>`

## Configuration reference

| Variable | Values | Used for |
|---|---|---|
| `MODEL_LOCATION` | `local` or `gcs` | where `save_model` / `load_model` save and load models |
| `GCP_PROJECT` | your project id | the Google Cloud project |
| `BUCKET_NAME` | your bucket name | the bucket that stores the models (in `models/`) |
| `DATA_URL` | optional | where to load the training data from (defaults to the seaborn penguins CSV) |

## Clean up

```bash
gcloud storage rm -r gs://$BUCKET
gcloud compute instances delete <vm-name> --zone <zone>
```
