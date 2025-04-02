
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

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
        "other_meat_products_consumed":  "How much other meat products consumed in kg the last month",
        "dairy_products_consumed": "How much dairy products consumed in kg the last month",
        "fish_products_consumed": "How much fish products consumed in kg the last month",
        "other_food_products_consumed": "How much other food products have you consumed in kg the last month",
        "hotel_stay": "How many nights stayed in hotels the last month"
    }
    return activity_mappings.get(activity, activity.replace("_", " ").capitalize())

# Streamlit UI
st.title("Carbon Footprint Calculator")
st.markdown("Calculate your carbon footprint and compare it to national and global averages!")
st.image('carbon_image.jpg', use_container_width=True)

# User details
name = st.text_input("Enter your name:")
age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1)
gender = st.selectbox("Select your gender:", ["Prefer not to say", "Female", "Male", "Other"])

if not name or not age or not gender:
    st.warning("Please enter your name and age, and choose your gender before proceeding.")
else:
    st.write(f"Welcome {name} ({gender}, {age} years old)! Let's calculate your Carbon Footprint.")

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
                activity_description = format_activity_name(activity)
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

                # Add space before the chart
                st.markdown("<br><br>", unsafe_allow_html=True)

                # Create comparison bar chart
                labels = ['You', country, 'EU (27)', 'World']
                values = [
                    total_emission,
                    country_avg if country_avg is not None else 0,
                    eu_avg if eu_avg is not None else 0,
                    world_avg if world_avg is not None else 0
                ]

                # Determine user bar color based on comparison to world average
                user_color = '#4CAF50' if total_emission < values[3] else '#FF4B4B'  # green if less, red if more

                # Define colors for all bars
                colors = [user_color, '#4682B4', '#2E8B57', '#FFA500']  # You, Country, EU, World

                fig, ax = plt.subplots(figsize=(8, 5))
                bars = ax.bar(labels, values, color=colors, width=0.4)

                # Increase y-limit to give space for top labels
                ax.set_ylim(0, max(values) + 20)

                # Annotate each bar with its value
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.2f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 5),  # Offset above the bar
                                textcoords='offset points',
                                ha='center', va='bottom')

                ax.set_ylabel("Tons CO₂ per year")
                ax.set_title("Your Carbon Footprint vs. Averages")

                plt.tight_layout()
                st.pyplot(fig)
