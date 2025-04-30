import os
import pandas as pd
from datetime import datetime
from config import DATASET_PATH
from .processing import preprocess_text, analyze_sentiment, extract_entities

def encode_image(image_path):
    import base64
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def save_to_csv(image_path, description):
    from .classifier import classify_text
    cleaned = preprocess_text(description)
    sentiment = analyze_sentiment(cleaned)
    entities = extract_entities(description)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    category = classify_text(description)

    new_row = pd.DataFrame([{
        "image": image_path,
        "description": description,
        "cleaned_description": cleaned,
        "sentiment": sentiment,
        "named_entities": entities,
        "category": category,
        "timestamp": timestamp
    }])

    if os.path.exists(DATASET_PATH):
        existing = pd.read_csv(DATASET_PATH)
        combined = pd.concat([existing, new_row], ignore_index=True)
    else:
        combined = new_row

    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    combined.to_csv(DATASET_PATH, index=False)
    print(f"✅ Saved data to: {DATASET_PATH}")

def load_dataset():
    if os.path.exists(DATASET_PATH):
        return pd.read_csv(DATASET_PATH)
    else:
        return pd.DataFrame()
