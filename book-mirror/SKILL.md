---
name: book-mirror
description: Personalized chapter-by-chapter book analysis. Left column preserves the author's content; right column mirrors it to the reader's actual life using their real words, situations, people, and patterns from memory.
version: 1.0.0
category: productivity
tools:
  - terminal
  - file
  - browser
  - search
---

# Book Mirror

Takes any book + everything Hermes knows about the reader → produces a personalized chapter-by-chapter analysis with a two-column format.

Concept by Garry Tan (President & CEO of Y Combinator): https://x.com/garrytan/status/2049059060427952164

## What It Produces

For each chapter, a two-column table:

| What the Author Says | How This Applies to You |
|---|---|
| Detailed preservation of stories, stats, quotes, frameworks — detailed enough you could skip the book | Name real people, dates, situations from the reader's life. Read like a therapist who knows them writing notes in the margins. |

## The Pipeline

### Step 1: Get the Book

Accept the book in any of these formats:
- **PDF file** — local path provided by user
- **EPUB file** — local path provided by user
- **URL** — download if accessible
- **Title only** — search for a free/public domain version (Project Gutenberg, Archive.org)

Extraction commands:

**PDF:**
```bash
python3 << 'EOF'
import fitz  # pymupdf
doc = fitz.open("book.pdf")
for i, page in enumerate(doc):
    text = page.get_text()
    with open(f"raw/page-{i+1:04d}.txt", "w") as f:
        f.write(text)
print(f"Extracted {len(doc)} pages")
EOF
```

**EPUB:**
```bash
python3 << 'EOF'
from ebooklib import epub
book = epub.read_epub("book.epub")
for i, item in enumerate(book.get_items_of_type(9)):  # ITEM_DOCUMENT
    content = item.get_content().decode('utf-8', errors='replace')
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    with open(f"raw/chunk-{i+1:04d}.txt", "w") as f:
        f.write(text)
print(f"Extracted {i+1} chunks")
EOF
```

### Step 2: Split into Chapters

Read the raw text and split by chapter markers. Common patterns:
- "Chapter 1", "CHAPTER 1", "Chapter One", "1.", "Part One"
- Numbered sections
- Explicit markers like "***" or "---"

Use this script:
```bash
python3 << 'EOF'
import re, os

with open("raw/full-text.txt", "r") as f:
    text = f.read()

# Common chapter heading patterns (ordered by specificity)
patterns = [
    r'^\s*(CHAPTER|Chapter|chapter)\s+[IVXLCDM\d]+\s*.*$',
    r'^\s*(CHAPTER|Chapter|chapter)\s+\w+\s*.*$',
    r'^\s*(PART|Part|part)\s+[IVXLCDM\d]+\s*.*$',
    r'^\s*\d+\.\s+[A-Z].*$',  # "1. Title"
    r'^\s*---+\s*$',
    r'^\s*\*\*\*\s*$',
]

combined = '|'.join(f'({p})' for p in patterns)
splits = re.split(f'(?m){combined}', text)

# Reassemble: splits[0] is pre-chapter content (title page, copyright, etc.)
# Then alternating: chapter heading, chapter body
chapters = []
prematter = splits[0].strip() if splits else ""
if prematter:
    chapters.append(("Preface / Front Matter", prematter))

i = 1
while i < len(splits):
    # Collect the heading parts (non-None captures) and the body
    heading_parts = []
    while i < len(splits) and splits[i] is not None and len(splits[i].strip()) < 100:
        if splits[i] and splits[i].strip():
            heading_parts.append(splits[i].strip())
        i += 1
    heading = " ".join(heading_parts) if heading_parts else f"Section {len(chapters)+1}"
    
    body_parts = []
    while i < len(splits) and (splits[i] is None or len(splits[i].strip()) >= 100 or not splits[i]):
        if splits[i] and splits[i].strip():
            body_parts.append(splits[i].strip())
        i += 1
    body = "\n\n".join(body_parts)
    
    if body:
        chapters.append((heading, body))

os.makedirs("chapters", exist_ok=True)
for idx, (title, content) in enumerate(chapters):
    safe_title = re.sub(r'[^\w\s-]', '', title)[:60].strip().replace(' ', '_')
    with open(f"chapters/{idx+1:02d}_{safe_title}.txt", "w") as f:
        f.write(content)
    print(f"Chapter {idx+1}: {title[:60]}... ({len(content)} chars)")

print(f"\nTotal chapters: {len(chapters)}")
EOF
```

If the regex split fails (messy formatting), fall back to:
1. Fixed-size chunking (every ~5000 words with overlap)
2. Manual split — ask the user where chapters begin

### Step 3: Build Context Pack

This is the most critical step. The right column is only as good as the context.

**Gather from memory system:**
1. `memory` tool — user profile, preferences, personal details
2. `session_search` — past conversations, recurring themes, emotional patterns
3. `lcm_grep` — specific quotes, situations, people mentioned in recent sessions
4. Direct questions to the user if memory is thin

**Context pack structure:**
```
READER CONTEXT PACK
====================
Name: [from memory]
Role/Occupation: [from memory]
Key relationships: [names, dynamics]
Recurring emotional patterns: [from session history]
Active projects/stressors: [current]
Therapy/self-improvement work: [if known]
Core values and conflicts: [inferred from conversations]
Specific quotes in their own words: [extracted from session history]
Recent life events: [dates, specifics]
```

**If context is thin:**
- Ask the user: "To make this mirror truly personal, tell me about: your main relationships, what you're struggling with right now, your core values, and any patterns you keep seeing in your life"
- A book-mirror for a stranger is just a book summary. The more context, the better.

### Step 4: Per-Chapter Analysis

For each chapter, read the full chapter text and produce the two-column analysis.

**Process each chapter sequentially (not parallel — context builds across chapters):**

1. Read the chapter text from `chapters/XX_title.txt`
2. Generate the analysis with both columns
3. Write to `analysis/XX_title.md`
4. Build a running thread — reference insights from earlier chapters when they connect

**Left column guidelines:**
- Preserve the actual stories, stats, quotes, and frameworks
- Be detailed enough the reader could skip the original book
- Include specific numbers, names of studies, direct quotes
- Keep the author's voice — if they're casual, stay casual; if academic, stay academic
- Don't summarize into vagueness — the point is you DON'T need the book after reading this

**Right column guidelines:**
- Mirror each concept to the reader's specific life
- Use their actual words (from the context pack) when possible
- Name real people from their life (not "a family member" — "your brother", "Maria")
- Reference real dates, real situations, real decisions they made
- Read like a therapist who knows them writing notes in the margins
- If a chapter genuinely doesn't apply, say so: "This chapter covers corporate governance structures. Unless you're dealing with board dynamics at Decrypt, this won't land directly."
- NEVER force connections — a weak mirror is worse than an honest "this doesn't apply to you"
- NO generic advice ("consider reflecting on...", "you might want to think about...")
- ONLY specific mirrors ("This is exactly what happened when you...")

**Format per chapter:**

```markdown
# Chapter N: [Title]

## Key Ideas
[2-3 sentence summary of the chapter's core argument]

| What the Author Says | How This Applies to You |
|---|---|
| [Author's specific content] | [Your specific life mirror] |
```

### Step 5: Fact-Check Personal Claims

After generating all chapters, verify every personal claim in the right column:
1. Cross-reference against the context pack
2. Cross-reference against session history
3. Flag anything you inferred but can't verify: mark with [unverified]
4. Correct anything that contradicts known facts

Run this as a separate pass — read all analysis files and check.

### Step 6: Generate Output

**HTML Report (preferred — best for reading):**

Use the template at `templates/book-mirror-report.html`. It produces a clean two-column layout with:
- Dark background, serif fonts for readability
- Sticky chapter navigation sidebar
- Print-ready CSS (switches to white background for PDF export)
- Responsive — readable on phone, tablet, desktop

Customize per book:
- Title and author in the header
- Reader's name in the subtitle
- Color accent: `--accent` variable (default #4a9eff blue)

Save to: `~/Desktop/Hermes/book-mirror-{book-title}.html`

**PDF (optional):**
```bash
# Open in browser, then Cmd+P → Save as PDF
open ~/Desktop/Hermes/book-mirror-{book-title}.html
```

Or use weasyprint if installed:
```bash
python3 -m weasyprint book-mirror.html book-mirror.pdf
```

**Markdown (fallback):**
Concatenate all chapter analysis files into a single markdown document.
Save to: `~/Desktop/Hermes/book-mirror-{book-title}.md`

## Quality Bar

The output must pass these checks:

1. **Left column completeness**: Could someone who hasn't read the book understand the author's argument, stories, and evidence from this column alone? If not, add more detail.

2. **Right column specificity**: Does every right-column entry reference something specific and verifiable about the reader's life? Generic observations ("you value relationships") fail. Specific ones ("this mirrors how you kept editing that Frontierbeat piece at 2am because finishing imperfectly felt worse than not finishing at all") pass.

3. **No forced connections**: If a chapter about corporate finance doesn't map to a freelance journalist's life, say so. Don't stretch.

4. **No generic advice**: Ban these phrases and their equivalents:
   - "Consider reflecting on..."
   - "You might want to think about..."
   - "This could be an opportunity to..."
   - "It's worth noting that..."
   Replace with specific observations or nothing.

5. **Voice matching**: The right column should sound like someone who has known the reader for years, not a self-help book.

## Optimization Notes

### For Large Books (20+ chapters)
- Process chapters in batches of 3-5
- After each batch, update the running thread (key patterns that connect across chapters)
- The last 2-3 chapters will have the richest right column because they benefit from the full thread

### For Thin Context
- Before starting analysis, explicitly tell the user what you know and what you're missing
- Give them the option to provide more context before proceeding
- A thin-context mirror is still useful — just be honest about its limitations in the intro

### Chapter Size Handling
- Short chapters (<1000 words): combine with adjacent chapter if thematically linked
- Long chapters (>10000 words): split into thematic sections within the chapter
- Aim for 2000-6000 words of raw text per analysis unit

## Pitfalls

- **PDF extraction can be garbage** — scanned PDFs (image-based) need OCR first. Check `pymupdf` output quality before splitting chapters. If text is garbled, try `ocrmypdf` first.
- **EPUB encoding issues** — always use `errors='replace'` when decoding. Some EPUBs have mixed encodings.
- **Chapter detection is unreliable** — regex patterns miss weird formatting. Always verify the split before analysis. Show the user the chapter list and ask "does this look right?"
- **Context pack is the bottleneck** — a 5-minute conversation about the user's life produces better mirrors than 30 minutes of analysis time. Invest in context gathering.
- **Right column drift** — as you process many chapters, the right column can become repetitive. Track which life events/patterns you've already used. Don't keep referencing the same story.
- **Hermes memory may be thin for new users** — if there's not enough context, the mirror degrades to a summary. Be upfront about this.
- **Very long books may hit token limits** — for 30+ chapter books, process in batches and write intermediate results to files. Don't try to hold all chapters in context at once.
- **ReportLab for PDFs is complex** — prefer HTML output. The browser's Print-to-PDF produces better results with less code.
- **Some books are purely technical** (textbooks, manuals) — the right column will naturally be thin. Don't force personal connections to a chapter about differential equations.

## Quick Reference

| Command | Action |
|---|---|
| `book mirror [path/to/book.pdf]` | Full pipeline on a PDF |
| `book mirror [path/to/book.epub]` | Full pipeline on an EPUB |
| `book mirror [URL]` | Download and process |
| `book mirror "[Title]" by [Author]` | Search and process (public domain) |

## Acknowledgment

Concept by **Garry Tan**, President & CEO of Y Combinator.
Source: https://x.com/garrytan/status/2049059060427952164
