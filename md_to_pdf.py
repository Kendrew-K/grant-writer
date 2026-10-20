#!/usr/bin/env python
"""Convert a grant narrative, budget or support letter from Markdown to PDF via headless Chrome.
Usage: python md_to_pdf.py applications/<id>/narrative.md
Prints the page count, because most funders cap narrative length in pages.
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import markdown

# Any Chromium build works. Set CHROME_PATH if yours is not on PATH or at one
# of the usual install locations.
CHROME_CANDIDATES = [
    os.environ.get("CHROME_PATH"),
    "google-chrome", "chromium", "chromium-browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

# Plain document style: funders print and score these, so readability beats design.
# 12pt serif with 1in margins is what most guidelines ask for when they specify anything.
CSS = """
@page { size: letter; margin: 1in; }
body { font-family: 'Times New Roman', Times, serif; font-size: 12pt; line-height: 1.35; color: #000; }
h1 { font-size: 16pt; margin: 0 0 10px; }
h2 { font-size: 13pt; margin: 16px 0 6px; }
h3 { font-size: 12pt; margin: 12px 0 4px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; }
th, td { border: 1px solid #000; padding: 4px 6px; text-align: left; }
td:last-child, th:last-child { text-align: right; }
a { color: #000; }
"""


def find_chrome():
    for candidate in CHROME_CANDIDATES:
        if candidate and (os.path.isfile(candidate) or shutil.which(candidate)):
            return candidate
    raise SystemExit("No Chrome/Chromium found. Install one or set CHROME_PATH to its executable.")


def main(md_path):
    md_path = pathlib.Path(md_path).resolve()
    body = markdown.markdown(md_path.read_text(encoding="utf-8"), extensions=["tables"])
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(html)
    pdf_path = md_path.with_suffix(".pdf")
    try:
        subprocess.run([find_chrome(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf_path}", "file:///" + tmp.name.replace(os.sep, "/")],
                       check=True, capture_output=True)
    finally:
        os.unlink(tmp.name)
    pages = re.findall(rb"/Count (\d+)", pdf_path.read_bytes())
    print(f"Wrote {pdf_path} ({max(map(int, pages)) if pages else '?'} pages)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python md_to_pdf.py <file>.md")
    main(sys.argv[1])
