import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- App Config ---
st.set_page_config(
    page_title="Green Tomorrow",
    page_icon="🌿",
    layout="centered"
)

# --- Logo & Styles ---
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
csv_url = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/emission_factor_formated.csv"
per_capita_url = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered_monthly.csv"

try:
    df = pd.read_csv(csv_url)
    df1 = pd.read_csv(per_capita_url)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

available_countries = [col for col in df.columns if col != "Activity"]

# --- Format input labels ---
def format_activity_name(activity):
    mapping = {
        "Domestic flight": "How many km of Domestic Flights taken the last month",
        "International flight": "How many km of International Flights taken the last month",
        "km_diesel_local_passenger_train_traveled": "How many km traveled by diesel-powered local trains",
        "km_diesel_long_distance_passenger_train_traveled": "How many km traveled by diesel long-distance trains",
        "km_electric_passenger_train_traveled": "How many km traveled by electric trains",
        "km_bus_traveled": "How many km traveled by bus",
        "km_petrol_car_traveled": "How many km traveled by petrol car",
        "km_Motorcycle_traveled": "How many km traveled by motorcycle",
        "km_ev_scooter_traveled": "How many km traveled by electric scooter",
        "km_ev_car_traveled": "How many km traveled by electric car",
        "diesel_car_traveled": "How many km traveled by diesel car",
        "water_consumed": "How much water consumed (liters)",
        "electricity_used": "How much electricity used (kWh)",
        "hotel_stay": "How many nights stayed in hotels"
    }
    return mapping.get(activity, activity.replace("_", " ").capitalize())

# --- UI Layout ---
st.title("Carbon Footprint Calculator")
st.markdown("Calculate your carbon footprint and compare it to national and global averages!")

# --- Country Selection ---
st.markdown("### 🌍 Select your country of residence:")
def_country = "-- Select --"
country = st.selectbox(" ", [def_country] + available_countries)

if country != def_country:
    st.success("✅ **Next steps:**\nPlease go through the **Travel**, **Food**, **Energy & Water**, and **Other** tabs.\nFill in values relevant to you. When ready, click *“Calculate My Carbon Footprint”* at the bottom.")

    # Maintain tab state
    if "tab_index" not in st.session_state:
        st.session_state.tab_index = 0

    tabs = ["\U0001F697 Travel", "\U0001F37D Food", "\u26a1 Energy & Water", "\U0001F3E8 Other"]
    current_tab = st.session_state.tab_index
    tab_title = tabs[current_tab]
    st.header(tab_title.split(" ", 1)[-1])

    # Input Activities
    travel_activities = [
        "Domestic flight", "International flight", "km_diesel_local_passenger_train_traveled",
        "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled",
        "km_bus_traveled", "km_petrol_car_traveled", "km_Motorcycle_traveled",
        "km_ev_scooter_traveled", "km_ev_car_traveled", "diesel_car_traveled"
    ]
    energy_activities = ["electricity_used", "water_consumed"]
    other_activities = ["hotel_stay"]

    if current_tab == 0:
        for a in travel_activities:
            st.number_input(format_activity_name(a), min_value=0.0, key=f"travel_{a}")
    elif current_tab == 1:
        diet_type = st.selectbox("🥗 What is your diet type?", ["Select...", "Vegan", "Vegetarian", "Pescatarian", "Omnivore", "Heavy Meat Eater"])
        if diet_type != "Select...":
            st.markdown("#### How much of the following do you consume per month?")
            base_foods = ["processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed", "other_food_products_consumed", "beverages_consumed"]
            diet_foods = {
                "Vegan": [],
                "Vegetarian": ["dairy_products_consumed", "other_meat_products_consumed"],
                "Pescatarian": ["fish_products_consumed", "dairy_products_consumed"],
                "Omnivore": ["beef_products_consumed", "poultry_products_consumed", "pork_products_consumed", "dairy_products_consumed", "fish_products_consumed"],
                "Heavy Meat Eater": ["beef_products_consumed", "poultry_products_consumed", "pork_products_consumed", "dairy_products_consumed", "fish_products_consumed", "other_meat_products_consumed"]
            }
            food_activities = base_foods + diet_foods.get(diet_type, [])
            for a in food_activities:
                label = a.replace("_", " ").replace("products", "").replace("consumed", "").strip().capitalize()
                st.number_input(label, min_value=0.0, key=f"food_{a}", format="%.1f")
    elif current_tab == 2:
        for a in energy_activities:
            st.number_input(format_activity_name(a), min_value=0.0, key=f"energy_{a}")
    elif current_tab == 3:
        for a in other_activities:
            st.number_input(format_activity_name(a), min_value=0.0, key=f"other_{a}")
        st.markdown("---")
        confirmed = st.checkbox("I have reviewed all fields and want to calculate my footprint")
        calculate = st.button("Calculate My Carbon Footprint", disabled=not confirmed)

        if calculate:
            st.session_state.emission_values = {}

            all_inputs = {
                "travel": travel_activities,
                "energy": energy_activities,
                "other": other_activities,
                "food": food_activities
            }

            for prefix, activities in all_inputs.items():
                for activity in activities:
                    key = f"{prefix}_{activity}"
                    if key in st.session_state:
                        user_value = st.session_state[key]
                        try:
                            factor = df.loc[df["Activity"] == activity, country].values[0]
                            st.session_state.emission_values[key] = user_value * factor
                        except IndexError:
                            st.warning(f"⚠️ No emission factor found for {activity}")

            total_emission = sum(st.session_state.emission_values.values())
            st.subheader(f"🌍 Your Carbon Footprint: {total_emission:.1f} kg CO₂")

            trees_cut = total_emission / 21.77
            st.markdown(f"🌳 **Equivalent to cutting down ~{trees_cut:.0f} trees!**")

            def get_avg(country_name):
                row = df1[df1["Country"] == country_name]
                return row["PerCapitaCO2"].values[0] if not row.empty else None

            avg_vals = [get_avg(c) for c in [country, "European Union (27)", "World"]]
            labels = ["You", country, "EU", "World"]
            values = [total_emission] + avg_vals
            colors = ['#4CAF50'] + ['#4682B4'] * 3

            labels, values, colors = labels[::-1], values[::-1], colors[::-1]
            fig, ax = plt.subplots(figsize=(8, 3.2))
            bars = ax.barh(labels, values, color=colors, height=0.6)
            ax.set_xlim(0, max(values) * 1.1)
            for bar in bars:
                ax.annotate(f'{bar.get_width():.1f}', xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
                            xytext=(5, 0), textcoords='offset points', ha='left', va='center')
            ax.set_xlabel("Tons CO₂ per year")
            ax.xaxis.grid(True, linestyle='--', alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)

            st.markdown("""
                <div style='text-align: center; color: gray;'>
                Comparison of your estimated annual carbon footprint with national and global averages.
                </div>
            """, unsafe_allow_html=True)

    # --- Navigation Buttons ---
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("← Previous", disabled=current_tab == 0, use_container_width=True):
                st.session_state.tab_index -= 1
                st.rerun()
        with col_next:
            if st.button("Next →", disabled=current_tab == len(tabs) - 1, use_container_width=True):
                st.session_state.tab_index += 1
                st.rerun()
