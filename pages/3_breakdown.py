import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

# --- App Config ---
st.set_page_config(
    page_title="GreenPrint",
    page_icon="🌿",
    layout="centered"
)

# --- Force Logo to Appear at Top of Sidebar ---
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
            margin: 1.5rem auto -4rem auto;  /* SUPER tight top & bottom spacing */
        }

        section[data-testid="stSidebar"] {
            background-color: #d6f5ec;
        }

        .stApp {
            background-color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Emission Breakdown")
st.write("Here is how your estimated carbon footprint breaks down by activity.")

# --- Ensure emissions data is available ---
if "emission_values" not in st.session_state or not st.session_state.emission_values:
    st.warning("No emission data found. Please fill in your activity data on the main page first.")
else:
    # Retrieve and clean up data
    emissions_dict = st.session_state.emission_values
    emissions_filtered = {k: v for k, v in emissions_dict.items() if v > 0}

    if emissions_filtered:
        # --- Categorization logic ---
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

        # --- Compute category totals ---
        category_totals = {}
        for cat, acts in categories.items():
            category_totals[cat] = sum(emissions_filtered.get(act, 0) for act in acts)

        category_df = pd.DataFrame({
            "Category": list(category_totals.keys()),
            "Emissions (t CO₂)": list(category_totals.values())
        })

        # --- Category Overview Chart ---
        st.subheader("🔍 Emission by Category")
        cat_fig = px.bar(category_df.sort_values("Emissions (t CO₂)", ascending=True),
                         x="Emissions (t CO₂)", y="Category",
                         orientation='h',
                         color="Emissions (t CO₂)",
                         color_continuous_scale="Greens")
        st.plotly_chart(cat_fig, use_container_width=True)

        # --- Top 10 Emitting Activities ---
        st.subheader("🏆 Top 10 Emitting Activities")
        activity_df = pd.DataFrame(list(emissions_filtered.items()), columns=["Activity", "Emissions"])
        top10_df = activity_df.sort_values("Emissions", ascending=False).head(10)

        top10_fig = px.bar(top10_df.sort_values("Emissions", ascending=True),
                           x="Emissions", y="Activity",
                           orientation='h',
                           color="Emissions",
                           color_continuous_scale="Blues")
        st.plotly_chart(top10_fig, use_container_width=True)

        # --- Detailed View Per Category ---
        for cat, acts in categories.items():
            cat_activities = {a: emissions_filtered[a] for a in acts if a in emissions_filtered}
            if cat_activities:
                st.markdown(f"### 📦 Detailed Breakdown: {cat}")
                detail_df = pd.DataFrame(list(cat_activities.items()), columns=["Activity", "Emissions"])
                detail_fig = px.bar(detail_df.sort_values("Emissions", ascending=True),
                                    x="Emissions", y="Activity",
                                    orientation='h',
                                    color="Emissions",
                                    color_continuous_scale="Purples")
                st.plotly_chart(detail_fig, use_container_width=True)
    else:
        st.info("Your inputs resulted in zero emissions. Try entering some activity data.")
