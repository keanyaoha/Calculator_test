import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- App Config ---
st.set_page_config(page_title="Green Tomorrow", page_icon="🌿", layout="centered")

# --- Logo & Style ---
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

# --- Load CSVs ---
csv_url = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/emission_factor_formated.csv"
per_capita_url = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered_monthly.csv"

try:
    df = pd.read_csv(csv_url)
    df1 = pd.read_csv(per_capita_url)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

available_countries = [col for col in df.columns if col != "Activity"]

# --- UI ---
st.title("Carbon Footprint Calculator")
st.markdown("Calculate your carbon footprint and compare it to national and global averages.")

# --- Country ---
country = st.selectbox("🌍 Select your country of residence:", ["-- Select --"] + available_countries)

if country != "-- Select --":
    if "tab_index" not in st.session_state:
        st.session_state.tab_index = 0

    tabs = ["Travel", "Food", "Energy & Water", "Other"]
    current_tab = st.session_state.tab_index

    st.subheader(tabs[current_tab])

    travel_activities = [
        "Domestic flight", "International flight", "km_diesel_local_passenger_train_traveled",
        "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled",
        "km_bus_traveled", "km_petrol_car_traveled", "km_Motorcycle_traveled",
        "km_ev_scooter_traveled", "km_ev_car_traveled", "diesel_car_traveled"
    ]
    energy_activities = ["electricity_used", "water_consumed"]
    other_activities = ["hotel_stay"]
    base_foods = ["processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed", "other_food_products_consumed", "beverages_consumed"]
    diet_foods = {
        "Vegan": [],
        "Vegetarian": ["dairy_products_consumed", "other_meat_products_consumed"],
        "Pescatarian": ["fish_products_consumed", "dairy_products_consumed"],
        "Omnivore": ["beef_products_consumed", "poultry_products_consumed", "pork_products_consumed", "dairy_products_consumed", "fish_products_consumed"],
        "Heavy Meat Eater": ["beef_products_consumed", "poultry_products_consumed", "pork_products_consumed", "dairy_products_consumed", "fish_products_consumed", "other_meat_products_consumed"]
    }

    # Tab 1: Travel
    if current_tab == 0:
        for act in travel_activities:
            st.number_input(f"{act.replace('_', ' ').capitalize()} (km)", min_value=0.0, key=f"travel_{act}")

    # Tab 2: Food
    elif current_tab == 1:
        diet_type = st.selectbox("🍽️ What is your diet type?", ["Select...", *diet_foods.keys()])
        if diet_type != "Select...":
            food_activities = base_foods + diet_foods[diet_type]
            for act in food_activities:
                st.number_input(f"{act.replace('_', ' ').capitalize()} (kg)", min_value=0.0, key=f"food_{act}")

    # Tab 3: Energy & Water
    elif current_tab == 2:
        for act in energy_activities:
            st.number_input(f"{act.replace('_', ' ').capitalize()}", min_value=0.0, key=f"energy_{act}")

    # Tab 4: Other
    elif current_tab == 3:
        for act in other_activities:
            st.number_input(f"{act.replace('_', ' ').capitalize()}", min_value=0.0, key=f"other_{act}")
        st.markdown("---")
        confirmed = st.checkbox("I reviewed all fields")
        calculate = st.button("Calculate My Carbon Footprint", disabled=not confirmed)

        if calculate:
            st.session_state.emission_values = {}
            # Check all prefixed inputs
            for pref, activities in {
                "travel": travel_activities,
                "energy": energy_activities,
                "other": other_activities,
                "food": base_foods + sum(diet_foods.values(), [])
            }.items():
                for a in activities:
                    k = f"{pref}_{a}"
                    if k in st.session_state:
                        try:
                            factor = df.loc[df["Activity"] == a, country].values[0]
                            val = st.session_state[k]
                            st.session_state.emission_values[k] = val * factor
                        except:
                            st.warning(f"Missing factor for: {a}")

            total = sum(st.session_state.emission_values.values())
            st.subheader(f"🌍 Your Carbon Footprint: {total:.1f} kg CO₂")
            trees = total / 21.77
            st.markdown(f"🌳 Equivalent to cutting down ~{trees:.0f} trees.")

            def get_avg(country_name):
                row = df1[df1["Country"] == country_name]
                return row["PerCapitaCO2"].values[0] if not row.empty else None

            you = total
            country_avg = get_avg(country) or 0
            eu_avg = get_avg("European Union (27)") or 0
            world_avg = get_avg("World") or 0

            # Chart
            labels = ["You", country, "EU", "World"]
            values = [you, country_avg, eu_avg, world_avg]
            colors = ['#4CAF50'] + ['#4682B4'] * 3

            fig, ax = plt.subplots(figsize=(8, 3))
            bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1])
            ax.set_xlim(0, max(values) * 1.1)
            for bar in bars:
                ax.annotate(f'{bar.get_width():.1f}', xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
                            xytext=(5, 0), textcoords='offset points', ha='left', va='center')
            ax.set_xlabel("Tons CO₂ per year")
            ax.xaxis.grid(True, linestyle='--', alpha=0.3)
            st.pyplot(fig)

    # --- Navigation ---
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
