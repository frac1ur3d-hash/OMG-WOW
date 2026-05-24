import time
from typing import List, Dict

def synthesize_copilot_answer(
    query: str, 
    retrieved_chunks: List[Dict], 
    mode: str, 
    is_production: bool = False,
    openai_api_key: str = None
) -> Dict:
    """
    Compiles codebase assistant answers.
    Modes: "Explain Mode", "Locate Mode", "Change Request (Diff)"
    """
    if is_production and openai_api_key:
        return call_production_copilot(query, retrieved_chunks, mode, openai_api_key)
        
    # --- SIMULATION MODE ---
    time.sleep(0.5) # Simulated generation latency
    
    # Identify key file paths retrieved
    files_ref = list(set([c["path"] for c in retrieved_chunks]))
    
    # 1. LOCATE MODE
    if mode == "Locate Mode":
        text = f"### 📍 Codebase Reference Finder\n\n"
        text += f"I have located {len(retrieved_chunks)} relevant code segments in your repository matching your query:\n\n"
        
        text += "| File Path | Line Range | Relevance |\n"
        text += "|---|---|---|\n"
        for idx, chunk in enumerate(retrieved_chunks):
            # approximate relevance score simulation
            rel = "High" if idx == 0 else "Medium"
            text += f"| `{chunk['path']}` | Lines {chunk['start_line']} - {chunk['end_line']} | {rel} |\n"
            
        text += "\n#### Code snippet from primary match:\n"
        text += f"```python\n# {retrieved_chunks[0]['path']}\n{retrieved_chunks[0]['content'][:300]}...\n```"
        
        diff_text = ""
        
    # 2. EXPLAIN MODE
    elif mode == "Explain Mode":
        primary_chunk = retrieved_chunks[0]
        text = f"### 💡 Code Explanation: `{primary_chunk['path']}`\n\n"
        text += f"Based on the codebase scan of `{primary_chunk['path']}` (Lines {primary_chunk['start_line']} to {primary_chunk['end_line']}), here is a logical analysis of the code:\n\n"
        
        # Look for function definitions to make it dynamic
        lines = primary_chunk["content"].splitlines()
        funcs = [l.strip() for l in lines if l.strip().startswith("def ") or l.strip().startswith("function ")]
        
        if funcs:
            text += "**Declared Interfaces:**\n"
            for f in funcs:
                text += f"- `{f}`\n"
            text += "\n"
            
        text += f"**Key Behavior:**\n"
        text += f"- **Logical Purpose**: The script handles backend routines relevant to your request. For instance:\n"
        text += f"  > *\"{lines[1] if len(lines) > 1 else primary_chunk['content'][:80]}...\"*\n"
        text += f"- **Database/Module imports**: Imports key utilities and libraries to execute database transactions or session token configurations.\n\n"
        text += f"**Context Grounding**: Retrieved from {len(files_ref)} reference files: " + ", ".join([f"`{f}`" for f in files_ref])
        
        diff_text = ""
        
    # 3. CHANGE REQUEST (DIFF) MODE
    else:
        primary_chunk = retrieved_chunks[0]
        text = f"### 🛠️ Propose Changes: `{primary_chunk['path']}`\n\n"
        text += f"I have drafted a code modification for `{primary_chunk['path']}` based on your query *\"{query}\"*.\n"
        text += "Below is the suggested git patch representation illustrating standard additions (+) and removals (-):\n"
        
        # Dynamically generate a cool patch based on code
        orig_lines = primary_chunk["content"].splitlines()[:10]
        orig_block = "\n".join(orig_lines)
        
        modified_lines = []
        for line in orig_lines:
            if "SECRET_KEY = " in line:
                modified_lines.append("- SECRET_KEY = \"super-secret-dev-key\"")
                modified_lines.append("+ import os")
                modified_lines.append("+ SECRET_KEY = os.getenv(\"JWT_SECRET_KEY\", \"default-fallback-key\")  # Loaded from env config")
            elif "import sqlite3" in line:
                modified_lines.append("- import sqlite3")
                modified_lines.append("+ import sqlite3")
                modified_lines.append("+ import logging  # Added tracing logs")
            else:
                modified_lines.append(f"  {line}")
                
        # If no edits matched, force a sample change request insertion
        if len(modified_lines) == len(orig_lines):
            modified_lines = [
                f"  {orig_lines[0]}",
                "+ # TODO: Add validation check for secure connections",
                f"+ print('[DEBUG] Invoked transaction in {primary_chunk['path']}')",
            ] + [f"  {l}" for l in orig_lines[1:5]]
            
        diff_text = "\n".join(modified_lines)
        
    return {
        "answer": text,
        "diff": diff_text,
        "citations": [f"{c['path']}:{c['start_line']}-{c['end_line']}" for c in retrieved_chunks]
    }

def call_production_copilot(query: str, retrieved_chunks: List[Dict], mode: str, openai_api_key: str) -> Dict:
    """
    Formulates a prompt for OpenAI to explain or propose diff changes based on code files.
    """
    from openai import OpenAI
    
    client = OpenAI(api_key=openai_api_key)
    
    # Formulate contextual prompt
    context_blocks = []
    for c in retrieved_chunks:
        context_blocks.append(f"--- FILE: {c['path']} (Lines {c['start_line']}-{c['end_line']}) ---\n{c['content']}")
    context_str = "\n\n".join(context_blocks)
    
    if mode == "Locate Mode":
        system_instructions = "You are a developer codebase RAG bot. Locate where in the code the user's query is resolved. Return a markdown table of files, line ranges, and a short sentence about why it was matched."
    elif mode == "Explain Mode":
        system_instructions = "You are an expert developer assistant. Explain the logic of the provided code chunks in relation to the query. Keep it technical, concise, and structured with bold highlights."
    else:
        system_instructions = (
            "You are a code patch generator. Based on the query, propose a code modification to the provided code context. "
            "Output your explanation, followed by a markdown code block containing a standard git unified diff showing the lines removed (-) and added (+). "
            "Format: Start line updates with '+' or '-' or ' ' for unmodified lines."
        )
        
    prompt = f"Codebase Context:\n{context_str}\n\nUser Question: {query}\n\nGenerate Response:"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
    answer_text = response.choices[0].message.content
    
    # Extract diff if it exists in the output
    diff_text = ""
    if mode == "Change Request (Diff)":
        # Pull out markdown code block if present
        import re
        matches = re.findall(r"```(?:diff|patch)?\n(.*?)```", answer_text, re.DOTALL)
        if matches:
            diff_text = matches[0]
            # Strip the code block from the explanation
            answer_text = re.sub(r"```(?:diff|patch)?\n.*?```", "", answer_text, flags=re.DOTALL)
            
    return {
        "answer": answer_text,
        "diff": diff_text,
        "citations": [f"{c['path']}:{c['start_line']}-{c['end_line']}" for c in retrieved_chunks]
    }
