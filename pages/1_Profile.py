import streamlit as st
import re  # for email validation

# Optional: for redirect
try:
    from streamlit_extras.switch_page_button import switch_page
except ImportError:
    switch_page = None

# --- Page config ---
st.set_page_config(page_title="Profile", page_icon="🌿")

# --- Custom CSS ---
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

# ✅ Fixed Email Validation Function
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

# --- UI: Title & Description ---
st.title("Create Your Profile")
st.write("Let us know a bit about you so we can personalize your carbon footprint journey.")

# --- Profile Form ---
with st.form("profile_form"):
    name = st.text_input("Full Name *", key="name")
    age = st.number_input("Age *", min_value=0, max_value=120, step=1, key="age")
    gender = st.selectbox("Gender *", ["-- Select --", "Female", "Male", "Other", "Prefer not to say"], key="gender")
    email = st.text_input("Email Address *", key="email")

    consent = st.checkbox(
        "I agree to participate in the carbon footprint analysis and share anonymous data for research.",
        key="consent"
    )

    submitted = st.form_submit_button("Save Profile")

# --- Form Submission Handling ---
if submitted:
    if not name or not email or gender == "-- Select --":
        st.warning("⚠️ Please fill in all required fields.")
    elif age == 0:
        st.warning("⚠️ Please enter a valid age.")
    elif not is_valid_email(email):
        st.warning("⚠️ Please enter a valid email address.")
    else:
        st.success(f"Thank you, {name}! Your profile has been saved.")

        # Save profile in session
        st.session_state["user_profile"] = {
            "name": name,
            "age": age,
            "gender": gender,
            "email": email,
            "consent": consent
        }

        # Set redirect flag
        st.session_state["go_to_calculator"] = True
        st.experimental_rerun()

# --- Redirect after save ---
if "go_to_calculator" in st.session_state and st.session_state["go_to_calculator"]:
    if switch_page is not None:
        st.session_state["go_to_calculator"] = False
        switch_page("Calculator")
    else:
        st.info("✅ Profile saved. Use the sidebar to go to the Calculator page.")
