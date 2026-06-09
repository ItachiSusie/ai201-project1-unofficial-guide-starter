import os
import re

from config import DOCS_PATH


def load_documents():
    """Load all professor review .txt files from the documents folder.

    Returns a list of dicts, each with:
      - "professor" : the professor's name, derived from the filename
                      (e.g. "kaan_onarlioglu.txt" -> "Kaan Onarlioglu") (str)
      - "filename"  : the source filename, e.g. "kaan_onarlioglu.txt" (str)
      - "text"      : the full raw file text (str)
    """
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(DOCS_PATH, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        documents.append({
            "professor": filename.replace(".txt", "").replace("_", " ").title(),
            "filename": filename,
            "text": text,
        })
    print(f"Loaded {len(documents)} document(s): {[d['professor'] for d in documents]}")
    return documents


def clean_text(text):
    """Light cleaning for already-plain-text files.

    The source files are hand-curated plain text (no HTML, nav bars, or ads),
    so cleaning is intentionally minimal:
      - normalize line endings,
      - strip trailing whitespace on each line,
      - drop the standalone "STUDENT REVIEWS" section header (a structural label
        with no content; left in, it would sit at the end of the summary chunk
        and add a misleading "review" signal there),
      - collapse 3+ consecutive blank lines into a single blank line,
      - strip leading/trailing whitespace for the whole document.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"(?m)^STUDENT REVIEWS[ \t]*\n?", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_document(text, professor):
    """Split one professor file into chunks ready for embedding.

    Strategy: structure-based split on the "[Review N]" markers (review-based
    chunking, as specified in planning.md). No fixed character window, no
    overlap, because each review is short and self-contained.
      - chunk_0            : the header + SUMMARY block (everything before the
                             first review). Holds the site-wide rating.
      - chunk_1 .. chunk_n : one student review each, kept intact.

    Returns a list of dicts, each with:
      - "text"     : the chunk text (str)
      - "professor": the professor's name (str)
      - "chunk_id" : a unique id, e.g. "kaan_onarlioglu_0" (str)
    """
    prefix = professor.lower().replace(" ", "_")

    # The lookahead splits right before each "[Review N]" marker, so every
    # marker stays attached to the review text that follows it.
    pieces = re.split(r"(?=\[Review \d+\])", text)

    chunks = []
    counter = 0
    for piece in pieces:
        piece = piece.strip()
        if not piece:  # never emit empty/whitespace-only chunks
            continue
        # Prefix professor name so it's part of the embedded text.
        # Without this, review chunks contain no professor name, and queries
        # like "Which courses has Jonathan Bell taught?" match the wrong professor.
        text_with_prefix = f"PROFESSOR: {professor}\n{piece}" if piece.startswith("[Review") else piece
        chunks.append({
            "text": text_with_prefix,
            "professor": professor,
            "chunk_id": f"{prefix}_{counter}",
        })
        counter += 1
    return chunks


def build_all_chunks():
    """Load, clean, and chunk every document. Returns one flat list of chunks."""
    all_chunks = []
    for doc in load_documents():
        cleaned = clean_text(doc["text"])
        all_chunks.extend(chunk_document(cleaned, doc["professor"]))
    return all_chunks


if __name__ == "__main__":
    chunks = build_all_chunks()

    # 1. Total count (expect 91 reviews + 10 summary chunks = 101).
    print(f"\nTotal chunks: {len(chunks)}")

    # 2. Per-professor counts.
    print("\nChunks per professor:")
    counts = {}
    for c in chunks:
        counts[c["professor"]] = counts.get(c["professor"], 0) + 1
    for professor, n in counts.items():
        print(f"  {professor:<20} {n}")

    # 3. Sanity check on Kaan Onarlioglu: 1 summary + 10 reviews = 11 chunks.
    kaan = [c for c in chunks if c["professor"] == "Kaan Onarlioglu"]
    kaan_ids = [c["chunk_id"] for c in kaan]
    expected_ids = [f"kaan_onarlioglu_{i}" for i in range(11)]
    assert kaan_ids == expected_ids, f"Kaan chunk ids unexpected: {kaan_ids}"
    assert kaan[0]["text"].startswith("PROFESSOR:"), "chunk_0 should be the summary block"
    assert all(c["text"].startswith("[Review") for c in kaan[1:]), \
        "chunks 1..n should each start with a [Review N] marker"
    print("\nKaan Onarlioglu check passed: 11 chunks "
          "(chunk_0 summary + chunk_1..10 reviews).")

    # 4. Print 5 representative chunks to eyeball against the checklist.
    samples = [kaan[0], kaan[1], kaan[5], chunks[0], chunks[-1]]
    print("\n" + "=" * 70)
    print("5 SAMPLE CHUNKS")
    print("=" * 70)
    for c in samples:
        print(f"\n[{c['chunk_id']}]  professor={c['professor']}  "
              f"length={len(c['text'])} chars")
        print("-" * 70)
        print(c["text"])