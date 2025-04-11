# -*- coding: utf-8 -*-
import streamlit as st
# import matplotlib.pyplot as plt # Not used here
import plotly.express as px
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader # To read image data for ReportLab
from io import BytesIO
import urllib.request # To fetch the logo URL
import traceback # For detailed error logging

# --- Constants ---
CO2_SUB = "CO\u2082" # Unicode for subscript 2

# --- PDF Report Generator ---
def generate_pdf_report(category_data, top_activities_data):
    buffer = BytesIO()
    try:
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin = 2 * cm # Define margin

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - margin, "GreenPrint Carbon Footprint Report")

        y_pos = height - margin - 1.5*cm # Starting Y below title

        # --- Section 1: Emission by Category ---
        c.setFont("Helvetica-Bold", 12)
        # Check page boundary
        if y_pos < margin + 1*cm: c.showPage(); c.setFont("Helvetica-Bold", 12); y_pos = height - margin
        c.drawString(margin, y_pos, "Emission by Category:")
        c.setFont("Helvetica", 10) # Smaller font for list items
        y_pos -= 0.7 * cm

        if isinstance(category_data, dict) and category_data:
            for category, emission in category_data.items():
                if y_pos < margin: c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin
                emission_val = emission if isinstance(emission, (int, float)) else 0
                c.drawString(margin + 0.5*cm, y_pos, f"• {category}: {emission_val:.2f} kg {CO2_SUB}") # Use subscript
                y_pos -= 0.6 * cm # Adjust spacing
        else:
            if y_pos < margin: c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin
            c.drawString(margin + 0.5*cm, y_pos, "Category data unavailable.")
            y_pos -= 0.6*cm

        # --- Section 2: Top Emitting Activities ---
        y_pos -= 0.5 * cm # Space before next section
        if y_pos < margin + 2*cm: # Check space for title
             c.showPage(); y_pos = height - margin

        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_pos, "Top Emitting Activities:")
        c.setFont("Helvetica", 10) # Smaller font for list
        y_pos -= 0.7 * cm

        # Handle input data type for top activities
        if isinstance(top_activities_data, pd.DataFrame):
            top_activities_dict = dict(zip(top_activities_data.iloc[:,0], top_activities_data.iloc[:,1]))
        elif isinstance(top_activities_data, dict):
            top_activities_dict = top_activities_data
        else:
            top_activities_dict = {}

        if top_activities_dict:
            # Define or import format_activity_name function for PDF consistency
            def format_activity_name_pdf(activity_key):
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

            for activity_key, emission in top_activities_dict.items():
                if y_pos < margin: c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin
                emission_val = emission if isinstance(emission, (int, float)) else 0
                display_name = format_activity_name_pdf(activity_key)
                # Truncate if needed
                display_name = (display_name[:45] + '...') if len(display_name) > 48 else display_name
                c.drawString(margin + 0.5*cm, y_pos, f"• {display_name}: {emission_val:.2f} kg {CO2_SUB}") # Use subscript
                y_pos -= 0.6 * cm # Adjust spacing
        else:
            if y_pos < margin: c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin
            c.drawString(margin + 0.5*cm, y_pos, "Top activities data unavailable.")
            y_pos -= 0.6*cm

        c.save()
        buffer.seek(0)
        return buffer

    except Exception as pdf_err:
        print(f"Critical error during PDF generation: {pdf_err}")
        print(traceback.format_exc())
        buffer = BytesIO() # Return empty on failure
        # Optionally write error to buffer
        # c_err = canvas.Canvas(buffer, pagesize=A4)
        # c_err.drawString(2*cm, height/2, f"Error generating PDF: {pdf_err}")
        # c_err.save()
        buffer.seek(0)
        return buffer


# --- App Config ---
st.set_page_config(page_title="GreenPrint", page_icon="🌿", layout="centered")

# --- Sidebar Logo ---
st.markdown("""
    <style>
        [data-testid="stSidebar"]::before {
            content: ""; display: block;
            background-image: url('https://raw.githubusercontent.com/GhazalMoradi8/Carbon_Footprint_Calculator/main/GreenPrint_logo.png');
            background-size: 90% auto; background-repeat: no-repeat;
            background-position: center; height: 140px;
            margin: 1.5rem auto -4rem auto;
        }
        section[data-testid="stSidebar"] { background-color: #d6f5ec; }
        .stApp { background-color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Emission Breakdown")
st.write("Here is how your estimated carbon footprint breaks down by activity.")

# --- Check for emission data ---
emission_values_state = st.session_state.get("emission_values", {})

if not emission_values_state:
    st.warning("No emission data found. Please fill in your activity data on the main 'Calculator' page first.")
    st.stop()
else:
    emissions_filtered = {
        k: v for k, v in emission_values_state.items()
        if isinstance(v, (int, float)) and v > 0 and not k.endswith('_input')
    }

    if not emissions_filtered:
         st.warning("No positive emissions recorded. Cannot generate breakdown.")
         st.stop()
    else:
        # --- Define categories ---
        categories = {
            "Travel": ["Domestic_flight_traveled", "International_flight_traveled", "km_diesel_local_passenger_train_traveled", "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled", "km_bus_traveled", "km_petrol_car_traveled", "km_ev_car_traveled", "km_ev_scooter_traveled", "km_Motorcycle_traveled", "diesel_car_traveled"],
            "Food": ["beef_products_consumed", "poultry_products_consumed", "pork_products_consumed", "dairy_products_consumed", "fish_products_consumed", "processed_rice_consumed", "sugar_consumed", "vegetable_oils_fats_consumed", "other_food_products_consumed", "other_meat_products_consumed"],
            "Energy & Water": ["electricity_used", "water_consumed"],
            "Other": ["hotel_stay"]
        }

        # --- Compute totals ---
        category_totals = {}
        all_categorized_emissions = {}
        for cat, acts_in_cat in categories.items():
            cat_total = sum(emissions_filtered.get(act_key, 0) for act_key in acts_in_cat)
            if cat_total > 0:
                category_totals[cat] = cat_total
                for act_key in acts_in_cat:
                     if emissions_filtered.get(act_key, 0) > 0:
                         all_categorized_emissions[act_key] = emissions_filtered[act_key]

        if not category_totals:
            st.warning("Could not calculate category totals.")
            st.stop()

        category_df = pd.DataFrame(list(category_totals.items()), columns=["Category", f"Emissions (kg {CO2_SUB})"]) # Use subscript in DF column name

        # --- Category Chart ---
        st.subheader("🔍 Emission by Category")
        # Use the column name with subscript for x-axis data
        fig1 = px.bar(category_df.sort_values(f"Emissions (kg {CO2_SUB})", ascending=True),
                      x=f"Emissions (kg {CO2_SUB})", y="Category",
                      orientation='h', color=f"Emissions (kg {CO2_SUB})",
                      color_continuous_scale="Greens",
                      text=f"Emissions (kg {CO2_SUB})") # Use subscript for text labels too
        fig1.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        # Update axis title to use subscript
        fig1.update_layout(yaxis_title=None, xaxis_title=f"Emissions (kg {CO2_SUB})")
        st.plotly_chart(fig1, use_container_width=True)

        # --- Top Emitting Activities ---
        activity_df = pd.DataFrame(list(emissions_filtered.items()), columns=["Activity Key", "Emissions"])

        # --- Format Activity Names for Display ---
        def format_activity_name(activity_key): # Ensure this function is defined/accessible
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

        top_n = min(10, len(activity_df))
        top_n_df = activity_df.sort_values("Emissions", ascending=False).head(top_n)

        if not top_n_df.empty:
             st.subheader(f"🏆 Top {top_n} Emitting Activities")
             fig2 = px.bar(top_n_df.sort_values("Emissions", ascending=True),
                           x="Emissions", y="Activity Name", # Use formatted name
                           orientation='h', color="Emissions",
                           color_continuous_scale="Blues",
                           text="Emissions")
             fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
              # Update axis title to use subscript
             fig2.update_layout(yaxis_title=None, xaxis_title=f"Emissions (kg {CO2_SUB})")
             st.plotly_chart(fig2, use_container_width=True)

             # --- Prepare data for PDF ---
             # Pass the original keys and emissions for PDF
             pdf_top_activities_data = dict(zip(top_n_df["Activity Key"], top_n_df["Emissions"]))

             # --- PDF Download Button ---
             st.subheader("📄 Download Your Report")
             # Generate PDF (only contains text data now)
             pdf_bytes = generate_pdf_report(
                 category_data=category_totals,
                 top_activities_data=pdf_top_activities_data
             )
             st.download_button(
                 label="⬇️ Download Report as PDF",
                 data=pdf_bytes,
                 file_name="GreenPrint_Carbon_Report_Text.pdf", # Changed name slightly
                 mime="application/pdf"
             )
        else:
            st.info("No activities with emissions found to display top emitters.")

# --- No detailed breakdown or graph embedding in PDF in this version ---
