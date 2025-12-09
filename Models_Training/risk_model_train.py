# risk_model_train.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
import joblib
file_path = r'C:\Users\Ahmad Hassan\Desktop\RealEstateEXsys\Models_Training\risk_training_data.csv'
# Load dataset
df = pd.read_csv(file_path)  # 60,000+ synthetic rows

# Features and target
X = df.drop(columns=["risk_score"])
y = df["risk_score"]

# Identify categorical and numerical columns
categorical_cols = ["location", "property_type", "condition"]
numerical_cols = [
    "area", "bedrooms", "bathrooms", "age", "amenities_score",
    "crime_index", "market_volatility", "economic_stability", "demand_score"
]

# Preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
    ]
)

# Define the model pipeline
pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", GradientBoostingRegressor(
        n_estimators=600,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    ))
])

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

# Train model
pipeline.fit(X_train, y_train)

# Evaluate
score = pipeline.score(X_test, y_test)
print(f"Risk Score Model R^2 Score: {score:.4f}")

# Save model
joblib.dump(pipeline, "risk_model.pkl")
print("Risk score prediction model saved as risk_model.pkl")
