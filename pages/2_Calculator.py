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

# --- Initialize profile_completed if not already done ---
if "profile_completed" not in st.session_state:
    st.session_state.profile_completed = False  # Set to False initially if not defined

# --- Load Emission Data ---
CSV_URL = "https://drive.google.com/uc?export=download&id=1PWeBZKB6adZKORvtMDLFwCX__gfzH33g"
PER_CAPITA_URL = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered_monthly.csv"

try:
    df = pd.read_csv(CSV_URL)
    df1 = pd.read_csv(PER_CAPITA_URL)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Clean the column names (removing any extra spaces or unexpected characters)
df.columns = df.columns.str.strip()

# Get available countries (i.e., columns excluding 'Activity')
available_countries = [col for col in df.columns if col != "Activity"]

# --- Format Activity Titles ---
def format_activity_name(activity):
    mapping = {
        "Domestic_flight_traveled": "How many km of Domestic Flights taken last month",
        "International_flight_traveled": "How many km of International Flights taken last month",
        "km_diesel_local_passenger_train_traveled": "How many km by diesel-powered local trains",
        "km_diesel_long_distance_passenger_train_traveled": "How many km by diesel-powered long-distance trains",
        "km_electric_passenger_train_traveled": "How many km by electric-powered trains",
        "km_bus_traveled": "How many km by bus",
        "km_petrol_car_traveled": "How many km by petrol-powered car",
        "km_Motorcycle_traveled": "How many km by motorcycle",
        "km_ev_scooter_traveled": "How many km by electric scooter",
        "km_ev_car_traveled": "How many km by electric car",
        "diesel_car_traveled": "How many km by diesel-powered car",
        "beef_products_consumed": "How much beef products consumed (kg)",
        "poultry_products_consumed": "How much poultry products consumed (kg)",
        "pork_products_consumed": "How much pork products consumed (kg)",
        "fish_products_consumed": "How much fish products consumed (kg)",
        "other_meat_products_consumed": "How much other meat products consumed (kg)",
        "processed_rice_consumed": "How much processed rice consumed (kg)",
        "sugar_consumed": "How much sugar consumed (kg)",
        "vegetable_oils_fats_consumed": "How much vegetable oils/fats consumed (kg)",
        "dairy_products_consumed": "How much dairy products consumed (kg)",
        "other_food_products_consumed": "How much other food products consumed (kg)",
        "water_consumed": "How much water consumed (liters)",
        "electricity_used": "How much electricity used (kWh)",
        "hotel_stay": "How many nights in hotels",
    }
    return mapping.get(activity, activity.replace("_", " ").capitalize())

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

# --- Tab Switching Logic ---
if "current_tab" not in st.session_state:
    st.session_state.current_tab = 0  # Default to the first tab

tab_labels = ["Transport", "Food", "Energy & Water", "Hotel"]
tab_content = [
    "Transport-related activities",
    "Food-related activities",
    "Energy and Water-related activities",
    "Hotel-related activities"
]

# Show the current tab
tab1, tab2, tab3, tab4 = st.tabs(tab_labels)

# Transport Tab
with tab1:
    transport_activities = ["Domestic_flight_traveled", "International_flight_traveled", "km_diesel_local_passenger_train_traveled", 
        "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled", 
        "km_bus_traveled", "km_petrol_car_traveled", "km_Motorcycle_traveled", 
        "km_ev_scooter_traveled", "km_ev_car_traveled", "diesel_car_traveled"]
    
    for activity in transport_activities:
        label = format_activity_name(activity)
        user_input = st.number_input(label, min_value=0.0, step=0.1, key=f"transport_{activity}")
        try:
            factor = df.loc[df["Activity"] == activity, country].values[0]
            st.session_state.emission_values[activity] = user_input * factor
        except IndexError:
            st.error(f"Error fetching data for activity: {activity} and country: {country}")

    if st.button("Next"):
        st.session_state.current_tab = 1  # Move to the next tab

# Food Tab
with tab2:
    food_activities = [
        "beef_products_consumed", "poultry_products_consumed", "pork_products_consumed",
        "processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed", 
        "other_meat_products_consumed", "dairy_products_consumed", "fish_products_consumed", 
        "other_food_products_consumed"
    ]
    
    for activity in food_activities:
        label = format_activity_name(activity)
        user_input = st.number_input(label, min_value=0.0, step=0.1, key=f"food_{activity}")
        try:
            factor = df.loc[df["Activity"] == activity, country].values[0]
            st.session_state.emission_values[activity] = user_input * factor
        except IndexError:
            st.error(f"Error fetching data for activity: {activity} and country: {country}")

    if st.button("Next"):
        st.session_state.current_tab = 2  # Move to the next tab

# Energy and Water Tab
with tab3:
    energy_water_activities = ["electricity_used", "water_consumed"]
    
    for activity in energy_water_activities:
        label = format_activity_name(activity)
        user_input = st.number_input(label, min_value=0.0, step=0.1, key=f"energy_{activity}")
        try:
            factor = df.loc[df["Activity"] == activity, country].values[0]
            st.session_state.emission_values[activity] = user_input * factor
        except IndexError:
            st.error(f"Error fetching data for activity: {activity} and country: {country}")

    if st.button("Next"):
        st.session_state.current_tab = 3  # Move to the next tab

# Hotel Tab
with tab4:
    hotel_activities = ["hotel_stay"]
    for activity in hotel_activities:
        label = format_activity_name(activity)
        user_input = st.number_input(label, min_value=0.0, step=0.1, key=f"hotel_{activity}")
        try:
            factor = df.loc[df["Activity"] == activity, country].values[0]
            st.session_state.emission_values[activity] = user_input * factor
        except IndexError:
            st.error(f"Error fetching data for activity: {activity} and country: {country}")

# --- Checkbox to enable "Calculate My Carbon Footprint" button ---
reviewed_all = st.checkbox("I have reviewed all the questions above.")

# --- Calculate Emissions Button ---
if reviewed_all:
    if st.button("Calculate My Carbon Footprint"):
        emission_values = st.session_state.emission_values
        total_emission = sum(emission_values.values())
        st.subheader(f"Your Carbon Footprint: **{total_emission:.1f} kg CO₂**")

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
else:
    st.warning("Please review all the questions before calculating your carbon footprint.")
