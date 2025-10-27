import streamlit as st

st.set_page_config(page_title="Dosha Analysis", page_icon="🔬")

st.title("🔬 Discover Your Ayurvedic Constitution (Prakriti)")
st.markdown("""
Answer the following questions to get an initial understanding of your dominant dosha.
This quiz is a starting point to help us personalize your wellness journey.
""")

# Correctly handle the text input using session_state
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
st.session_state.user_name = st.text_input("First, what is your name?", st.session_state.user_name)

# --- FIX IS HERE ---
# 1. Define the questions and their corresponding options first.
questions = {
    "What is your typical body frame?": ("Slender and light", "Medium and athletic", "Large and sturdy"),
    "How would you describe your appetite?": ("Irregular, I forget to eat", "Strong and sharp, I get irritable when hungry", "Steady, but slow digestion"),
    "What is your skin type?": ("Dry, thin, and cool", "Sensitive, oily, and warm", "Thick, smooth, and cool"),
    "How do you react to stress?": ("I become anxious and worried", "I get irritable and impatient", "I withdraw and become quiet")
}

answers = {}
for question, options in questions.items():
    answers[question] = st.radio(question, options)

if st.button("Analyze My Dosha"):
    if not st.session_state.user_name:
        st.warning("Please enter your name before analyzing.")
    else:
        vata_score = 0
        pitta_score = 0
        kapha_score = 0

        # Simple scoring logic
        for q, ans in answers.items():
            idx = questions[q].index(ans)
            if idx == 0: vata_score += 1
            elif idx == 1: pitta_score += 1
            else: kapha_score += 1

        scores = {"Vata": vata_score, "Pitta": pitta_score, "Kapha": kapha_score}
        dominant_dosha = max(scores, key=scores.get)
        st.session_state.dosha = dominant_dosha

        st.success(f"### Analysis Complete, {st.session_state.user_name}!")
        st.write(f"Based on your answers, your dominant dosha appears to be **{dominant_dosha}**.")

        with st.expander(f"Learn more about {dominant_dosha} Dosha"):
            if dominant_dosha == "Vata":
                st.write("Vata is the energy of movement (Air + Ether). When balanced, you are creative, energetic, and flexible. When imbalanced, you may experience anxiety, dry skin, and irregular digestion.")
            elif dominant_dosha == "Pitta":
                st.write("Pitta is the energy of transformation (Fire + Water). When balanced, you are intelligent, focused, and a strong leader. When imbalanced, you may experience irritability, inflammation, and acidity.")
            else: # Kapha
                st.write("Kapha is the energy of structure and lubrication (Earth + Water). When balanced, you are calm, compassionate, and strong. When imbalanced, you may experience sluggishness, weight gain, and congestion.")

        st.info("Now you can explore your personalized **Wellness Guide** or **Chat with the Coach** using the sidebar!")