import os
from config import DOCS_PATH


def load_documents():
    """Load all .txt rule documents from the docs folder."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            professor_name = filename.replace(".txt", "").replace("_", " ").title()
            documents.append({
                "professor": professor_name,
                "filename": filename,
                "text": text,
            })
    print(f"Loaded {len(documents)} rule document(s): {[d['professor'] for d in documents]}")
    return documents


def chunk_document(text, professor_name):
    """
    Split a rule document into chunks ready for embedding.

    This function is already implemented — read through it and the inline
    comments before moving on. The decisions made here directly shape what
    retrieval returns in Milestones 2 and 3, so it's worth understanding
    before you build on top of it.

    Strategy: character-based sliding window with overlap.
      - chunk_size = 300 characters: long enough to carry the semantic
        meaning of a single rule, short enough to return targeted results
      - overlap = 50 characters: duplicates a small window of text at each
        boundary so a rule that spans two chunks can still be retrieved intact
      - min_length = 50 characters: filters out whitespace artifacts and
        very short fragments that add noise without useful semantic content

    Returns a list of dicts, each with:
      - "text"     : the chunk text (str)
      - "professor"     : the professor name, e.g. "Alden Jackson" (str)
      - "chunk_id" : a unique identifier, e.g. "alden_jackson_0", "alden_jackson_1" (str)
    """
    chunk_size = 300
    overlap = 50
    min_length = 50

    chunks = []
    prefix = professor_name.lower().replace(" ", "_")
    counter = 0

    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()

        if len(chunk_text) >= min_length:
            chunk_text = f"{professor_name} + {chunk_text}" 
            chunks.append({
                "text": chunk_text,
                "professor": prefix,
                "chunk_id": f"{prefix}_{counter}",
            })
            counter += 1

        # Advance by (chunk_size - overlap) so the next chunk shares
        # `overlap` characters with the tail of this one.
        start += chunk_size - overlap
    
    print(chunk for chunk in chunks)
    return chunks
