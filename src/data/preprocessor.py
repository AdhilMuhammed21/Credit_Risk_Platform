"""
src/data/preprocessor.py
Full preprocessing pipeline using sklearn.
Saves a fitted Pipeline to models/ so predict.py can use the exact same transforms.

Usage:
    from src.data.preprocessor import build_pipeline, fit_transform, transform
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from src.utils.config import (
    PIPELINE_PATH, MODELS_DIR, PROCESSED_DIR,
    MISSING_HIGH_THRESH, PROTECTED_COLS, SKEW_THRESH,
)
from src.utils.logger import get_logger

log = get_logger(__name__)

# Columns to always drop (IDs, not features)
DROP_COLS = ["SK_ID_CURR"]
TARGET_COL = "TARGET"


# ── Step 1: Initial cleaning (before sklearn pipeline) ───────────

def initial_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs non-sklearn cleaning steps that must happen before column selection:
    - Drop ID columns
    - Separate target
    - Drop extremely high-missing columns (except protected)
    - Log1p transform skewed numeric columns
    - Clip outliers on income/credit/annuity
    """
    df = df.copy()

    # Drop ID columns
    cols_to_drop = [c for c in DROP_COLS if c in df.columns]
    df.drop(columns=cols_to_drop, inplace=True)

    # Clip outlier-prone columns at p1/p99
    clip_cols = ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE"]
    for col in clip_cols:
        if col in df.columns:
            lo, hi = df[col].quantile([0.01, 0.99])
            df[col] = df[col].clip(lo, hi)

    # Drop high-missing columns — but never drop protected ones
    if TARGET_COL in df.columns:
        feature_df = df.drop(columns=[TARGET_COL])
    else:
        feature_df = df

    miss_rate = feature_df.isnull().mean()
    high_miss_cols = miss_rate[
        (miss_rate > MISSING_HIGH_THRESH) &
        (~miss_rate.index.isin(PROTECTED_COLS))
    ].index.tolist()

    if high_miss_cols:
        log.info(f"Dropping {len(high_miss_cols)} high-missing columns: {high_miss_cols[:5]}...")
        df.drop(columns=high_miss_cols, inplace=True)

    # Log1p transform skewed numeric columns (exclude target)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if TARGET_COL in num_cols:
        num_cols.remove(TARGET_COL)

    for col in num_cols:
        try:
            skew = df[col].skew()
            if abs(skew) > SKEW_THRESH and df[col].min() >= 0:
                df[col] = np.log1p(df[col])
        except Exception:
            pass

    log.info(f"After initial_clean: {df.shape}")
    return df


# ── Step 2: Encode categoricals (before sklearn pipeline) ────────

def encode_categoricals(df: pd.DataFrame, fit_encoders: dict = None):
    """
    Label-encodes binary categoricals.
    One-hot encodes low-cardinality categoricals (<= 10 unique).
    Drops high-cardinality categoricals (> 10 unique, excluding binary).

    Returns: (encoded_df, encoders_dict)
    fit_encoders: pass None to fit new encoders, or pass existing dict to reuse.
    """
    df = df.copy()
    encoders = fit_encoders or {}
    is_fitting = fit_encoders is None

    cat_cols = df.select_dtypes(include="object").columns.tolist()

    binary_cols    = [c for c in cat_cols if df[c].nunique() <= 2]
    low_card_cols  = [c for c in cat_cols if 2 < df[c].nunique() <= 10]
    high_card_cols = [c for c in cat_cols if df[c].nunique() > 10]

    # Binary → LabelEncoder
    for col in binary_cols:
        df[col] = df[col].fillna("Unknown")
        if is_fitting:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            le = encoders.get(col)
            if le:
                known = set(le.classes_)
                df[col] = df[col].apply(lambda x: x if x in known else le.classes_[0])
                df[col] = le.transform(df[col].astype(str))
            else:
                df[col] = 0

    # Low cardinality → get_dummies
    if low_card_cols:
        df = pd.get_dummies(df, columns=low_card_cols, drop_first=True, dtype=int)

    # High cardinality → drop for now (target encode in v2)
    if high_card_cols:
        log.info(f"Dropping {len(high_card_cols)} high-cardinality columns: {high_card_cols}")
        df.drop(columns=high_card_cols, inplace=True)

    return df, encoders


# ── Step 3: sklearn imputer + scaler ────────────────────────────

def build_numeric_pipeline() -> Pipeline:
    """Median impute → StandardScaler for numeric columns."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
    ])


# ── Main public functions ────────────────────────────────────────

def fit_transform(df: pd.DataFrame):
    """
    Full preprocessing on training data.
    Fits all transformers and saves them to MODELS_DIR.

    Returns: (X: np.ndarray, y: pd.Series, feature_names: list)
    """
    log.info("Starting fit_transform ...")

    # Separate target
    y = None
    if TARGET_COL in df.columns:
        y = df[TARGET_COL].copy()
        df = df.drop(columns=[TARGET_COL])

    # Step 1: clean
    df = initial_clean(df if y is None else pd.concat([df, y], axis=1))
    if TARGET_COL in df.columns:
        y = df.pop(TARGET_COL)

    # Step 2: encode
    df, encoders = encode_categoricals(df, fit_encoders=None)

    # Step 3: numeric pipeline
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    pipeline = build_numeric_pipeline()
    X = pipeline.fit_transform(df[num_cols])
    feature_names = num_cols

    # Save artifacts
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "pipeline":      pipeline,
        "encoders":      encoders,
        "feature_names": feature_names,
        "num_cols":      num_cols,
    }
    joblib.dump(artifact, PIPELINE_PATH)

    # Save processed dataframe as parquet (Day 1 success metric)
    processed_df = pd.DataFrame(X, columns=feature_names)
    if y is not None:
        processed_df["TARGET"] = y.values
    processed_df.to_parquet(PROCESSED_DIR / "application_processed.parquet", index=False)

    log.info(f"Pipeline saved → {PIPELINE_PATH}")
    log.info(f"Processed parquet saved → {PROCESSED_DIR / 'application_processed.parquet'}")
    log.info(f"Final feature matrix: {X.shape}")

    return X, y, feature_names


def transform(df: pd.DataFrame) -> np.ndarray:
    """
    Apply saved preprocessing pipeline to new data (test / live prediction).

    Returns: X: np.ndarray
    """
    if not PIPELINE_PATH.exists():
        raise FileNotFoundError(
            f"Pipeline not found at {PIPELINE_PATH}. Run fit_transform() first."
        )

    artifact = joblib.load(PIPELINE_PATH)
    pipeline      = artifact["pipeline"]
    encoders      = artifact["encoders"]
    feature_names = artifact["feature_names"]
    num_cols      = artifact["num_cols"]

    # Drop target if present
    if TARGET_COL in df.columns:
        df = df.drop(columns=[TARGET_COL])

    df = initial_clean(df)
    df, _ = encode_categoricals(df, fit_encoders=encoders)

    # Align columns — add missing cols as 0, drop extras
    for col in num_cols:
        if col not in df.columns:
            df[col] = 0.0
    df = df[num_cols]

    X = pipeline.transform(df)
    return X


def get_feature_names() -> list:
    """Return the feature names from the saved pipeline."""
    artifact = joblib.load(PIPELINE_PATH)
    return artifact["feature_names"]


if __name__ == "__main__":
    from src.data.loader import load_train
    df = load_train()
    X, y, features = fit_transform(df)
    print(f"X shape: {X.shape}")

if y is not None:
    print(f"y shape: {y.shape}")
    print(f"Class balance: {y.value_counts().to_dict()}")

print(f"First 5 features: {features[:5]}")