import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

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

# --- Format question titles ---
def format_activity_name(activity):
    mapping = {
        "Domestic flight": "How many km of Domestic Flights taken the last month",
        "International flight": "How many km of International Flights taken the last month",
        "km_diesel_local_passenger_train_traveled": "How many km traveled by diesel-powered local passenger trains",
        "km_diesel_long_distance_passenger_train_traveled": "How many km traveled by diesel-powered long-distance passenger trains",
        "km_electric_passenger_train_traveled": "How many km traveled by electric-powered passenger trains",
        "km_bus_traveled": "How many km traveled by bus",
        "km_petrol_car_traveled": "How many km traveled by petrol-powered car",
        "km_Motorcycle_traveled": "How many km traveled by motorcycle",
        "km_ev_scooter_traveled": "How many km traveled by electric scooter",
        "km_ev_car_traveled": "How many km traveled by electric-powered car",
        "diesel_car_traveled": "How many km traveled by diesel-powered car",
        "water_consumed": "How much water consumed in liters",
        "electricity_used": "How much electricity used in kWh",
        "hotel_stay": "How many nights stayed in hotels"
    }
    return mapping.get(activity, activity.replace("_", " ").capitalize())

# --- UI Layout ---
st.title("Carbon Footprint Calculator")
st.markdown("Calculate your carbon footprint and compare it to national and global averages!")

# --- Step 1: Country Selection ---
st.markdown("### \U0001F30D Select your country of residence:")
def_country = "-- Select --"
country = st.selectbox(" ", [def_country] + available_countries)

# Initialize session tab index
if "tab_index" not in st.session_state:
    st.session_state.tab_index = 0

def next_tab():
    st.session_state.tab_index += 1

# Continue only if valid country is selected
if country != def_country:
    st.success(
        "✅ **Next steps:**\n"
        "Please go through the **Travel**, **Food**, **Energy & Water**, and **Other** tabs.\n"
        "Fill in any values relevant to you. When you're ready, click *\u201cCalculate My Carbon Footprint\u201d* at the bottom."
    )

    # --- Tabs ---
    tab_labels = ["\U0001F697 Travel", "\U0001F37D Food", "⚡ Energy & Water", "\U0001F3E8 Other"]
    tabs = st.tabs(tab_labels)

    # --- Travel Tab ---
    with tabs[0]:
        if st.session_state.tab_index == 0:
            travel_activities = [
                "Domestic flight", "International flight", "km_diesel_local_passenger_train_traveled",
                "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled",
                "km_bus_traveled", "km_petrol_car_traveled", "km_Motorcycle_traveled",
                "km_ev_scooter_traveled", "km_ev_car_traveled", "diesel_car_traveled"
            ]
            for activity in travel_activities:
                st.number_input(format_activity_name(activity), min_value=0.0, key=activity)
            st.button("Next →", on_click=next_tab)

    # --- Food Tab ---
    with tabs[1]:
        if st.session_state.tab_index == 1:
            diet_type = st.selectbox("\U0001F957 What is your diet type?", [
                "Select...", "Vegan", "Vegetarian", "Pescatarian", "Omnivore", "Heavy Meat Eater"])

            if diet_type != "Select...":
                st.markdown("#### Now please answer the following questions:")
                st.markdown("How much of the following foods do you consume on average per month?")

                base_foods = [
                    "processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed",
                    "other_food_products_consumed", "beverages_consumed"]

                diet_foods = {
                    "Vegan": [],
                    "Vegetarian": ["dairy_products_consumed", "other_meat_products_consumed"],
                    "Pescatarian": ["fish_products_consumed", "dairy_products_consumed"],
                    "Omnivore": ["beef_products_consumed", "poultry_products_consumed", "pork_products_consumed",
                                 "dairy_products_consumed", "fish_products_consumed"],
                    "Heavy Meat Eater": ["beef_products_consumed", "poultry_products_consumed", "pork_products_consumed",
                                         "dairy_products_consumed", "fish_products_consumed", "other_meat_products_consumed"]
                }

                food_activities = base_foods + diet_foods.get(diet_type, [])
                for activity in food_activities:
                    label = activity.replace("_", " ").replace("products", "").replace("consumed", "").strip().capitalize()
                    st.number_input(f"{label}", min_value=0.0, key=activity, format="%.1f")
            st.button("Next →", on_click=next_tab)

    # --- Energy & Water Tab ---
    with tabs[2]:
        if st.session_state.tab_index == 2:
            for activity in ["electricity_used", "water_consumed"]:
                st.number_input(format_activity_name(activity), min_value=0.0, key=activity)
            st.button("Next →", on_click=next_tab)

    # --- Other Tab ---
    with tabs[3]:
        if st.session_state.tab_index == 3:
            st.number_input(format_activity_name("hotel_stay"), min_value=0.0, key="hotel_stay")
