"""
Load and clean the training data.
"""
import pandas as pd

from zoologist.params import DATA_URL


def load_data(source: str = DATA_URL) -> pd.DataFrame:
    """Load the penguins dataset and drop rows with missing values."""
    df = pd.read_csv(source)
    # The raw CSV says "MALE"/"FEMALE"; seaborn.load_dataset turns this into "Male"/"Female"
    df["sex"] = df["sex"].str.title()
    return df.dropna()
