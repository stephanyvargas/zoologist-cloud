"""
Load the latest trained model and make predictions on new data.

Run with: uv run python -m zoologist.predict
"""
import pandas as pd
from sklearn import set_config

from zoologist.params import PROJECT_ROOT
from zoologist.registry import load_model

set_config(transform_output="pandas")


def predict(model, data: pd.DataFrame):
    """Make predictions using the loaded model and input data."""
    return model.predict(data)


if __name__ == "__main__":
    model = load_model()
    sample_data = pd.read_csv(PROJECT_ROOT / "data" / "sample_input.csv")
    print("Predictions:", predict(model, sample_data))
