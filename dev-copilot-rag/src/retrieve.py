import re
import numpy as np
from typing import List, Dict, Tuple

def tokenize_code_and_query(text: str) -> List[str]:
    """Splits identifiers, function names, and comments into tokens."""
    # Find words, splitting camelCase and snake_case
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    # Sub-tokenize on symbols or case boundaries
    tokens = []
    for w in words:
        tokens.append(w)
        # Split on numbers or letter transitions if applicable
        splits = re.split(r'(?<=[a-zA-Z])(?=[0-9])|(?<=[0-9])(?=[a-zA-Z])', w)
        if len(splits) > 1:
            tokens.extend(splits)
    return list(set(tokens))

def simulate_code_search(query: str, chunks: List[Dict], top_k: int = 3) -> List[Tuple[Dict, float]]:
    """
    Simulates semantic search over codebase chunks.
    Scores chunks based on word overlap of code identifiers and comment keywords.
    """
    query_tokens = tokenize_code_and_query(query)
    scored_chunks = []
    
    for chunk in chunks:
        chunk_tokens = tokenize_code_and_query(chunk["content"] + " " + chunk["path"])
        
        if not query_tokens:
            score = 0.0
        else:
            overlap = set(query_tokens).intersection(set(chunk_tokens))
            # Calculate score: Jaccard overlap + path weight (if query mentions file path terms)
            jaccard = len(overlap) / max(len(set(query_tokens).union(set(chunk_tokens))), 1)
            
            path_weight = 0.0
            for t in query_tokens:
                if t in chunk["path"].lower():
                    path_weight += 0.25
                    
            score = min(0.2 + (jaccard * 0.7) + path_weight, 0.98)
            
            # Penalize completely irrelevant segments
            if len(overlap) == 0 and path_weight == 0:
                # small hash-based score variation
                score = 0.1 + ((hash(chunk["content"]) % 100) / 1000.0)
                
        scored_chunks.append((chunk, round(score, 4)))
        
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return scored_chunks[:top_k]

def retrieve_production_code(query: str, chunks: List[Dict], top_k: int = 3, openai_api_key: str = None) -> List[Tuple[Dict, float]]:
    """
    Production retriever for code chunks using FAISS and OpenAI Embeddings.
    """
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain_core.documents import Document
    
    if not openai_api_key:
        raise ValueError("OpenAI API key is required in production mode.")
        
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    
    docs = []
    for c in chunks:
        doc = Document(
            page_content=c["content"],
            metadata={
                "id": c["id"], 
                "path": c["path"],
                "start_line": c["start_line"],
                "end_line": c["end_line"],
                "source": c["source"]
            }
        )
        docs.append(doc)
        
    db = FAISS.from_documents(docs, embeddings)
    results = db.similarity_search_with_score(query, k=top_k)
    
    retrieved = []
    for doc, distance in results:
        sim_score = 1.0 / (1.0 + distance)
        chunk_dict = {
            "id": doc.metadata["id"],
            "path": doc.metadata["path"],
            "content": doc.page_content,
            "start_line": doc.metadata["start_line"],
            "end_line": doc.metadata["end_line"],
            "source": doc.metadata["source"]
        }
        retrieved.append((chunk_dict, round(sim_score, 4)))
        
    return retrieved
