from typing import List, Dict

def chunk_document_contents(
    text: str, 
    source_name: str, 
    collection_name: str = "General", 
    chunk_size: int = 400, 
    chunk_overlap: int = 50
) -> List[Dict]:
    """
    Chunks ingested documents and attaches source details and tags for granular indexing.
    """
    chunks = []
    text_len = len(text)
    
    if text_len == 0 or chunk_size <= 0:
        return chunks
        
    start = 0
    chunk_id = 1
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        content = text[start:end].strip()
        
        if content:
            chunks.append({
                "id": chunk_id,
                "content": content,
                "source": source_name,
                "collection": collection_name,
                "length": len(content)
            })
            chunk_id += 1
            
        start += (chunk_size - chunk_overlap)
        
        # Break out if size <= overlap to prevent infinite loops
        if chunk_size <= chunk_overlap:
            break
            
    return chunks
