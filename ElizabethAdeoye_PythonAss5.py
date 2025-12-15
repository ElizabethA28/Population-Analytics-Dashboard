#import dependencies
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Upload dataset
uploaded = st.sidebar.file_uploader("Upload Poverty/Millionaire Excel file (.xlsx)", type=["xlsx"])

if uploaded:
    df = pd.read_excel(uploaded)
    df = df.rename(columns={
        "State": "state",
        "Number in Poverty": "poverty",
        "Number of Millionaires": "millionaires",
        "State Popiulation": "population"
    })

    # Sidebar: state selection
    all_states = df["state"].tolist()
    default_states = sorted(all_states)[:5]
    selected_states = st.sidebar.multiselect(
        "Select at least 5 states",
        options=sorted(all_states),
        default=default_states
    )

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Poverty vs Millionaires", "Millionaire Density Map", "Poverty Rate"])

    
    # Tab 1: Poverty vs Millionaires
    with tab1:
        st.subheader("Poverty vs Millionaires by Selected States")
        if len(selected_states) < 5:
            st.warning("Please select at least 5 states to render the comparison chart.")
        else:
            sub = df[df["state"].isin(selected_states)].sort_values("state")
            x = range(len(sub))

            plt.figure(figsize=(10, 5))
            plt.bar([i - 0.2 for i in x], sub["poverty"], width=0.4, label="In Poverty", color="red")
            plt.bar([i + 0.2 for i in x], sub["millionaires"], width=0.4, label="Millionaires", color="green")

            plt.xticks(list(x), sub["state"], rotation=45, ha="right")
            plt.ylabel("Population Count")
            plt.xlabel("State")
            plt.title("Poverty vs Millionaires (Selected States)")
            plt.legend()
            plt.grid(axis="y", alpha=0.3)

            st.pyplot(plt.gcf())

        

    
    # Tab 2: Millionaire Density Map
    with tab2:
        st.subheader("Millionaire Density by U.S. State")
        df["millionaire_density"] = df["millionaires"] / df["population"]

        fig_map = px.choropleth(
            df,
            locations="state",
            locationmode="USA-states",
            color="millionaire_density",
            hover_name="state",
            hover_data={"population": True, "millionaires": True, "poverty": True, "millionaire_density": ":.6f"},
            scope="usa",
            color_continuous_scale="Viridis",
            labels={"millionaire_density": "Millionaires per capita"},
            title="Millionaire Density by State"
        )
        st.plotly_chart(fig_map, use_container_width=True)

    
    

    
    # Tab 3: Poverty Rate
    with tab3:
        st.subheader("Poverty Rate Across States")
        df["poverty_rate"] = df["poverty"] / df["population"]
        plot_df = df[["state", "poverty_rate"]].dropna().sort_values("poverty_rate", ascending=False)

        plt.figure(figsize=(10, max(8, len(plot_df) * 0.25)))
        plt.barh(plot_df["state"], plot_df["poverty_rate"] * 100, color="blue")

        plt.xlabel("Poverty rate (%)")
        plt.ylabel("State")
        plt.title("Poverty Rate by State (Highest to Lowest)")
        plt.grid(axis="x", alpha=0.3)

        st.pyplot(plt.gcf())

        
else:
    st.warning("Please upload the dataset to continue.")
