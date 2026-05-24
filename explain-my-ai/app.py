import streamlit as st
import os
import sys
import plotly.graph_objects as go
from dotenv import load_dotenv

# Ensure local source directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ingest import load_kb_document, chunk_document
from retrieve import simulate_semantic_search, retrieve_production
from prompt_builder import compile_rag_prompt
from llm import synthesize_mock_response, call_production_llm
from eval import evaluate_rag
from ui_components import inject_premium_css

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Explain My AI - RAG Debugger & Eval",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom premium CSS
inject_premium_css()

# Header
st.markdown('<h1 class="main-title">⚙️ Explain My AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Interactive RAG Debugger, Optimizer, & Evaluation Harness</p>', unsafe_allow_html=True)

# ----------------- SIDEBAR: CONTROLS -----------------
st.sidebar.markdown('<div class="section-header">Pipeline Environment</div>', unsafe_allow_html=True)

# Mode Selector
app_mode = st.sidebar.radio(
    "Mode",
    ["Simulation Mode (Free, Offline)", "Production Mode (Real API)"],
    help="Simulation Mode simulates vector databases and LLM responses offline. Production Mode uses real OpenAI calls."
)
is_production = "Production Mode" in app_mode

if is_production:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    if not api_key:
        st.sidebar.warning("⚠️ Please provide an API key to run in Production Mode.")
else:
    api_key = None

st.sidebar.markdown('<div class="section-header">Experimental Controls</div>', unsafe_allow_html=True)

# Failure simulation toggle
fail_simulation = st.sidebar.checkbox(
    "🔥 Failure Simulation Mode",
    value=False,
    help="Force bad retrieval/generation parameters to simulate common RAG failures."
)

if fail_simulation:
    st.sidebar.markdown(
        '<div class="alert-container">⚠️ FAILURE SIMULATION ACTIVE<br/>Forcing low top-K, poor chunking constraints, and high temperature to trigger hallucinations.</div>',
        unsafe_allow_html=True
    )
    # Forced bad parameters
    chunk_size = st.sidebar.slider("Chunk Size (characters)", 40, 1000, 80, disabled=True)
    chunk_overlap = st.sidebar.slider("Chunk Overlap", 0, 200, 0, disabled=True)
    top_k = st.sidebar.slider("Top-K Retrieved Chunks", 1, 5, 1, disabled=True)
    temperature = st.sidebar.slider("Temperature", 0.0, 1.5, 1.4, disabled=True)
else:
    # Customizable parameters
    chunk_size = st.sidebar.slider(
        "Chunk Size (characters)",
        50, 1000, 300,
        help="Size of split texts. Smaller means higher granularity but lower context."
    )
    chunk_overlap = st.sidebar.slider(
        "Chunk Overlap",
        0, 200, 50,
        help="Overlapping characters between chunks to preserve context boundaries."
    )
    top_k = st.sidebar.slider(
        "Top-K Retrieved Chunks",
        1, 5, 3,
        help="Number of chunks retrieved to compile the prompt."
    )
    temperature = st.sidebar.slider(
        "Temperature",
        0.0, 1.5, 0.3,
        help="Higher values increase generation variety but risk hallucination."
    )

system_instruction = st.sidebar.text_area(
    "System Grounding Prompt",
    value="You are a helpful assistant. Answer the user question ONLY using the provided Context. If the context does not contain the answer, reply that you do not have enough information."
)

# ----------------- SESSION STATE / INGESTION -----------------
# Load kb.txt data
document_text = load_kb_document("data/kb.txt")

if "kb_loaded" not in st.session_state:
    st.session_state["kb_loaded"] = True

# Process chunks dynamically based on settings
current_chunks = chunk_document(document_text, chunk_size, chunk_overlap)

# Show corpus status
badge_html = '<span class="mode-badge mode-prod">Production Ready</span>' if is_production else '<span class="mode-badge mode-sim">Offline Sim</span>'
st.markdown(
    f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 25px;">'
    f'<div>Status: {badge_html}</div>'
    f'<div>Indexed Corpus: <b>{len(current_chunks)} Chunks</b></div>'
    f'</div>',
    unsafe_allow_html=True
)

# User Query input
query = st.text_input(
    "Ask a question to test the RAG Pipeline:",
    value="What are the main causes of RAG failure?",
    placeholder="e.g., What is chunking? How does evaluation work?"
)

# Run pipeline execution
if query:
    # 1. Retrieve
    if is_production and api_key:
        try:
            retrieved = retrieve_production(query, current_chunks, top_k, api_key)
        except Exception as e:
            st.error(f"Error calling OpenAI Embeddings: {e}. Falling back to simulation.")
            retrieved = simulate_semantic_search(query, current_chunks, top_k)
    else:
        retrieved = simulate_semantic_search(query, current_chunks, top_k)
        
    # Check if we forced "missing context" in failure simulation
    if fail_simulation:
        # Override retrieved with irrelevant details to show context miss
        retrieved = [
            ({
                "id": 999,
                "content": "A separate unrelated recipe outlines how to make coffee: roast beans at 400 degrees, grind, and brew with hot water.",
                "source": "coffee_making.txt (Section 1)"
            }, 0.28)
        ]
        
    # Extract raw chunks
    raw_retrieved_chunks = [item[0] for item in retrieved]
    scores = [item[1] for item in retrieved]
    
    # 2. Compile prompt
    prompt_payload = compile_rag_prompt(system_instruction, query, raw_retrieved_chunks)
    
    # 3. Model Outputs
    model_outputs = {}
    
    if is_production and api_key:
        # Fetch actual GPT answer
        try:
            gpt_res = call_production_llm(prompt_payload["final_compiled_prompt"], "gpt", api_key)
            model_outputs["gpt"] = gpt_res
        except Exception as e:
            st.error(f"Error fetching actual LLM completion: {e}. Running simulation.")
            model_outputs["gpt"] = synthesize_mock_response(query, raw_retrieved_chunks, "gpt")
    else:
        model_outputs["gpt"] = synthesize_mock_response(query, raw_retrieved_chunks, "gpt")
        
    # Keep local and mock models as offline simulations for rich portfolio contrast
    model_outputs["local"] = synthesize_mock_response(query, raw_retrieved_chunks, "local")
    model_outputs["mock"] = synthesize_mock_response(query, raw_retrieved_chunks, "mock")
    
    # Run evaluation metrics on primary (GPT) output
    primary_answer = model_outputs["gpt"]["text"]
    eval_metrics = evaluate_rag(query, raw_retrieved_chunks, primary_answer)
    
    # ----------------- TABS WORKSPACE -----------------
    tab_debug, tab_compare, tab_eval = st.tabs([
        "🔍 RAG Debugger & Explainability",
        "⚖️ Multi-Model Comparison",
        "📊 Evaluation & Quality metrics"
    ])
    
    # === TAB 1: RAG DEBUGGER ===
    with tab_debug:
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.markdown('<div class="section-header">🧠 "Why this answer?" Panel</div>', unsafe_allow_html=True)
            st.write("Visualizing the semantic influence of each retrieved context chunk on the final answer:")
            
            # Extract influences from selected model
            influences = model_outputs["gpt"].get("influences", [])
            
            for idx, c_info in enumerate(influences):
                c_id = c_info["chunk_id"]
                c_inf = c_info["influence"]
                c_reason = c_info["reason"]
                
                # Match content from retrieved lists
                content_preview = ""
                for rc in raw_retrieved_chunks:
                    if rc["id"] == c_id:
                        content_preview = rc["content"][:120] + "..."
                        break
                        
                st.markdown(
                    f'<div class="glass-card">'
                    f'<h4>Chunk #{c_id} <span style="float:right; color:#00f2fe;">Influence: {c_inf*100}%</span></h4>'
                    f'<p style="font-size:0.9rem; color:#94a3b8;"><b>Source:</b> {c_reason}</p>'
                    f'<div class="source-box">{content_preview}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
            # Prompt Inspector Accordions
            st.markdown('<div class="section-header">📝 Prompt Inspector</div>', unsafe_allow_html=True)
            with st.expander("Show System Grounding Prompt"):
                st.code(prompt_payload["system_prompt"], language="markdown")
            with st.expander("Show Injected Context & User Query"):
                st.code(prompt_payload["user_input"], language="markdown")
            with st.expander("Show Final Compiled Prompt Sent to LLM"):
                st.code(prompt_payload["final_compiled_prompt"], language="markdown")
                
        with col_right:
            st.markdown('<div class="section-header">🎯 Retrieval Inspector</div>', unsafe_allow_html=True)
            st.write("Top-K matching vector results and similarity scores:")
            
            # Plotly Similarity Score Bar Graph
            fig = go.Figure(go.Bar(
                x=[f"Chunk #{rc['id']}" for rc in raw_retrieved_chunks],
                y=scores,
                marker_color=['#00f2fe' if s > 0.6 else '#ff4b4b' for s in scores],
                text=scores,
                textposition='auto',
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f8fafc'),
                margin=dict(l=20, r=20, t=20, b=20),
                height=250,
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', range=[0, 1])
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Full retrieved chunks text
            for idx, rc in enumerate(raw_retrieved_chunks):
                st.markdown(
                    f'<div class="glass-card">'
                    f'<h4>Vector Rank #{idx+1} | Chunk #{rc["id"]}</h4>'
                    f'<p style="font-size:0.85rem; margin-bottom:5px;"><b>Similarity Score:</b> <span style="color:#34d399;">{scores[idx]}</span></p>'
                    f'<p style="font-size:0.85rem; margin-bottom:10px;"><b>Source File:</b> {rc["source"]}</p>'
                    f'<div style="font-size:0.9rem; background:rgba(0,0,0,0.25); padding:10px; border-radius:6px; border:1px solid rgba(255,255,255,0.05);">'
                    f'{rc["content"]}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
    # === TAB 2: MODEL COMPARISON ===
    with tab_compare:
        st.markdown('<div class="section-header">⚖️ Multi-Model Configuration comparison</div>', unsafe_allow_html=True)
        st.write("Compare execution performance across three mock/real LLM configurations side-by-side:")
        
        col_gpt, col_local, col_mock = st.columns(3)
        
        with col_gpt:
            st.markdown(
                '<div class="glass-card" style="border-top: 4px solid #00f2fe;">'
                '<h3>🌐 GPT-4</h3>'
                '<p style="color:#64748b; font-size:0.85rem;">Production-Tier Cloud Engine</p>'
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown(f"**Answer:**\n{model_outputs['gpt']['text']}")
            
            # Metrics
            st.markdown(f'<div class="glow-metric"><div class="glow-metric-value">{model_outputs["gpt"]["latency"]}s</div><div class="glow-metric-label">Latency</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="glow-metric" style="margin-top:10px;"><div class="glow-metric-value">{model_outputs["gpt"]["quality"]}%</div><div class="glow-metric-label">Simulated Quality</div></div>', unsafe_allow_html=True)
            
        with col_local:
            st.markdown(
                '<div class="glass-card" style="border-top: 4px solid #a855f7;">'
                '<h3>💻 Local LLM</h3>'
                '<p style="color:#64748b; font-size:0.85rem;">Edge Deployment (Llama-3-8B)</p>'
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown(f"**Answer:**\n{model_outputs['local']['text']}")
            
            # Metrics
            st.markdown(f'<div class="glow-metric"><div class="glow-metric-value">{model_outputs["local"]["latency"]}s</div><div class="glow-metric-label">Latency</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="glow-metric" style="margin-top:10px;"><div class="glow-metric-value">{model_outputs["local"]["quality"]}%</div><div class="glow-metric-label">Simulated Quality</div></div>', unsafe_allow_html=True)
            
        with col_mock:
            st.markdown(
                '<div class="glass-card" style="border-top: 4px solid #f43f5e;">'
                '<h3>🤡 Mock Model</h3>'
                '<p style="color:#64748b; font-size:0.85rem;">Low-Tier Draft Model</p>'
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown(f"**Answer:**\n{model_outputs['mock']['text']}")
            
            # Metrics
            st.markdown(f'<div class="glow-metric"><div class="glow-metric-value">{model_outputs["mock"]["latency"]}s</div><div class="glow-metric-label">Latency</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="glow-metric" style="margin-top:10px;"><div class="glow-metric-value">{model_outputs["mock"]["quality"]}%</div><div class="glow-metric-label">Simulated Quality</div></div>', unsafe_allow_html=True)

    # === TAB 3: EVALUATION METRICS ===
    with tab_eval:
        st.markdown('<div class="section-header">📊 RAG Evaluation & Grounding Analysis</div>', unsafe_allow_html=True)
        st.write("Quantitative heuristic scoring evaluating the primary model's generation quality:")
        
        col_g, col_r, col_c = st.columns(3)
        
        with col_g:
            st.markdown(
                f'<div class="glass-card" style="text-align:center;">'
                f'<h3>Groundedness Score</h3>'
                f'<p style="color:#94a3b8; font-size:0.9rem;">Is the answer based <b>strictly</b> on context?</p>'
                f'<div style="font-size:3.5rem; font-weight:700; color:#34d399; margin: 15px 0;">{eval_metrics["groundedness"]}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if eval_metrics["groundedness"] < 60:
                st.warning("⚠️ Low Groundedness! The model output contains vocabulary absent from retrieved chunks. High risk of hallucination.")
            else:
                st.success("✅ Excellent Groundedness. Output aligns structurally with vector facts.")
                
        with col_r:
            st.markdown(
                f'<div class="glass-card" style="text-align:center;">'
                f'<h3>Answer Relevance</h3>'
                f'<p style="color:#94a3b8; font-size:0.9rem;">Does the answer address core query keywords?</p>'
                f'<div style="font-size:3.5rem; font-weight:700; color:#00f2fe; margin: 15px 0;">{eval_metrics["relevance"]}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if eval_metrics["relevance"] < 50:
                st.warning("⚠️ Low Relevance. The response may have missed answering the user's specific request.")
            else:
                st.success("✅ Good Relevance. Key vocabulary terms from query are resolved.")
                
        with col_c:
            st.markdown(
                f'<div class="glass-card" style="text-align:center;">'
                f'<h3>Citation Coverage</h3>'
                f'<p style="color:#94a3b8; font-size:0.9rem;">Percentage of retrieved chunks referenced.</p>'
                f'<div style="font-size:3.5rem; font-weight:700; color:#a855f7; margin: 15px 0;">{eval_metrics["citation_coverage"]}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if eval_metrics["citation_coverage"] == 0:
                st.info("ℹ️ No inline citations identified in response string. Use chunk tags in queries to improve reference linking.")
            else:
                st.success("✅ Inline citations successfully identified and parsed.")
                
        # Detailed feedback alert
        if fail_simulation:
            st.markdown(
                '<div class="alert-container" style="background:rgba(239, 68, 68, 0.08); border-color:rgba(239, 68, 68, 0.3); color:#f87171;">'
                '<h4>🔍 Failure Analysis Case Study</h4>'
                'Due to the <b>Failure Simulation Mode</b> being active, the chunk size was reduced to 80 characters, '
                'which fractured sentences. Additionally, the Top-K was set to 1 and Temperature set to 1.4. '
                'This resulted in a context retrieval miss, dropping Groundedness and leading to LLM text generation instability.'
                '</div>',
                unsafe_allow_html=True
            )
