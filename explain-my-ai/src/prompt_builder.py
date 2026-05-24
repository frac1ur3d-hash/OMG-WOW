from typing import List, Dict

def compile_rag_prompt(system_instruction: str, query: str, retrieved_chunks: List[Dict]) -> Dict[str, str]:
    """
    Compiles individual prompt components into a single formatted payload.
    Returns a dictionary showing:
    - system_prompt
    - user_input
    - final_compiled_prompt
    """
    # Build context block
    context_blocks = []
    for c in retrieved_chunks:
        context_blocks.append(f"--- CHUNK ID: {c['id']} ({c['source']}) ---\n{c['content']}")
        
    context_str = "\n\n".join(context_blocks)
    
    # Construct final compiled user prompt
    compiled_user_prompt = f"Context files:\n{context_str}\n\nUser Query: {query}\n\nAnswer:"
    
    return {
        "system_prompt": system_instruction,
        "user_input": query,
        "final_compiled_prompt": f"System:\n{system_instruction}\n\nUser:\n{compiled_user_prompt}"
    }
