#!/usr/bin/env python3
"""Book Mirror — Extract and split a book into chapter files.

Usage:
  python3 extract.py book.pdf
  python3 extract.py book.epub
  python3 extract.py https://example.com/book.pdf

Outputs:
  raw/        — extracted text (pages or chunks)
  chapters/   — one .txt file per detected chapter
"""

import sys, os, re, json

OUTPUT_DIR = os.environ.get("BOOK_MIRROR_DIR", ".")


def extract_pdf(path):
    """Extract text from PDF using PyMuPDF."""
    import fitz
    doc = fitz.open(path)
    raw_dir = os.path.join(OUTPUT_DIR, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    full_text = []
    for i, page in enumerate(doc):
        text = page.get_text()
        full_text.append(text)
        with open(os.path.join(raw_dir, f"page-{i+1:04d}.txt"), "w") as f:
            f.write(text)
    
    # Also write full text for chapter splitting
    combined = "\n".join(full_text)
    full_path = os.path.join(raw_dir, "full-text.txt")
    with open(full_path, "w") as f:
        f.write(combined)
    
    print(f"Extracted {len(doc)} pages → {full_path}")
    return full_path


def extract_epub(path):
    """Extract text from EPUB."""
    from ebooklib import epub
    from bs4 import BeautifulSoup
    
    book = epub.read_epub(path)
    raw_dir = os.path.join(OUTPUT_DIR, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    chunks = []
    for i, item in enumerate(book.get_items_of_type(9)):  # ITEM_DOCUMENT
        content = item.get_content().decode("utf-8", errors="replace")
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        if text.strip():
            chunks.append(text)
            with open(os.path.join(raw_dir, f"chunk-{i+1:04d}.txt"), "w") as f:
                f.write(text)
    
    combined = "\n\n".join(chunks)
    full_path = os.path.join(raw_dir, "full-text.txt")
    with open(full_path, "w") as f:
        f.write(combined)
    
    print(f"Extracted {len(chunks)} chunks → {full_path}")
    return full_path


def split_chapters(full_text_path):
    """Split full text into chapters based on heading patterns."""
    with open(full_text_path, "r") as f:
        text = f.read()
    
    if not text.strip():
        print("ERROR: No text extracted. The PDF may be image-based (scanned). Try OCR first.")
        sys.exit(1)
    
    # Chapter heading patterns (most specific first)
    patterns = [
        r'(?m)^\s*(CHAPTER|Chapter|chapter)\s+[IVXLCDM]+\s*[:.]?\s*.*$',
        r'(?m)^\s*(CHAPTER|Chapter|chapter)\s+\d+\s*[:.]?\s*.*$',
        r'(?m)^\s*(CHAPTER|Chapter|chapter)\s+\w+[\w\s]*$',
        r'(?m)^\s*(PART|Part|part)\s+[IVXLCDM]+\s*[:.]?\s*.*$',
        r'(?m)^\s*(PART|Part|part)\s+\d+\s*[:.]?\s*.*$',
        r'(?m)^\s*(Section|SECTION)\s+\d+\s*[:.]?\s*.*$',
    ]
    
    # Find all chapter heading positions
    headings = []
    for pattern in patterns:
        for m in re.finditer(pattern, text):
            heading_text = m.group(0).strip()
            # Avoid duplicates at same position
            if not any(h[1] == m.start() for h in headings):
                headings.append((m.start(), heading_text))
    
    # Sort by position
    headings.sort(key=lambda x: x[0])
    
    chapters_dir = os.path.join(OUTPUT_DIR, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)
    
    if not headings:
        # No chapters found — split by word count (~5000 words each)
        print("No chapter headings found. Splitting into ~5000-word sections...")
        words = text.split()
        chunk_size = 5000
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            idx = i // chunk_size + 1
            safe_title = f"Section_{idx}"
            path = os.path.join(chapters_dir, f"{idx:02d}_{safe_title}.txt")
            with open(path, "w") as f:
                f.write(chunk)
            print(f"Section {idx}: {len(chunk.split())} words")
        return chapters_dir
    
    # Add prematter (everything before first chapter)
    prematter = text[:headings[0][0]].strip()
    chapters = []
    if prematter and len(prematter) > 100:
        chapters.append(("Preface_and_Front_Matter", prematter))
    
    # Extract chapter content
    for i, (pos, heading) in enumerate(headings):
        # Content from this heading to the next (or end)
        end = headings[i+1][0] if i+1 < len(headings) else len(text)
        content = text[pos:end].strip()
        
        # Clean heading for filename
        safe_heading = re.sub(r'[^\w\s-]', '', heading)[:60].strip().replace(' ', '_')
        if not safe_heading:
            safe_heading = f"Chapter_{i+1}"
        
        chapters.append((safe_heading, content))
    
    # Write chapter files
    for idx, (title, content) in enumerate(chapters):
        path = os.path.join(chapters_dir, f"{idx+1:02d}_{title}.txt")
        with open(path, "w") as f:
            f.write(content)
        word_count = len(content.split())
        print(f"Chapter {idx+1}: {title[:50].replace('_',' ')} ({word_count} words)")
    
    print(f"\nTotal chapters: {len(chapters)}")
    
    # Write manifest
    manifest = {
        "total_chapters": len(chapters),
        "chapters": [
            {"index": i+1, "title": t.replace('_', ' '), "words": len(c.split()), "file": f"{i+1:02d}_{t}.txt"}
            for i, (t, c) in enumerate(chapters)
        ]
    }
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    return chapters_dir


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract.py <book.pdf|book.epub|url>")
        sys.exit(1)
    
    source = sys.argv[1]
    
    # Download if URL
    if source.startswith("http"):
        import urllib.request
        print(f"Downloading {source}...")
        ext = ".pdf" if ".pdf" in source.lower() else ".epub"
        local = os.path.join(OUTPUT_DIR, f"downloaded{ext}")
        urllib.request.urlretrieve(source, local)
        source = local
        print(f"Downloaded → {source}")
    
    # Extract
    ext = os.path.splitext(source)[1].lower()
    if ext == ".pdf":
        full_path = extract_pdf(source)
    elif ext == ".epub":
        full_path = extract_epub(source)
    else:
        print(f"Unsupported format: {ext}. Use PDF or EPUB.")
        sys.exit(1)
    
    # Split into chapters
    chapters_dir = split_chapters(full_path)
    print(f"\nDone. Chapter files in: {chapters_dir}")


if __name__ == "__main__":
    main()
