def load_pdf_content(file_path_or_bytes) -> str:
    """Reads PDF files and extracts text pages. Falls back gracefully on exceptions."""
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path_or_bytes)
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        return "\n".join(text_parts)
    except Exception as e:
        return f"Error parsing PDF payload: {str(e)}. Ensure 'pypdf' package is properly installed."
