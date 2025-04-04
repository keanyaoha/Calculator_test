import streamlit as st

# --- Page config ---
st.set_page_config(page_title="Profile", page_icon="🌿")

# --- Custom CSS for styling ---
st.markdown(
    """
    <style>
        .stApp {
            background-color: white;
        }
        section[data-testid="stSidebar"] {
            background-color: #e8f8f5;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Title ---
st.title("👤 Create Your Profile")
st.write("Let us know a bit about you so we can personalize your carbon footprint journey")

# --- EU-27 Countries (Alphabetical) ---
eu_countries = sorted([
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", 
    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania",
    "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"
])

# --- Profile Form ---
with st.form("profile_form"):
    name = st.text_input("Full Name *", key="name")
    age = st.number_input("Age *", min_value=0, max_value=120, step=1, key="age")
    gender = st.selectbox("Gender *", ["-- Select --", "Female", "Male", "Other", "Prefer not to say"], key="gender")
    email = st.text_input("Email Address *", key="email")
    country = st.selectbox("Country *", ["-- Select --"] + eu_countries, key="country")

    consent = st.checkbox("I agree to participate in the carbon footprint analysis and share anonymous data for research.", key="consent")

    submitted = st.form_submit_button("Save Profile")

# --- Submission handling ---
if submitted:
    if not name or not email or gender == "-- Select --" or country == "-- Select --":
        st.warning("⚠️ Please fill in all required fields.")
    else:
        st.success(f"Thank you, {name}! Your profile has been saved.")
        st.session_state["user_profile"] = {
            "name": name,
            "age": age,
            "gender": gender,
            "email": email,
            "country": country,
            "consent": consent
        }
