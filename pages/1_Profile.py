import streamlit as st

# Set page config
st.set_page_config(page_title="Profile", page_icon="🌿")

# Custom style: green sidebar, white main
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

# Helper function for required field labels
def required_label(label):
    return f'<span style="color:black">{label}</span><span style="color:red">*</span>'

# --- Title ---
st.title("👤 Create Your Profile")
st.write("Let us know a bit about you so we can personalize your carbon footprint journey")

# --- Form ---
with st.form("profile_form"):
    st.markdown(required_label("Full Name"), unsafe_allow_html=True)
    name = st.text_input("")

    st.markdown(required_label("Age"), unsafe_allow_html=True)
    age = st.number_input("", min_value=0, max_value=120, step=1)

    st.markdown(required_label("Gender"), unsafe_allow_html=True)
    gender = st.selectbox("", ["-- Select --", "Female", "Male", "Other", "Prefer not to say"])

    st.markdown(required_label("Email Address"), unsafe_allow_html=True)
    email = st.text_input("")

    st.markdown(required_label("Country"), unsafe_allow_html=True)
    country = st.selectbox("", ["-- Select --", "Germany", "France", "Italy", "Spain", "Poland", "Other"])

    consent = st.checkbox("I agree to participate in the carbon footprint analysis and share anonymous data for research.")

    # ✅ THIS must be inside the form!
    submitted = st.form_submit_button("Save Profile")

# --- Handle submission ---
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
