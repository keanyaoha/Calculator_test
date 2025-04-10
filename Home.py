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

# --- Page Title ---
st.title("Welcome to GreenPrint")
st.subheader("Your Personal Carbon Footprint Tracker")

# --- Intro Content ---
st.markdown("""
 
**GreenPrint** is your interactive guide to understanding and reducing your environmental impact.  
With just a few quick questions about how you **live, travel, eat**, and **consume resources**, you'll get:

<br>

✅ **A personalized estimate** of your yearly carbon emissions  
📊 **A clear breakdown** of which habits contribute the most  
🌍 **Comparisons** with your country, Europe, and global averages  
🌱 **Practical tips** to reduce your footprint and live more sustainably.  

<be>

You can also
📄 **Download a PDF report** containing your calculation and personalized recommendations  
🤖 **GreenPrint AI** to help answer your questions about your carbon footprint and offer real-time advice.

<br>

Whether you're just curious or committed to climate action, **GreenPrint** is here to support your journey.

---

### 🔍 What is a Carbon Footprint?

Your **carbon footprint** is the total amount of **greenhouse gases** released into the air because of your daily life.

Everyday things like:

- 🏠 **Using energy at home** (heating, electricity)
- 🚗 **Getting around** (cars, buses, flights)
- 🍔 **What you eat** (especially meat and dairy)
- 🛍️ **What you buy and throw away** (clothes, electronics, waste)

It's measured in **kg of CO₂ equivalent (CO₂e)** — a standard way to show how much impact your actions have on climate change.

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
""", unsafe_allow_html=True)

# --- Simulated Redirect to Profile using query param ---
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    if st.button("Next →", use_container_width=True):
        st.experimental_set_query_params(page="Profile")
        st.markdown('<meta http-equiv="refresh" content="0;url=./Profile">', unsafe_allow_html=True)
