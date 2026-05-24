import time
import re
from typing import List, Dict

def synthesize_mock_response(query: str, retrieved_chunks: List[Dict], model_type: str) -> Dict:
    """
    Synthesizes a dynamic response from the retrieved chunks to simulate different LLMs offline.
    """
    # Extract relevant sentences containing query keywords from chunks
    query_words = [w.lower() for w in re.findall(r'\b\w{4,}\b', query)]
    if not query_words:
        query_words = ["rag", "retrieval", "chunk"]
        
    sentences = []
    chunk_influences = []
    
    for chunk in retrieved_chunks:
        # Split chunk into sentences
        chunk_sentences = re.split(r'(?<=[.!?])\s+', chunk["content"])
        matched_sentences = []
        
        for sentence in chunk_sentences:
            for word in query_words:
                if word in sentence.lower():
                    matched_sentences.append(sentence)
                    break
                    
        if matched_sentences:
            sentences.extend(matched_sentences[:2])
            # Higher matching means more influence
            chunk_influences.append({
                "chunk_id": chunk["id"],
                "influence": 0.4 + (len(matched_sentences) * 0.15),
                "reason": f"Contains matching terms: {', '.join(set(query_words).intersection(set(sentence.lower().split())))}"
            })
        else:
            chunk_influences.append({
                "chunk_id": chunk["id"],
                "influence": 0.05,
                "reason": "Weak semantic alignment with query keywords."
            })
            
    # Default sentences if none match
    if not sentences:
        sentences = [retrieved_chunks[0]["content"].split('.')[0] + "."] if retrieved_chunks else ["No matching context could be analyzed."]
        if retrieved_chunks:
            chunk_influences[0]["influence"] = 0.8
            chunk_influences[0]["reason"] = "First retrieved chunk used as fallback context."
            
    # Normalize influences
    total_influence = sum(ci["influence"] for ci in chunk_influences) or 1.0
    for ci in chunk_influences:
        ci["influence"] = round(ci["influence"] / total_influence, 2)
        
    combined_sentences = " ".join(sentences[:3])
    
    # 1. GPT-4 Style: Premium, structured, citation rich, high detail
    if model_type == "gpt":
        time_taken = 0.75 # simulated latency
        text = f"### RAG Debugger Analysis (GPT-4 Simulation)\n\n"
        text += f"Based on the retrieved context from the knowledge base, here is the compiled response:\n\n"
        
        # Structure the response dynamically
        text += f"1. **Core Concept**: {combined_sentences}\n"
        if len(retrieved_chunks) > 1:
            text += f"2. **Pipeline Integration**: {retrieved_chunks[1]['content'].split('.')[0]}.\n"
        
        # Add simulated citation markers
        text += f"\n*References: Grounded directly in context chunk tags: "
        refs = [f"[Chunk #{c['id']}]" for c in retrieved_chunks[:2]]
        text += ", ".join(refs) + "."
        
        quality = 95
        correctness = 98
        length = len(text)
        
    # 2. Local LLM Style: Fast, slightly shorter, less structured
    elif model_type == "local":
        time_taken = 0.35 # simulated latency
        text = f"Here is a summary of the retrieved document details regarding your query:\n\n"
        text += f"{combined_sentences.replace('RAG', 'Retrieval-Augmented Generation')}\n\n"
        text += "This answers the query using the local vector database records but with simpler phrasing."
        
        quality = 80
        correctness = 85
        length = len(text)
        
    # 3. Mock Model Style: Basic, short, fails to capture nuances
    else:
        time_taken = 0.12 # simulated latency
        # Simulate ignoring some context
        first_sentence = combined_sentences.split('.')[0]
        text = f"Mock Answer: {first_sentence}. This is a simple generated text."
        
        quality = 45
        correctness = 50
        length = len(text)
        
    return {
        "text": text,
        "latency": time_taken,
        "quality": quality,
        "correctness": correctness,
        "length": length,
        "influences": chunk_influences
    }

def call_production_llm(compiled_prompt: str, model_name: str, openai_api_key: str) -> Dict:
    """
    Calls the actual OpenAI Chat Completion endpoint.
    """
    from openai import OpenAI
    
    client = OpenAI(api_key=openai_api_key)
    start_time = time.time()
    
    # Map model name
    api_model = "gpt-4o-mini" if "gpt" in model_name.lower() else "gpt-3.5-turbo"
    
    # We parse system and user messages from compiled_prompt or split them
    lines = compiled_prompt.split("\n\n")
    system_text = "You are a helpful assistant."
    user_text = compiled_prompt
    
    if len(lines) >= 2 and lines[0].startswith("System:"):
        system_text = lines[0].replace("System:", "").strip()
        user_text = "\n\n".join(lines[1:]).replace("User:", "").strip()
        
    response = client.chat.completions.create(
        model=api_model,
        messages=[
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text}
        ],
        temperature=0.7
    )
    
    latency = round(time.time() - start_time, 2)
    output_text = response.choices[0].message.content
    
    # Heuristics for score estimation
    length = len(output_text)
    quality = 90 if length > 200 else 75
    correctness = 95
    
    return {
        "text": output_text,
        "latency": latency,
        "quality": quality,
        "correctness": correctness,
        "length": length,
        # Default influence score
        "influences": []
    }
