from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

MODELS_DIR = BASE_DIR / "models"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PIPELINE_PATH = MODELS_DIR / "preprocessing_pipeline.joblib"

MISSING_HIGH_THRESH = 0.6
SKEW_THRESH = 1.0

PROTECTED_COLS = []