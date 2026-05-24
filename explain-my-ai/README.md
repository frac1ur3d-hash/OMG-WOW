# Explain My AI — RAG Debugger & Evaluation Harness

Explain My AI is an interactive RAG (Retrieval-Augmented Generation) debugger and evaluation harness. It visualizes each stage of a retrieval-augmented pipeline (ingestion → chunking → embeddings → retrieval → prompt assembly → generation) and exposes internal artifacts like retrieved context, similarity scores, and the final compiled prompt. The app supports a free **Simulation Mode** (which runs fully offline with simulated semantic scoring) and a **Production Mode** using real OpenAI embeddings and LLM generation. Designed to help developers diagnose hallucinations, retrieval misses, and prompt alignment issues through side-by-side configuration comparison and lightweight evaluation metrics.

---

## 🚀 Key Features

* **Why This Answer? Panel**: Visualizes the semantic influence of each retrieved context chunk on the generated answer.
* **Retrieval Inspector**: Real-time visualization of Top-K similarity scores with interactive Plotly bar charts.
* **Prompt Breakdown Viewer**: Side-by-side breakdown showing the System Prompt, User Query, and compiled Context payloads.
* **Multi-Model Comparison**: Side-by-side performance assessment across three configurations: GPT-4, Local LLM, and Mock Model.
* **Failure Simulation Mode**: Forces poor pipeline parameters (low Top-K, micro-chunk size, missing context, and high temperatures) to demonstrate RAG failure modes.
* **Offline Simulation / Production Toggle**: Runs out-of-the-box offline using rule-based scorers or links to OpenAI APIs when key is configured.

---

## 🛠️ Tech Stack

* **UI Framework**: Streamlit (Python)
* **Vector Store**: FAISS
* **Orchestration**: LangChain
* **Visualizations**: Plotly
* **LLM Engine**: OpenAI API (`gpt-4o-mini`) / Dynamic Local Simulator

---

## 📁 Repository Structure

```
explain-my-ai/
├── app.py                  # Main Streamlit web application
├── requirements.txt        # Package dependencies
├── .env.example            # Environment template
├── README.md               # Project documentation
├── data/
│   └── kb.txt              # Sample knowledge base text corpus
└── src/
    ├── ingest.py           # Document loading and text chunking logic
    ├── retrieve.py         # Semantic similarity search drivers (mock/real)
    ├── prompt_builder.py   # Multi-stage prompt compiler
    ├── llm.py              # Mock model engines and production API connectors
    ├── eval.py             # Rule-based Groundedness and Relevance evaluation
    └── ui_components.py    # Custom CSS/styling sheet for premium UI design
```

---

## 💻 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/explain-my-ai.git
   cd explain-my-ai
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file from the example template:
   ```bash
   cp .env.example .env
   ```
   Add your OpenAI API key to `.env` if you wish to run in Production Mode:
   ```env
   OPENAI_API_KEY=your_key_here
   ```

4. **Launch the application**:
   ```bash
   streamlit run app.py
   ```

---

## 🧾 Resume Bullets (ATS Optimized)

* **Built an interactive RAG debugging + evaluation platform** exposing retrieval results, similarity scores, compiled prompts, and generation outputs for pipeline transparency and iteration.
* **Implemented A/B configuration comparison** for chunking and Top-K retrieval to analyze and improve response grounding in a document Q&A workflow.
