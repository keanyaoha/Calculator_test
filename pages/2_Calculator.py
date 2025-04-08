import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- Styling ---
st.markdown("""
    <style>
        .stApp { background-color: white; }
        section[data-testid="stSidebar"] { background-color: #e8f8f5; }
        .unit-input input {
            padding-right: 40px !important;
        }
        .unit-label {
            position: relative;
            left: -35px;
            top: -34px;
            color: gray;
        }
    </style>
""", unsafe_allow_html=True)

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

# Continue only if valid country is selected
if country != def_country:
    st.success(
        "✅ **Next steps:**\n"
        "Please go through the **Travel**, **Food**, **Energy & Water**, and **Other** tabs.\n"
        "Fill in any values relevant to you. When you're ready, click *\u201cCalculate My Carbon Footprint\u201d* at the bottom."
    )

    # --- Tabs ---
    tabs = st.tabs(["\U0001F697 Travel", "\U0001F37D Food", "⚡ Energy & Water", "\U0001F3E8 Other"])

    # --- Travel Tab ---
    with tabs[0]:
        travel_activities = [
            "Domestic flight", "International flight", "km_diesel_local_passenger_train_traveled",
            "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled",
            "km_bus_traveled", "km_petrol_car_traveled", "km_Motorcycle_traveled",
            "km_ev_scooter_traveled", "km_ev_car_traveled", "diesel_car_traveled"
        ]
        for activity in travel_activities:
            st.number_input(format_activity_name(activity), min_value=0.0, key=activity)

    # --- Food Tab ---
    with tabs[1]:
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
                value = st.number_input(f"{label}", min_value=0.0, key=activity, format="%.1f")
                st.markdown(f"<div class='unit-label'>kg</div>", unsafe_allow_html=True)

    # --- Energy & Water Tab ---
    with tabs[2]:
        for activity in ["electricity_used", "water_consumed"]:
            st.number_input(format_activity_name(activity), min_value=0.0, key=activity)

    # --- Other Tab ---
    with tabs[3]:
        st.number_input(format_activity_name("hotel_stay"), min_value=0.0, key="hotel_stay")

    # --- Confirmation Checkbox ---
    st.markdown("---")
    confirmed = st.checkbox("I have reviewed all fields and want to calculate my footprint")
    calculate = st.button("Calculate My Carbon Footprint", disabled=not confirmed)

    if calculate:
        if "emission_values" not in st.session_state:
            st.session_state.emission_values = {}

        for activity in df["Activity"]:
            if activity in st.session_state:
                factor = df.loc[df["Activity"] == activity, country].values[0]
                user_input = st.session_state.get(activity, 0.0)
                st.session_state.emission_values[activity] = user_input * factor

        total_emission = sum(st.session_state.emission_values.values())
        st.subheader(f"\U0001F30D Your Carbon Footprint: {total_emission:.1f} kg CO₂")

        # Tree equivalent
        kg_co2 = total_emission * 1000
        trees_cut = kg_co2 / 21.77
        st.markdown(f"\U0001F333 **That’s equivalent to cutting down ~{trees_cut:.0f} trees!**")

        def get_per_capita_emission(country_name):
            match = df1.loc[df1["Country"] == country_name, "PerCapitaCO2"]
            return match.iloc[0] if not match.empty else None

        country_avg = get_per_capita_emission(country)
        eu_avg = get_per_capita_emission("European Union (27)")
        world_avg = get_per_capita_emission("World")

        labels = ['You', country, 'EU', 'World']
        values = [
            total_emission,
            country_avg if country_avg is not None else 0,
            eu_avg if eu_avg is not None else 0,
            world_avg if world_avg is not None else 0
        ]
        user_color = '#4CAF50' if total_emission < values[3] else '#FF4B4B'
        shared_color = '#4682B4'
        colors = [user_color] + [shared_color] * 3

        labels, values, colors = labels[::-1], values[::-1], colors[::-1]

        fig, ax = plt.subplots(figsize=(8, 3.2))
        bars = ax.barh(labels, values, color=colors, height=0.6)
        ax.set_xlim(0, max(values) + 0.1 * max(values))

        for bar in bars:
            width = bar.get_width()
            ax.annotate(f'{width:.1f}',
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(5, 0), textcoords='offset points',
                        ha='left', va='center')

        ax.set_xlabel("Tons CO₂ per year")
        ax.xaxis.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("""
            <div style='text-align: center; color: gray;'>
            Comparison of your estimated annual carbon footprint with national and global averages.
            </div>
        """, unsafe_allow_html=True)
