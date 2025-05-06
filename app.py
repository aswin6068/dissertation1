import streamlit as st
from utils.vision import generate_vision_explanation
from utils.feedback import handle_image_feedback
from utils.classifier import train_text_classifier
from utils.audio import convert_text_to_speech
from PIL import Image
import os
import time

# Page settings
st.set_page_config(page_title="🧠 Image Feedback Analyzer", layout="centered")

# Header
st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B;'>🧠 AI-Powered Image Feedback</h1>
    <p style='text-align: center; font-size: 18px;'>
        Upload an image to get a natural-language description, product analysis, and audio feedback — all powered by AI.
    </p>
""", unsafe_allow_html=True)

st.markdown("---")

# Upload section
uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png", "bmp", "gif"])

if uploaded_file:
    file_path = os.path.join("temp_image.jpg")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    image = Image.open(file_path)
    st.image(image, caption="✅ Image Uploaded", use_column_width=True)

    if st.button("🔍 Analyze Image"):
        st.markdown("### 🧾 Step 1: Image Description")
        with st.spinner("Analyzing image..."):
            final_message, description = generate_vision_explanation(file_path)
        st.success("📋 Description generated!")
        st.markdown(f"<div style='background-color: #f0f2f6; padding: 10px; border-radius: 8px;'>{final_message}</div>", unsafe_allow_html=True)

       # st.markdown("### 📚 Step 2: Training Text Classifier")
        #with st.spinner("Training classifier..."):
         #   train_text_classifier()
        #st.success("✅ Classifier trained.")

        st.markdown("### 🌍 Step 2: Web Feedback")
        with st.spinner("Searching for product reviews..."):
            feedback_text = handle_image_feedback(file_path, description, final_message)
        st.success("✅ Feedback retrieved!")
        st.markdown(f"<div style='background-color: #e8f4ea; padding: 10px; border-radius: 8px; color: #2b6b2d;'>{feedback_text}</div>", unsafe_allow_html=True)

        st.markdown("### 🔊 Step 3: Audio Playback")
        combined_text = f"{final_message}\n\n{feedback_text}"
        audio_path = convert_text_to_speech(combined_text)

        with st.spinner("🔄 Loading audio..."):
            time.sleep(0.5)  # Force spinner to show (simulate loading)
            if audio_path and os.path.exists(audio_path):
                with open(audio_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")
            else:
                st.error("⚠️ Failed to generate or load audio.")

# Footer
st.markdown("---")
st.markdown("""
    <p style='text-align: center; font-size: 14px; color: #999999;'>
         Powered by Groq Vision, Google Search, and Streamlit<br>
        Designed with  for Applied AI Research
        Aswin Michat Ramesh
    </p>
""", unsafe_allow_html=True)
