import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- App Config ---
st.set_page_config(page_title="Green Tomorrow", page_icon="🌿", layout="centered")

# --- Sidebar Branding ---
st.markdown("""
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
""", unsafe_allow_html=True)

# --- Load Data ---
CSV_URL = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/emission_factor_formated.csv"
AVG_URL = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered.csv"

try:
    df = pd.read_csv(CSV_URL)
    df_avg = pd.read_csv(AVG_URL)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- Format Activity Labels ---
def format_label(activity):
    return activity.replace("_", " ").replace("products", "").replace("consumed", "").capitalize()

# --- UI ---
st.title("Carbon Footprint Calculator 🌍")
name = st.text_input("What's your name?")
mood = st.selectbox("How do you feel today?", ["Happy 😊", "Neutral 😐", "Concerned 😟"])

if name and mood:
    st.success(f"Welcome, {name}! Let's calculate your footprint.")

    available_countries = [col for col in df.columns if col != "Activity"]
    country = st.selectbox("Choose your country:", available_countries)

    if country:
        # --- Initialize session ---
        if "emission_values" not in st.session_state:
            st.session_state.emission_values = {}

        st.markdown("### 📥 Enter your activity data (monthly):")
        for activity in df["Activity"]:
            label = format_label(activity)
            value = st.number_input(f"{label}", min_value=0.0, step=0.1, key=activity)
            st.session_state[activity] = value

        # --- Calculate Emissions ---
        if st.button("Calculate My Carbon Footprint"):
            total_emission = 0
            st.session_state.emission_values = {}

            for activity in df["Activity"]:
                user_val = st.session_state.get(activity, 0.0)
                factor = df.loc[df["Activity"] == activity, country].values[0]
                emission = user_val * factor
                st.session_state.emission_values[activity] = emission
                total_emission += emission

            st.subheader(f"🌍 Your Carbon Footprint: {total_emission:.1f} kg CO₂")

            trees_cut = total_emission / 21.77
            st.markdown(f"🌳 Equivalent to cutting down ~{trees_cut:.0f} trees!")

            def get_avg(c_name):
                match = df_avg.loc[df_avg["Country"] == c_name, "PerCapitaCO2"]
                return match.iloc[0] if not match.empty else None

            country_avg = get_avg(country)
            eu_avg = get_avg("European Union (27)")
            world_avg = get_avg("World")

            # --- Bar Chart ---
            labels = ["You", country, "EU (27)", "World"]
            values = [
                total_emission,
                country_avg if country_avg else 0,
                eu_avg if eu_avg else 0,
                world_avg if world_avg else 0
            ]

            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.barh(labels[::-1], values[::-1], color=["#4CAF50", "#4682B4", "#4682B4", "#4682B4"])
            ax.set_xlabel("Tons CO₂ per year")

            for bar in bars:
                width = bar.get_width()
                ax.text(width + 5, bar.get_y() + bar.get_height() / 2, f"{width:.1f}", va='center')

            st.pyplot(fig)
            st.markdown("<div style='text-align: center; color: gray;'>Comparison of your footprint vs averages</div>", unsafe_allow_html=True)
    else:
        st.info("Please select a country.")
else:
    st.warning("Please enter your name and mood to begin.")
