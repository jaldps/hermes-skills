#!/usr/bin/env python3
"""Book Mirror — Generate the final HTML report from chapter analysis files.

Usage:
  python3 generate-report.py <book_title> <book_author> <reader_name> [analysis_dir]

Reads markdown analysis files from analysis_dir (default: ./analysis)
and generates a complete HTML report using the template.
"""

import sys, os, re, json
from datetime import datetime

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "templates", "book-mirror-report.html")


def parse_markdown_table(text):
    """Parse a markdown table into list of (left, right) tuples."""
    rows = []
    lines = text.strip().split("\n")
    in_table = False
    for line in lines:
        if "|" in line and "---" not in line:
            cells = [c.strip() for c in line.split("|")[1:-1]]  # skip empty first/last
            if len(cells) >= 2:
                # Skip header row
                if cells[0] == "What the Author Says":
                    continue
                rows.append((cells[0], cells[1]))
                in_table = True
    return rows


def parse_chapter_file(filepath):
    """Parse a chapter analysis markdown file into structured data."""
    with open(filepath, "r") as f:
        content = f.read()
    
    chapter = {"file": os.path.basename(filepath)}
    
    # Extract chapter number and title
    title_match = re.search(r'^#\s+Chapter\s+(\d+)[.:]\s*(.+)$', content, re.MULTILINE)
    if title_match:
        chapter["num"] = int(title_match.group(1))
        chapter["title"] = title_match.group(2).strip()
    else:
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            chapter["num"] = 0
            chapter["title"] = title_match.group(1).strip()
        else:
            chapter["num"] = 0
            chapter["title"] = os.path.basename(filepath)
    
    # Extract key ideas
    ideas_match = re.search(r'##\s+Key\s+Ideas\s*\n(.+?)(?=\n##|\n\||$)', content, re.DOTALL)
    if ideas_match:
        chapter["key_ideas"] = ideas_match.group(1).strip()
    else:
        chapter["key_ideas"] = ""
    
    # Extract table rows
    chapter["rows"] = parse_markdown_table(content)
    
    # Extract non-applicable notice
    not_applicable = re.search(r'\*\*This chapter.*?\*\*', content, re.DOTALL)
    chapter["not_applicable"] = not_applicable.group(0) if not_applicable else None
    
    return chapter


def markdown_to_html(md_text):
    """Simple markdown to HTML conversion for table cells."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', md_text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Blockquote
    text = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    # Line breaks (double newline = paragraph)
    text = re.sub(r'\n\n+', '</p><p>', text)
    text = f"<p>{text}</p>"
    # Clean up empty paragraphs
    text = re.sub(r'<p>\s*</p>', '', text)
    return text


def generate_report(book_title, book_author, reader_name, analysis_dir):
    """Generate the full HTML report."""
    
    # Read template
    with open(TEMPLATE_PATH, "r") as f:
        template = f.read()
    
    # Parse all chapter files
    chapters = []
    for fname in sorted(os.listdir(analysis_dir)):
        if fname.endswith(".md"):
            filepath = os.path.join(analysis_dir, fname)
            chapter = parse_chapter_file(filepath)
            chapters.append(chapter)
    
    # Sort by chapter number
    chapters.sort(key=lambda c: c["num"])
    
    # Build nav links
    nav_links = ""
    for ch in chapters:
        nav_links += f'<a href="#ch-{ch["num"]}">Ch {ch["num"]}: {ch["title"][:30]}</a>\n      '
    
    # Build chapter HTML
    chapters_html = ""
    for ch in chapters:
        rows_html = ""
        if ch.get("not_applicable"):
            rows_html = f'<tr><td colspan="2" class="not-applicable">{ch["not_applicable"]}</td></tr>'
        else:
            for left, right in ch.get("rows", []):
                left_html = markdown_to_html(left)
                right_html = markdown_to_html(right)
                rows_html += f"""
        <tr>
          <td>{left_html}</td>
          <td>{right_html}</td>
        </tr>"""
        
        chapter_html = f"""
<div class="chapter" id="ch-{ch['num']}">
  <div class="chapter-title">
    <span class="num">Chapter {ch['num']}</span>
    {ch['title']}
  </div>
  <div class="key-ideas">{ch.get('key_ideas', '')}</div>
  <table class="mirror-table">
    <thead>
      <tr>
        <th>What the Author Says</th>
        <th>How This Applies to You</th>
      </tr>
    </thead>
    <tbody>{rows_html}
    </tbody>
  </table>
</div>"""
        chapters_html += chapter_html
    
    # Fill template
    html = template.replace("{{BOOK_TITLE}}", book_title)
    html = html.replace("{{BOOK_AUTHOR}}", book_author)
    html = html.replace("{{READER_NAME}}", reader_name)
    html = html.replace("{{DATE}}", datetime.now().strftime("%B %d, %Y"))
    html = html.replace("{{NAV_LINKS}}", nav_links)
    
    # Replace the sample chapter block with all chapters
    # Find the chapter template block and replace everything from first chapter div to closing body
    start_marker = '<!-- CHAPTERS'
    end_marker = '</body>'
    start_idx = html.find(start_marker)
    if start_idx == -1:
        # Fallback: replace the sample chapter div
        sample_start = html.find('<div class="chapter"')
        sample_end = html.find('</body>')
        if sample_start != -1 and sample_end != -1:
            html = html[:sample_start] + chapters_html + "\n" + html[sample_end:]
    else:
        end_idx = html.find(end_marker, start_idx)
        html = html[:start_idx] + chapters_html + "\n" + html[end_idx:]
    
    return html


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 generate-report.py <book_title> <book_author> <reader_name> [analysis_dir]")
        sys.exit(1)
    
    book_title = sys.argv[1]
    book_author = sys.argv[2]
    reader_name = sys.argv[3]
    analysis_dir = sys.argv[4] if len(sys.argv) > 4 else "./analysis"
    
    html = generate_report(book_title, book_author, reader_name, analysis_dir)
    
    # Save
    output_dir = os.path.expanduser("~/Desktop/Hermes")
    os.makedirs(output_dir, exist_ok=True)
    safe_title = re.sub(r'[^\w\s-]', '', book_title)[:40].strip().replace(' ', '-').lower()
    output_path = os.path.join(output_dir, f"book-mirror-{safe_title}.html")
    
    with open(output_path, "w") as f:
        f.write(html)
    
    print(f"Report saved to: {output_path}")
    print(f"Open with: open {output_path}")


if __name__ == "__main__":
    main()
