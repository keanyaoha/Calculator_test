import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO

# --- PDF Report Generator ---
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
    # Check if category_data is a dictionary before iterating
    if isinstance(category_data, dict):
        for category, emission in category_data.items():
            # Ensure emission is numeric before formatting
            emission_val = emission if isinstance(emission, (int, float)) else 0
            c.drawString(2.5 * cm, y, f"{category}: {emission_val:.2f} kg CO₂")
            y -= 0.7 * cm
    else:
         c.drawString(2.5 * cm, y, "Category data unavailable.")
         y -= 0.7*cm


    c.setFont("Helvetica-Bold", 12)
    y -= 0.5 * cm
    # Check page boundary before drawing next title
    if y < 4*cm:
        c.showPage()
        c.setFont("Helvetica-Bold", 12)
        y = height - 2 * cm
    c.drawString(2 * cm, y, "Top Emitting Activities:") # Changed title slightly for consistency
    c.setFont("Helvetica", 11)
    y -= 1 * cm

    # Handle input format for top activities
    if isinstance(top_activities_data, dict):
        top_activities_dict = top_activities_data
    # Added check in case a DataFrame was passed accidentally, take first two columns
    elif isinstance(top_activities_data, pd.DataFrame) and top_activities_data.shape[1] >= 2:
         top_activities_dict = dict(zip(top_activities_data.iloc[:,0], top_activities_data.iloc[:,1]))
    else:
        top_activities_dict = {} # Default to empty if format is unexpected


    if top_activities_dict:
        for activity, emission in top_activities_dict.items():
             # Check page boundary before drawing activity
            if y < 3 * cm:
                c.showPage()
                c.setFont("Helvetica", 11) # Reset font
                y = height - 2 * cm
            # Ensure emission is numeric before formatting
            emission_val = emission if isinstance(emission, (int, float)) else 0
            # Truncate activity name if too long
            display_activity = (str(activity)[:45] + '...') if len(str(activity)) > 48 else str(activity)
            c.drawString(2.5 * cm, y, f"{display_activity}: {emission_val:.2f} kg CO₂")
            y -= 0.6 * cm
    else:
        c.drawString(2.5*cm, y, "Top activities data unavailable.")
        y -= 0.6*cm


    c.save() # Use save() instead of showPage() at the end to finalize
    buffer.seek(0)
    return buffer

# --- App Config ---
st.set_page_config(page_title="GreenPrint", page_icon="🌿", layout="centered")

# --- Sidebar Logo ---
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

st.title("📊 Emission Breakdown")
st.write("Here is how your estimated carbon footprint breaks down by activity.")

# --- Check for emission data ---
# Use .get() for safer access to session state
emission_values_state = st.session_state.get("emission_values", {})

if not emission_values_state: # Check if the dictionary is empty or doesn't exist
    st.warning("No emission data found. Please fill in your activity data on the main 'Calculator' page first.")
    st.stop() # Stop execution if no data
else:
    # Filter out non-positive values and potential non-numeric entries safely
    emissions_filtered = {
        k: v for k, v in emission_values_state.items()
        if isinstance(v, (int, float)) and v > 0 and not k.endswith('_input') # Exclude raw inputs
    }

    if not emissions_filtered:
         st.warning("No positive emissions recorded. Cannot generate breakdown.")
         st.stop() # Stop if only zero/negative emissions
    else:
        # --- Define categories ---
        # Ensure keys match exactly those stored in session_state.emission_values
        # (Corrected Domestic/International flight keys based on likely main page format)
        categories = {
            "Travel": [
                "Domestic_flight_traveled", "International_flight_traveled", # Corrected keys
                "km_diesel_local_passenger_train_traveled",
                "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled",
                "km_bus_traveled", "km_petrol_car_traveled", "km_ev_car_traveled", "km_ev_scooter_traveled",
                "km_Motorcycle_traveled", "diesel_car_traveled"
            ],
            "Food": [
                "beef_products_consumed", "poultry_products_consumed", "pork_products_consumed",
                "dairy_products_consumed", "fish_products_consumed", "processed_rice_consumed",
                "sugar_consumed", "vegetable_oils_fats_consumed", "other_food_products_consumed",
                # "beverages_consumed", # Commented out if not used
                 "other_meat_products_consumed"
            ],
            "Energy & Water": ["electricity_used", "water_consumed"],
            "Other": ["hotel_stay"] # Assuming this is the key for hotel stays
        }

        # --- Compute totals ---
        category_totals = {}
        all_categorized_emissions = {} # Store activities that fall into categories for later use

        for cat, acts_in_cat in categories.items():
            cat_total = 0
            for act_key in acts_in_cat:
                emission_val = emissions_filtered.get(act_key, 0) # Get emission value, default 0 if not found
                cat_total += emission_val
                if emission_val > 0: # Keep track of activities with emissions
                    all_categorized_emissions[act_key] = emission_val
            if cat_total > 0: # Only include categories with non-zero emissions
                 category_totals[cat] = cat_total


        # Handle potential uncategorized emissions (optional but good practice)
        # uncategorized_emissions = {k: v for k, v in emissions_filtered.items() if k not in all_categorized_emissions}
        # if uncategorized_emissions:
        #     category_totals["Uncategorized"] = sum(uncategorized_emissions.values())

        if not category_totals:
            st.warning("Could not calculate category totals from available emission data.")
            st.stop()


        category_df = pd.DataFrame({
            "Category": category_totals.keys(),
            "Emissions (kg CO₂)": category_totals.values()
        })

        # --- Category Chart ---
        st.subheader("🔍 Emission by Category")
        fig1 = px.bar(category_df.sort_values("Emissions (kg CO₂)", ascending=True),
                      x="Emissions (kg CO₂)", y="Category",
                      orientation='h', color="Emissions (kg CO₂)",
                      color_continuous_scale="Greens",
                      text="Emissions (kg CO₂)") # Show values on bars
        fig1.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig1.update_layout(yaxis_title=None) # Remove y-axis title
        st.plotly_chart(fig1, use_container_width=True)

        # --- Top Emitting Activities (based on filtered, positive emissions) ---
        # st.subheader("🏆 Top Emitting Activities") # Changed number if less than 10 available
        # Create DataFrame from the filtered positive emissions
        activity_df = pd.DataFrame(list(emissions_filtered.items()), columns=["Activity Key", "Emissions"])

        # --- Format Activity Names for Display ---
        # Import the formatting function if it's defined in another file,
        # otherwise define it here or ensure it's accessible
        # Assuming format_activity_name is defined elsewhere or copy it here:
        def format_activity_name(activity_key): # Basic version if not imported
            mapping = {
                 "Domestic_flight_traveled": "Domestic Flights", "International_flight_traveled": "International Flights",
                 "km_diesel_local_passenger_train_traveled": "Diesel Local Train", "km_diesel_long_distance_passenger_train_traveled": "Diesel Long-Dist Train",
                 "km_electric_passenger_train_traveled": "Electric Train", "km_bus_traveled": "Bus",
                 "km_petrol_car_traveled": "Petrol Car", "km_Motorcycle_traveled": "Motorcycle",
                 "km_ev_scooter_traveled": "E-Scooter", "km_ev_car_traveled": "Electric Car",
                 "diesel_car_traveled": "Diesel Car", "beef_products_consumed": "Beef Products",
                 "poultry_products_consumed": "Poultry Products", "pork_products_consumed": "Pork Products",
                 "fish_products_consumed": "Fish Products", "other_meat_products_consumed": "Other Meat",
                 "processed_rice_consumed": "Rice", "sugar_consumed": "Sugar",
                 "vegetable_oils_fats_consumed": "Veg Oils/Fats", "dairy_products_consumed": "Dairy Products",
                 "other_food_products_consumed": "Other Food", "water_consumed": "Water",
                 "electricity_used": "Electricity", "hotel_stay": "Hotel Stay",
             }
            return mapping.get(activity_key, activity_key.replace("_", " ").capitalize())

        activity_df["Activity Name"] = activity_df["Activity Key"].apply(format_activity_name)
        # -----------------------------------------

        # Get top N activities, where N is min(10, number of activities)
        top_n = min(10, len(activity_df))
        top_n_df = activity_df.sort_values("Emissions", ascending=False).head(top_n)

        if not top_n_df.empty:
             st.subheader(f"🏆 Top {top_n} Emitting Activities") # Dynamic title
             fig2 = px.bar(top_n_df.sort_values("Emissions", ascending=True),
                           x="Emissions", y="Activity Name", # Use formatted name for y-axis
                           orientation='h', color="Emissions",
                           color_continuous_scale="Blues",
                           text="Emissions") # Show values
             fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
             fig2.update_layout(yaxis_title=None) # Remove y-axis title
             st.plotly_chart(fig2, use_container_width=True)

             # Prepare data for PDF (using original keys might be better for consistency)
             # Pass the original keys and emissions for PDF if needed
             pdf_top_activities_data = dict(zip(top_n_df["Activity Key"], top_n_df["Emissions"]))

             # --- PDF Download ---
             st.subheader("📄 Download Your Report")
             # Use the prepared dictionary for top activities in the PDF
             pdf_data = generate_pdf_report(category_totals, pdf_top_activities_data)
             st.download_button(
                 label="⬇️ Download Report as PDF",
                 data=pdf_data,
                 file_name="GreenPrint_Carbon_Report.pdf",
                 mime="application/pdf" # Set mime type for PDF
             )
        else:
            st.info("No activities with emissions found to display top emitters.")


# --- DETAILED BREAKDOWN SECTION REMOVED ---
#        st.subheader("📦 Detailed Breakdown by Category")
#        for cat, acts in categories.items():
#            cat_acts = {a: emissions_filtered[a] for a in acts if a in emissions_filtered}
#            if cat_acts:
#                st.markdown(f"**{cat}**")
#                df_cat = pd.DataFrame(list(cat_acts.items()), columns=["Activity", "Emissions"])
#                # Format activity names for display
#                df_cat["Activity Name"] = df_cat["Activity"].apply(format_activity_name)
#                fig = px.bar(df_cat.sort_values("Emissions", ascending=True),
#                             x="Emissions", y="Activity Name", # Use formatted names
#                             orientation='h', color="Emissions",
#                             color_continuous_scale="Purples",
#                             text="Emissions")
#                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
#                fig.update_layout(yaxis_title=None)
#                st.plotly_chart(fig, use_container_width=True)
# --- END OF REMOVED SECTION ---
