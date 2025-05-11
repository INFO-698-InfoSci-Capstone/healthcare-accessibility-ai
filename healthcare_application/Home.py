import streamlit as st

# 1️⃣ Page configuration
st.set_page_config(
    page_title="Healthcare Accessibility Dashboard",
    layout="wide",
    page_icon="🏥",
)

def show_home():
    # Header
    st.markdown(
        """
        <div style="display:flex; align-items:center; margin-bottom:1rem;">
          <img src="https://img.icons8.com/fluency/48/000000/hospital-2.png" style="margin-right:10px;"/>
          <h1 style="font-size:2.5rem; margin:0;">Healthcare Accessibility Dashboard</h1>
        </div>
        <p style='font-size:1.1rem; color:#555; margin-top:0;'>
          AI-driven insights into healthcare access gaps, risks, and outcomes across U.S. census tracts.
        </p>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Features
    st.markdown("## 🔑 Key Features")
    cols = st.columns(3)
    features = [
        ("🗺️ Interactive Maps", "Explore provider density and health metrics on dynamic geospatial maps."),
        ("🧠 Natural Language Q&A", "Ask questions to our AI assistant powered by LangChain + RAG."),
        ("📊 Comparative Analytics", "Rank tracts and compare socioeconomic & clinical indicators."),
    ]
    for col, (title, desc) in zip(cols, features):
        col.markdown(f"**{title}**")
        col.markdown(desc)
    st.markdown("---")

    # Data Sources (static, two-column layout)
    st.markdown("## 📚 Data Sources & Integration")
    left, right = st.columns(2)
    with left:
        st.markdown("**American Community Survey (ACS)**")  
        st.markdown("- Socioeconomic indicators: income, education, employment")
        st.markdown("**CDC Health Burden Estimates**")  
        st.markdown("- Disease prevalence and clinical outcome measures")
    with right:
        st.markdown("**OpenStreetMap Facilities**")  
        st.markdown("- Geocoded locations of hospitals, clinics, pharmacies")
        st.markdown("**GMO Hospital Beds**")  
        st.markdown("- Regional bed availability from Geospatial Management Office")
    st.markdown(
        """
        All datasets are joined via the common **GEOID** for seamless tract-level analysis.
        """
    )
    st.markdown("---")

    # Footer
    st.caption("Built with ❤️ using Streamlit · GeoPandas · FAISS · HuggingFace · LangChain · OpenAI APIs.")

# 3️⃣ Execute your home page
show_home()
