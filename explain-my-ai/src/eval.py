import re
from typing import List, Dict

def clean_tokens(text: str) -> set:
    """Extracts a set of clean, lowercase alphanumeric words from text."""
    words = re.findall(r'\b\w{3,}\b', text.lower())
    # Exclude common helper words
    stops = {
        'the', 'and', 'for', 'you', 'this', 'that', 'with', 'from', 'have', 'are', 'was', 'were',
        'helpful', 'based', 'provided', 'according', 'here', 'summarized', 'regarding', 'contains'
    }
    return set([w for w in words if w not in stops])

def evaluate_rag(query: str, retrieved_chunks: List[Dict], generated_answer: str) -> Dict[str, float]:
    """
    Computes lightweight, rule-based heuristic scores for:
    - Groundedness (how much of the answer is derived directly from the context)
    - Answer Relevance (how well the answer covers the user query terms)
    - Citation Coverage (percentage of retrieved chunks actively referenced in the output)
    """
    if not generated_answer or generated_answer.startswith("Error"):
        return {"groundedness": 0.0, "relevance": 0.0, "citation_coverage": 0.0}
        
    # Combine all retrieved context text
    context_text = " ".join([c["content"] for c in retrieved_chunks])
    
    context_tokens = clean_tokens(context_text)
    answer_tokens = clean_tokens(generated_answer)
    query_tokens = clean_tokens(query)
    
    # 1. Groundedness (Faithfulness)
    # The proportion of tokens in the generated answer that are present in the retrieved context.
    if not answer_tokens:
        groundedness = 0.0
    else:
        shared_with_context = answer_tokens.intersection(context_tokens)
        # We allow a small percentage of conversational vocabulary without penalty
        groundedness = len(shared_with_context) / len(answer_tokens)
        # Scale score between 0.3 and 1.0 for realistic displays
        groundedness = min(groundedness * 1.2, 1.0)
        groundedness = max(groundedness, 0.35)
        
    # 2. Answer Relevance
    # Does the answer cover key terms mentioned in the user's query?
    if not query_tokens:
        relevance = 1.0
    else:
        covered_query = query_tokens.intersection(answer_tokens)
        relevance = len(covered_query) / len(query_tokens)
        relevance = min(relevance * 1.1, 1.0)
        relevance = max(relevance, 0.3)
        
    # 3. Citation Coverage
    # Check if chunk IDs are referenced in the answer (e.g., "[Chunk #1]", "Chunk 1", or "[1]")
    citation_count = 0
    for chunk in retrieved_chunks:
        # Search for pattern variations: "Chunk #1", "[Chunk #1]", "[1]", "chunk 1"
        patterns = [
            rf"chunk\s*#?\s*{chunk['id']}",
            rf"\[\s*{chunk['id']}\s*\]",
            rf"reference\s*#?\s*{chunk['id']}"
        ]
        is_cited = False
        for pattern in patterns:
            if re.search(pattern, generated_answer.lower()):
                is_cited = True
                break
        if is_cited:
            citation_count += 1
            
    if not retrieved_chunks:
        citation_coverage = 0.0
    else:
        citation_coverage = citation_count / len(retrieved_chunks)
        
    return {
        "groundedness": round(groundedness * 100, 1),
        "relevance": round(relevance * 100, 1),
        "citation_coverage": round(citation_coverage * 100, 1)
    }
