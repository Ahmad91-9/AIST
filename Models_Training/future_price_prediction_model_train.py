# future_price_model_train.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
import joblib
file_path = r'C:\Users\Ahmad Hassan\Desktop\RealEstateEXsys\Models_Training\future_price_training_data.csv'
# Load dataset
df = pd.read_csv(file_path)  # 60,000+ synthetic rows

# Features and targets
X = df.drop(columns=["future_price_1yr", "future_price_3yr"])
y_1yr = df["future_price_1yr"]
y_3yr = df["future_price_3yr"]

# Identify categorical and numerical columns
categorical_cols = ["location", "property_type", "condition"]
numerical_cols = [
    "area", "bedrooms", "bathrooms", "age",
    "amenities_score", "demand_score",
    "current_price", "development_index",
    "economic_index", "market_trend"
]

# Preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
    ]
)

# Define pipeline for 1-year prediction
pipeline_1yr = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", GradientBoostingRegressor(
        n_estimators=600,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    ))
])

# Split and train 1-year model
X_train, X_test, y_train, y_test = train_test_split(X, y_1yr, test_size=0.15, random_state=42)
pipeline_1yr.fit(X_train, y_train)
score_1yr = pipeline_1yr.score(X_test, y_test)
print(f"Future Price 1-Year Model R^2 Score: {score_1yr:.4f}")
joblib.dump(pipeline_1yr, "future_price_1yr_model.pkl")
print("Future price 1-year model saved as future_price_1yr_model.pkl")

# Define pipeline for 3-year prediction
pipeline_3yr = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", GradientBoostingRegressor(
        n_estimators=600,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    ))
])

# Split and train 3-year model
X_train, X_test, y_train, y_test = train_test_split(X, y_3yr, test_size=0.15, random_state=42)
pipeline_3yr.fit(X_train, y_train)
score_3yr = pipeline_3yr.score(X_test, y_test)
print(f"Future Price 3-Year Model R^2 Score: {score_3yr:.4f}")
joblib.dump(pipeline_3yr, "future_price_3yr_model.pkl")
print("Future price 3-year model saved as future_price_3yr_model.pkl")
