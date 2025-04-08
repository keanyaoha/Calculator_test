import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- Styling ---
st.markdown(
    """
    <style>
        .stApp { background-color: white; }
        section[data-testid="stSidebar"] { background-color: #e8f8f5; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Load data ---
csv_url = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/emission_factor_formated.csv"
csv_url_1 = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered_monthly.csv"

try:
    df = pd.read_csv(csv_url)
    df1 = pd.read_csv(csv_url_1)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- Format questions ---
def format_activity_name(activity):
    mapping = {
        "Domestic flight": "How many km of Domestic Flights taken the last month",
        "International flight": "How many km of International Flights taken the last month",
        "km_diesel_local_passenger_train_traveled": "How many km traveled by diesel-powered local passenger trains the last month",
        "km_diesel_long_distance_passenger_train_traveled": "How many km traveled by diesel-powered long-distant passenger trains the last month",
        "km_electric_passenger_train_traveled": "How many km traveled by electric-powered passenger trains the last month",
        "km_bus_traveled": "How many km traveled by bus the last month",
        "km_petrol_car_traveled": "How many km traveled by petrol-powered car the last month",
        "km_Motorcycle_traveled": "How many km traveled by motorcycle the last month",
        "km_ev_scooter_traveled": "How many km traveled by electric scooter the last month",
        "km_ev_car_traveled": "How many km traveled by electric-powered car the last month",
        "diesel_car_traveled": "How many km traveled by diesel-powered car the last month",
        "water_consumed": "How much water consumed in liters the last month",
        "electricity_used": "How much electricity used in kWh the last month",
        "beef_products_consumed": "How much beef consumed in kg the last month",
        "beverages_consumed": "How much beverages consumed in liters the last month",
        "poultry_products_consumed": "How much poultry consumed in Kg the last month",
        "pork_products_consumed": "How much pork have you consumed in kg the last month",
        "processed_rice_consumed": "How much processed rice consumed in kg the last month",
        "sugar_consumed": "How much sugar have you consumed in kg the last month",
        "vegetable_oils_fats_consumed": "How much vegetable oils and fats consumed in kg the last month",
        "other_meat_products_consumed": "How much other meat products consumed in kg the last month",
        "dairy_products_consumed": "How much dairy products consumed in kg the last month",
        "fish_products_consumed": "How much fish products consumed in kg the last month",
        "other_food_products_consumed": "How much other food products have you consumed in kg the last month",
        "hotel_stay": "How many nights stayed in hotels the last month"
    }
    return mapping.get(activity, activity.replace("_", " ").capitalize())

# --- Inputs ---
st.title("Carbon Footprint Calculator")
st.image('carbon_image.jpg', use_container_width=True)
st.markdown("Calculate your carbon footprint and compare it to national and global averages!")

if "Activity" not in df.columns or "Country" not in df1.columns:
    st.error("Error: Missing required columns in dataset!")
    st.stop()

available_countries = [col for col in df.columns if col != "Activity"]
country = st.selectbox("🌍 Select a country:", available_countries)

# --- Define activity groups ---
activity_groups = {
    "🚗 Travel": [
        "Domestic flight", "International flight", "km_diesel_local_passenger_train_traveled",
        "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled",
        "km_bus_traveled", "km_petrol_car_traveled", "km_Motorcycle_traveled",
        "km_ev_scooter_traveled", "km_ev_car_traveled", "diesel_car_traveled"
    ],
    "🍽️ Food": [
        "beef_products_consumed", "poultry_products_consumed", "pork_products_consumed",
        "processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed",
        "other_meat_products_consumed", "dairy_products_consumed", "fish_products_consumed",
        "other_food_products_consumed", "beverages_consumed"
    ],
    "⚡ Energy & Water": ["electricity_used", "water_consumed"],
    "🏨 Other": ["hotel_stay"]
}

# --- Create tabs and inputs ---
tabs = st.tabs(list(activity_groups.keys()))
user_inputs = {}

for tab, label in zip(tabs, activity_groups.keys()):
    with tab:
        for activity in activity_groups[label]:
            formatted = format_activity_name(activity)
            user_inputs[activity] = st.number_input(formatted, min_value=0.0, key=activity)

# --- Only show the button if at least one field is filled ---
any_input = any(value > 0 for value in user_inputs.values())
st.markdown("----")

if st.button("🌍 Calculate My Carbon Footprint", disabled=not any_input):
    emission_values = {}
    for activity, input_val in user_inputs.items():
        factor = df.loc[df["Activity"] == activity, country].values[0]
        emission_values[activity] = input_val * factor

    total_emission = sum(emission_values.values())
    st.subheader(f"🌿 Your Carbon Footprint: **{total_emission:.4f} tons CO₂**")

    # 🌳 Tree equivalence
    kg_co2 = total_emission * 1000
    trees_cut = kg_co2 / 21.77
    st.markdown(f"🌲 That’s equivalent to cutting down ~**{trees_cut:.0f} trees**!")

    # --- Averages ---
    def get_per_capita_emission(c):
        match = df1.loc[df1["Country"] == c, "PerCapitaCO2"]
        return match.iloc[0] if not match.empty else None

    country_avg = get_per_capita_emission(country)
    eu_avg = get_per_capita_emission("European Union (27)")
    world_avg = get_per_capita_emission("World")

    if country_avg: st.subheader(f"🇨🇵 {country} Avg: {country_avg:.4f} tons CO₂")
    if eu_avg: st.subheader(f"🇪🇺 EU Avg: {eu_avg:.4f} tons CO₂")
    if world_avg: st.subheader(f"🌍 World Avg: {world_avg:.4f} tons CO₂")

    # --- Comparison Chart ---
    import matplotlib.pyplot as plt
    labels = ['You', country, 'EU', 'World']
    values = [total_emission, country_avg or 0, eu_avg or 0, world_avg or 0]
    colors = ['#4CAF50'] + ['#4682B4'] * 3

    labels.reverse()
    values.reverse()
    colors.reverse()

    fig, ax = plt.subplots(figsize=(8, 3.2))
    bars = ax.barh(labels, values, color=colors, height=0.6)
    ax.set_xlim(0, max(values) * 1.1)
    for bar in bars:
        ax.annotate(f'{bar.get_width():.2f}',
                    xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords='offset points',
                    ha='left', va='center')
    ax.set_xlabel("Tons CO₂ per year")
    ax.xaxis.grid(True, linestyle='--', alpha=0.3)
    st.pyplot(fig)

    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Comparison of your estimated annual carbon footprint with national and global averages."
        "</div>",
        unsafe_allow_html=True
    )
