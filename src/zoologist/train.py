"""
Train the penguin classifier and save it.

Run with: uv run python -m zoologist.train
"""
from sklearn import set_config
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from zoologist.data import load_data
from zoologist.model import build_pipeline
from zoologist.params import MODEL_LOCATION
from zoologist.registry import save_model

set_config(transform_output="pandas")


def train():
    df = load_data()
    print(f"📦 Loaded {len(df)} penguins")

    X = df.drop(columns=["species"])
    y = df["species"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, pipeline.predict(X_test))
    print(f"🎯 Test accuracy: {accuracy:.3f}")

    print(f"💾 Saving model (MODEL_LOCATION={MODEL_LOCATION})")
    save_model(pipeline)
    return pipeline


if __name__ == "__main__":
    train()
