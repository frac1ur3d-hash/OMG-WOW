# Knowledge Brain — Personal Second-Brain RAG

Knowledge Brain is a personal "second brain" assistant powered by Retrieval-Augmented Generation. It ingests notes and documents, builds a vector index for semantic retrieval, and answers questions with citations back to the original sources. Designed for fast knowledge recall, cross-document search, and grounded Q&A without retraining models—updates happen by re-indexing content.

---

## 🚀 Key Features

* **Multi-Format Ingestion**: Drag-and-drop file uploader supporting `.txt`, `.md`, and `.pdf` files (powered by `pypdf`).
* **Metadata Tag Filtering**: Enables users to isolate searches to specific collection categories (e.g., *Work*, *Personal*, *Bookmarks*, *Other*) to refine context query focus.
* **Daily Digest Briefings**: Automatically aggregates all active documents in the database and compiles structured, category-grouped summaries and suggested follow-up questions.
* **Seeded Sandbox Data**: Includes pre-loaded developer and productivity bookmarks for instant offline testing and Q&A operations.
* **Offline / Production Toggles**: Works offline out-of-the-box using rule-based estimators, or links to OpenAI embeddings and completions when configured.

---

## 🛠️ Tech Stack

* **UI Framework**: Streamlit (Python)
* **Vector Store**: FAISS
* **Orchestration**: LangChain
* **Parser Support**: PyPDF
* **LLM Engine**: OpenAI API (`gpt-4o-mini`) / Local offline summary processor

---

## 📁 Repository Structure

```
knowledge-brain/
├── app.py                  # Main Streamlit web application
├── requirements.txt        # Package dependencies
├── .env.example            # Environment template
├── README.md               # Project documentation
└── src/
    ├── chunk.py            # Document partitioner retaining collection tags
    ├── retrieve.py         # Semantic search and collection filter engine (mock/real)
    ├── answer.py           # Citation Q&A compiler and Daily Digest briefing report
    └── ingest/             # Multi-format parsing modules
        ├── load_txt.py     # Text loader driver
        ├── load_md.py      # Markdown loader driver
        └── load_pdf.py     # PDF loader driver (pypdf wrapper)
```

---

## 💻 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/knowledge-brain.git
   cd knowledge-brain
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

* **Built a personal knowledge assistant using RAG** to enable conversational search over notes/documents with source citations and grounded answers.
* **Implemented document ingestion, chunking, embeddings, and vector retrieval** to support scalable, updateable knowledge base Q&A.
