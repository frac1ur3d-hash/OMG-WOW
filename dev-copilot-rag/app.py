import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Ensure local source directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from scan_repo import scan_local_directory
from chunk_code import chunk_code_files
from retrieve import simulate_code_search, retrieve_production_code
from answer import synthesize_mock_answer, synthesize_copilot_answer
from ui_components import inject_premium_css

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Dev Copilot RAG - Codebase Q&A",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling injection (using glassmorphic styles similar to project 1)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif;
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .main-title {
        background: linear-gradient(135deg, #a855f7 0%, #4facfe 100%);
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
        border-bottom: 2px solid rgba(168, 85, 247, 0.15);
        padding-bottom: 8px;
        margin-bottom: 15px;
    }
    
    .citation-badge {
        background: rgba(168, 85, 247, 0.15);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 6px;
        padding: 2px 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 5px;
    }
    
    .diff-container {
        border-left: 4px solid #10b981;
        background-color: rgba(16, 185, 129, 0.04);
        padding: 10px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9rem;
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
st.markdown('<h1 class="main-title">💻 Dev Copilot RAG</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Locate, Explain, and Draft Code patches using semantic codebase index files</p>', unsafe_allow_html=True)

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.markdown('<div class="section-header">Environment Settings</div>', unsafe_allow_html=True)

# Ingestion Type Switcher
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

st.sidebar.markdown('<div class="section-header">Codebase Scanner</div>', unsafe_allow_html=True)

# Scanning Path Input
target_path = st.sidebar.text_input(
    "Local Folder Path to scan:",
    value=".",
    help="Absolute or relative path of the code repository to index."
)

scan_btn = st.sidebar.button("🔍 Index Codebase Files")

# Load and index state cache
if "scanned_files" not in st.session_state:
    # Pre-index default fallback data
    st.session_state["scanned_files"] = scan_local_directory("nonexistent-path-forces-mock")
    st.session_state["chunks"] = chunk_code_files(st.session_state["scanned_files"])
    st.session_state["scan_status"] = f"Initialized simulation codebase (Mock project loaded: {len(st.session_state['scanned_files'])} files, {len(st.session_state['chunks'])} chunks)"

if scan_btn:
    with st.spinner("Scanning files..."):
        scanned = scan_local_directory(target_path)
        chunks = chunk_code_files(scanned)
        st.session_state["scanned_files"] = scanned
        st.session_state["chunks"] = chunks
        st.session_state["scan_status"] = f"Index complete! Scanned {len(scanned)} files into {len(chunks)} code chunks."
        st.sidebar.success("Done!")

st.sidebar.markdown(f'<div style="font-size:0.85rem; color:#94a3b8; padding:5px; background:rgba(255,255,255,0.02); border-radius:6px;">{st.session_state["scan_status"]}</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="section-header">Copilot Mode</div>', unsafe_allow_html=True)
copilot_mode = st.sidebar.selectbox(
    "Select Assistant Mode",
    ["Explain Mode", "Locate Mode", "Change Request (Diff)"],
    help="Explain Mode describes logic. Locate Mode lists file ranges. Change Request drafts diff code blocks."
)

# ----------------- MAIN VIEW -----------------
# Status line
status_badge = '<span class="mode-badge mode-prod">Production Ready</span>' if is_production else '<span class="mode-badge mode-sim">Simulation Mode</span>'
st.markdown(f'<div style="margin-bottom:20px;">Retrieval Status: {status_badge}</div>', unsafe_allow_html=True)

# Query Input
query = st.text_input(
    "Ask the codebase a question:",
    value="How is the JWT session token verified?",
    placeholder="e.g., Where is DB session defined? Propose a change to load secret key from OS environment variables."
)

if query:
    current_chunks = st.session_state["chunks"]
    
    # 1. Retrieve
    if is_production and api_key:
        try:
            retrieved = retrieve_production_code(query, current_chunks, top_k=3, openai_api_key=api_key)
        except Exception as e:
            st.error(f"Error connecting to OpenAI Embeddings: {e}. Falling back to keyword search.")
            retrieved = simulate_code_search(query, current_chunks, top_k=3)
    else:
        retrieved = simulate_code_search(query, current_chunks, top_k=3)
        
    raw_retrieved = [item[0] for item in retrieved]
    scores = [item[1] for item in retrieved]
    
    # 2. Formulate Answer
    answer_payload = synthesize_copilot_answer(
        query, 
        raw_retrieved, 
        copilot_mode, 
        is_production, 
        api_key
    )
    
    # 3. Layout Display
    col_ans, col_source = st.columns([3, 2])
    
    with col_ans:
        st.markdown('<div class="section-header">💬 Copilot Output</div>', unsafe_allow_html=True)
        
        # Output primary answer
        st.markdown(answer_payload["answer"])
        
        # Display code patches if Change Request mode is active
        if copilot_mode == "Change Request (Diff)" and answer_payload["diff"]:
            st.markdown("#### Propose Code Diff:")
            st.code(answer_payload["diff"], language="diff")
            
    with col_source:
        st.markdown('<div class="section-header">📁 Grounded References & Citations</div>', unsafe_allow_html=True)
        st.write("Source snippets retrieved to formulate the generated response:")
        
        for idx, item in enumerate(retrieved):
            chunk = item[0]
            score = item[1]
            
            with st.expander(f"Rank #{idx+1} | {chunk['path']} (Score: {score})", expanded=(idx==0)):
                st.markdown(
                    f'<div style="margin-bottom:8px;">'
                    f'<span class="citation-badge">Lines {chunk["start_line"]} - {chunk["end_line"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
                # Check file extension to determine code syntax highlighting
                ext = os.path.splitext(chunk["path"])[1].lower()
                lang = "python"
                if ext in {".js", ".ts"}:
                    lang = "javascript"
                elif ext == ".md":
                    lang = "markdown"
                    
                st.code(chunk["content"], language=lang)
else:
    st.info("💡 Enter a question above and press enter to scan indexed code files.")
