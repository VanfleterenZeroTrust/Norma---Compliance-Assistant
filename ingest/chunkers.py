import fitz

def pdf_to_chunks(path: str, max_chars: int = 1500):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    chunks = []
    for i in range(0, len(text), max_chars):
        chunks.append({"text": text[i:i+max_chars]})
    return chunks
