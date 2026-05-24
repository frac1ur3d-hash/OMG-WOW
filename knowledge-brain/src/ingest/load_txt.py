def load_text_content(file_path_or_bytes) -> str:
    """Reads raw string content from text file or bytes payload."""
    if hasattr(file_path_or_bytes, "read"):
        return file_path_or_bytes.read().decode("utf-8", errors="ignore")
        
    with open(file_path_or_bytes, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
