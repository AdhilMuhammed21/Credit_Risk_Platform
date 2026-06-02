from src.ml.predict import predict_risk

result = predict_risk(
    100000,
    1000000,
    50000
)

print(result)