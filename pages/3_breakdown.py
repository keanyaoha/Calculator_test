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

# --- Constants ---
MARGIN = 1.8 * cm
CO2_SUB = "CO\u2082" # Unicode for subscript 2 - Ensure your PDF viewer/font supports it

# --- Enhanced PDF Report Generator with Images ---
def generate_pdf_report(logo_data, category_data, top_activities_data, fig1_img_data, fig2_img_data):
    buffer = BytesIO()
    try:
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # --- Draw Logo ---
        logo_height = 0
        if logo_data:
            try:
                logo_img = ImageReader(logo_data)
                img_w, img_h = logo_img.getSize()
                aspect = img_h / float(img_w) if img_w > 0 else 1
                draw_width = 5.5 * cm # Slightly larger logo
                draw_height = draw_width * aspect
                logo_height = draw_height
                c.drawImage(logo_img, width - MARGIN - draw_width, height - MARGIN - draw_height,
                            width=draw_width, height=draw_height, preserveAspectRatio=True, mask='auto')
            except Exception as logo_err:
                print(f"Error drawing logo: {logo_err}")

        # --- Title ---
        c.setFont("Helvetica-Bold", 16)
        title_y = height - MARGIN - (logo_height / 2 if logo_height > 0 else 0) - 0.5 * cm
        c.drawCentredString(width / 2.0, title_y, "GreenPrint Carbon Footprint Report")
        y_pos = title_y - 1.5 * cm # Start below title/logo

        # --- Section 1: Emission by Category (Text) ---
        c.setFont("Helvetica-Bold", 12)
        if y_pos < MARGIN + 2*cm: c.showPage(); c.setFont("Helvetica-Bold", 12); y_pos = height - MARGIN # New page if needed
        c.drawString(MARGIN, y_pos, f"Emission by Category:")
        c.setFont("Helvetica", 9.5)
        y_pos -= 0.6 * cm

        if isinstance(category_data, dict) and category_data:
            for category, emission in category_data.items():
                if y_pos < MARGIN + 1*cm: c.showPage(); c.setFont("Helvetica", 9.5); y_pos = height - MARGIN
                emission_val = emission if isinstance(emission, (int, float)) else 0
                c.drawString(MARGIN + 0.5*cm, y_pos, f"• {category}: {emission_val:.2f} kg {CO2_SUB}") # Use subscript
                y_pos -= 0.55 * cm
        else:
             if y_pos < MARGIN + 1*cm: c.showPage(); c.setFont("Helvetica", 9.5); y_pos = height - MARGIN
             c.drawString(MARGIN + 0.5*cm, y_pos, "Category data unavailable.")
             y_pos -= 0.55*cm

        # --- Draw Category Graph (fig1) ---
        y_pos -= 0.4 * cm # Space before graph
        if fig1_img_data:
            try:
                graph1_img = ImageReader(fig1_img_data)
                img_w, img_h = graph1_img.getSize()
                aspect = img_h / float(img_w) if img_w > 0 else 1
                draw_width = width - (2 * MARGIN)
                draw_height = draw_width * aspect
                max_graph_height = 7*cm # Limit height
                if draw_height > max_graph_height:
                    draw_height = max_graph_height
                    draw_width = draw_height / aspect if aspect > 0 else draw_width

                if y_pos - draw_height < MARGIN: # Check if graph fits
                    c.showPage(); c.setFont("Helvetica", 9.5); y_pos = height - MARGIN # Start new page
                    y_pos -= 0.3*cm # Space at top

                c.drawImage(graph1_img, MARGIN, y_pos - draw_height,
                            width=draw_width, height=draw_height, preserveAspectRatio=True, mask='auto')
                y_pos -= (draw_height + 0.6*cm) # Move below graph
            except Exception as graph1_err:
                print(f"Error drawing category graph: {graph1_err}")
                if y_pos < MARGIN + 1*cm: c.showPage(); c.setFont("Helvetica", 9.5); y_pos = height - MARGIN
                c.drawString(MARGIN, y_pos, "[Category graph could not be rendered]")
                y_pos -= 0.6 * cm

        # --- Section 2: Top Emitting Activities (Text) ---
        if y_pos < MARGIN + 3*cm : # Check space
             c.showPage(); y_pos = height - MARGIN

        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN, y_pos, "Top Emitting Activities:")
        c.setFont("Helvetica", 9.5)
        y_pos -= 0.6 * cm

        # Handle data format
        if isinstance(top_activities_data, pd.DataFrame):
            top_activities_dict = dict(zip(top_activities_data.iloc[:,0], top_activities_data.iloc[:,1]))
        elif isinstance(top_activities_data, dict):
            top_activities_dict = top_activities_data
        else:
            top_activities_dict = {}

        if top_activities_dict:
            def format_activity_name_pdf(activity_key): # Needs access to this mapping
                 mapping = {
                  "Domestic_flight": "Domestic Flights", "International_flight": "International Flights",
                  "Diesel_train_local": "Diesel Local Train", "Diesel_train_long": "Diesel Long-Dist Train",
                  "Electric_train": "Electric Train", "Bus": "Bus",
                  "Petrol_car": "Petrol Car", "Motorcycle": "Motorcycle",
                  "Ev_scooter": "E-Scooter", "Ev_car": "Electric Car",
                  "Diesel_car": "Diesel Car", "Beef": "Beef Products",
                  "Poultry": "Poultry Products", "Beverages": "Beverages", "Pork": "Pork Products",
                  "Fish_products": "Fish Products", "Other_meat": "Other Meat Products",
                  "Rice": "Rice", "Sugar": "Sugar",
                  "Oils_fats": "Veg Oils/Fats", "Dairy": "Dairy Products",
                  "Other_food": "Other Food", "Water": "Water",
                  "Electricity": "Electricity", "Hotel_stay": "Hotel Stay",
                 }
                 return mapping.get(activity_key, activity_key.replace("_", " ").capitalize())

            for activity_key, emission in top_activities_dict.items():
                if y_pos < MARGIN + 1*cm:
                    c.showPage(); c.setFont("Helvetica", 9.5); y_pos = height - MARGIN
                emission_val = emission if isinstance(emission, (int, float)) else 0
                display_name = format_activity_name_pdf(activity_key)
                display_name = (display_name[:45] + '...') if len(display_name) > 48 else display_name
                c.drawString(MARGIN + 0.5*cm, y_pos, f"• {display_name}: {emission_val:.2f} kg {CO2_SUB}") # Use subscript
                y_pos -= 0.55 * cm
        else:
            if y_pos < MARGIN + 1*cm: c.showPage(); c.setFont("Helvetica", 9.5); y_pos = height - MARGIN
            c.drawString(MARGIN + 0.5*cm, y_pos, "Top activities data unavailable.")
            y_pos -= 0.55*cm

        # --- Draw Top Activities Graph (fig2) ---
        y_pos -= 0.4 * cm # Space before graph
        if fig2_img_data:
            try:
                graph2_img = ImageReader(fig2_img_data)
                img_w, img_h = graph2_img.getSize()
                aspect = img_h / float(img_w) if img_w > 0 else 1
                draw_width = width - (2 * MARGIN)
                draw_height = draw_width * aspect
                max_graph_height = 7.5*cm # Limit height
                if draw_height > max_graph_height:
                    draw_height = max_graph_height
                    draw_width = draw_height / aspect if aspect > 0 else draw_width

                if y_pos - draw_height < MARGIN: # Check space
                    c.showPage(); c.setFont("Helvetica", 9.5); y_pos = height - MARGIN
                    y_pos -= 0.3*cm # Space at top

                c.drawImage(graph2_img, MARGIN, y_pos - draw_height,
                            width=draw_width, height=draw_height, preserveAspectRatio=True, mask='auto')
                # No need to decrease y_pos further after the last element
            except Exception as graph2_err:
                print(f"Error drawing top activities graph: {graph2_err}")
                if y_pos < MARGIN + 1*cm: c.showPage(); c.setFont("Helvetica", 9.5); y_pos = height - MARGIN
                c.drawString(MARGIN, y_pos, "[Top Activities graph could not be rendered]")

        # --- Finalize PDF ---
        c.save()
        buffer.seek(0)
        return buffer

    except Exception as pdf_err:
        print(f"Critical error during PDF generation: {pdf_err}")
        print(traceback.format_exc())
        buffer = BytesIO() # Return empty buffer on failure
        buffer.seek(0)
        return buffer

# --- App Config ---
st.set_page_config(page_title="GreenPrint", page_icon="🌿", layout="centered")

# --- Sidebar Logo ---
st.markdown("""
    <style>
        [data-testid="stSidebar"]::before {
            content: ""; display: block;
            background-image: url('https://raw.githubusercontent.com/keanyaoha/Calculator_test/main/GreenPrint_logo.png');
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
@st.cache_data(ttl=3600)
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
            "Travel": ["Domestic_flight", "International_flight", "Diesel_train_local", "Diesel_train_long", "Electric_train",  "Bus", "Petrol_car", "Ev_car", "Ev_scooter", "Motorcycle", "Diesel_car"],
            "Food": ["Beef", "Poultry", "Pork", "Dairy", "Fish_products", "Rice", "Sugar", "Oils_fats", "Other_food", "Beverages", "Other_meat"],
            "Energy & Water": ["Electricity", "Water"],
            "Other": ["Hotel_stay"]
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

        # Use CO2_SUB constant for column name
        category_df = pd.DataFrame(list(category_totals.items()), columns=["Category", f"Emissions (kg {CO2_SUB})"])

        # --- Category Chart ---
        st.subheader("🔍 Emission by Category")
        fig1 = px.bar(category_df.sort_values(f"Emissions (kg {CO2_SUB})", ascending=True),
                      x=f"Emissions (kg {CO2_SUB})", y="Category",
                      orientation='h', color=f"Emissions (kg {CO2_SUB})",
                      color_continuous_scale="Greens",
                      text=f"Emissions (kg {CO2_SUB})")
        fig1.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig1.update_layout(yaxis_title=None, xaxis_title=f"Emissions (kg {CO2_SUB})") # Use constant
        st.plotly_chart(fig1, use_container_width=True)

        # --- Top Emitting Activities ---
        activity_df = pd.DataFrame(list(emissions_filtered.items()), columns=["Activity Key", "Emissions"])

        # --- Format Activity Names for Display ---
        def format_activity_name(activity_key): # Keep consistent formatting function
             mapping = {
                 "Domestic_flight": "Domestic Flights", "International_flight": "International Flights",
                  "Diesel_train_local": "Diesel Local Train", "Diesel_train_long": "Diesel Long-Dist Train",
                  "Electric_train": "Electric Train", "Bus": "Bus",
                  "Petrol_car": "Petrol Car", "Motorcycle": "Motorcycle",
                  "Ev_scooter": "E-Scooter", "Ev_car": "Electric Car",
                  "Diesel_car": "Diesel Car", "Beef": "Beef Products",
                  "Poultry": "Poultry Products", "Beverages": "Beverages", "Pork": "Pork Products",
                  "Fish_products": "Fish Products", "Other_meat": "Other Meat Products",
                  "Rice": "Rice", "Sugar": "Sugar",
                  "Oils_fats": "Veg Oils/Fats", "Dairy": "Dairy Products",
                  "Other_food": "Other Food", "Water": "Water",
                  "Electricity": "Electricity", "Hotel_stay": "Hotel Stay",
             }
             return mapping.get(activity_key, activity_key.replace("_", " ").capitalize())

        activity_df["Activity Name"] = activity_df["Activity Key"].apply(format_activity_name)
        # -----------------------------------------

        top_n = min(10, len(activity_df))
        top_n_df = activity_df.sort_values("Emissions", ascending=False).head(top_n)

        if not top_n_df.empty:
             st.subheader(f"🏆 Top {top_n} Emitting Activities")
             fig2 = px.bar(top_n_df.sort_values("Emissions", ascending=True),
                           x="Emissions", y="Activity Name",
                           orientation='h', color="Emissions",
                           color_continuous_scale="Blues",
                           text="Emissions")
             fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
             fig2.update_layout(yaxis_title=None, xaxis_title=f"Emissions (kg {CO2_SUB})") # Use constant
             st.plotly_chart(fig2, use_container_width=True)

             # --- Prepare data for PDF ---
             fig1_img_data = None
             fig2_img_data = None
             logo_data = None
             pdf_ready = False

             try:
                 # Generate images first
                 fig1_img_data = BytesIO(fig1.to_image(format="png", scale=2))
                 fig2_img_data = BytesIO(fig2.to_image(format="png", scale=2))

                 # Get logo data
                 logo_url = 'https://raw.githubusercontent.com/keanyaoha/Calculator_test/main/GreenPrint_logo.png'
                 logo_data = get_logo_data(logo_url)

                 # Prepare top activities data dict
                 pdf_top_activities_data = dict(zip(top_n_df["Activity Key"], top_n_df["Emissions"]))

                 # Check if all components are ready
                 if logo_data and fig1_img_data and fig2_img_data and category_totals and pdf_top_activities_data:
                      pdf_ready = True

             except ImportError:
                 st.error("Plotly image export failed. Please ensure 'kaleido' is installed (`pip install kaleido`). PDF generation requires it.")
             except Exception as prep_err:
                  st.error(f"Could not prepare data for PDF report: {prep_err}")
                  st.error(traceback.format_exc()) # Log detailed error

             # --- PDF Download Button ---
             st.subheader("📄 Download Your Report")
             if pdf_ready:
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
                 st.warning("Could not generate PDF: Missing logo, graph images, or essential data.")
                 # More specific feedback
                 if not logo_data: st.caption(" - Logo failed to load.")
                 if not fig1_img_data: st.caption(" - Category graph failed to render.")
                 if not fig2_img_data: st.caption(" - Top Activities graph failed to render.")

        else:
            st.info("No activities with emissions found to display top emitters.")
