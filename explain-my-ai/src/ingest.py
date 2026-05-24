import os

def load_kb_document(file_path="data/kb.txt"):
    """Loads the main knowledge base text document."""
    if not os.path.exists(file_path):
        # Fallback to relative search or standard location
        alt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path)
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            return "Error: kb.txt file not found."
            
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_document(text: str, chunk_size: int = 300, chunk_overlap: int = 50):
    """
    Splits text into chunks of `chunk_size` characters, with `chunk_overlap` character overlap.
    Returns a list of dicts, each with keys: 'id', 'content', 'length', 'source'.
    """
    chunks = []
    if not text or chunk_size <= 0:
        return chunks
        
    # Standard Character-based chunking
    start = 0
    chunk_id = 1
    
    # We strip empty lines or treat document headers as metadata hints
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        content = text[start:end]
        
        # Determine some basic source header tracking (e.g. which Section it belongs to)
        # Find nearest section header preceding start
        section_name = "General RAG Docs"
        lines_before = text[:start].split('\n')
        for line in reversed(lines_before):
            if line.startswith("## ") or line.startswith("# "):
                section_name = line.replace("#", "").strip()
                break
                
        chunks.append({
            "id": chunk_id,
            "content": content.strip(),
            "length": len(content),
            "source": f"kb.txt ({section_name})"
        })
        
        chunk_id += 1
        start += (chunk_size - chunk_overlap)
        
        # Prevent infinite loops if overlap is greater than or equal to chunk_size
        if chunk_size <= chunk_overlap:
            break
            
    return chunks
