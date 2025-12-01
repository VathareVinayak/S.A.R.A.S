from typing import Dict, Any

def extract_text_or_fail(file_bytes: bytes) -> Dict[str, Any]:
    try:
        import fitz  # PyMuPDF
    except Exception:
        return {
            "error": "pymupdf_missing",
            "message": "PyMuPDF (fitz) is not installed. Install: pip install pymupdf"
        }

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        return {
            "error": "pdf_open_failed",
            "message": f"Failed to open PDF: {str(e)}"
        }

    full_text = ""
    pages = []

    try:
        for i, page in enumerate(doc):
            text = page.get_text()
            pages.append({"page": i + 1, "text": text})
            full_text += text + "\n"
    except Exception as e:
        return {
            "error": "pdf_read_failed",
            "message": f"Error reading PDF: {str(e)}"
        }

    if not full_text.strip():
        return {
            "error": "pdf_empty",
            "message": "PDF extracted but text content is empty."
        }

    return {
        "error": None,
        "text": full_text,
        "pages": pages
    }
