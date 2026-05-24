from typing import List, Dict

def chunk_code_files(files_data: List[Dict[str, str]], lines_per_chunk: int = 25, line_overlap: int = 5) -> List[Dict]:
    """
    Chunks scanned file contents by lines to preserve code boundaries.
    Attaches metadata tracking relative path, start line, and end line.
    """
    code_chunks = []
    chunk_id = 1
    
    for file_info in files_data:
        path = file_info["path"]
        content = file_info["content"]
        
        lines = content.splitlines()
        num_lines = len(lines)
        
        if num_lines == 0:
            continue
            
        start = 0
        while start < num_lines:
            end = min(start + lines_per_chunk, num_lines)
            chunk_lines = lines[start:end]
            chunk_content = "\n".join(chunk_lines)
            
            code_chunks.append({
                "id": chunk_id,
                "path": path,
                "content": chunk_content,
                "start_line": start + 1,  # 1-indexed for code display
                "end_line": end,
                "source": f"{path}:{start+1}-{end}"
            })
            
            chunk_id += 1
            start += (lines_per_chunk - line_overlap)
            
            # Break if overlap equals or exceeds chunk size to prevent infinite loop
            if lines_per_chunk <= line_overlap:
                break
                
    return code_chunks
