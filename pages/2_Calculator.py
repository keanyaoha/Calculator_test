import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt # Keep for potential future use, though replaced in results
import plotly.express as px    # Import Plotly Express
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO

# --- PDF Report Generator (If needed in this file, otherwise remove) ---
# Note: If this function is only used on the "Breakdown" page,
# it doesn't strictly need to be in this main calculator file unless called from here.
# Keeping it for now based on your previous code structure.
def generate_pdf_report(category_data, top_activities_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 2 * cm, "GreenPrint Carbon Footprint Report")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, height - 3 * cm, "Emission by Category:")
    c.setFont("Helvetica", 11)
    y = height - 4 * cm
    for category, emission in category_data.items():
        c.drawString(2.5 * cm, y, f"{category}: {emission:.2f} kg CO₂")
        y -= 0.7 * cm

    c.setFont("Helvetica-Bold", 12)
    y -= 0.5 * cm # Adjust spacing
    c.drawString(2 * cm, y, "Top Emitting Activities:") # Simplified title
    c.setFont("Helvetica", 11)
    y -= 0.7 * cm # Adjust spacing
    # Ensure top_activities_data is a dictionary or similar iterable
    if isinstance(top_activities_data, pd.DataFrame): # Handle if DataFrame passed
         top_activities_dict = dict(zip(top_activities_data.iloc[:,0], top_activities_data.iloc[:,1]))
    elif isinstance(top_activities_data, dict):
         top_activities_dict = top_activities_data
    else:
         top_activities_dict = {} # Default empty if format is wrong

    for activity, emission in top_activities_dict.items():
        # Truncate long activity names if necessary
        display_activity = (activity[:45] + '...') if len(str(activity)) > 48 else str(activity)
        c.drawString(2.5 * cm, y, f"{display_activity}: {emission:.2f} kg CO₂")
        y -= 0.6 * cm
        if y < 3 * cm: # Check for page break earlier
            c.showPage()
            # Reset Y for new page and potentially add headers again if needed
            c.setFont("Helvetica", 11) # Reset font
            y = height - 2 * cm

    c.save() # Save the canvas content to the buffer
    buffer.seek(0)
    return buffer

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
    # Make sure all keys used in the app are in this mapping
    mapping = {
        "Domestic_flight_traveled": "Domestic Flights (km)",
        "International_flight_traveled": "International Flights (km)",
        "km_diesel_local_passenger_train_traveled": "Diesel Local Train (km)",
        "km_diesel_long_distance_passenger_train_traveled": "Diesel Long-Distance Train (km)",
        "km_electric_passenger_train_traveled": "Electric Train (km)",
        "km_bus_traveled": "Bus (km)",
        "km_petrol_car_traveled": "Petrol Car (km)",
        "km_Motorcycle_traveled": "Motorcycle (km)",
        "km_ev_scooter_traveled": "Electric Scooter (km)",
        "km_ev_car_traveled": "Electric Car (km)",
        "diesel_car_traveled": "Diesel Car (km)",
        "beef_products_consumed": "Beef Products (kg)",
        "poultry_products_consumed": "Poultry Products (kg)",
        "pork_products_consumed": "Pork Products (kg)",
        "fish_products_consumed": "Fish Products (kg)",
        "other_meat_products_consumed": "Other Meat Products (kg)",
        "processed_rice_consumed": "Processed Rice (kg)",
        "sugar_consumed": "Sugar (kg)",
        "vegetable_oils_fats_consumed": "Vegetable Oils/Fats (kg)",
        "dairy_products_consumed": "Dairy Products (kg)",
        "other_food_products_consumed": "Other Food Products (kg)",
        "water_consumed": "Water Consumed (liters)",
        "electricity_used": "Electricity Used (kWh)",
        "hotel_stay": "Hotel Nights",
        # Add any other keys if they exist in your emission_values dict
    }
    # Return formatted name or a cleaned-up version of the original key
    return mapping.get(activity, activity.replace("_", " ").replace("km ", "").replace(" traveled", "").replace(" consumed", "").capitalize())


# --- App Title ---
st.title("🌍 Carbon Footprint Calculator")
st.markdown("Estimate your monthly carbon footprint and compare it to country and global averages.")
st.divider()

# --- Country Selection ---
# Use Markdown for label if needed for compatibility
st.markdown("**Step 1: Select your country**")
country_options = ["-- Select --"] + available_countries
selected_country = st.selectbox(
    label="country_select_hidden", # Internal label, hidden visually
    label_visibility="collapsed", # Hide the label
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
        st.rerun()


    # --- Display Content Based on Selected "Tab" ---
    def display_activity_inputs(activities, category_key, current_country):
        """Displays number inputs and calculates emissions for a list of activities."""
        for activity in activities:
            # Use the formatting function for labels
            label = format_activity_name(activity) # Get user-friendly label
            input_key = f"{category_key}_{activity}"
            # Retrieve the *user's input value* from state if it exists
            default_value = st.session_state.emission_values.get(f"{input_key}_input", 0.0)

            user_input = st.number_input(label, min_value=0.0, step=0.1, key=input_key, value=default_value)

            # Store the raw input value back into session state *immediately*
            st.session_state.emission_values[f"{input_key}_input"] = user_input

            # Calculate and store the emission value
            try:
                # Ensure the activity exists in the DataFrame's Activity column
                factor_series = df.loc[df["Activity"] == activity, current_country]

                if not factor_series.empty:
                    factor = factor_series.iloc[0]
                    if pd.isna(factor):
                        # Handle missing factors gracefully
                        st.session_state.emission_values[activity] = 0.0
                        # Optionally add a subtle warning if factor is missing for entered value > 0
                        # if user_input > 0:
                        #     st.caption(f"Factor missing for {label}, assuming 0 emission.")
                    else:
                        # Calculate emission based on the *current* user_input
                        st.session_state.emission_values[activity] = user_input * float(factor)
                else:
                    # Activity might not be relevant for the selected country or data issue
                    st.session_state.emission_values[activity] = 0.0
                    # Optionally add a subtle warning if factor is missing for entered value > 0
                    # if user_input > 0:
                    #     st.caption(f"Factor not found for {label}, assuming 0 emission.")

            except KeyError:
                # Handle cases where the country column might not exist (shouldn't happen with available_countries list)
                 st.error(f"Data error: Country column '{current_country}' not found.")
                 st.session_state.emission_values[activity] = 0.0
            except Exception as e:
                # Catch any other unexpected errors during calculation
                st.error(f"Calculation error for {label}: {e}")
                st.session_state.emission_values[activity] = 0.0

    # --- Display Input Sections and Navigation/Calculation Trigger ---
    current_index = st.session_state.current_tab_index

    # --- Tab 1: Transport ---
    if current_index == 0:
        transport_activities = [
            "Domestic_flight_traveled", "International_flight_traveled",
            "km_diesel_local_passenger_train_traveled", "km_diesel_long_distance_passenger_train_traveled",
            "km_electric_passenger_train_traveled", "km_bus_traveled",
            "km_petrol_car_traveled", "diesel_car_traveled", # Corrected key
            "km_Motorcycle_traveled", "km_ev_scooter_traveled", "km_ev_car_traveled"
        ]
        display_activity_inputs(transport_activities, "transport", country)
        # Navigation Button
        col1, col2 = st.columns([3, 1]) # Give button less space
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
             # Add "beverages_consumed" here if it exists in your CSV Activity column
        ]
        display_activity_inputs(food_activities, "food", country)
        # Navigation Buttons
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
        # Navigation Buttons
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
        # Navigation Button (Previous only)
        col1, col2 = st.columns([1, 3]) # Give button less space
        with col1:
            if st.button("← Previous", key="prev_hotel", use_container_width=True):
                st.session_state.current_tab_index = 2
                st.rerun()

        # --- Calculation Trigger Section (ONLY IN TAB 4) ---
        st.divider() # Visual separator
        st.markdown("**Step 3: Calculate your footprint**")
        reviewed_all = st.checkbox("I have reviewed/entered my data for all categories.", key="review_check")

        if reviewed_all:
            if st.button("Calculate My Carbon Footprint", type="primary", use_container_width=True, key="calculate_button"):
                # Perform Calculation using only calculated emission values (not the '_input' ones)
                emission_values_to_sum = {
                    k: v for k, v in st.session_state.emission_values.items()
                    if not k.endswith('_input') and isinstance(v, (int, float))
                }

                if not emission_values_to_sum or sum(emission_values_to_sum.values()) <= 0:
                     st.warning("No emissions calculated or total is zero. Please enter some consumption values in the categories above.")
                     st.session_state.calculation_done = False # Ensure status is false
                else:
                    total_emission = sum(emission_values_to_sum.values())
                    st.session_state.calculated_emission = total_emission # Store result

                    # Prepare comparison data (only includes averages found)
                    def get_avg(name, df_avg):
                        match = df_avg.loc[df_avg["Country"] == name, "PerCapitaCO2"]
                        return match.iloc[0] if not match.empty and pd.notna(match.iloc[0]) else None # Check for NaN

                    country_avg = get_avg(country, df1)
                    eu_avg = get_avg("European Union (27)", df1) # Ensure exact name match
                    world_avg = get_avg("World", df1) # Ensure exact name match

                    comparison_data = {
                         "country": {"name": country, "avg": country_avg},
                         "eu": {"name": "EU Average", "avg": eu_avg},
                         "world": {"name": "World Average", "avg": world_avg}
                    }
                    st.session_state.comparison_plot_data = comparison_data # Store for plotting

                    st.session_state.calculation_done = True # Set flag
                    st.rerun() # Rerun to display results below tabs

        else:
            # Show info only if checkbox isn't ticked *on this tab*
            st.info("Please review your inputs in all categories and check the box above to enable calculation.")


    # --- Display Results Area (Below Tabs, only if calculation is done) ---
    # This block is now OUTSIDE the tab selection if/elif/else structure
    # It uses st.session_state to check if calculation was done
    if st.session_state.get('calculation_done', False):
        st.divider()
        st.subheader(f"📊 Your Estimated Monthly Carbon Footprint:")

        total_emission = st.session_state.get('calculated_emission', 0) # Get stored emission

        if total_emission > 0: # Check if valid emission value exists
            st.metric(label="kg CO₂ equivalent", value=f"{total_emission:.1f}")

            # Tree equivalence calculation
            trees_monthly_equiv = total_emission / (21.77 / 12) # Assuming 21.77 kg/year/tree
            st.markdown(f"This is roughly equivalent to the amount of CO₂ absorbed by **{trees_monthly_equiv:.1f} mature trees** in a month.")

            st.divider()
            st.subheader("📈 Comparison with Averages")

            # Retrieve comparison data from session state
            comparison_data = st.session_state.get('comparison_plot_data')
            plot_data_list = [] # List to store data for DataFrame
            captions = [] # To collect notes about missing data

            # Add "You" data first
            plot_data_list.append({"Source": "You", "Emissions": total_emission})

            if comparison_data:
                # Add country data if average exists
                c_data = comparison_data["country"]
                if c_data["avg"] is not None:
                    plot_data_list.append({"Source": c_data["name"], "Emissions": c_data["avg"]})
                else:
                    captions.append(f"Note: Monthly average data for {c_data['name']} not available.")

                # Add EU data if average exists
                eu_data = comparison_data["eu"]
                if eu_data["avg"] is not None:
                    plot_data_list.append({"Source": eu_data["name"], "Emissions": eu_data["avg"]})
                else:
                     captions.append("Note: Monthly average data for EU not available.")

                # Add World data if average exists
                world_data = comparison_data["world"]
                if world_data["avg"] is not None:
                    plot_data_list.append({"Source": world_data["name"], "Emissions": world_data["avg"]})
                else:
                    captions.append("Note: Monthly average data for World not available.")

            # Display collected captions if any averages were missing
            for caption in captions:
                st.caption(caption)

            # Create DataFrame for Plotly if there's data
            if len(plot_data_list) > 0:
                df_comparison = pd.DataFrame(plot_data_list)

                # Plot only if there's data (at least "You")
                fig_comp = px.bar(
                    df_comparison.sort_values("Emissions", ascending=True), # Sort for consistent plotting order
                    x="Emissions",
                    y="Source",
                    orientation='h',
                    color="Emissions",              # Color intensity based on emission value
                    color_continuous_scale="Greens", # Color scheme
                    text="Emissions",               # Show values on bars
                    title="Monthly Carbon Footprint Comparison",
                    labels={'Emissions': 'kg CO₂ per month', 'Source': ''} # Axis labels
                )
                # Format text labels on bars
                fig_comp.update_traces(
                    texttemplate='%{text:.1f}', # Format to one decimal place
                    textposition='outside'      # Position text outside the bar
                )
                # Adjust layout for better text visibility if needed
                fig_comp.update_layout(margin=dict(l=10, r=10, t=50, b=10)) # Add more top margin for title

                st.plotly_chart(fig_comp, use_container_width=True)

                st.markdown("<div style='text-align: center; color: gray; font-size: small;'>Comparison of your estimated monthly carbon footprint with available national and global averages.</div>", unsafe_allow_html=True)

            else:
                # Should not happen if calculation_done is True and total_emission > 0
                st.warning("No data available to generate comparison plot.")
        else:
            # This message might appear briefly if rerun happens before emission is stored correctly
            st.warning("Calculated emission value not found or is zero.")


# --- Placeholder if no country is selected ---
elif not st.session_state.selected_country or st.session_state.selected_country == "-- Select --":
    # No message needed here as the main content area is not rendered
    pass

# --- Sidebar Content ---
st.sidebar.markdown("---")
# Add any other sidebar elements if needed, e.g., navigation links for multipage app
