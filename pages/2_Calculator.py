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
        /* Style radio buttons to look more like tabs */
        div[role="radiogroup"] > label > div:first-child {
            display: none; /* Hide the default radio circle */
        }
        div[role="radiogroup"] > label {
            margin: 0 !important;
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
            border-bottom: none;
            border-radius: 5px 5px 0 0;
            background-color: #f0f2f6;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        div[role="radiogroup"] > label:hover {
             background-color: #e0e2e6;
        }
        div[role="radiogroup"] input[type="radio"]:checked + div {
             background-color: white;
             border-bottom: 1px solid white; /* Make it look connected to content */
             font-weight: bold;
             color: #007bff; /* Highlight selected tab text */
        }
        /* Add a bottom border to the container to complete the tab look */
         div.stRadio > div {
             border-bottom: 1px solid #ddd;
             padding-bottom: 1rem; /* Add some space below the 'tabs' */
         }

    </style>
    """,
    unsafe_allow_html=True
)

# --- Initialize Session State Variables ---
# General App State
if "profile_completed" not in st.session_state:
    st.session_state.profile_completed = False
if "selected_country" not in st.session_state:
    st.session_state.selected_country = "-- Select --"
if "current_tab_index" not in st.session_state:
    st.session_state.current_tab_index = 0

# Input & Calculation State
if "emission_values" not in st.session_state:
    st.session_state.emission_values = {}
if "calculation_done" not in st.session_state:
    st.session_state.calculation_done = False
if "calculated_emission" not in st.session_state:
    st.session_state.calculated_emission = None
if "comparison_plot_data" not in st.session_state:
     st.session_state.comparison_plot_data = None


# --- Load Emission Data ---
CSV_URL = "https://drive.google.com/uc?export=download&id=1PWeBZKB6adZKORvtMDLFwCX__gfzH33g"
PER_CAPITA_URL = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered_monthly.csv"

@st.cache_data
def load_data(csv_url, per_capita_url):
    try:
        df = pd.read_csv(csv_url)
        df1 = pd.read_csv(per_capita_url)
        df.columns = df.columns.str.strip()
        return df, df1
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

df, df1 = load_data(CSV_URL, PER_CAPITA_URL)

if df is None or df1 is None:
    st.stop()

available_countries = sorted([col for col in df.columns if col != "Activity"])

# --- Format Activity Titles ---
def format_activity_name(activity):
    mapping = {
        "Domestic_flight_traveled": "How many km of Domestic Flights taken last month 🚀",
        "International_flight_traveled": "How many km of International Flights taken last month 🌍",
        "km_diesel_local_passenger_train_traveled": "How many km by diesel-powered local trains 🚆",
        "km_diesel_long_distance_passenger_train_traveled": "How many km by diesel-powered long-distance trains 🚄",
        "km_electric_passenger_train_traveled": "How many km by electric-powered trains ⚡🚆",
        "km_bus_traveled": "How many km by bus 🚌",
        "km_petrol_car_traveled": "How many km by petrol-powered car 🚗",
        "km_Motorcycle_traveled": "How many km by motorcycle 🏍️",
        "km_ev_scooter_traveled": "How many km by electric scooter 🛴",
        "km_ev_car_traveled": "How many km by electric car 🚙⚡",
        "diesel_car_traveled": "How many km by diesel-powered car 🚙💨",
        "beef_products_consumed": "How much beef products consumed (kg) 🥩",
        "poultry_products_consumed": "How much poultry products consumed (kg) 🍗",
        "pork_products_consumed": "How much pork products consumed (kg) 🍖",
        "fish_products_consumed": "How much fish products consumed (kg) 🐟",
        "other_meat_products_consumed": "How much other meat products consumed (kg) 🍖",
        "processed_rice_consumed": "How much processed rice consumed (kg) 🍚",
        "sugar_consumed": "How much sugar consumed (kg) 🍬",
        "vegetable_oils_fats_consumed": "How much vegetable oils/fats consumed (kg) 🧈",
        "dairy_products_consumed": "How much dairy products consumed (kg) 🧀🥛",
        "other_food_products_consumed": "How much other food products consumed (kg) 🍽️",
        "water_consumed": "How much water consumed (liters) 💧",
        "electricity_used": "How much electricity used (kWh) 💡",
        "hotel_stay": "How many nights in hotels 🏨",
    }
    return mapping.get(activity, activity.replace("_", " ").capitalize())

# --- App Title ---
st.title("🌍 Carbon Footprint Calculator")
st.markdown("Estimate your monthly carbon footprint and compare it to country and global averages. 🌱")
st.divider()

# --- Country Selection ---
country_options = ["-- Select --"] + available_countries
selected_country = st.selectbox(
    "**Step 1: Select your country** 🌍",
    options=country_options,
    index=country_options.index(st.session_state.selected_country),
    key="country_selector_main"
)

# --- Update Session State on Country Change ---
if selected_country != st.session_state.selected_country:
    st.session_state.selected_country = selected_country
    # Reset state when country changes
    st.session_state.current_tab_index = 0
    st.session_state.emission_values = {}
    st.session_state.calculation_done = False
    st.session_state.calculated_emission = None
    st.session_state.comparison_plot_data = None
    st.rerun()

# --- Main Content Area (Tabs and Calculation) ---
if st.session_state.selected_country != "-- Select --":
    country = st.session_state.selected_country

    st.markdown("**Step 2: Enter your monthly consumption details**")

    # --- Tab Simulation using Radio Buttons --- 
    tab_labels = ["Transport 🚗", "Food 🍽️", "Energy & Water 💡💧", "Hotel 🏨"]
    selected_tab_label = st.radio(
        "Select Category:",
        tab_labels,
        index=st.session_state.current_tab_index,
        key="tab_selector",
        horizontal=True,
        label_visibility="collapsed"
    )

    # Update session state index if user clicks a radio button directly
    clicked_index = tab_labels.index(selected_tab_label)
    if clicked_index != st.session_state.current_tab_index:
        st.session_state.current_tab_index = clicked_index
        # We might need to rerun if the content display relies solely on this index
        st.rerun()

    # --- Display Content Based on Selected "Tab" ---
    current_index = st.session_state.current_tab_index

    # --- Tab 1: Transport ---
    if current_index == 0:
        transport_activities = [
            "Domestic_flight_traveled", "International_flight_traveled",
            "km_diesel_local_passenger_train_traveled", "km_diesel_long_distance_passenger_train_traveled",
            "km_electric_passenger_train_traveled", "km_bus_traveled",
            "km_petrol_car_traveled", "diesel_car_traveled",
            "km_Motorcycle_traveled", "km_ev_scooter_traveled", "km_ev_car_traveled"
        ]
        display_activity_inputs(transport_activities, "transport", country)
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Next →", key="next_transport", use_container_width=True):
                st.session_state.current_tab_index = 1
                st.rerun()

    # --- Tab 2: Food ---
    elif current_index == 1:
        food_activities = [
            "beef_products_consumed", "poultry_products_consumed", "pork_products_consumed",
            "fish_products_consumed", "other_meat_products_consumed", "dairy_products_consumed",
            "processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed",
            "other_food_products_consumed"
        ]
        display_activity_inputs(food_activities, "food", country)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous", key="prev_food", use_container_width=True):
                st.session_state.current_tab_index = 0
                st.rerun()
        with col2:
            if st.button("Next →", key="next_food", use_container_width=True):
                st.session_state.current_tab_index = 2
                st.rerun()

    # --- Tab 3: Energy & Water ---
    elif current_index == 2:
        energy_water_activities = ["electricity_used", "water_consumed"]
        display_activity_inputs(energy_water_activities, "energy", country)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous", key="prev_energy", use_container_width=True):
                st.session_state.current_tab_index = 1
                st.rerun()
        with col2:
            if st.button("Next →", key="next_energy", use_container_width=True):
                st.session_state.current_tab_index = 3
                st.rerun()

    # --- Tab 4: Hotel (with Calculation Trigger) ---
    elif current_index == 3:
        hotel_activities = ["hotel_stay"]
        display_activity_inputs(hotel_activities, "hotel", country)

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("← Previous", key="prev_hotel", use_container_width=True):
                st.session_state.current_tab_index = 2
                st.rerun()

        # --- Calculation Trigger Section (ONLY IN TAB 4) ---
        st.divider()
        st.markdown("**Step 3: Calculate your footprint** 🧮")
        reviewed_all = st.checkbox("I have reviewed/entered my data for all categories.", key="review_check")

        if reviewed_all:
            if st.button("Calculate My Carbon Footprint", type="primary", use_container_width=True, key="calculate_button"):
                # Perform Calculation
                emission_values_to_sum = {
                    k: v for k, v in st.session_state.emission_values.items()
                    if not k.endswith('_input') and isinstance(v, (int, float))
                }

                if not emission_values_to_sum:
                     st.warning("No emission data calculated. Please enter some values in the categories above.")
                     st.session_state.calculation_done = False
                else:
                    total_emission = sum(emission_values_to_sum.values())
                    st.session_state.calculated_emission = total_emission

                    # Prepare comparison data
                    def get_avg(name, df_avg):
                        match = df_avg.loc[df_avg["Country"] == name, "PerCapitaCO2"]
                        return match.iloc[0] if not match.empty else None

                    country_avg = get_avg(country, df1)
                    eu_avg = get_avg("European Union (27)", df1)
                    world_avg = get_avg("World", df1)

                    comparison_data = {
                         "country": {"name": country, "avg": country_avg, "color": '#4682B4'},
                         "eu": {"name": "EU Average", "avg": eu_avg, "color": '#ADD8E6'},
                         "world": {"name": "World Average", "avg": world_avg, "color": '#D3D3D3'}


                    }
                    st.session_state.comparison_plot_data = comparison_data

                    st.session_state.calculation_done = True
                    st.rerun()
        else:
            # Show info only if checkbox isn't ticked on this tab
            st.info("Please review your inputs in all categories and check the box above to enable calculation.")
        
