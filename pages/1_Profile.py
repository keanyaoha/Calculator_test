import streamlit as st
import re

# --- App Config ---
st.set_page_config(
    page_title="Green Tomorrow",
    page_icon="🌿",
    layout="centered"
)

# --- Force Logo to Appear at Top of Sidebar ---
st.markdown(
    """
    <style>
        [data-testid="stSidebar"]::before {
            content: "";
            display: block;
            background-image: url('https://raw.githubusercontent.com/GhazalMoradi8/Carbon_Footprint_Calculator/main/GreenPrint_logo.png');
            background-size: 90% auto;
            background-repeat: no-repeat;
            background-position: center;
            height: 140px;
            margin: 1.5rem auto -4rem auto;  /* SUPER tight top & bottom spacing */
        }

        section[data-testid="stSidebar"] {
            background-color: #d6f5ec;
        }

        .stApp {
            background-color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Initialize session state if not already set ---
if "profile_completed" not in st.session_state:
    st.session_state.profile_completed = False

# ✅ Fixed Email Validation
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

# --- Page Title ---
st.title("Create Your Profile")
st.write("Please fill out the following information to help us calculate your carbon footprint.")

# --- Profile Form ---
with st.form("profile_form"):
    name = st.text_input("Your Name *", key="name")
    age = st.number_input("Age *", min_value=0, max_value=120, step=1, key="age")
    gender = st.selectbox("Gender *", ["-- Select --", "Female", "Male", "Other", "Prefer not to say"], key="gender")
    email = st.text_input("Email Address *", key="email")

    consent = st.checkbox(
        "I agree to participate in the carbon footprint analysis and share anonymous data for research.",
        key="consent"
    )

    submitted = st.form_submit_button("Save Profile")

# --- Handle Form Submission ---
if submitted:
    if not name or not email or gender == "-- Select --":
        st.warning("⚠️ Please fill in all required fields.")
    elif age == 0:
        st.warning("⚠️ Please enter a valid age.")
    elif not is_valid_email(email):
        st.warning("⚠️ Please enter a valid email address.")
    else:
        st.success(f"Thank you, {name}! Your profile has been saved.")

        # Save user profile in session state
        st.session_state["user_profile"] = {
            "name": name,
            "age": age,
            "gender": gender,
            "email": email,
            "consent": consent
        }

        # Mark profile as completed
        st.session_state.profile_completed = True  # Ensure this flag is set to True

        # Trigger "redirect" to calculator page
        st.session_state["go_to_calculator"] = True

        # Simulate a redirect without rerun
        st.experimental_rerun()  # Use experimental_rerun to reload the page

# --- Simulated Redirect ---
if st.session_state.get("go_to_calculator"):
    st.session_state["go_to_calculator"] = False  # reset flag

    st.markdown("✅ Profile saved. Redirecting to Calculator page...")
    st.markdown(
        """
        <meta http-equiv="refresh" content="0; url=/Calculator">
        """,
        unsafe_allow_html=True
    )
