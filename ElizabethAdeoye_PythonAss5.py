#IMPORT DEPENDENCIES
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Poverty & Millionaire Analytics", layout="wide")


st.sidebar.title("Controls")
uploaded = st.sidebar.file_uploader("Upload Poverty/Millionaire Excel file (.xlsx)", type=["xlsx"])

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    # Align to expected internal names (note: dataset column 'State Popiulation' typo is handled)
    df = df.rename(columns={
        "State": "state",
        "Number in Poverty": "poverty",
        "Number of Millionaires": "millionaires",
        "State Popiulation": "population"
    })
    # Ensure numeric
    for c in ["poverty", "millionaires", "population"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # Basic validation
    df = df.dropna(subset=["state", "poverty", "millionaires", "population"])
    return df

if not uploaded:
    st.warning("Please upload the provided povertymillionaires.xlsx file to proceed.")
    st.stop()

df = load_data(uploaded)

# -----------------------------------
# Global header
# -----------------------------------
st.title("Poverty & Millionaire Analytics Dashboard")
st.caption("Interactive insights using Streamlit, Pandas, Matplotlib, and Plotly.")

# -----------------------------------
# Sidebar filters
# -----------------------------------
all_states = df["state"].tolist()
default_states = sorted(all_states)[:5] if len(all_states) >= 5 else all_states
selected_states = st.sidebar.multiselect(
    "Select at least 5 states",
    options=sorted(all_states),
    default=default_states
)

# -----------------------------------
# Tabs
# -----------------------------------
tab1, tab2, tab3 = st.tabs(["Poverty vs Millionaires", "Millionaire Density Map", "Poverty Rate"])

# -----------------------------------
# Q1: Poverty vs Millionaires (Matplotlib)
# -----------------------------------
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
        plt.ylabel("People (count)")
        plt.xlabel("State")
        plt.title("Poverty vs Millionaires (Selected States)")
        plt.legend()
        plt.grid(axis="y", alpha=0.3)

        # Render the current figure
        st.pyplot(plt.gcf())



# -----------------------------------
# Q2: Millionaire Density Map (Plotly choropleth)
# -----------------------------------
with tab2:
    st.subheader("Millionaire Density by U.S. State")
    df["millionaire_density"] = df["millionaires"] / df["population"]

    # The dataset uses state abbreviations (AK, AL, …), which match locationmode="USA-states"
    fig_map = px.choropleth(
        df,
        locations="state",
        locationmode="USA-states",
        color="millionaire_density",
        hover_name="state",
        hover_data={
            "population": True,
            "millionaires": True,
            "poverty": True,
            "millionaire_density": ":.6f"
        },
        scope="usa",
        color_continuous_scale="Viridis",
        labels={"millionaire_density": "Millionaires per capita"},
        title="Millionaire Density by State"
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown(
        "> Interpretation: Higher millionaire density tends to concentrate in coastal and metro-centric states with strong finance, "
        "technology, and services sectors. Interior states often show lower density overall but may include pockets of high net worth "
        "near energy, logistics, or manufacturing hubs. Tax policy, industry mix, and cost of living influence where wealth clusters. "
        "These patterns reveal how regional economic ecosystems and migration shape the geography of wealth."
    )

# -----------------------------------
# Q3: Poverty Rate (Matplotlib horizontal bar)
# -----------------------------------
with tab3:
    st.subheader("Poverty Rate Across States")
    # Calculate poverty rate
    df["poverty_rate"] = df["poverty"] / df["population"]
    plot_df = df[["state", "poverty_rate"]].dropna().sort_values("poverty_rate", ascending=False)

    # Create the figure directly with pyplot
    plt.figure(figsize=(10, max(8, len(plot_df) * 0.25)))
    plt.barh(plot_df["state"], plot_df["poverty_rate"] * 100, color="blue")

    plt.xlabel("Poverty rate (%)")
    plt.ylabel("State")
    plt.title("Poverty Rate by State (Highest to Lowest)")
    plt.grid(axis="x", alpha=0.3)

    # Render the current figure
    st.pyplot(plt.gcf())




# -----------------------------------
# Footer
# -----------------------------------
st.divider()
st.markdown("**Note:** Visuals update automatically based on your uploaded dataset and state selections.")
