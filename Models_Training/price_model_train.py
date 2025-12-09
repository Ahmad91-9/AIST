# price_model_train.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
import joblib
file_path = r'C:\Users\Ahmad Hassan\Desktop\RealEstateEXsys\Models_Training\price_training_data.csv'

# Load dataset
df = pd.read_csv(file_path)

# Features and target
X = df.drop(columns=["price"])
y = df["price"]

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
print(f"Price Model R^2 Score: {score:.4f}")

# Save model
joblib.dump(pipeline, "price_model.pkl")
print("Price prediction model saved as price_model.pkl")
