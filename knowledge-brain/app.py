import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Ensure local source directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ingest.load_txt import load_text_content
from ingest.load_md import load_markdown_content
from ingest.load_pdf import load_pdf_content
from chunk import chunk_document_contents
from retrieve import retrieve_knowledge_chunks
from answer import generate_knowledge_answer, generate_daily_digest

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Personal Knowledge Brain - Second-Brain RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif;
    }
    
    .glass-card {
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .main-title {
        background: linear-gradient(135deg, #10b981 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    .section-header {
        font-weight: 700;
        font-size: 1.3rem;
        color: #f8fafc;
        border-bottom: 2px solid rgba(16, 185, 129, 0.15);
        padding-bottom: 8px;
        margin-bottom: 15px;
    }
    
    .citation-card {
        border-left: 4px solid #10b981;
        background-color: rgba(16, 185, 129, 0.03);
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    
    .mode-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .mode-sim {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .mode-prod {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<h1 class="main-title">🧠 Personal Knowledge Brain</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Conversational Search & Daily Digests across your Private Notes & Bookmarks</p>', unsafe_allow_html=True)

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.markdown('<div class="section-header">Environment Settings</div>', unsafe_allow_html=True)

# Mode Selector
app_mode = st.sidebar.radio(
    "Mode Setting",
    ["Simulation Mode (Free, Offline)", "Production Mode (Real API)"],
    help="Select whether to use offline mock simulations or OpenAI API connections."
)
is_production = "Production Mode" in app_mode

if is_production:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    if not api_key:
        st.sidebar.warning("⚠️ Please provide an API key to run in Production Mode.")
else:
    api_key = None

st.sidebar.markdown('<div class="section-header">Upload & Ingest documents</div>', unsafe_allow_html=True)

# File uploader
uploaded_files = st.sidebar.file_uploader(
    "Choose Notes / Bookmarks:",
    type=["txt", "md", "pdf"],
    accept_multiple_files=True
)

collection_choice = st.sidebar.selectbox(
    "Target Collection Category",
    ["Work", "Personal", "Bookmarks", "Other"]
)

ingest_btn = st.sidebar.button("⚙️ Ingest Uploaded Files")

# ----------------- SESSION STATE / DEFAULT SEED -----------------
if "knowledge_base_chunks" not in st.session_state:
    # Seed default document contents for immediate simulation
    default_docs = [
        {
            "content": "Review authentication pipeline integration by Tuesday. Secrets must be moved from constants to OS environment variables. Run unit tests on database connection modules.",
            "source": "project_todo.md",
            "collection": "Work"
        },
        {
            "content": "RAG retrieval performance tips: Ensure Top-K is set between 3 and 5 to prevent context dilution. Keep chunk sizes around 300 characters to balance accuracy and text volume.",
            "source": "rag_tuning_tips.txt",
            "collection": "Bookmarks"
        },
        {
            "content": "Goals for 2026: Expand AI developer portfolio with 3 interactive Streamlit RAG apps showing pipeline explainability, repository indexing, and multi-source document QA.",
            "source": "personal_goals.md",
            "collection": "Personal"
        }
    ]
    
    seeded_chunks = []
    for doc in default_docs:
        chunks = chunk_document_contents(doc["content"], doc["source"], doc["collection"], chunk_size=300, chunk_overlap=30)
        seeded_chunks.extend(chunks)
        
    st.session_state["knowledge_base_chunks"] = seeded_chunks
    st.session_state["ingest_status"] = f"Initialized simulation (Seeded {len(seeded_chunks)} default docs)"

if ingest_btn and uploaded_files:
    new_chunks = []
    for file in uploaded_files:
        filename = file.name
        ext = os.path.splitext(filename)[1].lower()
        
        # Read content based on format
        content = ""
        if ext == ".txt":
            content = load_text_content(file)
        elif ext == ".md":
            content = load_markdown_content(file)
        elif ext == ".pdf":
            content = load_pdf_content(file)
            
        if content and not content.startswith("Error"):
            chunks = chunk_document_contents(content, filename, collection_choice, chunk_size=400, chunk_overlap=50)
            new_chunks.extend(chunks)
            
    if new_chunks:
        st.session_state["knowledge_base_chunks"].extend(new_chunks)
        st.session_state["ingest_status"] = f"Success! Ingested {len(uploaded_files)} files into {len(new_chunks)} chunks."
        st.sidebar.success("Ingestion Complete!")
    else:
        st.sidebar.error("Could not parse files. Check extensions.")

st.sidebar.markdown(f'<div style="font-size:0.85rem; color:#94a3b8; padding:5px; background:rgba(255,255,255,0.02); border-radius:6px;">{st.session_state["ingest_status"]}</div>', unsafe_allow_html=True)

# Collection Search Filter
st.sidebar.markdown('<div class="section-header">Metadata Filtering</div>', unsafe_allow_html=True)
category_filter = st.sidebar.selectbox(
    "Query Filter (Category)",
    ["All", "Work", "Personal", "Bookmarks", "Other"],
    help="Restricts RAG search queries strictly to the selected collection category."
)

# ----------------- MAIN VIEW -----------------
# Status display
status_badge = '<span class="mode-badge mode-prod">Production Ready</span>' if is_production else '<span class="mode-badge mode-sim">Simulation Mode</span>'
st.markdown(
    f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 25px;">'
    f'<div>RAG Status: {status_badge}</div>'
    f'<div>Active Database: <b>{len(st.session_state["knowledge_base_chunks"])} chunks</b></div>'
    f'</div>',
    unsafe_allow_html=True
)

tab_search, tab_digest = st.tabs([
    "💬 Conversational Search Q&A",
    "📅 Knowledge Daily Digest"
])

# === TAB 1: CONVERSATIONAL SEARCH ===
with tab_search:
    query = st.text_input(
        "Search your private knowledge files:",
        value="What are my portfolio goals for 2026?",
        placeholder="e.g., What are the performance tuning tips for RAG?"
    )
    
    if query:
        current_chunks = st.session_state["knowledge_base_chunks"]
        
        # Retrieve chunks
        retrieved = retrieve_knowledge_chunks(
            query, 
            current_chunks, 
            category_filter, 
            top_k=3, 
            is_production=is_production, 
            openai_api_key=api_key
        )
        
        if retrieved:
            raw_retrieved = [item[0] for item in retrieved]
            scores = [item[1] for item in retrieved]
            
            # Formulate response
            answer_payload = generate_knowledge_answer(
                query, 
                raw_retrieved, 
                is_production, 
                api_key
            )
            
            col_left, col_right = st.columns([3, 2])
            
            with col_left:
                st.markdown('<div class="section-header">💬 Response</div>', unsafe_allow_html=True)
                st.markdown(answer_payload["answer"])
                
            with col_right:
                st.markdown('<div class="section-header">📁 Sources Citation Panel</div>', unsafe_allow_html=True)
                st.write("Retrieved grounded segments:")
                
                for idx, item in enumerate(retrieved):
                    chunk = item[0]
                    score = item[1]
                    
                    st.markdown(
                        f'<div class="citation-card">'
                        f'<h4>Rank #{idx+1} | {chunk["source"]}</h4>'
                        f'<p style="font-size:0.8rem; color:#94a3b8; margin-bottom:5px;">'
                        f'Collection: <b>{chunk["collection"]}</b> | Similarity Score: <b>{score}</b>'
                        f'</p>'
                        f'<div style="font-size:0.85rem; background:rgba(0,0,0,0.15); padding:8px; border-radius:4px;">'
                        f'{chunk["content"]}'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
        else:
            st.warning(f"No matching files found in collection filter '{category_filter}' for your search.")
            
# === TAB 2: DAILY DIGEST ===
with tab_digest:
    st.markdown('<div class="section-header">📅 Autogenerated Knowledge Briefing</div>', unsafe_allow_html=True)
    st.write("Aggregated summaries of all documents currently indexed in your Second-Brain database:")
    
    current_chunks = st.session_state["knowledge_base_chunks"]
    digest_report = generate_daily_digest(current_chunks, is_production, api_key)
    
    st.markdown(
        f'<div class="glass-card">'
        f'{digest_report}'
        f'</div>',
        unsafe_allow_html=True
    )
