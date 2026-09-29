import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier

print("\n--- Reproducibility Validation ---")

# Load processed data
X_train = np.load("data/processed/X_train_final.npy")
X_test = np.load("data/processed/X_test_final.npy")
y_train = np.load("data/processed/y_train.npy")

# Load saved model
saved_model = joblib.load("models/random_forest_model.pkl")

# Train another model with the same parameters
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# Compare predictions
old_predictions = saved_model.predict(X_test)
new_predictions = model.predict(X_test)

if np.array_equal(old_predictions, new_predictions):
    print("Reproducibility check PASSED!")
    print("Predictions are identical.")
else:
    print("Reproducibility check FAILED!")
    print("Predictions are different.")

print("--- Reproducibility Validation Completed ---")