import os
import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
from openai import OpenAI

# ───────────────────────────────────────────────────
# Page Config
# ───────────────────────────────────────────────────
st.set_page_config(page_title="Health Equity & Risk Prioritization", layout="wide")

# ───────────────────────────────────────────────────
# Load Data
# ───────────────────────────────────────────────────
if "gdf" not in st.session_state:
    with st.spinner("Loading data..."):
        gdf = gpd.read_file("data/gdf.geojson")
        gdf['simple_geometry'] = gdf.geometry.simplify(tolerance=0.001, preserve_topology=True)
        st.session_state["gdf"] = gdf
else:
    gdf = st.session_state["gdf"]

cities = sorted(gdf["PlaceName"].dropna().unique(), key=lambda x: x.lower())

# Calculate Composite Risk Score
risk_factors = ["Uninsured_Rate", "No_Internet_Rate", "Limited_English_Proficiency_Rate"]
gdf["Risk_Score"] = gdf[risk_factors].mean(axis=1)

# ───────────────────────────────────────────────────
# Sidebar Controls
# ───────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 Equity Explorer Settings")

    selected_metric_label = st.selectbox("Select Metric", [
        "Uninsured Rate", "Annual Checkup Rate", "Doctors Available",
        "Clinics Available", "Median Household Income", "No Internet Access Rate",
        "Limited English Proficiency Rate", "Risk Score"
    ])
    rank_type = st.radio("View", ["Top 10", "Bottom 10"], horizontal=True)
    selected_city = st.selectbox("Filter by City", ["All Cities"] + cities)
    priority_only = st.checkbox("Show Priority Zones Only", value=False)

    st.markdown("---")

ranking_columns = {
    "Uninsured Rate": "Uninsured_Rate",
    "Annual Checkup Rate": "CHECKUP_CrudePrev",
    "Doctors Available": "properties.doctors",
    "Clinics Available": "properties.clinic",
    "Median Household Income": "Median_Household_Income",
    "No Internet Access Rate": "No_Internet_Rate",
    "Limited English Proficiency Rate": "Limited_English_Proficiency_Rate",
    "Risk Score": "Risk_Score"
}

# ───────────────────────────────────────────────────
# Main Page Title
# ───────────────────────────────────────────────────
st.title("📈 Health Equity & Risk Prioritization Dashboard")

st.markdown("Analyze healthcare gaps, strengths, and emerging risks to guide intervention planning across cities and census tracts.")

# Filter Data
selected_column = ranking_columns[selected_metric_label]
ascending = True if rank_type == "Bottom 10" else False

filtered_gdf = gdf.copy()
if selected_city != "All Cities":
    filtered_gdf = filtered_gdf[filtered_gdf["PlaceName"] == selected_city]

if priority_only:
    filtered_gdf = filtered_gdf[filtered_gdf["Risk_Score"] > 0.5]

ranking_df = filtered_gdf[["GEOID", "PlaceName", selected_column]].dropna()
ranking_df = ranking_df.sort_values(by=selected_column, ascending=ascending).head(10)
ranking_df["PlaceName"] = ranking_df["PlaceName"].fillna("Unknown")

if ranking_df.empty:
    st.warning("No data available for selection.")
    st.stop()

# Display
st.subheader(f"{rank_type} Tracts by {selected_metric_label} in {selected_city}")

st.dataframe(ranking_df.rename(columns={
    "GEOID": "Census Tract", "PlaceName": "City", selected_column: selected_metric_label
}), hide_index=True, use_container_width=True)

fig = px.bar(
    ranking_df,
    y="PlaceName",
    x=selected_column,
    orientation="h",
    text=selected_column,
    labels={selected_column: selected_metric_label, "PlaceName": "City"},
    title=f"{rank_type} Census Tracts by {selected_metric_label}"
)
fig.update_layout(height=500, margin=dict(l=20, r=20, t=50, b=20), yaxis=dict(autorange="reversed"))
fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")

st.plotly_chart(fig, use_container_width=True)

# ───────────────────────────────────────────────────
# Optional: Policy Summary
# ───────────────────────────────────────────────────
st.markdown("---")

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    prompt = f"Summarize healthcare risks and opportunities based on the {rank_type.lower()} 10 census tracts for {selected_metric_label} in {selected_city}. Suggest a high-level policy intervention."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=150
    )
    policy_summary = response.choices[0].message.content
    st.success(policy_summary)
except Exception as e:
    st.warning(f"Could not generate AI policy summary. ({e})")

# Export
csv = ranking_df.to_csv(index=False).encode('utf-8')
st.download_button("🔹 Download Data", csv, "tract_rankings.csv", "text/csv")
