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

# --- Question formatter ---
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
        "hotel_stay": "How many nights stayed in hotels the last month"
    }
    return mapping.get(activity, activity.replace("_", " ").capitalize())

# --- UI Layout ---
st.title("Carbon Footprint Calculator")
st.image('carbon_image.jpg', use_container_width=True)
st.markdown("Calculate your carbon footprint and compare it to national and global averages!")

# --- Country selection ---
if "Activity" not in df.columns or "Country" not in df1.columns:
    st.error("Error: Missing required columns in dataset!")
    st.stop()

available_countries = [col for col in df.columns if col != "Activity"]
country = st.selectbox("\U0001F30D Select a country:", available_countries)

# --- Define tabs ---
tabs = st.tabs(["\U0001F697 Travel", "\U0001F37D Food", "\u26A1 Energy & Water", "\U0001F3E8 Other"])

# --- Travel tab inputs ---
with tabs[0]:
    travel_activities = [
        "Domestic flight", "International flight", "km_diesel_local_passenger_train_traveled",
        "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled",
        "km_bus_traveled", "km_petrol_car_traveled", "km_Motorcycle_traveled",
        "km_ev_scooter_traveled", "km_ev_car_traveled", "diesel_car_traveled"
    ]
    for activity in travel_activities:
        st.number_input(format_activity_name(activity), min_value=0.0, key=activity)

# --- Food tab with simplified layout ---
with tabs[1]:
    diet_type = st.selectbox("\U0001F957 What is your diet type?", [
        "Select...", "Vegan", "Vegetarian", "Pescatarian", "Omnivore", "Heavy Meat Eater"
    ])

    if diet_type != "import pandas as pd
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

# --- Question formatter ---
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
        "hotel_stay": "How many nights stayed in hotels the last month"
    }
    return mapping.get(activity, activity.replace("_", " ").capitalize())

# --- UI Layout ---
st.title("Carbon Footprint Calculator")
st.image('carbon_image.jpg', use_container_width=True)
st.markdown("Calculate your carbon footprint and compare it to national and global averages!")

# --- Country selection ---
if "Activity" not in df.columns or "Country" not in df1.columns:
    st.error("Error: Missing required columns in dataset!")
    st.stop()

available_countries = [col for col in df.columns if col != "Activity"]
country = st.selectbox("\U0001F30D Select a country:", available_countries)

# --- Define tabs ---
tabs = st.tabs(["\U0001F697 Travel", "\U0001F37D Food", "\u26A1 Energy & Water", "\U0001F3E8 Other"])

# --- Travel tab inputs ---
with tabs[0]:
    travel_activities = [
        "Domestic flight", "International flight", "km_diesel_local_passenger_train_traveled",
        "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled",
        "km_bus_traveled", "km_petrol_car_traveled", "km_Motorcycle_traveled",
        "km_ev_scooter_traveled", "km_ev_car_traveled", "diesel_car_traveled"
    ]
    for activity in travel_activities:
        st.number_input(format_activity_name(activity), min_value=0.0, key=activity)

# --- Food tab with simplified layout ---
with tabs[1]:
    diet_type = st.selectbox("\U0001F957 What is your diet type?", [
        "Select...", "Vegan", "Vegetarian", "Pescatarian", "Omnivore", "Heavy Meat Eater"
    ])

    if diet_type != "-- Select --":
        st.markdown("#### Now please answer the following questions:")
        st.markdown("How much of the following foods do you consume on average per month?")

        base_foods = [
            "processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed",
            "other_food_products_consumed", "beverages_consumed"
        ]

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
            st.number_input(f"{label} (kg)", min_value=0.0, key=activity)

# --- Energy & Water tab ---
with tabs[2]:
    for activity in ["electricity_used", "water_consumed"]:
        st.number_input(format_activity_name(activity), min_value=0.0, key=activity)

# --- Other tab ---
with tabs[3]:
    st.number_input(format_activity_name("hotel_stay"), min_value=0.0, key="hotel_stay")
":
        st.markdown("#### Now please answer the following questions:")
        st.markdown("How much of the following foods do you consume on average per month?")

        base_foods = [
            "processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed",
            "other_food_products_consumed", "beverages_consumed"
        ]

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
            st.number_input(f"{label} (kg)", min_value=0.0, key=activity)

# --- Energy & Water tab ---
with tabs[2]:
    for activity in ["electricity_used", "water_consumed"]:
        st.number_input(format_activity_name(activity), min_value=0.0, key=activity)

# --- Other tab ---
with tabs[3]:
    st.number_input(format_activity_name("hotel_stay"), min_value=0.0, key="hotel_stay")
