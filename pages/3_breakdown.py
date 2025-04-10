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
    for category, emission in category_data.items():
        c.drawString(2.5 * cm, y, f"{category}: {emission:.2f} kg CO₂")
        y -= 0.7 * cm

    c.setFont("Helvetica-Bold", 12)
    y -= 0.5 * cm
    c.drawString(2 * cm, y, "Top 10 Emitting Activities:")
    c.setFont("Helvetica", 11)
    y -= 1 * cm
    for activity, emission in top_activities_data.items():
        c.drawString(2.5 * cm, y, f"{activity}: {emission:.2f} kg CO₂")
        y -= 0.6 * cm
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm

    c.showPage()
    c.save()
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
if "emission_values" not in st.session_state or not st.session_state.emission_values:
    st.warning("No emission data found. Please fill in your activity data on the main page first.")
else:
    emissions_dict = st.session_state.emission_values
    emissions_filtered = {k: v for k, v in emissions_dict.items() if v > 0}

    if emissions_filtered:
        # --- Define categories ---
        categories = {
            "Travel": [
                "Domestic flight", "International flight", "km_diesel_local_passenger_train_traveled",
                "km_diesel_long_distance_passenger_train_traveled", "km_electric_passenger_train_traveled",
                "km_bus_traveled", "km_petrol_car_traveled", "km_ev_car_traveled", "km_ev_scooter_traveled",
                "km_Motorcycle_traveled", "diesel_car_traveled"
            ],
            "Food": [
                "beef_products_consumed", "poultry_products_consumed", "pork_products_consumed",
                "dairy_products_consumed", "fish_products_consumed", "processed_rice_consumed",
                "sugar_consumed", "vegetable_oils_fats_consumed", "other_food_products_consumed",
                "beverages_consumed", "other_meat_products_consumed"
            ],
            "Energy & Water": ["electricity_used", "water_consumed"],
            "Other": ["hotel_stay"]
        }

        # --- Compute totals ---
        category_totals = {
            cat: sum(emissions_filtered.get(a, 0) for a in acts)
            for cat, acts in categories.items()
        }

        category_df = pd.DataFrame({
            "Category": category_totals.keys(),
            "Emissions (kg CO₂)": category_totals.values()
        })

        # --- Category Chart ---
        st.subheader("🔍 Emission by Category")
        fig1 = px.bar(category_df.sort_values("Emissions (kg CO₂)", ascending=True),
                      x="Emissions (kg CO₂)", y="Category",
                      orientation='h', color="Emissions (kg CO₂)",
                      color_continuous_scale="Greens")
        st.plotly_chart(fig1, use_container_width=True)

        # --- Top 10 Activities ---
        st.subheader("🏆 Top 10 Emitting Activities")
        activity_df = pd.DataFrame(list(emissions_filtered.items()), columns=["Activity", "Emissions"])
        top10_df = activity_df.sort_values("Emissions", ascending=False).head(10)
        fig2 = px.bar(top10_df.sort_values("Emissions", ascending=True),
                      x="Emissions", y="Activity",
                      orientation='h', color="Emissions",
                      color_continuous_scale="Blues")
        st.plotly_chart(fig2, use_container_width=True)

        # --- Detailed by Category ---
        st.subheader("📦 Detailed Breakdown by Category")
        for cat, acts in categories.items():
            cat_acts = {a: emissions_filtered[a] for a in acts if a in emissions_filtered}
            if cat_acts:
                st.markdown(f"**{cat}**")
                df_cat = pd.DataFrame(list(cat_acts.items()), columns=["Activity", "Emissions"])
                fig = px.bar(df_cat.sort_values("Emissions", ascending=True),
                             x="Emissions", y="Activity",
                             orientation='h', color="Emissions",
                             color_continuous_scale="Purples")
                st.plotly_chart(fig, use_container_width=True)

        # --- PDF Download ---
        st.subheader("📄 Download Your Report")
        pdf_data = generate_pdf_report(category_totals, dict(top10_df.values))
        st.download_button("⬇️ Download Report as PDF", data=pdf_data, file_name="carbon_report.pdf")
