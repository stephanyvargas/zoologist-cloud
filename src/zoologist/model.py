"""
Build the model pipeline, refactored from the data scientist's notebook.
"""
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def build_pipeline() -> Pipeline:
    """Preprocessing + logistic regression, exactly as in the notebook."""
    preprocessor = ColumnTransformer(
        [
            ("num", StandardScaler(), make_column_selector(dtype_include="number")),
            (
                "cat",
                OneHotEncoder(drop="if_binary", sparse_output=False),
                make_column_selector(dtype_include="object"),
            ),
        ]
    )
    return Pipeline([("preprocessor", preprocessor), ("model", LogisticRegression())])
