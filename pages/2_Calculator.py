import pandas as pd
import streamlit as st
# import matplotlib.pyplot as plt # No longer needed for this script if only using Plotly
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO

# --- PDF Report Generator (If needed in this file) ---
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
    y -= 0.5 * cm
    c.drawString(2 * cm, y, "Top Emitting Activities:")
    c.setFont("Helvetica", 11)
    y -= 0.7 * cm

    # Handle different input types for top activities
    if isinstance(top_activities_data, pd.DataFrame):
        top_activities_dict = dict(zip(top_activities_data.iloc[:,0], top_activities_data.iloc[:,1]))
    elif isinstance(top_activities_data, dict):
        top_activities_dict = top_activities_data
    else:
        top_activities_dict = {} # Default empty

    for activity, emission in top_activities_dict.items():
        display_activity = (str(activity)[:45] + '...') if len(str(activity)) > 48 else str(activity)
        c.drawString(2.5 * cm, y, f"{display_activity}: {emission:.2f} kg CO₂")
        y -= 0.6 * cm
        if y < 3 * cm: # Check for page break
            c.showPage()
            c.setFont("Helvetica", 11) # Reset font on new page
            y = height - 2 * cm

    c.save() # Save canvas content
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
    # Using shorter names for display
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
    # Return formatted name or a cleaned-up default
    return mapping.get(activity, activity.replace("_", " ").replace("km ", "").replace(" traveled", "").replace(" consumed", "").capitalize())


# --- App Title ---
st.title("🌍 Carbon Footprint Calculator")
st.markdown("Estimate your monthly carbon footprint and compare it to country and global averages.")
st.divider()

# --- Country Selection ---
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

    clicked_index = tab_labels.index(selected_tab_label)
    if clicked_index != st.session_state.current_tab_index:
        st.session_state.current_tab_index = clicked_index
        st.rerun()


    # --- Display Content Based on Selected "Tab" ---
    def display_activity_inputs(activities, category_key, current_country):
        """Displays number inputs and calculates emissions for a list of activities."""
        for activity in activities:
            label = format_activity_name(activity)
            input_key = f"{category_key}_{activity}"
            default_value = st.session_state.emission_values.get(f"{input_key}_input", 0.0)
            user_input = st.number_input(label, min_value=0.0, step=0.1, key=input_key, value=default_value)
            st.session_state.emission_values[f"{input_key}_input"] = user_input

            try:
                factor_series = df.loc[df["Activity"] == activity, current_country]
                if not factor_series.empty:
                    factor = factor_series.iloc[0]
                    if pd.isna(factor):
                        st.session_state.emission_values[activity] = 0.0
                    else:
                        st.session_state.emission_values[activity] = user_input * float(factor)
                else:
                    st.session_state.emission_values[activity] = 0.0
            except KeyError:
                 st.error(f"Data error: Country column '{current_country}' not found.")
                 st.session_state.emission_values[activity] = 0.0
            except Exception as e:
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

        # Calculation Trigger Section
        st.divider()
        st.markdown("**Step 3: Calculate your footprint**")
        reviewed_all = st.checkbox("I have reviewed/entered my data for all categories.", key="review_check")

        if reviewed_all:
            if st.button("Calculate My Carbon Footprint", type="primary", use_container_width=True, key="calculate_button"):
                emission_values_to_sum = {
                    k: v for k, v in st.session_state.emission_values.items()
                    if not k.endswith('_input') and isinstance(v, (int, float))
                }

                if not emission_values_to_sum or sum(emission_values_to_sum.values()) <= 0:
                     st.warning("No emissions calculated or total is zero. Please enter some consumption values.")
                     st.session_state.calculation_done = False
                else:
                    total_emission = sum(emission_values_to_sum.values())
                    st.session_state.calculated_emission = total_emission

                    def get_avg(name, df_avg):
                        match = df_avg.loc[df_avg["Country"] == name, "PerCapitaCO2"]
                        return match.iloc[0] if not match.empty and pd.notna(match.iloc[0]) else None

                    country_avg = get_avg(country, df1)
                    eu_avg = get_avg("European Union (27)", df1)
                    world_avg = get_avg("World", df1)

                    comparison_data = {
                         "country": {"name": country, "avg": country_avg},
                         "eu": {"name": "EU Average", "avg": eu_avg},
                         "world": {"name": "World Average", "avg": world_avg}
                    }
                    st.session_state.comparison_plot_data = comparison_data
                    st.session_state.calculation_done = True
                    st.rerun()
        else:
            st.info("Please review your inputs in all categories and check the box above to enable calculation.")


    # --- Display Results Area (Below Tabs, only if calculation is done) ---
    if st.session_state.get('calculation_done', False):
        st.divider()
        st.subheader(f"📊 Your Estimated Monthly Carbon Footprint:")

        total_emission = st.session_state.get('calculated_emission', 0)

        if total_emission > 0:
            st.metric(label="kg CO₂ equivalent", value=f"{total_emission:.1f}")

            trees_monthly_equiv = total_emission / (21.77 / 12)
            st.markdown(f"This is roughly equivalent to the amount of CO₂ absorbed by **{trees_monthly_equiv:.1f} mature trees** in a month.")

            st.divider()
            st.subheader("📈 Comparison with Averages")

            comparison_data = st.session_state.get('comparison_plot_data')
            plot_data_list = []
            captions = []

            # Add "You" data with a specific Type
            plot_data_list.append({"Source": "You", "Emissions": total_emission, "Type": "You"})

            if comparison_data:
                # Add comparison data with Type 'Average' if avg exists
                c_data = comparison_data["country"]
                if c_data["avg"] is not None:
                    plot_data_list.append({"Source": c_data["name"], "Emissions": c_data["avg"], "Type": "Average"})
                else:
                    captions.append(f"Note: Monthly average data for {c_data['name']} not available.")

                eu_data = comparison_data["eu"]
                if eu_data["avg"] is not None:
                    plot_data_list.append({"Source": eu_data["name"], "Emissions": eu_data["avg"], "Type": "Average"})
                else:
                     captions.append("Note: Monthly average data for EU not available.")

                world_data = comparison_data["world"]
                if world_data["avg"] is not None:
                    plot_data_list.append({"Source": world_data["name"], "Emissions": world_data["avg"], "Type": "Average"})
                else:
                    captions.append("Note: Monthly average data for World not available.")

            for caption in captions:
                st.caption(caption)

            if len(plot_data_list) > 0:
                df_comparison = pd.DataFrame(plot_data_list)

                # Define discrete colors
                color_map = {'You': '#1a9850', 'Average': '#a6cee3'} # Green for You, Light Blue for Averages

                fig_comp = px.bar(
                    df_comparison.sort_values("Emissions", ascending=True),
                    x="Emissions",
                    y="Source",
                    orientation='h',
                    color="Type",                 # Color by the 'Type' column
                    color_discrete_map=color_map, # Apply the defined colors
                    text="Emissions",
                    title="Monthly Carbon Footprint Comparison",
                    labels={'Emissions': 'kg CO₂ per month', 'Source': '', 'Type': 'Category'}
                )

                # --- Beautification Updates ---
                fig_comp.update_traces(
                    texttemplate='%{text:.1f}',   # Format text labels
                    textposition='outside',       # Position labels outside bars
                    marker_line_width=1,          # Add a subtle line around bars
                    marker_line_color='rgba(0,0,0,0.3)', # Darker line color
                    hovertemplate="<b>%{y}</b><br>Emission: %{x:.1f} kg CO₂<extra></extra>" # Clean hover text
                )

                fig_comp.update_layout(
                    font_family="sans-serif",     # Use a clean sans-serif font
                    title_font_size=18,           # Slightly larger title
                    yaxis={'categoryorder':'total ascending'}, # Ensure bars are ordered by value
                    xaxis_title_font_size=12,     # Standard axis title size
                    yaxis_title_font_size=12,
                    xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'), # Subtle vertical grid lines
                    yaxis=dict(showgrid=False),   # No horizontal grid lines
                    plot_bgcolor='rgba(0,0,0,0)', # Transparent plot background
                    paper_bgcolor='rgba(0,0,0,0)',# Transparent paper background
                    margin=dict(l=5, r=5, t=50, b=20), # Adjust margins
                    showlegend=False              # Hide legend
                )
                # --- End Beautification ---

                st.plotly_chart(fig_comp, use_container_width=True)

                st.markdown("<div style='text-align: center; color: gray; font-size: small;'>Comparison of your estimated monthly carbon footprint with available national and global averages.</div>", unsafe_allow_html=True)

            else:
                st.warning("No data available to generate comparison plot.")
        else:
            st.warning("Calculated emission value not found or is zero.")


# --- Placeholder if no country is selected ---
elif not st.session_state.selected_country or st.session_state.selected_country == "-- Select --":
    pass # Main content area is not rendered

# --- Sidebar Content ---
st.sidebar.markdown("---")
# Removed other sidebar elements like data source info based on previous request
