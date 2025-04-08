import streamlit as st

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

# --- Main App Content ---
st.title("Welcome to GreenPrint")
st.subheader("Your Personal Carbon Footprint Tracker")

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

Start by heading to the **Profile** page in the sidebar!
""")
