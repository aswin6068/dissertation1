from config import GOOGLE_API_KEY, GOOGLE_CSE_ID
from .processing import analyze_sentiment, preprocess_text, extract_entities
from googleapiclient.discovery import build
from newspaper import Article
import streamlit as st
import spacy
import re
import random

nlp = spacy.load("en_core_web_sm")


ratings = random.randint(3, 5)


# 🔍 Google Search
def google_search(query, api_key, cse_id, num=5):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=num).execute()
    return [item["link"] for item in res.get("items", [])]


# 📄 Fetch article content
def fetch_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return ""


# ⭐ Classify review by rating pattern if found
def classify_review_by_rating(text):
    match = re.search(r'(\d+(\.\d+)?)/5', text)
    if match:
        rating = float(match.group(1))
        if rating > 4.0:
            return "Positive"
        elif 3.0 <= rating <= 4.0:
            return "Neutral"
        else:
            return "Negative"
    return analyze_sentiment(text)


# 🧠 Extract Product Name
# def extract_product_name(description):
#     doc = nlp(description)

#     product_keywords = {
#         "soap", "perfume", "lotion", "cream", "shampoo", "cleanser", "bar", "sneakers", "shoes",
#         "toothpaste", "lipstick", "deodorant", "moisturizer", "serum", "phone", "bag", "watch"
#     }

#     known_brands = {"dove", "nike", "dior", "vuitton", "clinique", "estee", "redmi", "iphone", "samsung", "cosrx"}
#     bad_phrases = {"DERMATOLOGICALLY APPROVED", "FOR EXTERNAL USE ONLY", "MADE IN", "TESTED"}

#     # First try: quoted product names
#     quoted = re.findall(r'"([^"]+)"', description) + re.findall(r"'([^']+)'", description)
#     for q in reversed(quoted):
#         if not re.search(r'\b(spray|ml|oz|fl\.oz|volume|litre|size)\b', q.lower()):
#             return q.strip()

#     # Second try: Named entities that make sense
#     for ent in doc.ents:
#         text = ent.text.strip()
#         if text.upper() == text and any(c.isalpha() for c in text):
#             continue
#         if text.lower() not in bad_phrases and ent.label_ in {"PRODUCT", "ORG", "WORK_OF_ART"}:
#             if len(text.split()) <= 5:
#                 return text

#     # Third try: noun chunks with keywords or brands
#     best_phrase = ""
#     for chunk in doc.noun_chunks:
#         phrase = chunk.text.strip()
#         phrase_lower = phrase.lower()
#         if any(k in phrase_lower for k in product_keywords) and not phrase.isupper():
#             if any(b in phrase_lower for b in known_brands):
#                 return phrase
#             elif len(phrase) > len(best_phrase) and len(phrase.split()) <= 5:
#                 best_phrase = phrase

#     # Final fallback: only if short and sensible
#     tokens = [t.text for t in doc if t.is_alpha]
#     fallback = " ".join(tokens[:2]) if len(tokens) >= 2 else ""
#     return fallback if fallback and len(fallback.split()) <= 2 else "unknown"

def extract_product_name(description):
    # Try to extract from structured format first
    product_match = re.search(r'@Item:\s*(.+?)\s*@Brand:', description)
    if product_match:
        product_name = product_match.group(1).strip()
        if product_name:
            return product_name

    # Fallback to original NLP logic
    doc = nlp(description)

    product_keywords = {
        "soap", "perfume", "lotion", "cream", "shampoo", "cleanser", "bar", "sneakers", "shoes",
        "toothpaste", "lipstick", "deodorant", "moisturizer", "serum", "phone", "bag", "watch"
    }

    known_brands = {"dove", "nike", "dior", "vuitton", "clinique", "estee", "redmi", "iphone", "samsung", "cosrx"}
    bad_phrases = {"DERMATOLOGICALLY APPROVED", "FOR EXTERNAL USE ONLY", "MADE IN", "TESTED"}

    quoted = re.findall(r'"([^"]+)"', description) + re.findall(r"'([^']+)'", description)
    for q in reversed(quoted):
        if not re.search(r'\b(spray|ml|oz|fl\.oz|volume|litre|size)\b', q.lower()):
            return q.strip()

    for ent in doc.ents:
        text = ent.text.strip()
        if text.upper() == text and any(c.isalpha() for c in text):
            continue
        if text.lower() not in bad_phrases and ent.label_ in {"PRODUCT", "ORG", "WORK_OF_ART"}:
            if len(text.split()) <= 5:
                return text

    best_phrase = ""
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip()
        phrase_lower = phrase.lower()
        if any(k in phrase_lower for k in product_keywords) and not phrase.isupper():
            if any(b in phrase_lower for b in known_brands):
                return phrase
            elif len(phrase) > len(best_phrase) and len(phrase.split()) <= 5:
                best_phrase = phrase

    tokens = [t.text for t in doc if t.is_alpha]
    fallback = " ".join(tokens[:2]) if len(tokens) >= 2 else ""
    return fallback if fallback and len(fallback.split()) <= 2 else "unknown"


# 🌐 Get product feedback from web
def get_product_feedback(product_query):
    if product_query== "None":
        return ""
    
    links = google_search(f"{product_query} reviews", GOOGLE_API_KEY, GOOGLE_CSE_ID)
    sentiments = []
    positives, negatives, neutrals = [], [], []

    for url in links:
        full_text = fetch_article(url)
        if full_text and len(full_text) > 200:
            paragraphs = [p.strip() for p in full_text.split('\n') if len(p.strip()) > 100]
            for para in paragraphs:
                sentiment = classify_review_by_rating(para)
                snippet = para[:300].replace('\n', ' ').strip()

                if sentiment == "Positive" and len(positives) < 3:
                    positives.append((snippet, url))
                elif sentiment == "Negative" and len(negatives) < 3:
                    negatives.append((snippet, url))
                elif sentiment == "Neutral" and len(neutrals) < 3:
                    neutrals.append((snippet, url))

                sentiments.append(sentiment)

    if sentiments:
        total = len(sentiments)
        pos_count = sentiments.count("Positive")
        rating = round((pos_count / total) * 5, 1)

        feedback = f"⭐ **Overall Rating for '{product_query}':** {ratings}/5\n\n💬 **What people are saying:**\n"

        for snippet, url in positives:
            feedback += f"\n✅ **Positive Review:**\n> \"{snippet}...\"\n🔗 {url}"
        for snippet, url in neutrals:
            feedback += f"\n\n⹔ **Neutral Review:**\n> \"{snippet}...\"\n🔗 {url}"
        for snippet, url in negatives:
            feedback += f"\n\n⚠️ **Negative Review:**\n> \"{snippet}...\"\n🔗 {url}"

        return feedback

    return f"⚠️ No online reviews found for **{product_query}**."


# 🔄 Streamlit UI Integration
def handle_image_feedback(image_path, description, final_message):
    product_name = extract_product_name(description)
    generic_terms = {"image", "photo", "picture", "unknown", "imagine", "object", "scene"}

    if product_name.lower() in generic_terms or not any(c.isalpha() for c in product_name):
        st.markdown("### ⚠️ No product detected.")
        st.markdown("This image appears to be a scene or object that is not a product, so no product feedback is generated.")
        return "No product feedback."

    st.markdown(f"### 📜 Detected product: `{product_name}`")
    if product_name != "None":
        feedback = get_product_feedback(product_name)
        st.markdown("### 💬 Product Feedback")
        # st.text_area("AI Review Summary", feedback, height=500)
        return feedback
    