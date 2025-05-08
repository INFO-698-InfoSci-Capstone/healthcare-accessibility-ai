import geopandas as gpd
import streamlit as st

def get_data():
    if "gdf" not in st.session_state:
        with st.spinner("Loading map data..."):
            gdf = gpd.read_file("data/gdf.geojson")
            gdf['simple_geometry'] = gdf.geometry.simplify(tolerance=0.001, preserve_topology=True)
            st.session_state["gdf"] = gdf
    return st.session_state["gdf"]