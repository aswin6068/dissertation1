import os
import joblib
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from config import DATASET_PATH, MODEL_PATH
from .processing import preprocess_text

def train_text_classifier():
    """Train a text classifier using cleaned descriptions and labeled categories."""
    if not os.path.exists(DATASET_PATH):
        print(f"⚠️ Dataset not found at {DATASET_PATH}.")
        return

    dataset = pd.read_csv(DATASET_PATH)

    # Check for necessary column
    if "category" not in dataset.columns:
        print("⚠️ 'category' column is missing from the dataset.")
        return

    # Filter dataset with valid categories
    dataset = dataset[dataset["category"].notnull()]
    if dataset.empty:
        print("⚠️ No labeled data available for training.")
        return

    # Preprocess descriptions
    dataset["cleaned_description"] = dataset["description"].apply(preprocess_text)

    if len(dataset) < 5:
        print("⚠️ Not enough data to train a reliable classifier (minimum 5 samples required).")
        return

    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        dataset["cleaned_description"],
        dataset["category"],
        test_size=0.2,
        random_state=42
    )

    # Build model pipeline
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(X_train, y_train)

    # Save model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Classifier trained successfully and saved to: {MODEL_PATH}")

def classify_text(description: str) -> str:
    """Classify a new description using the trained model."""
    if not os.path.exists(MODEL_PATH):
        return "⚠️ Classifier not trained yet."

    model = joblib.load(MODEL_PATH)
    return model.predict([description])[0]
