import streamlit as st
from streamlit_lottie import st_lottie
import requests

# Function to load Lottie animation from URL
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

st.set_page_config(
    page_title="Ayurvedic Wellness Coach",
    page_icon="🌿",
    layout="wide"
)

# --- Header and Animation ---
col1, col2 = st.columns([1, 2])
with col1:
    st.title("🌿 Your Personal Ayurvedic Wellness Coach")
    st.write("""
    ### Your Journey to Balance and Vitality Starts Here

    This application is your personal guide to understanding and applying the ancient wisdom of Ayurveda in your modern life.
    Our goal is to help you discover your unique constitution and provide personalized, proactive guidance to help you thrive.
    """)
with col2:
    # --- Updated animation to be more Ayurvedic/herbal ---
    lottie_url = "https://lottie.host/5a016f27-1f81-4354-8b04-106606082463/Y5Y3Cr3bYk.json"
    lottie_animation = load_lottie_url(lottie_url)
    if lottie_animation:
        # Adjusted height and key for new animation
        st_lottie(lottie_animation, height=350, key="herbal_animation")

st.markdown("---")

# --- How to Use Section ---
st.subheader("How to Use This App:")
st.markdown("""
1.  **Dosha Analysis:** Navigate to the 'Dosha Analysis' page to take a short quiz and discover your primary dosha (*Prakriti*).
2.  **Your Wellness Guide:** Once your dosha is identified, visit this page to receive a comprehensive set of proactive recommendations for your diet, lifestyle, yoga, and more.
3.  **Chat with Your Coach:** Use this interactive chat to ask any specific questions. Our AI coach will provide answers grounded in Ayurvedic texts and also offer holistic advice.
""")

st.markdown("---")
st.info("Please begin by navigating to the **Dosha Analysis** page from the sidebar on the left.")

# Initialize session state variables
if 'dosha' not in st.session_state:
    st.session_state.dosha = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
