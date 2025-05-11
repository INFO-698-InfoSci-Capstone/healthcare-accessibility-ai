import os
import streamlit as st
import geopandas as gpd
import plotly.express as px
from utils.data_loader import get_data

# ──────────────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────────────
st.set_page_config(page_title="Unified Healthcare Accessibility Dashboard", layout="wide")

# ──────────────────────────────────────────────────────
# Load Data
# ──────────────────────────────────────────────────────
gdf = get_data()
cities = sorted(gdf['PlaceName'].dropna().unique(), key=lambda x: x.lower())

# ──────────────────────────────────────────────────────
# Sidebar Controls
# ──────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔎 Explore Options")

    selected_city = st.selectbox("Select City", ["All Cities"] + cities)

    selected_view = st.selectbox(
        "Select View",
        ["Facilities", "Health Outcomes", "HPSA Scores", "Social Barriers"]
    )

    reverse_color = st.checkbox("Reverse Color Scale", value=False)

    st.markdown("---")

# ──────────────────────────────────────────────────────
# Dynamic Metric Selection Based on View
# ──────────────────────────────────────────────────────
def select_facility_view():
    facility_cols = {
        'Hospitals': 'properties.hospital',
        'Clinics': 'properties.clinic',
        'Pharmacies': 'properties.pharmacy',
        'Dentist': 'properties.dentist',
        'Doctors': 'properties.doctors',
        'Nursing Home': 'properties.nursing_home',
        'Social Facility': 'properties.social_facility'
    }
    with st.sidebar:
        selected = st.selectbox("Facility Type", list(facility_cols.keys()))
        normalize = st.radio("Normalize By", ["None", "Population", "Area"], index=0)

    col = facility_cols[selected]

    if normalize == "Population":
        filtered_gdf["value"] = filtered_gdf[col] / filtered_gdf["Total_Population"] * 1000
        label = f"{selected} per 1,000 people"
    elif normalize == "Area":
        filtered_gdf["value"] = filtered_gdf[col] / (filtered_gdf["area_sq_meters"] / 1e6)
        label = f"{selected} per sq km"
    else:
        filtered_gdf["value"] = filtered_gdf[col]
        label = selected
    return label

def select_health_outcome_view():
    health_cols = {
        "Uninsured Rate": "Uninsured_Rate",
        "Annual Checkup Rate": "CHECKUP_CrudePrev",
        "Cholesterol Screening": "CHOLSCREEN_CrudePrev",
        "Colon Cancer Screening": "COLON_SCREEN_CrudePrev",
        "Pap Smear Screening": "PAPTEST_CrudePrev",
        "Binge Drinking": "BINGE_CrudePrev",
        "Cancer Prevalence": "CANCER_CrudePrev"
    }
    with st.sidebar:
        selected = st.selectbox("Health Outcome", list(health_cols.keys()))
    filtered_gdf["value"] = filtered_gdf[health_cols[selected]]
    return selected

def select_hpsa_score_view():
    with st.sidebar:
        hpsa_only = st.checkbox("Show Only Designated HPSA Tracts")
    temp_gdf = filtered_gdf
    if hpsa_only:
        temp_gdf = temp_gdf[temp_gdf["HPSA Status Code"].notna()]
    temp_gdf = temp_gdf.dropna(subset=["HPSA Score"])
    temp_gdf["value"] = temp_gdf["HPSA Score"]
    return "HPSA Score", temp_gdf

def select_social_barrier_view():
    barrier_cols = {
        "Median Household Income": "Median_Household_Income",
        "No Vehicle Access (%)": "No_Vehicle_Rate",
        "No Internet Access (%)": "No_Internet_Rate",
        "Limited English Proficiency (%)": "Limited_English_Proficiency_Rate",
        "Rent as % of Income": "Rent_as_Income_Percentage"
    }
    with st.sidebar:
        selected = st.selectbox("Social Barrier", list(barrier_cols.keys()))
    filtered_gdf["value"] = filtered_gdf[barrier_cols[selected]]
    return selected

# ──────────────────────────────────────────────────────
# Main Page Title
# ──────────────────────────────────────────────────────
st.title("🏥 Unified Healthcare Accessibility Dashboard")
st.markdown(
    "Visualize healthcare resource availability, health risks, and social barriers at the census-tract level."
)

# ──────────────────────────────────────────────────────
# Filter by City
# ──────────────────────────────────────────────────────
filtered_gdf = gdf if selected_city == "All Cities" else gdf[gdf["PlaceName"] == selected_city]

# View Control
if selected_view == "Facilities":
    label = select_facility_view()
elif selected_view == "Health Outcomes":
    label = select_health_outcome_view()
elif selected_view == "HPSA Scores":
    label, filtered_gdf = select_hpsa_score_view()
elif selected_view == "Social Barriers":
    label = select_social_barrier_view()

# ──────────────────────────────────────────────────────
# Handle Missing Values
# ──────────────────────────────────────────────────────
filtered_gdf = filtered_gdf.dropna(subset=["value"])

if filtered_gdf.empty:
    st.warning("No data available for this selection.")
    st.stop()

# ──────────────────────────────────────────────────────
# Summary Statistics
# ──────────────────────────────────────────────────────
st.subheader(f"{label} in {selected_city}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Average", f"{filtered_gdf['value'].mean():.2f}")
col2.metric("Median", f"{filtered_gdf['value'].median():.2f}")
col3.metric("Min", f"{filtered_gdf['value'].min():.2f}")
col4.metric("Max", f"{filtered_gdf['value'].max():.2f}")

# ──────────────────────────────────────────────────────
# Helper: Map Center & Zoom
# ──────────────────────────────────────────────────────
def get_center_zoom(geometry):
    bounds = geometry.total_bounds
    center = {"lon": (bounds[0] + bounds[2]) / 2, "lat": (bounds[1] + bounds[3]) / 2}
    lon_diff = bounds[2] - bounds[0]
    zoom = 6 if lon_diff > 5 else 8 if lon_diff > 2 else 10
    return center, zoom

center, zoom = get_center_zoom(filtered_gdf.geometry)

# ──────────────────────────────────────────────────────
# Choropleth Map
# ──────────────────────────────────────────────────────
color_scale = "RdYlGn_r" if reverse_color else "YlOrRd"

fig = px.choropleth_mapbox(
    filtered_gdf,
    geojson=filtered_gdf.set_geometry("simple_geometry").geometry,
    locations=filtered_gdf.index,
    color="value",
    color_continuous_scale=color_scale,
    custom_data=["Geography", "value"],
    center=center,
    zoom=zoom,
    mapbox_style="carto-positron",
    labels={"value": label},
    title=f"{label} by Census Tract"
)

fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=750, uirevision="static")
fig.update_traces(
    marker_line_width=1,
    hovertemplate=f"<b>%{{customdata[0]}}</b><br>{label}: %{{customdata[1]:.2f}}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)
