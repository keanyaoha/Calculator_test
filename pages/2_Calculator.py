import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- App Config ---
st.set_page_config(page_title="GreenPrint", page_icon="🌿", layout="centered")

# --- Sidebar Logo Styling ---
st.markdown(
    """
    <style>
        [data-testid="stSidebar"]::before {
            content: "";
            display: block;
            background-image: url('/static/GreenPrint_logo.png');
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
# --- Load Data ---
csv_url = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/emission_factor_formated.csv"
csv_url_1 = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered_monthly.csv"

try:
    df = pd.read_csv(csv_url)
    df1 = pd.read_csv(csv_url_1)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

available_countries = [col for col in df.columns if col != "Activity"]

# Function to format activity names
def format_activity_name(activity):
    activity_mappings = {
        "Domestic_flight": "How many km of Domestic Flights taken the last month",
        "International_flight": "How many km of International Flights taken the last month",
        "Diesel_train_local": "How many km traveled by diesel-powered local passenger trains the last month",
        "Diesel_train_long": "How many km traveled by diesel-powered long-distant passenger trains the last month",
        "Electric_train": "How many km traveled by electric-powered passenger trains the last month",
        "Bus": "How many km traveled by bus the last month",
        "Petrol_car": "How many km traveled by petrol-powered car the last month",
        "Motorcycle": "How many km traveled by motorcycle the last month",
        "Ev_scooter": "How many km traveled by electric scooter the last month",
        "Ev_car": "How many km traveled by electric-powered car the last month",
        "Diesel_car": "How many km traveled by diesel-powered car the last month",
        "Water": "How much water consumed in liters the last month",
        "Electricity": "How much electricity used in kWh the last month",
        "Beef": "How much beef consumed in kg the last month",
        "Beverages": "How much beverages consumed in liters the last month",
        "Poultry": "How much poultry consumed in Kg the last month",
        "Pork": "How much pork have you consumed in kg the last month",
        "Rice": "How much processed rice consumed in kg the last month",
        "Sugar": "How much sugar have you consumed in kg the last month",
        "Oils_fats": "How much vegetable oils and fats consumed in kg the last month",
        "Other_meat": "How much other meat products consumed in kg the last month",
        "Dairy": "How much dairy products consumed in kg the last month",
        "Fish_products": "How much fish products consumed in kg the last month",
        "Other_food": "How much other food products have you consumed in kg the last month",
        "Hotel_stay": "How many nights stayed in hotels the last month"
    }
    return activity_mappings.get(activity, activity.replace("_", " ").capitalize())


# --- App Title ---
st.title("🌍 Carbon Footprint Calculator")
st.markdown("Estimate your monthly carbon footprint and compare it to country and global averages.")

# --- Country Selection ---
country = st.selectbox("Select your country:", ["-- Select --"] + available_countries)
if country == "-- Select --":
    st.stop()

# --- User Input for Activities ---
if "emission_values" not in st.session_state:
    st.session_state.emission_values = {}

st.markdown("### ✏️ Fill in your monthly activity data:")
for activity in df["Activity"]:
    label = format_activity_name(activity)
    user_input = st.number_input(label, min_value=0.0, step=0.1, key=activity)
    factor = df.loc[df["Activity"] == activity, country].values[0]
    st.session_state.emission_values[activity] = user_input * factor

# --- Calculate Emissions ---
if st.button("📊 Calculate My Carbon Footprint"):
    emission_values = st.session_state.emission_values
    total_emission = sum(emission_values.values())
    st.subheader(f"🌱 Your Carbon Footprint: **{total_emission:.1f} kg CO₂**")

    trees_cut = total_emission / 21.77
    st.markdown(f"🌳 Equivalent to cutting down ~**{trees_cut:.0f} trees**!")

    # --- Compare to Averages ---
    def get_avg(name):
        match = df1.loc[df1["Country"] == name, "PerCapitaCO2"]
        return match.iloc[0] if not match.empty else 0

    country_avg = get_avg(country)
    eu_avg = get_avg("European Union (27)")
    world_avg = get_avg("World")

    # Plot comparison chart
    labels = ["You", country, "EU", "World"]
    values = [total_emission, country_avg, eu_avg, world_avg]
    colors = ['#4CAF50'] + ['#4682B4'] * 3

    labels, values, colors = labels[::-1], values[::-1], colors[::-1]
    fig, ax = plt.subplots(figsize=(8, 3))
    bars = ax.barh(labels, values, color=colors)
    ax.set_xlim(0, max(values) * 1.1)

    for bar in bars:
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2, f"{bar.get_width():.1f}", va='center')

    ax.set_xlabel("kg CO₂ per month")
    st.pyplot(fig)

    st.markdown("<div style='text-align: center; color: gray;'>Comparison of your estimated monthly carbon footprint with national and global averages.</div>", unsafe_allow_html=True)
