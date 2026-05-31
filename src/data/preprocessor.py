"""
src/data/preprocessor.py

Two outputs from one pipeline run:

  1. ML dataset   → scaled features as numpy array  → for train.py / predict.py
  2. Chatbot dataset → cleaned but NOT scaled        → for SQLite / talk_to_data

Saved files:
  models/preprocessing_pipeline.pkl        ← fitted imputer + scaler
  data/processed/application_processed.parquet   ← ML-ready (scaled)
  data/processed/chatbot_data.parquet            ← human-readable (unscaled)

Usage:
    from src.data.preprocessor import fit_transform, transform, get_feature_names
"""

import numpy as np
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from src.utils.config import (
    PIPELINE_PATH, MODELS_DIR, PROCESSED_DIR,
    MISSING_HIGH_THRESH, PROTECTED_COLS, SKEW_THRESH,
)
from src.utils.logger import get_logger

log = get_logger(__name__)

DROP_COLS  = ["SK_ID_CURR"]
TARGET_COL = "TARGET"


# ── Step 1: Clean (shared by both outputs) ───────────────────────

def initial_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleaning that applies to BOTH the ML dataset and the chatbot dataset:
    - Drop ID columns
    - Clip income/credit/annuity outliers at p1/p99
    - Drop high-missing columns (except protected EXT_SOURCE etc.)
    - Log1p transform skewed numerics

    NOTE: NO scaling here. Scaling is applied later, only for the ML output.
    """
    df = df.copy()

    # Drop IDs
    df.drop(columns=[c for c in DROP_COLS if c in df.columns], inplace=True)

    # Clip outlier-prone columns
    for col in ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE"]:
        if col in df.columns:
            lo, hi = df[col].quantile([0.01, 0.99])
            df[col] = df[col].clip(lo, hi)

    # Drop high-missing (protect important ML features)
    feat_df = df.drop(columns=[TARGET_COL], errors="ignore")
    miss    = feat_df.isnull().mean()
    drop_cols = miss[
        (miss > MISSING_HIGH_THRESH) &
        (~miss.index.isin(PROTECTED_COLS))
    ].index.tolist()
    if drop_cols:
        log.info(f"Dropping {len(drop_cols)} high-missing cols: {drop_cols[:5]} ...")
        df.drop(columns=drop_cols, inplace=True)

    # Log1p skewed numerics (only non-negative columns)
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns
                if c != TARGET_COL]
    for col in num_cols:
        try:
            if abs(df[col].skew()) > SKEW_THRESH and df[col].min() >= 0:
                df[col] = np.log1p(df[col])
        except Exception:
            pass

    log.info(f"After initial_clean: {df.shape}")
    return df


# ── Step 2: Encode categoricals ──────────────────────────────────

def encode_categoricals(df: pd.DataFrame, fit_encoders: dict = None):
    """
    Binary  → LabelEncoder (0/1)
    Low-cardinality (3–10 unique) → pd.get_dummies
    High-cardinality (>10)        → drop (target-encode in v2)

    fit_encoders=None  → fit new encoders (training)
    fit_encoders=dict  → reuse existing (inference)
    """
    df       = df.copy()
    encoders = fit_encoders or {}
    fitting  = fit_encoders is None

    cat_cols       = df.select_dtypes(include="object").columns.tolist()
    binary_cols    = [c for c in cat_cols if df[c].nunique() <= 2]
    low_card_cols  = [c for c in cat_cols if 2 < df[c].nunique() <= 10]
    high_card_cols = [c for c in cat_cols if df[c].nunique() > 10]

    for col in binary_cols:
        df[col] = df[col].fillna("Unknown")
        if fitting:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            le = encoders.get(col)
            if le:
                known    = set(le.classes_)
                df[col]  = df[col].apply(lambda x: x if x in known else le.classes_[0])
                df[col]  = le.transform(df[col].astype(str))
            else:
                df[col] = 0

    if low_card_cols:
        df = pd.get_dummies(df, columns=low_card_cols, drop_first=True, dtype=int)

    if high_card_cols:
        log.info(f"Dropping {len(high_card_cols)} high-card cols: {high_card_cols[:3]} ...")
        df.drop(columns=high_card_cols, inplace=True)

    return df, encoders


# ── Step 3: Impute (shared) + Scale (ML only) ────────────────────

def _build_imputer() -> SimpleImputer:
    return SimpleImputer(strategy="median")


def _build_scaler() -> StandardScaler:
    return StandardScaler()


# ── Public API ───────────────────────────────────────────────────

def fit_transform(df: pd.DataFrame):
    """
    Run full preprocessing on training data. Produces TWO saved parquets:

      application_processed.parquet  ← scaled, for ML training
      chatbot_data.parquet            ← cleaned only, for chatbot/SQL

    Returns: (X: np.ndarray, y: pd.Series, feature_names: list)
    """
    log.info("Starting fit_transform ...")

    # Pull out target
    y = None
    if TARGET_COL in df.columns:
        y  = df[TARGET_COL].copy()
        df = df.drop(columns=[TARGET_COL])

    # ── CHATBOT SNAPSHOT — before ANY transform ───────────────────
    # log1p, scaling, encoding — none of it has run yet.
    # Values are exactly what the applicant sees: 200000, 450000 etc.
    chatbot_df = df.copy()
    chatbot_df.drop(columns=[c for c in DROP_COLS if c in chatbot_df.columns],
                    inplace=True, errors="ignore")
    if y is not None:
        chatbot_df[TARGET_COL] = y.values

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    chatbot_path = PROCESSED_DIR / "chatbot_data.parquet"
    chatbot_df.to_parquet(chatbot_path, index=False)
    log.info(f"Chatbot parquet saved → {chatbot_path}  ← raw business values, no transforms")

    # ── ML pipeline: log1p → encode → impute → scale ─────────────
    df_with_y = pd.concat([df, y], axis=1) if y is not None else df
    df_clean  = initial_clean(df_with_y)
    if TARGET_COL in df_clean.columns:
        y = df_clean.pop(TARGET_COL)

    df_encoded, encoders = encode_categoricals(df_clean, fit_encoders=None)
    num_cols = df_encoded.select_dtypes(include=[np.number]).columns.tolist()

    imputer   = _build_imputer()
    X_imputed = imputer.fit_transform(df_encoded[num_cols])

    # ── ML SAVE: scale on top of imputed values ──────────────────
    scaler  = _build_scaler()
    X       = scaler.fit_transform(X_imputed)

    ml_df = pd.DataFrame(X, columns=num_cols)
    if y is not None:
        ml_df[TARGET_COL] = y.values
    ml_path = PROCESSED_DIR / "application_processed.parquet"
    ml_df.to_parquet(ml_path, index=False)
    log.info(f"ML parquet saved     → {ml_path}  (scaled, for training)")

    # ── Save full pipeline artifact ──────────────────────────────
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "imputer":       imputer,
        "scaler":        scaler,
        "encoders":      encoders,
        "feature_names": num_cols,
        "num_cols":      num_cols,
    }
    joblib.dump(artifact, PIPELINE_PATH)
    log.info(f"Pipeline artifact saved → {PIPELINE_PATH}")
    log.info(f"Feature matrix shape: {X.shape}")

    return X, y, num_cols


def transform(df: pd.DataFrame) -> np.ndarray:
    """
    Apply the saved pipeline to new/live data for prediction.
    Returns scaled numpy array — same space the model was trained on.
    """
    if not PIPELINE_PATH.exists():
        raise FileNotFoundError(
            f"No pipeline at {PIPELINE_PATH}. Run fit_transform() first."
        )

    art      = joblib.load(PIPELINE_PATH)
    imputer  = art["imputer"]
    scaler   = art["scaler"]
    encoders = art["encoders"]
    num_cols = art["num_cols"]

    if TARGET_COL in df.columns:
        df = df.drop(columns=[TARGET_COL])

    df       = initial_clean(df)
    df, _    = encode_categoricals(df, fit_encoders=encoders)

    # Align columns
    for col in num_cols:
        if col not in df.columns:
            df[col] = 0.0
    df = df[num_cols]

    X = scaler.transform(imputer.transform(df))
    return X


def get_feature_names() -> list:
    return joblib.load(PIPELINE_PATH)["feature_names"]


if __name__ == "__main__":
    from src.data.loader import load_train
    df = load_train()
    X, y, features = fit_transform(df)
    print(f"\nML matrix : {X.shape}  (scaled)")
    print(f"Features  : {features[:5]}")
    print(f"Target    : {y.value_counts().to_dict()}")

    from src.utils.config import PROCESSED_DIR
    chatbot = pd.read_parquet(PROCESSED_DIR / "chatbot_data.parquet")
    print(f"\nChatbot df: {chatbot.shape}  (unscaled)")
    print(chatbot[["AMT_INCOME_TOTAL", "AMT_CREDIT", "TARGET"]].head(3))