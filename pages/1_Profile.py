import streamlit as st

# Set page config (optional)
st.set_page_config(page_title="Profile", page_icon="👤")

# Custom CSS styling for green/environmental theme
st.markdown("""
    <style>
    .title {
        font-size: 32px;
        color: #2E8B57;
        font-weight: 600;
    }
    .subtitle {
        font-size: 20px;
        color: #4CAF50;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title">👤 Create Your Profile</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Let us know a bit about you so we can personalize your carbon footprint journey 🌍</div>', unsafe_allow_html=True)

# Inputs
with st.form("profile_form"):
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    gender = st.selectbox("Gender", ["-- Select --", "Female", "Male", "Other", "Prefer not to say"])
    email = st.text_input("Email Address")
    country = st.selectbox("Country", ["-- Select --", "Germany", "France", "Italy", "Spain", "Poland", "Other"])
    mood = st.selectbox("How are you feeling today?", ["😊 Happy", "😐 Neutral", "😟 Concerned"])

    consent = st.checkbox("I agree to participate in the carbon footprint analysis and share anonymous data for research.")

    submitted = st.form_submit_button("Save Profile")

    if submitted:
        if not name or not email or gender == "-- Select --" or country == "-- Select --":
            st.warning("Please fill in all required fields.")
        else:
            st.success(f"Thank you, {name}! Your profile has been saved.")
            st.session_state["user_profile"] = {
                "name": name,
                "age": age,
                "gender": gender,
                "email": email,
                "country": country,
                "mood": mood,
                "consent": consent
            }
