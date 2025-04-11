# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader # To read image data for ReportLab
from io import BytesIO
import urllib.request # To fetch the logo URL
import traceback # For detailed error logging

# --- Enhanced PDF Report Generator ---
def generate_pdf_report(logo_data, category_data, top_activities_data, fig1_img_data, fig2_img_data):
    buffer = BytesIO()
    try:
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin = 2 * cm

        # --- Draw Logo ---
        if logo_data:
            try:
                logo_img = ImageReader(logo_data)
                img_w, img_h = logo_img.getSize()
                aspect = img_h / float(img_w)
                draw_width = 4 * cm # Desired width for logo
                draw_height = draw_width * aspect
                # Position top-right (adjust x as needed)
                c.drawImage(logo_img, width - margin - draw_width, height - margin - draw_height,
                            width=draw_width, height=draw_height, preserveAspectRatio=True, mask='auto')
            except Exception as logo_err:
                print(f"Error drawing logo: {logo_err}") # Log error

        # --- Title ---
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - margin - (draw_height / 2 if logo_data else 0) - 0.5*cm , "GreenPrint Carbon Footprint Report") # Adjust title position based on logo

        # --- Current Y Position ---
        # Start below title/logo area
        y_pos = height - margin - (draw_height if logo_data else 0) - 2*cm

        # --- Section 1: Emission by Category ---
        c.setFont("Helvetica-Bold", 12)
        y_pos -= 1*cm
        c.drawString(margin, y_pos, "Emission by Category:")
        c.setFont("Helvetica", 10)
        y_pos -= 0.7 * cm

        if isinstance(category_data, dict) and category_data:
            for category, emission in category_data.items():
                if y_pos < margin + 1*cm: # Check space before drawing text
                    c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin # New page
                emission_val = emission if isinstance(emission, (int, float)) else 0
                c.drawString(margin + 0.5*cm, y_pos, f"• {category}: {emission_val:.2f} kg CO₂")
                y_pos -= 0.6 * cm
        else:
            if y_pos < margin + 1*cm: c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin
            c.drawString(margin + 0.5*cm, y_pos, "Category data unavailable.")
            y_pos -= 0.6*cm

        # --- Draw Category Graph (fig1) ---
        y_pos -= 0.5 * cm # Space before graph
        if fig1_img_data:
            try:
                graph1_img = ImageReader(fig1_img_data)
                img_w, img_h = graph1_img.getSize()
                aspect = img_h / float(img_w)
                # Calculate available width, leave margins
                draw_width = width - (2 * margin)
                draw_height = draw_width * aspect
                # Check if graph fits on current page
                if y_pos - draw_height < margin:
                    c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin # New page
                    y_pos -= 0.5*cm # Add a little space at top of new page graph

                c.drawImage(graph1_img, margin, y_pos - draw_height,
                            width=draw_width, height=draw_height, preserveAspectRatio=True, mask='auto')
                y_pos -= (draw_height + 1*cm) # Move y below graph + add space
            except Exception as graph1_err:
                print(f"Error drawing category graph: {graph1_err}")
                if y_pos < margin + 1*cm: c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin
                c.drawString(margin, y_pos, "[Category graph could not be rendered]")
                y_pos -= 0.6 * cm

        # --- Section 2: Top Emitting Activities ---
        if y_pos < margin + 3*cm : # Check space before section title
             c.showPage(); y_pos = height - margin

        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_pos, "Top Emitting Activities:")
        c.setFont("Helvetica", 10)
        y_pos -= 0.7 * cm

        # Prepare top activities data (ensure it's a dict)
        if isinstance(top_activities_data, pd.DataFrame):
            top_activities_dict = dict(zip(top_activities_data.iloc[:,0], top_activities_data.iloc[:,1]))
        elif isinstance(top_activities_data, dict):
            top_activities_dict = top_activities_data
        else:
            top_activities_dict = {}

        if top_activities_dict:
            # Use the same formatting function as the Streamlit page
            # (ensure it's accessible here or redefine it)
            def format_activity_name_pdf(activity_key):
                 mapping = { # Copied from Streamlit page - keep consistent!
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
                if y_pos < margin + 1*cm: # Check space before text
                    c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin
                emission_val = emission if isinstance(emission, (int, float)) else 0
                display_name = format_activity_name_pdf(activity_key)
                # Truncate display name if needed
                display_name = (display_name[:45] + '...') if len(display_name) > 48 else display_name
                c.drawString(margin + 0.5*cm, y_pos, f"• {display_name}: {emission_val:.2f} kg CO₂")
                y_pos -= 0.6 * cm
        else:
            if y_pos < margin + 1*cm: c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin
            c.drawString(margin + 0.5*cm, y_pos, "Top activities data unavailable.")
            y_pos -= 0.6*cm

        # --- Draw Top Activities Graph (fig2) ---
        y_pos -= 0.5 * cm # Space before graph
        if fig2_img_data:
            try:
                graph2_img = ImageReader(fig2_img_data)
                img_w, img_h = graph2_img.getSize()
                aspect = img_h / float(img_w)
                draw_width = width - (2 * margin)
                draw_height = draw_width * aspect
                if y_pos - draw_height < margin: # Check space
                    c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin
                    y_pos -= 0.5*cm # Space at top

                c.drawImage(graph2_img, margin, y_pos - draw_height,
                            width=draw_width, height=draw_height, preserveAspectRatio=True, mask='auto')
                y_pos -= (draw_height + 1*cm) # Move below graph
            except Exception as graph2_err:
                print(f"Error drawing top activities graph: {graph2_err}")
                if y_pos < margin + 1*cm: c.showPage(); c.setFont("Helvetica", 10); y_pos = height - margin
                c.drawString(margin, y_pos, "[Top Activities graph could not be rendered]")
                y_pos -= 0.6 * cm

        # --- Finalize PDF ---
        c.save() # Finalizes the PDF document
        buffer.seek(0)
        return buffer

    except Exception as pdf_err:
        print(f"Critical error during PDF generation: {pdf_err}")
        print(traceback.format_exc())
        # Return an empty buffer or handle error appropriately
        buffer = BytesIO() # Create empty buffer on failure
        # Optionally write an error message to the buffer itself
        # c_err = canvas.Canvas(buffer, pagesize=A4)
        # c_err.drawString(2*cm, height/2, "Error generating PDF report.")
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

# --- Function to fetch logo (cached) ---
@st.cache_data(ttl=3600) # Cache logo data for an hour
def get_logo_data(url):
    try:
        with urllib.request.urlopen(url) as response:
            return BytesIO(response.read())
    except Exception as e:
        st.error(f"Failed to download logo: {e}")
        return None

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
            "Travel": [
                "Domestic_flight_traveled", "International_flight_traveled",
                "km_diesel_local_passenger_train_traveled",
                "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled",
                "km_bus_traveled", "km_petrol_car_traveled", "km_ev_car_traveled", "km_ev_scooter_traveled",
                "km_Motorcycle_traveled", "diesel_car_traveled"
            ],
            "Food": [
                "beef_products_consumed", "poultry_products_consumed", "pork_products_consumed",
                "dairy_products_consumed", "fish_products_consumed", "processed_rice_consumed",
                "sugar_consumed", "vegetable_oils_fats_consumed", "other_food_products_consumed",
                 "other_meat_products_consumed"
            ],
            "Energy & Water": ["electricity_used", "water_consumed"],
            "Other": ["hotel_stay"]
        }

        # --- Compute totals ---
        category_totals = {}
        all_categorized_emissions = {}

        for cat, acts_in_cat in categories.items():
            cat_total = 0
            for act_key in acts_in_cat:
                emission_val = emissions_filtered.get(act_key, 0)
                cat_total += emission_val
                if emission_val > 0:
                    all_categorized_emissions[act_key] = emission_val
            if cat_total > 0:
                 category_totals[cat] = cat_total

        if not category_totals:
            st.warning("Could not calculate category totals from available emission data.")
            st.stop()

        category_df = pd.DataFrame(list(category_totals.items()), columns=["Category", "Emissions (kg CO₂)"])

        # --- Category Chart ---
        st.subheader("🔍 Emission by Category")
        # Ensure text aligns with the x-axis label
        fig1 = px.bar(category_df.sort_values("Emissions (kg CO₂)", ascending=True),
                      x="Emissions (kg CO₂)", y="Category",
                      orientation='h', color="Emissions (kg CO₂)",
                      color_continuous_scale="Greens",
                      text="Emissions (kg CO₂)")
        fig1.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig1.update_layout(yaxis_title=None, xaxis_title="Emissions (kg CO₂)")
        st.plotly_chart(fig1, use_container_width=True)

        # --- Top Emitting Activities ---
        activity_df = pd.DataFrame(list(emissions_filtered.items()), columns=["Activity Key", "Emissions"])

        # --- Format Activity Names for Display ---
        def format_activity_name(activity_key): # Ensure this function is available
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
             fig2.update_layout(yaxis_title=None, xaxis_title="Emissions (kg CO₂)")
             st.plotly_chart(fig2, use_container_width=True)

             # --- Prepare data for PDF ---
             # Convert figures to image bytes
             fig1_img_data = None
             fig2_img_data = None
             try:
                 # Increase scale for better resolution in PDF
                 fig1_img_data = BytesIO(fig1.to_image(format="png", scale=2))
                 fig2_img_data = BytesIO(fig2.to_image(format="png", scale=2))
             except Exception as img_err:
                  st.error(f"Could not generate images for PDF report: {img_err}")
                  st.error("Please ensure 'kaleido' is installed (`pip install kaleido`).")

             # Get logo data
             logo_url = 'https://raw.githubusercontent.com/GhazalMoradi8/Carbon_Footprint_Calculator/main/GreenPrint_logo.png'
             logo_data = get_logo_data(logo_url)

             # Prepare top activities data as dict (using original keys)
             pdf_top_activities_data = dict(zip(top_n_df["Activity Key"], top_n_df["Emissions"]))

             # --- PDF Download Button ---
             st.subheader("📄 Download Your Report")
             # Generate PDF only if image generation was successful
             if logo_data and fig1_img_data and fig2_img_data:
                 pdf_bytes = generate_pdf_report(
                     logo_data=logo_data,
                     category_data=category_totals,
                     top_activities_data=pdf_top_activities_data,
                     fig1_img_data=fig1_img_data,
                     fig2_img_data=fig2_img_data
                 )
                 st.download_button(
                     label="⬇️ Download Report as PDF",
                     data=pdf_bytes,
                     file_name="GreenPrint_Carbon_Report.pdf",
                     mime="application/pdf"
                 )
             else:
                 st.warning("Could not generate PDF because logo or graph images failed to load/render.")

        else:
            st.info("No activities with emissions found to display top emitters.")

# --- No detailed breakdown needed based on user request ---
