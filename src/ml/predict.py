import joblib
import pandas as pd

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = BASE_DIR / "models" / "lightgbm_model.joblib"

model = joblib.load(MODEL_PATH)

EXPECTED_COLUMNS = model.feature_name_

def predict_risk(income, credit, annuity):

    credit_income_ratio = credit / income if income > 0 else 0
    annuity_income_ratio = annuity / income if income > 0 else 0

    sample = {
        "AMT_INCOME_TOTAL": income,
        "AMT_CREDIT": credit,
        "AMT_ANNUITY": annuity,
        "CREDIT_INCOME_RATIO": credit_income_ratio,
        "ANNUITY_INCOME_RATIO": annuity_income_ratio
    }

    input_df = pd.DataFrame([sample])

    for col in EXPECTED_COLUMNS:
        if col not in input_df.columns:
            input_df[col] = 0

    input_df = input_df[EXPECTED_COLUMNS]

    probability = model.predict_proba(input_df)[:, 1][0]

    if probability < 0.3:
        band = "Low Risk"
    elif probability < 0.7:
        band = "Medium Risk"
    else:
        band = "High Risk"

    return {
        "risk_score": round(float(probability), 4),
        "risk_band": band
    }