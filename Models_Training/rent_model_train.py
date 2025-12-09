# rent_model_train.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
import joblib

# Load dataset
file_path = r'C:\Users\Ahmad Hassan\Desktop\RealEstateEXsys\Models_Training\rent_training_data.csv'
df = pd.read_csv(file_path)

# Features and target
X = df.drop(columns=["rent"])
y = df["rent"]

# Identify categorical and numerical columns
categorical_cols = ["location", "property_type", "condition"]
numerical_cols = ["area", "bedrooms", "bathrooms", "age", "amenities_score", "demand_score"]

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
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    ))
])

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

# Train model
pipeline.fit(X_train, y_train)

# Evaluate
score = pipeline.score(X_test, y_test)
print(f"Rent Model R^2 Score: {score:.4f}")

# Save model
joblib.dump(pipeline, "rent_model.pkl")
print("Rent prediction model saved as rent_model.pkl")
