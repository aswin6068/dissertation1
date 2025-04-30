from config import GOOGLE_API_KEY, GOOGLE_CSE_ID
from .processing import analyze_sentiment, preprocess_text, extract_entities
from googleapiclient.discovery import build
from newspaper import Article
import streamlit as st

def google_search(query, api_key, cse_id, num=5):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=num).execute()
    return [item["link"] for item in res.get("items", [])]

def fetch_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return ""

def extract_product_name(description):
    entities = extract_entities(description)
    priority_order = ["PRODUCT", "ORG", "WORK_OF_ART", "FAC", "PERSON"]
    
    for label in priority_order:
        for text, ent_label in entities:
            if ent_label == label:
                return text

    tokens = preprocess_text(description).split()
    return tokens[0] if tokens else "unknown"

def get_product_feedback(product_query):
    links = google_search(f"{product_query} reviews", GOOGLE_API_KEY, GOOGLE_CSE_ID)
    sentiments = []
    positives = []
    negatives = []

    for url in links:
        text = fetch_article(url)
        if text:
            sentiment = analyze_sentiment(text)
            if len(text) > 150 and any(kw in text.lower() for kw in ["review", "rating", "feedback", "customer", "opinion", "pros", "cons"]):
                if sentiment == "Positive":
                    positives.append((text[:300], url))
                elif sentiment == "Negative":
                    negatives.append((text[:300], url))
                sentiments.append(sentiment)

    if sentiments:
        total = len(sentiments)
        pos_count = sentiments.count("Positive")
        rating = round((pos_count / total) * 5, 1)
        feedback = f"⭐ **Overall Rating for '{product_query}':** {rating}/5\n\n💬 **What people are saying:**\n"
        if positives:
            snippet, url = positives[0]
            feedback += f'\n✅ **Positive:** "{snippet.strip()}..."\n🔗 {url}\n'
        if negatives:
            snippet, url = negatives[0]
            feedback += f'\n⚠️ **Negative:** "{snippet.strip()}..."\n🔗 {url}\n'
        return feedback
    else:
        return f"⚠️ No online reviews found for **{product_query}**."

def handle_image_feedback(image_path, description, final_message):
    product_name = extract_product_name(description)
    st.markdown(f"### 🧾 Detected product: `{product_name}`")

    feedback = get_product_feedback(product_name)
    st.markdown("### 💬 Product Feedback")
    st.text_area("AI Review Summary", feedback, height=250)

    return feedback
