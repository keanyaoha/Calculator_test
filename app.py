import streamlit as st
import pandas as pd


# Title
st.title("Carbon FootPrint Calculator")

# Markdown
st.markdown("""
Show that you care about the Environment. Calculate your carbon footprint and get the ball rolling towards offsetting them.
""")

# List of 25 categorical activities
activities = ["km_domestic_flight_traveled",
"km_international_flight_traveled",
"km_diesel_local_passenger_train_traveled",
"km_diesel_long_distance_passenger_train_traveled",
"km_electric_passenger_train_traveled",
"km_bus_traveled",
"km_petrol_car_traveled",
"km_Motorcycle_traveled",
"km_ev_scooter_traveled",
"km_ev_car_traveled",
"diesel_car_traveled",
"water_consumed",
"electricity_used",
"beef_products_consumed",
"beverages_consumed",
"poultry_products_consumed",
"pork_products_consumed",
"processed_rice_consumed",
"sugar_consumed",
"vegetable_oils_fats_consumed",
"other_meat_products_consumed",
"dairy_products_consumed",
"fish_products_consumed",
"other_food_products_consumed",
"hotel_stay"]

csv_url = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/emission_factor_formated.csv"
emission_factor_formated = pd.read_csv(csv_url, index_col=0)
# User selects a country
available_countries = emission_factor_formated.columns[0:].tolist()  # Exclude 'Activity' column


# Streamlit dropdown
dropdown_value = st.selectbox("Select your country:", available_countries )
st.write(f"You selected: {dropdown_value}")


# Extract available countries
available_countries = emission_factor_formated.index.tolist()

# Streamlit dropdown for country selection
country = st.selectbox("Select a country:", available_countries)

if country:
    st.write(f"You selected: {country}")

    # Example activity names (Replace with actual ones)
    activities = emission_factor_formated.columns.tolist()
    numbers = []

    # Get user inputs for each activity
    for activity in activities:
        value = st.number_input(f"Enter value for {activity}:", min_value=0.0, step=0.1)
        numbers.append(value)

    # Calculate total emissions
    total = sum(num * factor for num, factor in zip(numbers, emission_factor_formated.loc[country]))
    st.write(f"Total emissions: {total}")

per_capita_EU_27 = per_capita_filtered.loc[per_capita_filtered["Country"] == "European Union (27)", "PerCapitaCO2"].item()
per_capita_World = per_capita_filtered.loc[per_capita_filtered["Country"] == "World", "PerCapitaCO2"].item()

# Display results
print(f"Your carbon footprint is: {total} kgCO2 equivalent")

print(f"Per Capita Emission for European Union (27) is: {per_capita_EU_27} kgCO2 equivalent")
print(f"Per Capita Emission for World is: {per_capita_World} kgCO2 equivalent")
