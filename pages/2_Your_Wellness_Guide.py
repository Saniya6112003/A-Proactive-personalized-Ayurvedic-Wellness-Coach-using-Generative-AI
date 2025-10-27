import streamlit as st
from streamlit_lottie import st_lottie
import requests
import json

def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code!= 200:
        return None
    return r.json()

st.set_page_config(page_title="Your Wellness Guide", page_icon="🧘‍♀️")
st.title("🧘‍♀️ Your Personalized Wellness Guide")

if st.session_state.get('dosha') is None:
    st.warning("Please complete the 'Dosha Analysis' first to generate your personalized guide.")
else:
    dosha = st.session_state.dosha
    user_name = st.session_state.user_name
    st.header(f"A Holistic Plan for {user_name} ({dosha.capitalize()} Dominant)")
    st.markdown("---")

    # Load the knowledge base to get recommendations
    with open('ayurvedic_kb.json', 'r', encoding='utf-8') as f:
        kb = json.load(f)

    # Provide a list of strings to name each tab
tab1, tab2, tab3, tab4 = st.tabs(["Dietary Guidance", "Yoga & Pranayama", "Herbal Remedies", "Lifestyle Routines"])

with tab1:
        st.subheader("🍎 Dietary Guidance")
        lottie_food = load_lottie_url("https://lottie.host/937c8856-b677-4383-9318-b26b248c8189/37i62oKa3k.json")
        if lottie_food:
            st_lottie(lottie_food, height=200, key="food_animation")
        
        st.write(f"For balancing **{dosha}**, your diet should focus on the following principles:")
        
        foods_to_favor = [f['name'] for cat in kb['foods'].values() for f in cat if f['effects_on_doshas'].get(dosha, '').lower() == 'pacifies']
        foods_to_avoid = [f['name'] for cat in kb['foods'].values() for f in cat if f['effects_on_doshas'].get(dosha, '').lower() == 'aggravates']

        col1, col2 = st.columns(2)
        with col1:
            st.success("Foods to Favor:")
            st.markdown("- " + "\n- ".join(foods_to_favor[:15]))
        with col2:
            st.error("Foods to Avoid:")
            st.markdown("- " + "\n- ".join(foods_to_avoid[:15]))

with tab2:
        st.subheader("🧘 Yoga & Meditation")
        lottie_yoga = load_lottie_url("https://lottie.host/0e8a4740-49b8-4b71-8e7a-305123289182/3h8iA3e4AM.json")
        if lottie_yoga:
            st_lottie(lottie_yoga, height=200, key="yoga_animation")

        st.write(f"The following practices are recommended to balance **{dosha}**:")
        
        asanas = [a['name'] for a in kb['yoga_asanas'] if dosha in a['balancing_for_doshas']]
        pranayama = [p['name'] for p in kb['pranayama'] if dosha in p['balancing_for_doshas']]

        st.info("**Recommended Yoga Asanas (Poses):**")
        st.markdown("- " + "\n- ".join(asanas))
        
        st.info("**Recommended Pranayama (Breathing Exercises):**")
        st.markdown("- " + "\n- ".join(pranayama))

with tab3:
        st.subheader("📅 Daily Routine (Dinacharya)")
        st.write("Following a daily routine helps align your body with natural rhythms.")
        
        for period, activities in kb['dinacharya'].items():
            with st.expander(f"**{period.replace('_', ' ').title()}**"):
                for act in activities:
                    st.markdown(f"**{act['activity_name']}:** {act[dosha.lower() + '_recommendation']}")

with tab4:
    st.subheader("🌿 Lifestyle & Sensory Therapy")
    st.write("Incorporate these practices into your life to support overall balance.")

    # --- CORRECTED LIFESTYLE SECTION ---
    st.info("**General Lifestyle Advice:**")
    # Loop through each adjustment and display the correct recommendation for the user's dosha
    for adjustment in kb['lifestyle_adjustments']:
        activity = adjustment['activity_name']
        recommendation_key = dosha.lower() + '_recommendation'
        recommendation = adjustment[recommendation_key]
        st.markdown(f"**{activity}:** {recommendation}")
    
    # --- This part was already correct and remains the same ---
    aromatherapy = next((item for item in kb['sensory_therapies']['aromatherapy'] if item['dosha'].lower() == dosha.lower()), None)
    color_therapy = next((item for item in kb['sensory_therapies']['color_therapy'] if item['dosha'].lower() == dosha.lower()), None)

    if aromatherapy:
        st.info("**Balancing Aromatherapy:**")
        st.markdown(f"- **Effect:** {aromatherapy['effect']}")
        st.markdown(f"- **Suggested Oils:** {', '.join(aromatherapy['oils'])}")
    
    if color_therapy:
        st.info("**Balancing Colors:**")
        st.markdown(f"- **Effect:** {color_therapy['effect']}")
        st.markdown(f"- **Suggested Colors:** {', '.join(color_therapy['colors'])}")