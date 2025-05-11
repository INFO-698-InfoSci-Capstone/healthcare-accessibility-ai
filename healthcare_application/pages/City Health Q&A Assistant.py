# city_health_app.py  – 2025-04-23
# ---------------------------------------------------------------
#  ─ NEW FEATURES ─
#  1) Pandas tool prompt now tells the LLM to return a markdown
#     table whenever the answer is a DataFrame-like list.
#  2) run_pandas() detects markdown tables and Streamlit renders
#     them nicely.
# ---------------------------------------------------------------

import os, re, streamlit as st, geopandas as gpd, pandas as pd
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_experimental.agents import create_pandas_dataframe_agent

# ────────────────────────────────────────────────────────────────
# Streamlit config
# ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="City-Health Q&A", layout="wide")
st.title("City-Health Q&A Assistant")
st.markdown(
    "Ask *any* question about U.S. census-tract health metrics —\n"
    "aggregations **or** full lists (e.g. “List the census tracts in "
    "Tucson that have no doctors”)."
)

# ────────────────────────────────────────────────────────────────
# 1. GeoDataFrame
# ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_tracts():
    here = os.path.dirname(__file__)
    return gpd.read_file(os.path.join(here, "..", "data", "gdf.geojson"))

gdf = load_tracts()
df  = gdf.drop(columns="geometry")           # plain pandas

# ────────────────────────────────────────────────────────────────
# 2. Vector store for RAG answers
# ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_vectorstore() -> FAISS:
    embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    docs   = []
    for _, r in gdf.iterrows():
        text = (
            f"Census Tract {r.GEOID} in {r.PlaceName}, {r.StateAbbr}: "
            f"population {r.Total_Population}, median income ${r.Median_Household_Income:,}. "
            f"Uninsured {r.Uninsured_Rate} %, HPSA {r['HPSA Score']}."
        )
        meta = r.drop(labels="geometry").to_dict() | {"source": f"Tract {r.GEOID}"}
        docs.append(Document(page_content=text, metadata=meta))
    return FAISS.from_documents(docs, embeds)

vectorstore = load_vectorstore()
retriever   = vectorstore.as_retriever(search_type="similarity", k=5)

# ────────────────────────────────────────────────────────────────
# 3. LLMs
# ────────────────────────────────────────────────────────────────
api_key = st.secrets["OPENAI_API_KEY"]
llm_fast = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, openai_api_key=api_key)
llm_best = ChatOpenAI(model="gpt-4o-mini",       temperature=0, openai_api_key=api_key)

# ────────────────────────────────────────────────────────────────
# 4A. RAG tool
# ────────────────────────────────────────────────────────────────
rag_chain = RetrievalQA.from_chain_type(llm=llm_best, retriever=retriever)
rag_tool = Tool(
    name="RAGAnswerer",
    func=lambda q: rag_chain.run(q),
    description=(
        "Use to answer contextual questions with background from census-tract "
        "summaries (vector search)."
    )
)

# ────────────────────────────────────────────────────────────────
# 4B. Pandas tool  (now table-aware)
# ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_pandas_agent():
    return create_pandas_dataframe_agent(
        llm   = llm_fast,
        df    = df,
        verbose=False,
        allow_dangerous_code=True
    )

pandas_agent = load_pandas_agent()

TABLE_REGEX = re.compile(r"^\s*\|.+\|\s*$", re.MULTILINE)   # crude markdown sniff

def run_pandas(q: str) -> str:
    """
    Forward the question to the pandas agent.
    If the agent prints a DataFrame, ensure it leaves pandas' repr
    (which already looks like a table) or markdown - the Streamlit
    caller will handle formatting.
    """
    try:
        answer = pandas_agent.run(q)
        # Ensure DataFrame outputs become markdown tables
        if isinstance(answer, pd.DataFrame):
            return answer.to_markdown(index=False)
        if TABLE_REGEX.search(str(answer)):
            return str(answer)
        return str(answer)
    except Exception as err:
        return f"💥 Computation failed: {err}"

pandas_tool = Tool(
    name="HealthcareDataAnalyzer",
    func=run_pandas,
    description=(
        "Run pandas code on the full census-tract DataFrame.  "
        "**Uninsured_Rate is already in percent** (0.5 means 0.5%), so do NOT multiply by 100.  "
        "If the user asks for an average uninsured rate, just return the raw mean and append “%.”"
        "number.\n\n"
        "Example list-type prompts:\n"
        "• “List the census tracts in Tucson that have no doctors.”\n"
        "• “Show the top 10 tracts in Phoenix by uninsured rate.”"
    )
)

# ────────────────────────────────────────────────────────────────
# 5. Multi-tool agent
# ────────────────────────────────────────────────────────────────
agent = initialize_agent(
    tools   = [rag_tool, pandas_tool],
    llm     = llm_best,
    agent   = AgentType.OPENAI_FUNCTIONS,
    verbose = True
)

# ────────────────────────────────────────────────────────────────
# 6. Streamlit UI
# ────────────────────────────────────────────────────────────────
query = st.text_input(
    "Ask a healthcare or demographics question:",
    placeholder="e.g. List the census tracts in Tucson that have no doctors"
)

if query:
    with st.spinner("Thinking …"):
        try:
            result = agent.run(query)
            st.subheader("Answer")

            # If it looks like a markdown table, show it as such
            if TABLE_REGEX.search(str(result)):
                st.markdown(result)
            else:
                st.write(result)

        except Exception as e:
            st.error(f"Error: {e}")
