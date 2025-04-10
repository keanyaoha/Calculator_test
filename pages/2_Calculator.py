# -*- coding: utf-8 -*- # Add encoding declaration just in case
import pandas as pd
import streamlit as st
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
import traceback # For more detailed error logging if needed

# --- PDF Report Generator ---
def generate_pdf_report(category_data, top_activities_data):
    buffer = BytesIO()
    try: # Add error handling to PDF generation
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - 2 * cm, "GreenPrint Carbon Footprint Report")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, height - 3.5 * cm, "Emission by Category:")
        c.setFont("Helvetica", 10) # Slightly smaller font for details
        y = height - 4.5 * cm
        if isinstance(category_data, dict):
            for category, emission in category_data.items():
                if y < 3 * cm: # Check before drawing
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - 2 * cm
                c.drawString(2.5 * cm, y, f"{category}: {emission:.2f} kg CO₂")
                y -= 0.6 * cm
        else:
            c.drawString(2.5 * cm, y, "Category data unavailable.")
            y -= 0.6 * cm


        c.setFont("Helvetica-Bold", 12)
        y -= 0.5 * cm # Add space
        if y < 4 * cm: # Check position before drawing title
             c.showPage()
             c.setFont("Helvetica-Bold", 12)
             y = height - 2 * cm
        c.drawString(2 * cm, y, "Top Emitting Activities:")
        c.setFont("Helvetica", 10) # Smaller font
        y -= 0.7 * cm

        # Handle different input types for top activities
        if isinstance(top_activities_data, pd.DataFrame):
            # Use the first two columns assuming Activity, Emission
            top_activities_dict = dict(zip(top_activities_data.iloc[:,0], top_activities_data.iloc[:,1]))
        elif isinstance(top_activities_data, dict):
            top_activities_dict = top_activities_data
        else:
            top_activities_dict = {}

        if top_activities_dict:
            for activity, emission in top_activities_dict.items():
                if y < 3 * cm: # Check before drawing
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - 2 * cm
                # Ensure emission is numeric before formatting
                emission_val = emission if isinstance(emission, (int, float)) else 0
                display_activity = (str(activity)[:45] + '...') if len(str(activity)) > 48 else str(activity)
                c.drawString(2.5 * cm, y, f"{display_activity}: {emission_val:.2f} kg CO₂")
                y -= 0.6 * cm
        else:
             c.drawString(2.5 * cm, y, "Top activities data unavailable.")
             y -= 0.6 * cm

        c.save() # Save canvas content
        buffer.seek(0)
    except Exception as e:
        # Log error or handle gracefully
        st.error(f"Error generating PDF: {e}")
        # Optionally return an empty buffer or raise error
        buffer = BytesIO() # Return empty buffer on error
    return buffer


# --- App Config ---
st.set_page_config(page_title="GreenPrint", page_icon="🌿", layout="centered")

# --- Sidebar Logo Styling ---
# Using a raw string for the CSS block just in case
st.markdown(r"""
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
def init_session_state():
    defaults = {
        "profile_completed": False,
        "selected_country": "-- Select --",
        "current_tab_index": 0,
        "emission_values": {},
        "calculation_done": False,
        "calculated_emission": None,
        "comparison_plot_data": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state() # Ensure all keys exist

# --- Load Emission Data ---
CSV_URL = "https://drive.google.com/uc?export=download&id=1PWeBZKB6adZKORvtMDLFwCX__gfzH33g"
PER_CAPITA_URL = "https://raw.githubusercontent.com/keanyaoha/Final_Project_WBS/main/per_capita_filtered_monthly.csv"

@st.cache_data
def load_data(csv_url, per_capita_url):
    try:
        df_emis = pd.read_csv(csv_url)
        df_cap = pd.read_csv(per_capita_url)
        df_emis.columns = df_emis.columns.str.strip()
        # Add basic validation if needed (e.g., check for 'Activity' column)
        if 'Activity' not in df_emis.columns:
             st.error("Emission data CSV is missing the required 'Activity' column.")
             return None, None
        return df_emis, df_cap
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Optionally log the full traceback for debugging
        # st.error(traceback.format_exc())
        return None, None

df, df1 = load_data(CSV_URL, PER_CAPITA_URL)

if df is None or df1 is None:
    st.warning("Could not load necessary data. Please check the data sources or network connection.")
    st.stop() # Stop execution if data loading failed

# Define available countries after successful load
available_countries = sorted([col for col in df.columns if col != "Activity"])

# --- Format Activity Titles ---
def format_activity_name(activity_key):
    mapping = {
        "Domestic_flight_traveled": "Domestic Flights (km)",
        "International_flight_traveled": "International Flights (km)",
        "km_diesel_local_passenger_train_traveled": "Diesel Local Train (km)",
        "km_diesel_long_distance_passenger_train_traveled": "Diesel Long-Dist Train (km)",
        "km_electric_passenger_train_traveled": "Electric Train (km)",
        "km_bus_traveled": "Bus (km)",
        "km_petrol_car_traveled": "Petrol Car (km)",
        "km_Motorcycle_traveled": "Motorcycle (km)",
        "km_ev_scooter_traveled": "E-Scooter (km)",
        "km_ev_car_traveled": "Electric Car (km)",
        "diesel_car_traveled": "Diesel Car (km)",
        "beef_products_consumed": "Beef Products (kg)",
        "poultry_products_consumed": "Poultry Products (kg)",
        "pork_products_consumed": "Pork Products (kg)",
        "fish_products_consumed": "Fish Products (kg)",
        "other_meat_products_consumed": "Other Meat (kg)",
        "processed_rice_consumed": "Rice (kg)",
        "sugar_consumed": "Sugar (kg)",
        "vegetable_oils_fats_consumed": "Veg Oils/Fats (kg)",
        "dairy_products_consumed": "Dairy Products (kg)",
        "other_food_products_consumed": "Other Food (kg)",
        "water_consumed": "Water Consumed (L)",
        "electricity_used": "Electricity Used (kWh)",
        "hotel_stay": "Hotel Nights",
    }
    return mapping.get(activity_key, activity_key.replace("_", " ").capitalize())

# --- App Title ---
st.title("🌍 Carbon Footprint Calculator")
st.markdown("Estimate your monthly carbon footprint and compare it to country and global averages.")
st.divider()

# --- Country Selection ---
st.markdown("**Step 1: Select your country**")
country_options = ["-- Select --"] + available_countries
# Check if selected_country in state is valid, otherwise reset to default
current_selection = st.session_state.selected_country
if current_selection not in country_options:
    current_selection = "-- Select --"
    st.session_state.selected_country = current_selection

selected_country_widget = st.selectbox(
    label="country_select_hidden",
    label_visibility="collapsed",
    options=country_options,
    index=country_options.index(current_selection), # Use validated current_selection
    key="country_selector_main"
)

# --- Update Session State on Country Change ---
# Compare widget value to state value before updating
if selected_country_widget != st.session_state.selected_country:
    st.session_state.selected_country = selected_country_widget
    # Reset dependent state
    st.session_state.current_tab_index = 0
    st.session_state.emission_values = {}
    st.session_state.calculation_done = False
    st.session_state.calculated_emission = None
    st.session_state.comparison_plot_data = None
    st.rerun() # Rerun to apply changes immediately

# --- Main Content Area (Tabs and Calculation) ---
# Proceed only if a valid country (not "-- Select --") is stored in session state
if st.session_state.selected_country != "-- Select --":
    country = st.session_state.selected_country # Use the validated country from state

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
        st.rerun() # Rerun needed to show correct tab content

    # --- Display Content Based on Selected "Tab" ---
    def display_activity_inputs(activities, category_key, current_country):
        """Displays number inputs and calculates emissions for a list of activities."""
        if not isinstance(activities, list): # Basic input validation
            st.error("Internal error: activities must be a list.")
            return

        for activity in activities:
            label = format_activity_name(activity)
            input_key = f"{category_key}_{activity}"
            # Ensure the _input key exists before getting
            if f"{input_key}_input" not in st.session_state.emission_values:
                 st.session_state.emission_values[f"{input_key}_input"] = 0.0
            default_value = st.session_state.emission_values.get(f"{input_key}_input", 0.0)

            user_input = st.number_input(label, min_value=0.0, step=0.1, key=input_key, value=float(default_value)) # Ensure value is float

            # Store the raw input value back into session state
            st.session_state.emission_values[f"{input_key}_input"] = user_input

            # Calculate and store the emission value
            try:
                if activity not in df['Activity'].values:
                     # Optionally inform user activity isn't in base data
                     # st.caption(f"'{label}' not applicable or data missing.")
                     st.session_state.emission_values[activity] = 0.0
                     continue # Skip to next activity

                factor_series = df.loc[df["Activity"] == activity, current_country]

                if not factor_series.empty:
                    factor = factor_series.iloc[0]
                    if pd.isna(factor):
                        st.session_state.emission_values[activity] = 0.0
                    else:
                        st.session_state.emission_values[activity] = user_input * float(factor)
                else:
                    # Should not happen if country column exists, but safety check
                    st.session_state.emission_values[activity] = 0.0

            except KeyError:
                 # This means the country column is missing, which load_data should prevent
                 st.error(f"Data error: Country column '{current_country}' not found in emission factors.")
                 st.session_state.emission_values[activity] = 0.0
            except Exception as e:
                st.error(f"Calculation error for {label}: {e}")
                st.session_state.emission_values[activity] = 0.0

    # --- Define Activity Lists ---
    # Define these lists outside the if/elif block for clarity
    transport_activities = [
        "Domestic_flight_traveled", "International_flight_traveled",
        "km_diesel_local_passenger_train_traveled", "km_diesel_long_distance_passenger_train_traveled",
        "km_electric_passenger_train_traveled", "km_bus_traveled",
        "km_petrol_car_traveled", "diesel_car_traveled",
        "km_Motorcycle_traveled", "km_ev_scooter_traveled", "km_ev_car_traveled"
    ]
    food_activities = [
        "beef_products_consumed", "poultry_products_consumed", "pork_products_consumed",
        "fish_products_consumed", "other_meat_products_consumed", "dairy_products_consumed",
        "processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed",
        "other_food_products_consumed"
    ]
    energy_water_activities = ["electricity_used", "water_consumed"]
    hotel_activities = ["hotel_stay"]

    # --- Display Input Sections and Navigation/Calculation Trigger ---
    current_index = st.session_state.current_tab_index

    if current_index == 0: # Transport Tab
        display_activity_inputs(transport_activities, "transport", country)
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Next →", key="next_transport", use_container_width=True):
                st.session_state.current_tab_index = 1
                st.rerun()

    elif current_index == 1: # Food Tab
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

    elif current_index == 2: # Energy & Water Tab
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

    elif current_index == 3: # Hotel Tab
        display_activity_inputs(hotel_activities, "hotel", country)
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("← Previous", key="prev_hotel", use_container_width=True):
                st.session_state.current_tab_index = 2
                st.rerun()

        # Calculation Trigger Section
        st.divider()
        st.markdown("**Step 3: Calculate your footprint**")
        # Use a unique key for the checkbox
        reviewed_all = st.checkbox("I have reviewed/entered my data for all categories.", key="review_final_check")

        if reviewed_all:
             # Use a unique key for the button
            if st.button("Calculate My Carbon Footprint", type="primary", use_container_width=True, key="calculate_final_button"):
                # Perform Calculation
                emission_values_to_sum = {
                    k: v for k, v in st.session_state.emission_values.items()
                    if not k.endswith('_input') and isinstance(v, (int, float)) and v > 0 # Only sum positive values
                }

                if not emission_values_to_sum: # Check if the filtered dict is empty
                     st.warning("No positive emissions calculated. Please enter some consumption values.")
                     st.session_state.calculation_done = False
                else:
                    total_emission = sum(emission_values_to_sum.values())
                    st.session_state.calculated_emission = total_emission

                    # Prepare comparison data
                    def get_avg(name, df_avg):
                        # Ensure 'Country' and 'PerCapitaCO2' columns exist
                        if "Country" not in df_avg.columns or "PerCapitaCO2" not in df_avg.columns:
                             st.warning(f"Average data columns missing ('Country' or 'PerCapitaCO2'). Cannot get average for {name}.")
                             return None
                        match = df_avg.loc[df_avg["Country"] == name, "PerCapitaCO2"]
                        # Check match is not empty and the value is not NaN
                        return match.iloc[0] if not match.empty and pd.notna(match.iloc[0]) else None

                    # Safely get averages
                    country_avg = get_avg(country, df1) if df1 is not None else None
                    eu_avg = get_avg("European Union (27)", df1) if df1 is not None else None
                    world_avg = get_avg("World", df1) if df1 is not None else None

                    comparison_data = {
                         "country": {"name": country, "avg": country_avg},
                         "eu": {"name": "EU Average", "avg": eu_avg},
                         "world": {"name": "World Average", "avg": world_avg}
                    }
                    st.session_state.comparison_plot_data = comparison_data
                    st.session_state.calculation_done = True
                    st.rerun() # Rerun immediately to show results
        else:
            st.info("Please review your inputs in all categories and check the box above to enable calculation.")


    # --- Display Results Area (Below Tabs, only if calculation is done) ---
    # Check the calculation_done flag from session state
    if st.session_state.get('calculation_done', False):
        st.divider()
        st.subheader("📊 Your Estimated Monthly Carbon Footprint:")

        # Retrieve calculated emission, default to 0 if not found
        total_emission = st.session_state.get('calculated_emission', 0)

        # Display metric only if emission is positive
        if total_emission > 0:
            st.metric(label="kg CO₂ equivalent", value=f"{total_emission:.1f}")

            # Tree equivalence calculation
            # Ensure division by zero doesn't happen, though 21.77 is fixed
            tree_absorb_monthly = (21.77 / 12.0)
            if tree_absorb_monthly > 0:
                 trees_monthly_equiv = total_emission / tree_absorb_monthly
                 st.markdown(f"This is roughly equivalent to the amount of CO₂ absorbed by **{trees_monthly_equiv:.1f} mature trees** in a month.")
            else:
                 st.markdown("Tree equivalence calculation unavailable.")


            st.divider()
            st.subheader("📈 Comparison with Averages")

            # Retrieve comparison data
            comparison_data = st.session_state.get('comparison_plot_data')
            plot_data_list = [] # Data for the plot DataFrame
            captions = []       # Notes for missing averages

            # Add user's data
            plot_data_list.append({"Source": "You", "Emissions": total_emission, "Type": "You"})

            # Safely add comparison data if it exists and averages are valid
            if comparison_data:
                c_data = comparison_data.get("country", {})
                if c_data.get("avg") is not None:
                    plot_data_list.append({"Source": c_data.get("name", "Country"), "Emissions": c_data["avg"], "Type": "Average"})
                else:
                    captions.append(f"Note: Monthly average data for {c_data.get('name', 'your country')} not available.")

                eu_data = comparison_data.get("eu", {})
                if eu_data.get("avg") is not None:
                    plot_data_list.append({"Source": eu_data.get("name", "EU Average"), "Emissions": eu_data["avg"], "Type": "Average"})
                else:
                     captions.append("Note: Monthly average data for EU not available.")

                world_data = comparison_data.get("world", {})
                if world_data.get("avg") is not None:
                    plot_data_list.append({"Source": world_data.get("name", "World Average"), "Emissions": world_data["avg"], "Type": "Average"})
                else:
                    captions.append("Note: Monthly average data for World not available.")

            # Display notes about missing data
            for caption in captions:
                st.caption(caption)

            # Proceed with plotting only if data exists
            if plot_data_list:
                df_comparison = pd.DataFrame(plot_data_list)

                # Define discrete colors
                color_map = {'You': '#1a9850', 'Average': '#a6cee3'} # Green, Light Blue

                try: # Add try-except around plotting
                    fig_comp = px.bar(
                        df_comparison.sort_values("Emissions", ascending=True),
                        x="Emissions",
                        y="Source",
                        orientation='h',
                        color="Type",
                        color_discrete_map=color_map,
                        text="Emissions",
                        title="Monthly Carbon Footprint Comparison",
                        labels={'Emissions': 'kg CO₂ per month', 'Source': '', 'Type': 'Category'}
                    )

                    # Beautification Updates
                    fig_comp.update_traces(
                        texttemplate='%{text:.1f}',
                        textposition='outside',
                        marker_line_width=1,
                        marker_line_color='rgba(0,0,0,0.3)',
                        # Simplified hover template just in case
                        hovertemplate="<b>%{y}</b><br>Emission: %{x:.1f} kg CO₂<extra></extra>"
                    )

                    fig_comp.update_layout(
                        font_family="sans-serif",
                        title_font_size=18,
                        yaxis={'categoryorder':'total ascending'},
                        xaxis_title_font_size=12,
                        yaxis_title_font_size=12,
                        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                        yaxis=dict(showgrid=False),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=5, r=5, t=50, b=20),
                        showlegend=False
                    )

                    st.plotly_chart(fig_comp, use_container_width=True)

                    st.markdown("<div style='text-align: center; color: gray; font-size: small;'>Comparison of your estimated monthly carbon footprint with available national and global averages.</div>", unsafe_allow_html=True)

                except Exception as plot_error:
                    st.error(f"An error occurred while generating the comparison plot: {plot_error}")
                    # st.error(traceback.format_exc()) # Uncomment for detailed debug info

            else:
                st.warning("No data available to generate comparison plot.")
        # else: # Case where total_emission is 0 or less
            # Warning about zero emissions was already shown during calculation step
            # st.info("Your calculated emissions are zero.")


# --- Placeholder if no country is selected ---
elif not st.session_state.selected_country or st.session_state.selected_country == "-- Select --":
    # Optionally add a message prompting selection, or leave blank
    st.info("Please select your country in Step 1 to begin.")
    pass

# --- Sidebar Content ---
st.sidebar.markdown("---")
# Add other sidebar content if needed
