
import pandas as pd
import streamlit as st

# Load DataFrames from GitHub
csv_url = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/emission_factor_formated.csv"
csv_url_1 = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered.csv"

try:
    df = pd.read_csv(csv_url)
    df1 = pd.read_csv(csv_url_1)
    st.success("Datasets Loaded Successfully")
except Exception as e:
    st.error(f"Error loading data: {e}")

# Function to format activity names
def format_activity_name(activity):
    activity_mappings = {
        "Domestic flight": "How many km of Domestic Flights taken the last month?",
        "International flight": "How many km of International Flights taken the last month?",
        "km_diesel_local_passenger_train_traveled": "How many km traveled by diesel-powered local passenger trains the last month?",
        "km_diesel_long_distance_passenger_train_traveled": "How many km traveled by diesel-powered long-distant passenger trains the last month?",
        "km_electric_passenger_train_traveled": "How many km traveled by electric-powered passenger trains the last month?",
        "km_bus_traveled": "How many km traveled by bus the last month?",
        "km_petrol_car_traveled": "How many km traveled by petrol-powered car the last month?",
        "km_Motorcycle_traveled": "How many km traveled by motorcycle the last month?",
        "km_ev_scooter_traveled": "How many km traveled by electric scooter the last month?",
        "km_ev_car_traveled": "How many km traveled by electric-powered car the last month?",
        "diesel_car_traveled": "How many km traveled by diesel-powered car the last month?",
        "water_consumed": "How much water consumed in liters the last month?",
        "electricity_used": "How much electricity used in kWh the last month?",
        "beef_products_consumed": "How much beef consumed in kg the last month?",
        "beverages_consumed": "How much beverages consumed in liters the last month?",
        "poultry_products_consumed": "How much poultry consumed in Kg the last month?",
        "pork_products_consumed": "How much pork have you consumed in kg the last month?",
        "processed_rice_consumed": "How much processed rice consumed in kg the last month?",
        "sugar_consumed": "How much sugar have you consumed in kg the last month?",
        "vegetable_oils_fats_consumed": "How much vegetable oils and fats consumed in kg the last month?",
        "other_meat_products_consumed":  "How much other meat products consumed in kg the last month?",
        "dairy_products_consumed": "How much dairy products consumed in kg the last month?",
        "fish_products_consumed": "How much fish products consumed in kg the last month?",
        "other_food_products_consumed": "How much other food products have you consumed in kg the last month?",
        "hotel_stay": "How many nights stayed in hotels the last month?"
    }
    return activity_mappings.get(activity, activity.replace("_", " ").capitalize())

# Streamlit UI
st.title("Carbon Footprint Calculator")

st.markdown("Calculate your carbon footprint and compare it to national and global averages!")

# Display an image
st.image('carbon_image.jpg', use_container_width=True)

# User details
name = st.text_input("Enter your name:")
mood = st.selectbox("How do you feel today?", ["Happy 😊", "Neutral 😐", "Concerned 😟"])

if not name or not mood:
    st.warning("Please enter your name and select your mood before proceeding.")
else:
    st.write(f"Welcome {name}! Let's calculate your Carbon Footprint.")

# Validate dataframe structure
if "Activity" not in df.columns or "Country" not in df1.columns:
    st.error("Error: Missing required columns in dataset!")
else:
    # Extract available countries
    available_countries = [col for col in df.columns if col != "Activity"]
    country = st.selectbox("Select a country:", available_countries)

    if country:
        # Initialize session state
        if "emission_values" not in st.session_state:
            st.session_state.emission_values = {}

        # User input for activities
        for activity in df["Activity"]:
            factor = df.loc[df["Activity"] == activity, country].values[0]
            activity_description = format_activity_name(activity)  # Use the formatting function
            user_input = st.number_input(f"{activity_description}:", min_value=0.0, step=0.1, key=activity)
            st.session_state.emission_values[activity] = user_input * factor

        # Calculate total emissions
        if st.button("Calculate Carbon Footprint"):
            total_emission = sum(st.session_state.emission_values.values())
            st.subheader(f"Your Carbon Footprint: {total_emission:.4f} tons CO₂")

            # Fetch per capita emissions safely
            def get_per_capita_emission(country_name):
                match = df1.loc[df1["Country"] == country_name, "PerCapitaCO2"]
                return match.iloc[0] if not match.empty else None

            country_avg = get_per_capita_emission(country)
            eu_avg = get_per_capita_emission("European Union (27)")
            world_avg = get_per_capita_emission("World")

            # Display comparison if data exists
            if country_avg is not None:
                st.subheader(f"Avg emission for {country}: {country_avg:.4f} tons CO₂")
            if eu_avg is not None:
                st.subheader(f"Avg emission for EU (27): {eu_avg:.4f} tons CO₂")
            if world_avg is not None:
                st.subheader(f"Avg emission for World: {world_avg:.4f} tons CO₂")
    else:
        st.warning("Please select a country.")
