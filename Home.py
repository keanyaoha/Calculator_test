import streamlit as st

st.set_page_config(
    page_title="Green Tomorrow",
    page_icon="🌿",
    layout="centered"
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: white;  /* main content area */
        }
        section[data-testid="stSidebar"] {
            background-color: #e8f8f5;  /* soft green sidebar */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- App Overview Section ---
st.title("🌍 Welcome to Green Tomorrow")
st.subheader("Your Personal Carbon Footprint Tracker")

st.markdown("""
**Green Tomorrow** is an interactive tool designed to help you measure your **carbon footprint** — the total amount of greenhouse gases, primarily carbon dioxide, that your lifestyle and choices emit into the atmosphere.

---

### 🧠 What is a Carbon Footprint?

A **carbon footprint** includes emissions from:
- 🏠 Household energy use (heating, electricity)
- 🚗 Transportation (car, flights, public transport)
- 🍔 Food and consumption habits
- 🛒 Shopping, waste, and more

It's measured in **tons of CO₂ equivalent (CO₂e)**.

---

### 🚨 Why It Matters

The higher our carbon footprint, the more we contribute to climate change. By understanding your own emissions, you can:

- Reduce your environmental impact
- Save money through efficient choices
- Join the global effort to combat the climate crisis

---

### 🛠️ How This App Works

1. Go to the **Calculator** page and enter details about your daily habits.
2. Get an estimate of your **annual carbon footprint**.
3. Compare your score to **national and global averages**.
4. See personalized suggestions on how to **reduce** it.

---

### 🌿 Ready to make a difference?

Start by heading to the **Calculator** page in the sidebar!
""")

