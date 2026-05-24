import numpy as np
import re
from typing import List, Dict, Tuple

def clean_and_tokenize(text: str) -> List[str]:
    """Cleans text and breaks it into lowercase words, filtering out common stop words."""
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'to', 'for', 'in', 
        'on', 'at', 'by', 'of', 'with', 'about', 'as', 'into', 'like', 'through', 'this', 'that',
        'these', 'those', 'it', 'its', 'they', 'them', 'their', 'we', 'us', 'our', 'you', 'your'
    }
    return [w for w in words if w not in stop_words]

def simulate_semantic_search(query: str, chunks: List[Dict], top_k: int = 3) -> List[Tuple[Dict, float]]:
    """
    Simulates a vector similarity search offline.
    Calculates TF-IDF/Jaccard similarity to return the most relevant chunks with realistic scores.
    """
    query_tokens = clean_and_tokenize(query)
    scored_chunks = []
    
    for chunk in chunks:
        chunk_tokens = clean_and_tokenize(chunk["content"])
        
        if not query_tokens:
            score = 0.0
        else:
            # Calculate overlapping words
            overlap = set(query_tokens).intersection(set(chunk_tokens))
            
            # Basic TF calculation
            tf = 0
            for token in query_tokens:
                tf += chunk_tokens.count(token)
                
            # Normalize with length penalty
            jaccard = len(overlap) / max(len(set(query_tokens).union(set(chunk_tokens))), 1)
            
            # Score scaling to mimic Cosine Similarity [0.3 - 0.95]
            raw_score = (jaccard * 0.7) + (min(tf * 0.05, 0.2))
            
            # Add a small random jitter to make it look like dense vector search
            jitter = (hash(chunk["content"] + query) % 100) / 2000.0  # 0 to 0.05
            score = min(0.3 + raw_score + jitter, 0.98)
            
            # Penalize completely irrelevant segments
            if len(overlap) == 0:
                score = max(0.1 + jitter, 0.25)
                
        scored_chunks.append((chunk, round(score, 4)))
        
    # Sort descending by score
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return scored_chunks[:top_k]

def retrieve_production(query: str, chunks: List[Dict], top_k: int = 3, openai_api_key: str = None) -> List[Tuple[Dict, float]]:
    """
    Production retriever using FAISS and OpenAI Embeddings.
    """
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain_core.documents import Document
    
    if not openai_api_key:
        raise ValueError("OpenAI API key must be provided in production mode.")
        
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    
    # Map dictionary chunks to LangChain Documents
    docs = []
    for c in chunks:
        doc = Document(
            page_content=c["content"],
            metadata={"id": c["id"], "source": c["source"]}
        )
        docs.append(doc)
        
    # Build a temporary in-memory vector store
    db = FAISS.from_documents(docs, embeddings)
    
    # Perform similarity search with scores (L2 distance is returned, we convert to approximate cosine score)
    results = db.similarity_search_with_score(query, k=top_k)
    
    retrieved = []
    for doc, distance in results:
        # FAISS score is L2 distance, smaller is better.
        # Convert distance to a similarity-like score (1 / (1 + distance))
        sim_score = 1.0 / (1.0 + distance)
        chunk_dict = {
            "id": doc.metadata["id"],
            "content": doc.page_content,
            "source": doc.metadata["source"]
        }
        retrieved.append((chunk_dict, round(sim_score, 4)))
        
    return retrieved
