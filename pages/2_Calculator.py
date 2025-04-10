import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- App Config ---
st.set_page_config(page_title="GreenPrint", page_icon="🌿", layout="centered")

# --- Sidebar Logo Styling (Still in Sidebar) ---
# Keep your sidebar styling as is, it applies to the sidebar container
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
            margin: 1.5rem auto -4rem auto; /* Adjust margins as needed */
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
if "profile_completed" not in st.session_state:
    st.session_state.profile_completed = False
if "emission_values" not in st.session_state:
    st.session_state.emission_values = {}
if "current_tab_index" not in st.session_state:
    st.session_state.current_tab_index = 0
if "selected_country" not in st.session_state:
    # Initialize with the placeholder to ensure it exists
    st.session_state.selected_country = "-- Select --"


# --- Load Emission Data ---
CSV_URL = "https://drive.google.com/uc?export=download&id=1PWeBZKB6adZKORvtMDLFwCX__gfzH33g"
PER_CAPITA_URL = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered_monthly.csv"

@st.cache_data # Cache the data loading
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
st.divider() # Add a line after the title

# --- Country Selection (Moved to Main Page) ---
country_options = ["-- Select --"] + available_countries
# Use st.session_state.selected_country to keep the selection sticky across reruns
selected_country = st.selectbox(
    "**Step 1: Select your country**",
    options=country_options,
    index=country_options.index(st.session_state.selected_country), # Set index based on session state
    key="country_selector_main" # Use a unique key
)

# --- Update Session State on Country Change ---
# Important: Check if the *widget's current value* is different from the state
# This prevents unnecessary state updates on reruns where the selection didn't change
if selected_country != st.session_state.selected_country:
    st.session_state.selected_country = selected_country
    # Reset tab index and potentially stored emission values when country changes?
    # This might be desirable behavior, otherwise previous entries remain associated with a new country's factors
    st.session_state.current_tab_index = 0
    st.session_state.emission_values = {} # Reset emissions if country changes
    st.rerun() # Rerun immediately to reflect the change and potentially reset state

# --- Conditional Display of Tabs and Calculation ---
# Only show the rest of the app if a valid country is selected
if st.session_state.selected_country != "-- Select --":
    country = st.session_state.selected_country # Use the confirmed selected country for calculations

    st.markdown("**Step 2: Enter your monthly consumption details**")

    # --- Tab Simulation using Radio Buttons ---
    tab_labels = ["Transport", "Food", "Energy & Water", "Hotel"]
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
        st.rerun() # Rerun needed to show the correct content for the clicked tab

    # --- Display Content Based on Selected "Tab" ---
    # Helper function (ensure it uses the correct 'country' variable from session state)
    def display_activity_inputs(activities, category_key, current_country):
        for activity in activities:
            label = format_activity_name(activity)
            input_key = f"{category_key}_{activity}" # Unique key per input
            # Retrieve previous input *value* if exists in state, otherwise default to 0.0
            default_value = st.session_state.emission_values.get(f"{input_key}_input", 0.0)

            user_input = st.number_input(label, min_value=0.0, step=0.1, key=input_key, value=default_value)

            # Store the raw input value back into session state
            st.session_state.emission_values[f"{input_key}_input"] = user_input

            try:
                factor_series = df.loc[df["Activity"] == activity, current_country]
                if not factor_series.empty:
                    factor = factor_series.iloc[0]
                    # Store calculated emission value for this activity
                    # Use the raw input value just retrieved/stored
                    st.session_state.emission_values[activity] = user_input * factor
                else:
                    st.warning(f"Emission factor not found for '{activity}' in {current_country}. Skipping calculation for this item.")
                    st.session_state.emission_values[activity] = 0
            except Exception as e:
                st.error(f"Error processing factor for activity '{activity}' in {current_country}: {e}")
                st.session_state.emission_values[activity] = 0


    # --- Display Input Sections and Navigation Buttons ---
    current_index = st.session_state.current_tab_index

    if current_index == 0:
        # st.subheader("🚗 Transport") # Subheader might be redundant with tab selection
        transport_activities = [
            "Domestic_flight_traveled", "International_flight_traveled",
            "km_diesel_local_passenger_train_traveled", "km_diesel_long_distance_passenger_train_traveled",
            "km_electric_passenger_train_traveled", "km_bus_traveled",
            "km_petrol_car_traveled", "diesel_car_traveled",
            "km_Motorcycle_traveled", "km_ev_scooter_traveled", "km_ev_car_traveled"
        ]
        display_activity_inputs(transport_activities, "transport", country)
        col1, col2 = st.columns([3, 1]) # Give more space to potential content on left
        with col2:
            if st.button("Next →", key="next_transport", use_container_width=True):
                st.session_state.current_tab_index = 1
                st.rerun()

    elif current_index == 1:
        # st.subheader("🍔 Food")
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

    elif current_index == 2:
        # st.subheader("💡 Energy & 💧 Water")
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

    elif current_index == 3:
        # st.subheader("🏨 Hotel")
        hotel_activities = ["hotel_stay"]
        display_activity_inputs(hotel_activities, "hotel", country)
        col1, col2 = st.columns([1, 3]) # Adjust column ratios
        with col1:
            if st.button("← Previous", key="prev_hotel", use_container_width=True):
                st.session_state.current_tab_index = 2
                st.rerun()
        # No "Next" button on the last tab

    # --- Calculation and Results Section ---
    st.divider() # Add a visual separator

    st.markdown("**Step 3: Calculate your footprint**")

    reviewed_all = st.checkbox("I have reviewed/entered my data for all categories.")

    if reviewed_all:
        if st.button("Calculate My Carbon Footprint", type="primary", use_container_width=True):
            emission_values_to_sum = {k: v for k, v in st.session_state.emission_values.items() if not k.endswith('_input') and isinstance(v, (int, float))} # Ensure values are numeric

            if not emission_values_to_sum:
                 st.warning("No emission data calculated. Please enter some values in the categories above.")
            else:
                total_emission = sum(emission_values_to_sum.values())
                st.subheader(f"📊 Your Estimated Monthly Carbon Footprint:")
                st.metric(label="kg CO₂ equivalent", value=f"{total_emission:.1f}")

                # Using 21.77 kg CO2 absorption per tree per year (Source: European Environment Agency)
                # Monthly absorption per tree = 21.77 / 12 = 1.814 kg CO2/month/tree
                trees_monthly_equiv = total_emission / (21.77 / 12)
                st.markdown(f"This is roughly equivalent to the amount of CO₂ absorbed by **{trees_monthly_equiv:.1f} mature trees** in a month.")

                st.divider()
                st.subheader("📈 Comparison with Averages")

                def get_avg(name, df_avg):
                    match = df_avg.loc[df_avg["Country"] == name, "PerCapitaCO2"]
                    return match.iloc[0] if not match.empty else None

                country_avg = get_avg(country, df1)
                eu_avg = get_avg("European Union (27)", df1)
                world_avg = get_avg("World", df1)

                plot_labels = ["You"]
                plot_values = [total_emission]
                plot_colors = ['#4CAF50']

                comparison_data = {}
                if country_avg is not None: comparison_data[country] = (country_avg, '#4682B4')
                else: st.caption(f"Note: Monthly average data for {country} not available for comparison.")

                if eu_avg is not None: comparison_data["EU Average"] = (eu_avg, '#ADD8E6')
                else: st.caption("Note: Monthly average data for EU not available for comparison.")

                if world_avg is not None: comparison_data["World Average"] = (world_avg, '#D3D3D3')
                else: st.caption("Note: Monthly average data for World not available for comparison.")

                # Add comparison data if available
                for label, (value, color) in comparison_data.items():
                    plot_labels.append(label)
                    plot_values.append(value)
                    plot_colors.append(color)

                if len(plot_values) > 1:
                    fig, ax = plt.subplots(figsize=(8, max(3, len(plot_labels) * 0.6)))
                    bars = ax.barh(plot_labels, plot_values, color=plot_colors)
                    ax.set_xlim(0, max(plot_values) * 1.15)

                    for bar in bars:
                        ax.text(bar.get_width() + (max(plot_values) * 0.01),
                                bar.get_y() + bar.get_height()/2,
                                f"{bar.get_width():.1f}",
                                va='center', ha='left', fontsize=9)

                    ax.set_xlabel("kg CO₂ per month")
                    ax.set_title("Monthly Carbon Footprint Comparison")
                    plt.tight_layout()
                    st.pyplot(fig)

                    st.markdown("<div style='text-align: center; color: gray; font-size: small;'>Comparison of your estimated monthly carbon footprint with available national and global averages.</div>", unsafe_allow_html=True)
                else:
                    st.info("Could not retrieve average data for comparison.")

    else:
        st.info("Please review your inputs in all categories and check the box above to enable calculation.")

# --- Show prompt if no country is selected ---
elif not st.session_state.selected_country or st.session_state.selected_country == "-- Select --":
    st.info("👈 Please select your country from the dropdown above to begin.")

# --- Optional: Add Footer or Info in Sidebar ---
st.sidebar.markdown("---")
st.sidebar.info("Tip: Fill in your typical monthly consumption.")
st.sidebar.markdown("*(Data Sources: Emission factors adapted from public datasets, Per capita averages aggregated)*") # Example source note
