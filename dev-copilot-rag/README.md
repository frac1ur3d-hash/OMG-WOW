# Dev Copilot RAG — Codebase Q&A & Code Citation Assistant

Dev Copilot RAG is a local "chat with your codebase" assistant. It indexes source files, performs semantic retrieval to find relevant code snippets, and generates answers grounded in retrieved context with exact file citations. Built to support onboarding, faster debugging, and repository discovery by combining retrieval and LLM generation in a lightweight developer-focused interface.

---

## 🚀 Key Features

* **Local Repository Scanner**: Recursively reads local files (`.py`, `.js`, `.ts`, `.md`, `.json`, `.css`, `.html`) while ignoring runtime and cache folders (`node_modules`, `venv`, `__pycache__`).
* **Line-Based Code Chunking**: Employs semantic code boundaries tracking exact file paths and code line numbers.
* **Locate, Explain, & Patch Modes**:
  * **Explain Mode**: Breaks down internal system logic, classes, and parameter bindings.
  * **Locate Mode**: Outputs structured matrices mapping files, line ranges, and relevance ranking.
  * **Change Request (Diff) Mode**: Outputs proposed file edits inside standard Git unified diff displays showing additions (+) and removals (-).
* **Interactive Source Explorer**: Synchronizes side-by-side with chat output, rendering syntax-highlighted source snippets with line range badges.
* **Offline / Production Toggles**: Works offline out-of-the-box using a simulated mock repository, or links to OpenAI embeddings and completions when configured.

---

## 🛠️ Tech Stack

* **UI Framework**: Streamlit (Python)
* **Vector Store**: FAISS
* **Orchestration**: LangChain
* **LLM Engine**: OpenAI API (`gpt-4o-mini`) / Rule-based local syntax generator

---

## 📁 Repository Structure

```
dev-copilot-rag/
├── app.py                  # Main Streamlit web application
├── requirements.txt        # Package dependencies
├── .env.example            # Environment template
├── README.md               # Project documentation
└── src/
    ├── scan_repo.py        # Recursive local directory scanner and mock generator
    ├── chunk_code.py       # Line-based code chunking engine
    ├── retrieve.py         # Code-focused semantic search helpers (mock/real)
    ├── answer.py           # Multi-mode response compilation and Git patch formatter
    └── ui_components.py    # Custom CSS injection styles (shared component design)
```

---

## 💻 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/dev-copilot-rag.git
   cd dev-copilot-rag
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

* **Built a codebase Q&A assistant** that indexes repositories for semantic retrieval and generates file-cited answers to developer questions using a RAG pipeline.
* **Implemented retrieval + citation formatting** to support developer onboarding and debugging workflows by grounding responses in source code context.
