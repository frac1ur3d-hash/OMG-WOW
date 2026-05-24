import re
from typing import List, Dict, Tuple

def tokenize_text(text: str) -> set:
    """Tokenize and return lowercase word tokens, ignoring short words."""
    words = re.findall(r'\b\w{3,}\b', text.lower())
    stops = {'the', 'and', 'for', 'you', 'this', 'that', 'with', 'from', 'have', 'are', 'was', 'were'}
    return set([w for w in words if w not in stops])

def retrieve_knowledge_chunks(
    query: str, 
    chunks: List[Dict], 
    collection_filter: str = "All", 
    top_k: int = 3, 
    is_production: bool = False,
    openai_api_key: str = None
) -> List[Tuple[Dict, float]]:
    """
    Retrieves matching document chunks.
    Filters by collection category (e.g., 'Work', 'Bookmarks', 'Personal') prior to searching.
    """
    # 1. Apply Metadata Filtering
    filtered_chunks = chunks
    if collection_filter != "All":
        filtered_chunks = [c for c in chunks if c.get("collection") == collection_filter]
        
    if not filtered_chunks:
        return []
        
    # 2. Production Indexing & Query
    if is_production and openai_api_key:
        from langchain_community.vectorstores import FAISS
        from langchain_openai import OpenAIEmbeddings
        from langchain_core.documents import Document
        
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        docs = []
        for c in filtered_chunks:
            doc = Document(
                page_content=c["content"],
                metadata={"id": c["id"], "source": c["source"], "collection": c["collection"]}
            )
            docs.append(doc)
            
        db = FAISS.from_documents(docs, embeddings)
        results = db.similarity_search_with_score(query, k=top_k)
        
        retrieved = []
        for doc, distance in results:
            sim_score = 1.0 / (1.0 + distance)
            chunk_dict = {
                "id": doc.metadata["id"],
                "content": doc.page_content,
                "source": doc.metadata["source"],
                "collection": doc.metadata["collection"]
            }
            retrieved.append((chunk_dict, round(sim_score, 4)))
        return retrieved
        
    # 3. Simulation Retrieval (Offline fallback)
    query_tokens = tokenize_text(query)
    scored = []
    
    for c in filtered_chunks:
        c_tokens = tokenize_text(c["content"])
        if not query_tokens:
            score = 0.0
        else:
            intersection = query_tokens.intersection(c_tokens)
            union = query_tokens.union(c_tokens)
            jaccard = len(intersection) / max(len(union), 1)
            # Normalize Jaccard overlap to a realistic dense vector score range [0.2 - 0.95]
            score = min(0.25 + (jaccard * 0.7), 0.98)
            
            # Simple fallback random variance if zero keywords overlap
            if len(intersection) == 0:
                score = 0.15 + ((hash(c["content"]) % 100) / 1000.0)
                
        scored.append((c, round(score, 4)))
        
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
