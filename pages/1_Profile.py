import streamlit as st
import re

# --- App Config ---
st.set_page_config(
    page_title="Green Tomorrow",
    page_icon="🌿",
    layout="centered"
)

# --- Email Validation ---
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

    consent = st.checkbox("I agree to participate in the carbon footprint analysis and share anonymous data for research.", key="consent")

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

        # Save the user profile in session state
        st.session_state["user_profile"] = {
            "name": name,
            "age": age,
            "gender": gender,
            "email": email,
            "consent": consent
        }

        # Mark profile as completed
        st.session_state.profile_completed = True  # Ensure this flag is set to True

        # Add a success message with redirection
        st.success("You can now proceed to the Calculator page.")
        
        # Trigger the page to refresh so it updates the session state correctly
        st.experimental_rerun()
