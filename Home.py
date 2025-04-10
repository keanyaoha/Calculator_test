import streamlit as st

# --- App Config ---
st.set_page_config(
    page_title="Green Tomorrow",
    page_icon="🌿",
    layout="centered"
)

# --- Custom Sidebar Logo + Background ---
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
            margin: 1.5rem auto -4rem auto;
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

# --- Track session state ---
if "profile_completed" not in st.session_state:
    st.session_state.profile_completed = False
if "calculator_completed" not in st.session_state:
    st.session_state.calculator_completed = False
if "tab_index" not in st.session_state:
    st.session_state.tab_index = 0

# --- Page Title ---
st.title("Welcome to GreenPrint")
st.subheader("Your Personal Carbon Footprint Tracker")


# --- Tab Content ---
with tab:
    if st.session_state.tab_index == 0:  # Profile
        st.markdown("""
        **GreenPrint** is an interactive tool designed to help you measure your **carbon footprint** — the total amount of greenhouse gases, primarily carbon dioxide, that your lifestyle and choices emit into the atmosphere.

        ---

        ### 🧠 What is a Carbon Footprint?

        A **carbon footprint** includes emissions from:
        - 🏠 Household energy use (heating, electricity)
        - 🚗 Transportation (car, flights, public transport)
        - 🍔 Food and consumption habits
        - 🛒 Shopping, waste, and more

        It's measured in **kg of CO₂ equivalent (CO₂e)**.

        ---

        ### 🚨 Why It Matters

        The higher our carbon footprint, the more we contribute to climate change. By understanding your own emissions, you can:

        - Reduce your environmental impact  
        - Save money through efficient choices  
        - Join the global effort to combat the climate crisis  

        ---

        ### 🛠️ How This App Works

        1. Go to the **Profile** page and create your profile, which brings you directly to the **Calculator** and enter details about your daily habits.  
        2. Get an estimate of your **annual carbon footprint**.  
        3. Compare your score to **national and global averages**.  
        4. See personalized suggestions on how to **reduce** it.

        ---

        ### 🌿 Ready to make a difference?

        Click **Next →** to start your profile.
        """)

    elif st.session_state.tab_index == 1:  # Calculator
        if not st.session_state.profile_completed:
            st.warning("🚫 Please complete your profile first.")
        else:
            st.success("✅ You may now proceed to the Calculator tab via the sidebar.")
            st.markdown("👉 Or you can navigate using the **Calculator** tab on the left.")

    elif st.session_state.tab_index == 2:  # Breakdown
        if not st.session_state.calculator_completed:
            st.warning("🚫 Please complete the calculator before viewing breakdown results.")
        else:
            st.success("✅ You can now view your carbon emission breakdown!")

# --- Navigation Buttons ---
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    col_prev, col_next = st.columns(2)

    with col_prev:
        if st.session_state.tab_index > 0:
            if st.button("← Previous", use_container_width=True):
                st.session_state.tab_index -= 1
                st.rerun()

    with col_next:
        if st.session_state.tab_index < len(tab_labels) - 1:
            if st.button("Next →", use_container_width=True):
                st.session_state.tab_index += 1
                st.rerun()
