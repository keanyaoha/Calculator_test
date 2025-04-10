# --- (Keep all the code above this section as is) ---

    # --- Display Results Area (Below Tabs, only if calculation is done) ---
    if st.session_state.get('calculation_done', False):
        st.divider()
        st.subheader(f"📊 Your Estimated Monthly Carbon Footprint:")

        total_emission = st.session_state.calculated_emission
        if total_emission is not None: # Check if emission value exists
            st.metric(label="kg CO₂ equivalent", value=f"{total_emission:.1f}")

            trees_monthly_equiv = total_emission / (21.77 / 12)
            st.markdown(f"This is roughly equivalent to the amount of CO₂ absorbed by **{trees_monthly_equiv:.1f} mature trees** in a month.")

            st.divider()
            st.subheader("📈 Comparison with Averages")

            # Retrieve comparison data from session state
            comparison_data = st.session_state.comparison_plot_data
            plot_data_list = [] # List to store data for DataFrame
            captions = [] # To collect notes about missing data

            # Add "You" data first
            plot_data_list.append({"Source": "You", "Emissions": total_emission, "ColorGroup": "You"}) # Add a group for potential discrete color later

            if comparison_data:
                # Add country data if available
                c_data = comparison_data["country"]
                if c_data["avg"] is not None:
                    plot_data_list.append({"Source": c_data["name"], "Emissions": c_data["avg"], "ColorGroup": "Average"})
                else:
                    captions.append(f"Note: Monthly average data for {c_data['name']} not available.")

                # Add EU data if available
                eu_data = comparison_data["eu"]
                if eu_data["avg"] is not None:
                    plot_data_list.append({"Source": eu_data["name"], "Emissions": eu_data["avg"], "ColorGroup": "Average"})
                else:
                     captions.append("Note: Monthly average data for EU not available.")

                # Add World data if available
                world_data = comparison_data["world"]
                if world_data["avg"] is not None:
                    plot_data_list.append({"Source": world_data["name"], "Emissions": world_data["avg"], "ColorGroup": "Average"})
                else:
                    captions.append("Note: Monthly average data for World not available.")

                # Display collected captions
                for caption in captions:
                    st.caption(caption)

                # Create DataFrame for Plotly
                if len(plot_data_list) > 0: # Check if there's any data to plot
                    df_comparison = pd.DataFrame(plot_data_list)

                    # Plot only if there's data besides potentially just "You"
                    if len(df_comparison) > 0:
                        # *** Create Plotly Express Bar Chart ***
                        fig_comp = px.bar(
                            df_comparison.sort_values("Emissions", ascending=True), # Sort for consistent plotting order
                            x="Emissions",
                            y="Source",
                            orientation='h',
                            color="Emissions",  # Color based on the emission value
                            color_continuous_scale="Greens", # Use Greens scale like breakdown page
                            # Alternative: Use discrete colors
                            # color="ColorGroup",
                            # color_discrete_map={"You": "#4CAF50", "Average": "#4682B4"},
                            text="Emissions", # Add values as text labels
                            title="Monthly Carbon Footprint Comparison",
                            labels={'Emissions': 'kg CO₂ per month', 'Source': ''} # Customize axis labels
                        )

                        # Format text labels on bars
                        fig_comp.update_traces(
                            texttemplate='%{text:.1f}', # Format to one decimal place
                            textposition='outside'      # Position text outside the bar
                        )

                        # Optional: Ensure y-axis doesn't reverse order automatically based on value
                        # fig_comp.update_layout(yaxis={'categoryorder':'array', 'categoryarray': df_comparison.sort_values("Emissions", ascending=True)['Source'].tolist()})

                        st.plotly_chart(fig_comp, use_container_width=True)

                        st.markdown("<div style='text-align: center; color: gray; font-size: small;'>Comparison of your estimated monthly carbon footprint with available national and global averages.</div>", unsafe_allow_html=True)

                    else:
                        # This case might happen if only "You" is plotted and no averages were found
                         st.info("Could not retrieve average data for comparison.")
                else:
                    st.warning("No data available to generate comparison plot.")

            else:
                 st.warning("Comparison data not found in session state.")
        else:
            st.warning("Calculated emission value not found in session state.")


# --- Show prompt if no country is selected ---
elif not st.session_state.selected_country or st.session_state.selected_country == "-- Select --":
    pass # Do nothing, main area is not rendered

# --- Sidebar Content ---
st.sidebar.markdown("---")
# (Keep sidebar styling and other potential sidebar elements)

# --- (End of Script) ---
