import joblib
import pandas as pd

MODEL_PATH = "models/lightgbm_model.pkl"

model = joblib.load(MODEL_PATH)

def predict_risk(input_df):
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