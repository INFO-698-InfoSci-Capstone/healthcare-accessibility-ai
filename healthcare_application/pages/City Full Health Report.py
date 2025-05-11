# -----------------------------------------------------------------------------
# City Health Dashboard & Report – Streamlit Page (Comprehensive)
# This single page integrates all city-level statistics, multiple visualisations,
# and an AI‑generated narrative + policy section.
# -----------------------------------------------------------------------------
import os
import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI

# ──────────────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────────────
st.set_page_config(page_title="City Health Dashboard & Report", layout="wide")

def reset_report():
    # Drop only if they exist – avoids KeyError
    st.session_state.pop("narrative", None)
    st.session_state.pop("policy", None)

# ──────────────────────────────────────────────────────
# Data Loading
# ──────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_data() -> gpd.GeoDataFrame:
    gdf = gpd.read_file("data/gdf.geojson")
    gdf["simple_geometry"] = gdf.geometry.simplify(tolerance=0.001, preserve_topology=True)
    return gdf

gdf = load_data()
cities = sorted(gdf["PlaceName"].dropna().unique().tolist(), key=lambda x: x.lower())

# ──────────────────────────────────────────────────────
# OpenAI Setup
# ──────────────────────────────────────────────────────
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ──────────────────────────────────────────────────────
# Sidebar – City Selection
# ──────────────────────────────────────────────────────
st.sidebar.title("🏙️ City Selector")
selected_city = st.sidebar.selectbox("Select a City", cities,          # Give the widget a stable key
    on_change=reset_report   )

city_data = gdf[gdf["PlaceName"] == selected_city]
if city_data.empty:
    st.warning("No data available for this city.")
    st.stop()

# ──────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────

def compute_summary_stats(df: pd.DataFrame) -> dict:
    """Compute a comprehensive dictionary of statistics for the city."""
    return {
        # Demographics
        "Population": int(df["Total_Population"].sum()),
        "Median Income": int(df["Median_Household_Income"].median()),
        "Uninsured Rate": df["Uninsured_Rate"].mean(),
        # Facility counts
        "Hospitals": int(df["properties.hospital"].sum()),
        "Clinics": int(df["properties.clinic"].sum()),
        "Doctors": int(df["properties.doctors"].sum()),
        "Pharmacies": int(df["properties.pharmacy"].sum()),
        "Dentists": int(df["properties.dentist"].sum()),
        "Nursing Homes": int(df["properties.nursing_home"].sum()),
        "Social Facilities": int(df["properties.social_facility"].sum()),
        # Preventive care
        "Check‑up %": df["CHECKUP_CrudePrev"].mean(),
        "Cholesterol %": df["CHOLSCREEN_CrudePrev"].mean(),
        "ColonScreen %": df["COLON_SCREEN_CrudePrev"].mean(),
        "PapTest %": df["PAPTEST_CrudePrev"].mean(),
        # Chronic conditions
        "Arthritis %": df["ARTHRITIS_CrudePrev"].mean(),
        "Asthma %": df["CASTHMA_CrudePrev"].mean(),
        "CHD %": df["CHD_CrudePrev"].mean(),
        "Cancer %": df["CANCER_CrudePrev"].mean(),
        "Binge %": df["BINGE_CrudePrev"].mean(),
        # Barriers
        "LEP %": df["Limited_English_Proficiency_Rate"].mean(),
        "No Vehicle %": df["No_Vehicle_Rate"].mean(),
        "No Internet %": df["No_Internet_Rate"].mean(),
        "Rent Burden %": df["Rent_as_Income_Percentage"].mean(),
        # HPSA
        "Avg HPSA Score": round(df["HPSA Score"].dropna().mean(), 1) if not df["HPSA Score"].dropna().empty else "N/A",
    }

summary = compute_summary_stats(city_data)

# Insight generators

def generate_narrative(city: str, stats: dict) -> str:
    """Generate a narrative string using OpenAI."""
    bullet_stats = "\n".join([f"• {k}: {v:.1f}%" if isinstance(v, float) else f"• {k}: {v}" for k, v in stats.items()])
    prompt = f"""
    You are a public‑health analyst. Draft a detailed narrative analysing healthcare access, outcomes, and social barriers in {city} for policymakers. Use the following statistics:\n{bullet_stats}\nConclude with key risks and 3 strategic interventions.
    """
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=700,
    )
    return resp.choices[0].message.content.strip()


def recommend_policy(city: str) -> str:
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Propose three concise evidence‑based policy actions for {city}."}],
        temperature=0.5,
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()

# ──────────────────────────────────────────────────────
# Layout Tabs
# ──────────────────────────────────────────────────────
TABS = [
    "Overview", "Access", "Outcomes", "Preventive", "Barriers", "Equity", "Report",
]

t0, t1, t2, t3, t4, t5, t6 = st.tabs(TABS)

# ------------- Tab 0: Overview -------------
with t0:
    st.title(f"City Health Profile – {selected_city}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Population", f"{summary['Population']:,}")
    c1.metric("Median Income", f"${summary['Median Income']:,}")
    c1.metric("Uninsured", f"{summary['Uninsured Rate']:.1f}%")
    c2.metric("Hospitals", summary['Hospitals'])
    c2.metric("Clinics", summary['Clinics'])
    c2.metric("Doctors", summary['Doctors'])
    c3.metric("Check‑up", f"{summary['Check‑up %']:.1f}%")
    c3.metric("CHD", f"{summary['CHD %']:.1f}%")
    c3.metric("HPSA", summary['Avg HPSA Score'])

# ------------- Tab 1: Access -------------
with t1:
    st.subheader("Facility Distribution")
    facility_cols = [
        "Hospitals", "Clinics", "Doctors", "Pharmacies", "Dentists", "Nursing Homes", "Social Facilities",
    ]
    counts = [summary[k] for k in facility_cols]
    fig_access = px.bar(x=facility_cols, y=counts, labels={"x": "Facility", "y": "Count"})
    st.plotly_chart(fig_access, use_container_width=True)

# ------------- Tab 2: Outcomes -------------
with t2:
    st.subheader("Chronic Disease Prevalence")
    chronic_keys = [k for k in summary if k.endswith("%") and k.split()[0] in [
        "Arthritis", "Asthma", "CHD", "Cancer", "Binge"]]
    values = [summary[k] for k in chronic_keys]
    fig_outcomes = px.bar(x=chronic_keys, y=values, labels={"x": "Condition", "y": "Prevalence %"})
    st.plotly_chart(fig_outcomes, use_container_width=True)

# ------------- Tab 3: Preventive -------------
with t3:
    st.subheader("Preventive Care Coverage")
    prev_keys = [k for k in summary if k.endswith("%") and k.split()[0] in [
        "Check‑up", "Cholesterol", "ColonScreen", "PapTest"]]
    prev_vals = [summary[k] for k in prev_keys]
    fig_prev = go.Figure(go.Scatterpolar(r=prev_vals, theta=prev_keys, fill="toself"))
    fig_prev.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
    st.plotly_chart(fig_prev, use_container_width=True)

# ------------- Tab 4: Barriers -------------
with t4:
    st.subheader("Social & Economic Barriers")
    barrier_keys = ["LEP %", "No Vehicle %", "No Internet %", "Rent Burden %"]
    barrier_vals = [summary[k] for k in barrier_keys]
    fig_barriers = px.bar(x=barrier_keys, y=barrier_vals, labels={"x": "Barrier", "y": "%"})
    st.plotly_chart(fig_barriers, use_container_width=True)

# ------------- Tab 5: Equity -------------
with t5:
    st.subheader("Equity & Resource Gaps")
    indicator = st.selectbox("Select Indicator", [
        "Uninsured_Rate", "CHECKUP_CrudePrev", "CHD_CrudePrev", "Median_Household_Income",
    ])
    top = city_data.nlargest(5, indicator)[["GEOID", indicator]]
    bottom = city_data.nsmallest(5, indicator)[["GEOID", indicator]]
    st.markdown("##### Top 5 Tracts")
    st.dataframe(top, use_container_width=True)
    st.markdown("##### Bottom 5 Tracts")
    st.dataframe(bottom, use_container_width=True)

# ------------- Tab 6: Report -------------
with t6:
    st.header("📝 Comprehensive Narrative & Policy")
    if st.button("Generate Full Report"):
        with st.spinner("Generating …"):
            narrative_text = generate_narrative(selected_city, summary)
            policy_text = recommend_policy(selected_city)
            st.session_state["narrative"] = narrative_text
            st.session_state["policy"] = policy_text

    if "narrative" in st.session_state:
        st.subheader("Narrative Analysis")
        st.markdown(st.session_state["narrative"])

        st.subheader("Policy Recommendations")
        st.markdown(st.session_state["policy"])

        st.markdown("---")
        st.subheader("Visual Summary")
        colA, colB = st.columns(2)

        # ─────── Left column ───────
        with colA:
            # Risk Map – Uninsured-Rate choropleth
            risk_map = px.choropleth_mapbox(
                city_data,
                geojson=city_data.set_geometry("simple_geometry").geometry,
                locations=city_data.index,
                color="Uninsured_Rate",
                color_continuous_scale="YlOrRd",
                zoom=9,
                center={
                    "lon": city_data.geometry.centroid.x.mean(),
                    "lat": city_data.geometry.centroid.y.mean(),
                },
                mapbox_style="carto-positron",
                hover_data=["GEOID", "Uninsured_Rate"],
            )
            risk_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)

            st.plotly_chart(risk_map, use_container_width=True, key="risk_map_uninsured")
            st.plotly_chart(fig_prev, use_container_width=True,  key="previous_trend")

        # ─────── Right column ───────
        with colB:
            st.plotly_chart(fig_outcomes, use_container_width=True, key="outcomes_chart")
            st.plotly_chart(fig_barriers, use_container_width=True, key="barriers_chart")

        st.markdown("---")
        st.subheader("Statistics Table")
        stats_df = pd.DataFrame(list(summary.items()), columns=["Metric", "Value"])
        st.dataframe(stats_df, use_container_width=True, key="stats_table")

        csv_bytes = city_data.drop(columns="geometry").to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Tract Data",
            csv_bytes,
            file_name=f"{selected_city.replace(' ', '_')}_tracts.csv",
            mime="text/csv",
        )
    else:
        st.info("Click **Generate Full Report** to see narrative, policy, and full visuals.")

# End of file
