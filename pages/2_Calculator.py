import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- App Config ---
st.set_page_config(page_title="GreenPrint", page_icon="🌿", layout="centered")

# --- Sidebar Logo Styling ---
# (Keep your existing sidebar styling)
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
if "profile_completed" not in st.session_state:
    st.session_state.profile_completed = False
if "emission_values" not in st.session_state:
    st.session_state.emission_values = {}
if "current_tab_index" not in st.session_state:
    st.session_state.current_tab_index = 0  # Use index (0, 1, 2, 3)

# --- Load Emission Data ---
# Using URLs directly might be slow or unreliable depending on the host.
# Consider downloading the files or using a more robust data loading method if issues persist.
CSV_URL = "https://drive.google.com/uc?export=download&id=1PWeBZKB6adZKORvtMDLFwCX__gfzH33g"
PER_CAPITA_URL = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered_monthly.csv"

@st.cache_data # Cache the data loading
def load_data(csv_url, per_capita_url):
    try:
        df = pd.read_csv(csv_url)
        df1 = pd.read_csv(per_capita_url)
        # Clean the column names (removing any extra spaces or unexpected characters)
        df.columns = df.columns.str.strip()
        return df, df1
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

df, df1 = load_data(CSV_URL, PER_CAPITA_URL)

if df is None or df1 is None:
    st.stop()

# Get available countries (i.e., columns excluding 'Activity')
available_countries = sorted([col for col in df.columns if col != "Activity"]) # Sort alphabetically

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
        "diesel_car_traveled": "How many km by diesel-powered car", # Added missing diesel car key
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

# --- Country Selection ---
# Place country selection in the sidebar for better layout
with st.sidebar:
    st.header("Your Profile")
    country = st.selectbox("Select your country:", ["-- Select --"] + available_countries, key="country_select")

if country == "-- Select --":
    st.info("Please select your country from the sidebar to begin.")
    st.stop()

# --- Tab Simulation using Radio Buttons ---
tab_labels = ["Transport", "Food", "Energy & Water", "Hotel"]

# Use radio buttons for navigation, controlled by session state index
selected_tab_label = st.radio(
    "Select Category:",
    tab_labels,
    index=st.session_state.current_tab_index,
    key="tab_selector", # Assign a key for state persistence
    horizontal=True,
    label_visibility="collapsed" # Hide the label "Select Category:"
)

# Update session state if the user clicks directly on a radio button
# Find the index corresponding to the clicked label
clicked_index = tab_labels.index(selected_tab_label)
if clicked_index != st.session_state.current_tab_index:
    st.session_state.current_tab_index = clicked_index
    # No rerun needed here, as Streamlit handles radio change reruns automatically

# --- Display Content Based on Selected "Tab" ---

# Helper function to display inputs and handle emission calculation
def display_activity_inputs(activities, category_key):
    for activity in activities:
        label = format_activity_name(activity)
        # Use a unique key combining category and activity
        input_key = f"{category_key}_{activity}"
        # Retrieve previous value if exists, otherwise default to 0.0
        default_value = st.session_state.emission_values.get(f"{input_key}_input", 0.0)

        user_input = st.number_input(label, min_value=0.0, step=0.1, key=input_key, value=default_value)

        # Store the raw input value in session state as well
        st.session_state.emission_values[f"{input_key}_input"] = user_input

        try:
            factor_series = df.loc[df["Activity"] == activity, country]
            if not factor_series.empty:
                factor = factor_series.iloc[0]
                # Store calculated emission value for this activity
                st.session_state.emission_values[activity] = user_input * factor
            else:
                st.warning(f"Emission factor not found for '{activity}' in {country}. Skipping calculation for this item.")
                st.session_state.emission_values[activity] = 0 # Ensure key exists but is 0
        except Exception as e: # Catch potential errors like missing keys or non-numeric factors
            st.error(f"Error processing factor for activity '{activity}' in {country}: {e}")
            st.session_state.emission_values[activity] = 0


# --- Display Input Sections and Navigation Buttons ---

current_index = st.session_state.current_tab_index

if current_index == 0:
    st.subheader("🚗 Transport")
    transport_activities = [
        "Domestic_flight_traveled", "International_flight_traveled",
        "km_diesel_local_passenger_train_traveled", "km_diesel_long_distance_passenger_train_traveled",
        "km_electric_passenger_train_traveled", "km_bus_traveled",
        "km_petrol_car_traveled", "diesel_car_traveled", # Ensure this matches a key in your mapping and CSV
        "km_Motorcycle_traveled", "km_ev_scooter_traveled", "km_ev_car_traveled"
    ]
    display_activity_inputs(transport_activities, "transport")
    col1, col2 = st.columns([1, 1]) # Adjust column ratios as needed
    with col2: # Place button on the right
        if st.button("Next →", key="next_transport"):
            st.session_state.current_tab_index = 1
            st.rerun() # Force rerun to update the radio button selection

elif current_index == 1:
    st.subheader("🍔 Food")
    food_activities = [
        "beef_products_consumed", "poultry_products_consumed", "pork_products_consumed",
        "fish_products_consumed", "other_meat_products_consumed", "dairy_products_consumed",
        "processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed",
        "other_food_products_consumed"
    ]
    display_activity_inputs(food_activities, "food")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Previous", key="prev_food"):
            st.session_state.current_tab_index = 0
            st.rerun()
    with col2:
        if st.button("Next →", key="next_food"):
            st.session_state.current_tab_index = 2
            st.rerun()

elif current_index == 2:
    st.subheader("💡 Energy & 💧 Water")
    energy_water_activities = ["electricity_used", "water_consumed"]
    display_activity_inputs(energy_water_activities, "energy")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Previous", key="prev_energy"):
            st.session_state.current_tab_index = 1
            st.rerun()
    with col2:
        if st.button("Next →", key="next_energy"):
            st.session_state.current_tab_index = 3
            st.rerun()

elif current_index == 3:
    st.subheader("🏨 Hotel")
    hotel_activities = ["hotel_stay"]
    display_activity_inputs(hotel_activities, "hotel")
    col1, col2 = st.columns([1,1]) # Keep consistent layout
    with col1:
        if st.button("← Previous", key="prev_hotel"):
            st.session_state.current_tab_index = 2
            st.rerun()
    # No "Next" button on the last tab

# --- Calculation and Results Section ---
st.divider() # Add a visual separator

# --- Checkbox to enable "Calculate My Carbon Footprint" button ---
# Moved below the input sections
reviewed_all = st.checkbox("I have reviewed/entered my data for all categories.")

# --- Calculate Emissions Button ---
if reviewed_all:
    if st.button("Calculate My Carbon Footprint", type="primary"): # Make button prominent
        # Filter out the stored input values (keys ending with '_input') before summing
        emission_values_to_sum = {k: v for k, v in st.session_state.emission_values.items() if not k.endswith('_input')}
        
        if not emission_values_to_sum:
             st.warning("No emission data calculated. Please enter some values in the categories above.")
        else:
            total_emission = sum(emission_values_to_sum.values())
            st.subheader(f"📊 Your Estimated Monthly Carbon Footprint:")
            st.metric(label="kg CO₂ equivalent", value=f"{total_emission:.1f}")


            trees_cut = total_emission / 21.77 # Assuming 21.77 kg CO2 per tree per year / 12 months? Clarify source/unit.
                                             # Or maybe it's absorption capacity? Be specific if possible.
            st.markdown(f"This is roughly equivalent to the amount of CO₂ absorbed by **{trees_cut:.1f} mature trees** in a month.") # Phrased for clarity

            st.divider()
            st.subheader("📈 Comparison with Averages")

            # --- Compare to Averages ---
            def get_avg(name, df_avg):
                match = df_avg.loc[df_avg["Country"] == name, "PerCapitaCO2"]
                # Handle cases where the country/region might not be in the average dataset
                return match.iloc[0] if not match.empty else None # Return None if not found

            country_avg = get_avg(country, df1)
            eu_avg = get_avg("European Union (27)", df1) # Make sure this name matches df1 exactly
            world_avg = get_avg("World", df1) # Make sure this name matches df1 exactly

            # Prepare data for plotting - handle missing averages gracefully
            plot_labels = ["You"]
            plot_values = [total_emission]
            plot_colors = ['#4CAF50'] # Your color

            if country_avg is not None:
                plot_labels.append(country)
                plot_values.append(country_avg)
                plot_colors.append('#4682B4') # Country color
            else:
                 st.caption(f"Note: Monthly average data for {country} not available.")

            if eu_avg is not None:
                 plot_labels.append("EU Average")
                 plot_values.append(eu_avg)
                 plot_colors.append('#ADD8E6') # EU color
            else:
                 st.caption("Note: Monthly average data for EU not available.")


            if world_avg is not None:
                 plot_labels.append("World Average")
                 plot_values.append(world_avg)
                 plot_colors.append('#D3D3D3') # World color
            else:
                 st.caption("Note: Monthly average data for World not available.")


            # Plot comparison chart only if there's something to compare
            if len(plot_values) > 1:
                # Sort by value for better visualization (optional)
                # combined = sorted(zip(plot_values, plot_labels, plot_colors), reverse=True)
                # plot_values, plot_labels, plot_colors = zip(*combined)

                fig, ax = plt.subplots(figsize=(8, max(3, len(plot_labels) * 0.6))) # Dynamic height
                bars = ax.barh(plot_labels, plot_values, color=plot_colors)
                ax.set_xlim(0, max(plot_values) * 1.15) # Adjust xlim for labels

                # Add labels to bars
                for bar in bars:
                    ax.text(bar.get_width() + (max(plot_values) * 0.01), # Small offset
                            bar.get_y() + bar.get_height()/2,
                            f"{bar.get_width():.1f}",
                            va='center', ha='left', fontsize=9)

                ax.set_xlabel("kg CO₂ per month")
                ax.set_title("Monthly Carbon Footprint Comparison")
                plt.tight_layout() # Adjust layout
                st.pyplot(fig)

                st.markdown("<div style='text-align: center; color: gray; font-size: small;'>Comparison of your estimated monthly carbon footprint with available national and global averages.</div>", unsafe_allow_html=True)
            else:
                st.info("Could not retrieve average data for comparison.")

else:
    # Show a reminder if the checkbox isn't ticked
    st.info("Please review your inputs in all categories and check the box above to enable calculation.")

# --- Optional: Add Footer or Info ---
st.sidebar.markdown("---")
st.sidebar.info("Data Sources: [Emission Factors](<Your Source Link>), [Averages](<Your Source Link>)")
