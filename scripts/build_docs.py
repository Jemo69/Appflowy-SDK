#!/usr/bin/env python3
"""Build a static HTML documentation site from markdown files in docs/.

Usage:
    python scripts/build_docs.py [--output site/] [--docs docs/]

This script parses all markdown files in the docs/ directory and generates
a static HTML site with navigation, syntax highlighting, and responsive design.

No external dependencies required - uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Markdown-to-HTML converter (stdlib only)
# ---------------------------------------------------------------------------


class MarkdownConverter:
    """Converts GitHub-flavored Markdown to HTML without external dependencies."""

    def __init__(self) -> None:
        self._code_block_re = re.compile(r"^```(\w*)\s*$", re.MULTILINE)
        self._inline_code_re = re.compile(r"`([^`]+)`")
        self._bold_re = re.compile(r"\*\*(.+?)\*\*")
        self._italic_re = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
        self._link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        self._image_re = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
        self._header_re = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        self._hr_re = re.compile(r"^(---|\*\*\*|___)\s*$", re.MULTILINE)
        self._ul_re = re.compile(r"^(\s*)[-*+]\s+(.+)$", re.MULTILINE)
        self._ol_re = re.compile(r"^(\s*)\d+\.\s+(.+)$", re.MULTILINE)
        self._blockquote_re = re.compile(r"^>\s*(.*)$", re.MULTILINE)

    def convert(self, md: str) -> str:
        """Convert markdown string to HTML."""
        # Normalize line endings
        md = md.replace("\r\n", "\n").replace("\r", "\n")

        # Extract fenced code blocks first (protect from other transforms)
        code_blocks: list[str] = []

        def _save_code_block(match: re.Match) -> str:
            lang = match.group(1)
            code = match.group(2)
            escaped = html.escape(code)
            idx = len(code_blocks)
            if lang:
                code_blocks.append(
                    f'<pre><code class="language-{html.escape(lang)}">{escaped}</code></pre>'
                )
            else:
                code_blocks.append(f"<pre><code>{escaped}</code></pre>")
            return f"\x00CODEBLOCK{idx}\x00"

        md = re.sub(
            r"^```(\w*)\s*\n(.*?)^```\s*$",
            _save_code_block,
            md,
            flags=re.MULTILINE | re.DOTALL,
        )

        # Process block-level elements
        lines = md.split("\n")
        html_parts: list[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Restore code blocks
            if "\x00CODEBLOCK" in line:
                idx = int(line.replace("\x00CODEBLOCK", "").replace("\x00", ""))
                html_parts.append(code_blocks[idx])
                i += 1
                continue

            # Headers
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                level = len(header_match.group(1))
                text = self._inline(header_match.group(2))
                anchor = self._slugify(header_match.group(2))
                html_parts.append(
                    f'<h{level} id="{anchor}">'
                    f'<a href="#{anchor}" class="anchor">#</a> {text}</h{level}>'
                )
                i += 1
                continue

            # Horizontal rule
            if re.match(r"^(---|\*\*\*|___)\s*$", line):
                html_parts.append("<hr>")
                i += 1
                continue

            # Blockquote
            bq_lines: list[str] = []
            while i < len(lines) and lines[i].startswith(">"):
                bq_lines.append(lines[i][1:].strip())
                i += 1
            if bq_lines:
                inner = self._inline("\n".join(bq_lines))
                html_parts.append(f"<blockquote><p>{inner}</p></blockquote>")
                continue

            # Unordered list
            ul_items: list[str] = []
            while i < len(lines) and re.match(r"^\s*[-*+]\s+", lines[i]):
                text = re.sub(r"^\s*[-*+]\s+", "", lines[i])
                ul_items.append(f"<li>{self._inline(text)}</li>")
                i += 1
            if ul_items:
                html_parts.append("<ul>" + "".join(ul_items) + "</ul>")
                continue

            # Ordered list
            ol_items: list[str] = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                text = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                ol_items.append(f"<li>{self._inline(text)}</li>")
                i += 1
            if ol_items:
                html_parts.append("<ol>" + "".join(ol_items) + "</ol>")
                continue

            # Table
            if (
                "|" in line
                and i + 1 < len(lines)
                and re.match(r"^\s*\|?[\s:|\-]+\|?\s*$", lines[i + 1])
            ):
                table_lines: list[str] = []
                while i < len(lines) and "|" in lines[i]:
                    table_lines.append(lines[i])
                    i += 1
                html_parts.append(self._build_table(table_lines))
                continue

            # Empty line
            if not line.strip():
                i += 1
                continue

            # Paragraph (collect consecutive non-empty, non-special lines)
            para_lines: list[str] = []
            while (
                i < len(lines)
                and lines[i].strip()
                and not self._is_block_start(lines[i])
            ):
                para_lines.append(lines[i])
                i += 1
            if para_lines:
                text = " ".join(para_lines)
                html_parts.append(f"<p>{self._inline(text)}</p>")

        # Restore code blocks in final output
        result = "\n".join(html_parts)
        for idx, block in enumerate(code_blocks):
            result = result.replace(f"\x00CODEBLOCK{idx}\x00", block)

        return result

    def _is_block_start(self, line: str) -> bool:
        """Check if a line starts a block-level element."""
        if not line.strip():
            return False
        if line.startswith("#"):
            return True
        if line.startswith(">"):
            return True
        if re.match(r"^\s*[-*+]\s+", line):
            return True
        if re.match(r"^\s*\d+\.\s+", line):
            return True
        if re.match(r"^```", line):
            return True
        if re.match(r"^(---|\*\*\*|___)\s*$", line):
            return True
        return False

    def _inline(self, text: str) -> str:
        """Process inline markdown elements."""
        # Inline code (protect from other transforms)
        code_spans: list[str] = []

        def _save_inline_code(m: re.Match) -> str:
            idx = len(code_spans)
            code_spans.append(f"<code>{html.escape(m.group(1))}</code>")
            return f"\x00IC{idx}\x00"

        text = self._inline_code_re.sub(_save_inline_code, text)

        # Images
        text = self._image_re.sub(
            lambda m: f'<img src="{html.escape(m.group(2))}" alt="{html.escape(m.group(1))}">',
            text,
        )

        # Links
        text = self._link_re.sub(
            lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>',
            text,
        )

        # Bold
        text = self._bold_re.sub(r"<strong>\1</strong>", text)

        # Italic
        text = self._italic_re.sub(r"<em>\1</em>", text)

        # Restore inline code
        for idx, code in enumerate(code_spans):
            text = text.replace(f"\x00IC{idx}\x00", code)

        return text

    def _build_table(self, lines: list[str]) -> str:
        """Build an HTML table from markdown table lines."""
        rows: list[list[str]] = []
        for line in lines:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(cells)

        if len(rows) < 2:
            return ""

        # Parse alignment from separator row
        alignments: list[str] = []
        for cell in rows[1]:
            cell = cell.strip()
            if cell.startswith(":") and cell.endswith(":"):
                alignments.append(' style="text-align:center"')
            elif cell.endswith(":"):
                alignments.append(' style="text-align:right"')
            else:
                alignments.append("")

        parts = ["<table>", "<thead><tr>"]
        for i, cell in enumerate(rows[0]):
            align = alignments[i] if i < len(alignments) else ""
            parts.append(f"<th{align}>{self._inline(cell)}</th>")
        parts.append("</tr></thead><tbody>")

        for row in rows[2:]:
            parts.append("<tr>")
            for i, cell in enumerate(row):
                align = alignments[i] if i < len(alignments) else ""
                parts.append(f"<td{align}>{self._inline(cell)}</td>")
            parts.append("</tr>")

        parts.append("</tbody></table>")
        return "".join(parts)

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to a URL-safe anchor."""
        text = re.sub(r"[^\w\s-]", "", text.lower())
        return re.sub(r"[\s_]+", "-", text).strip("-")


# ---------------------------------------------------------------------------
# Site generator
# ---------------------------------------------------------------------------

CSS = """
:root {
    --bg: #ffffff;
    --fg: #1a1a2e;
    --bg-secondary: #f8f9fa;
    --border: #e1e4e8;
    --accent: #6366f1;
    --accent-light: #eef2ff;
    --code-bg: #f1f3f5;
    --pre-bg: #1e1e2e;
    --pre-fg: #cdd6f4;
    --nav-bg: #fafafa;
    --link: #4f46e5;
    --link-hover: #3730a3;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg: #0d1117;
        --fg: #e6edf3;
        --bg-secondary: #161b22;
        --border: #30363d;
        --accent: #818cf8;
        --accent-light: #1e1b4b;
        --code-bg: #1e1e2e;
        --pre-bg: #0d1117;
        --pre-fg: #cdd6f4;
        --nav-bg: #161b22;
        --link: #818cf8;
        --link-hover: #a5b4fc;
    }
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
    line-height: 1.7;
    color: var(--fg);
    background: var(--bg);
}

.layout {
    display: flex;
    min-height: 100vh;
}

/* Sidebar */
.sidebar {
    width: 280px;
    background: var(--nav-bg);
    border-right: 1px solid var(--border);
    padding: 1.5rem 0;
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    overflow-y: auto;
}

.sidebar-title {
    padding: 0 1.5rem 1rem;
    font-size: 1.25rem;
    font-weight: 700;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
}

.sidebar-title a {
    color: var(--accent);
    text-decoration: none;
}

.sidebar nav ul {
    list-style: none;
}

.sidebar nav li a {
    display: block;
    padding: 0.4rem 1.5rem;
    color: var(--fg);
    text-decoration: none;
    font-size: 0.9rem;
    border-left: 3px solid transparent;
    transition: all 0.15s;
}

.sidebar nav li a:hover {
    background: var(--accent-light);
    color: var(--link);
}

.sidebar nav li a.active {
    border-left-color: var(--accent);
    color: var(--accent);
    font-weight: 600;
    background: var(--accent-light);
}

/* Main content */
.main {
    flex: 1;
    margin-left: 280px;
    padding: 2rem 3rem;
    max-width: 900px;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    margin-top: 2rem;
    margin-bottom: 0.75rem;
    line-height: 1.3;
}

h1 { font-size: 2.25rem; margin-top: 0; }
h2 { font-size: 1.75rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; }
h3 { font-size: 1.35rem; }
h4 { font-size: 1.15rem; }

.anchor {
    color: var(--border);
    text-decoration: none;
    margin-right: 0.25rem;
    font-weight: 400;
}

.anchor:hover { color: var(--accent); }

p { margin-bottom: 1rem; }

a { color: var(--link); }
a:hover { color: var(--link-hover); }

/* Code */
code {
    font-family: "SF Mono", "Fira Code", "Cascadia Code", Consolas, monospace;
    background: var(--code-bg);
    padding: 0.15em 0.4em;
    border-radius: 4px;
    font-size: 0.875em;
}

pre {
    background: var(--pre-bg);
    color: var(--pre-fg);
    padding: 1.25rem;
    border-radius: 8px;
    overflow-x: auto;
    margin-bottom: 1.5rem;
}

pre code {
    background: none;
    padding: 0;
    color: inherit;
    font-size: 0.85rem;
    line-height: 1.6;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
}

th, td {
    padding: 0.6rem 0.8rem;
    border: 1px solid var(--border);
    text-align: left;
}

th {
    background: var(--bg-secondary);
    font-weight: 600;
}

tr:hover td {
    background: var(--accent-light);
}

/* Lists */
ul, ol { margin-bottom: 1rem; padding-left: 1.5rem; }
li { margin-bottom: 0.25rem; }

/* Blockquote */
blockquote {
    border-left: 4px solid var(--accent);
    padding: 0.5rem 1rem;
    margin-bottom: 1rem;
    background: var(--bg-secondary);
    border-radius: 0 4px 4px 0;
}

hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

img { max-width: 100%; height: auto; }

/* Mobile */
@media (max-width: 768px) {
    .sidebar {
        position: static;
        width: 100%;
        border-right: none;
        border-bottom: 1px solid var(--border);
    }
    .main {
        margin-left: 0;
        padding: 1.5rem;
    }
    .layout { flex-direction: column; }
}
"""

NAV_ORDER = [
    ("index.md", "Home"),
    ("getting-started.md", "Getting Started"),
    ("authentication.md", "Authentication"),
    ("workspaces.md", "Workspaces"),
    ("databases.md", "Databases"),
    ("models.md", "Models Reference"),
    ("errors.md", "Error Handling"),
    ("api-reference.md", "API Reference"),
    ("changelog.md", "Changelog"),
]


def build_site(docs_dir: Path, output_dir: Path) -> None:
    """Build the documentation site."""
    converter = MarkdownConverter()

    # Clean and create output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # Read all docs
    pages: dict[str, tuple[str, str]] = {}  # slug -> (title, html)
    for filename, title in NAV_ORDER:
        md_path = docs_dir / filename
        if not md_path.exists():
            print(f"Warning: {md_path} not found, skipping")
            continue
        md_content = md_path.read_text(encoding="utf-8")
        body_html = converter.convert(md_content)
        slug = filename.replace(".md", "") if filename != "index.md" else "index"
        pages[slug] = (title, body_html)

    # Generate sidebar nav
    nav_html = '<div class="sidebar-title"><a href="index.html">AppFlowy SDK</a></div>\n<nav><ul>\n'
    for filename, title in NAV_ORDER:
        slug = filename.replace(".md", "") if filename != "index.md" else "index"
        if slug in pages:
            nav_html += (
                f'<li><a href="{slug}.html" data-page="{slug}">{title}</a></li>\n'
            )
    nav_html += "</ul></nav>"

    # Generate each page
    for slug, (title, body_html) in pages.items():
        page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - AppFlowy SDK</title>
    <style>{CSS}</style>
</head>
<body>
    <div class="layout">
        <aside class="sidebar">{nav_html}</aside>
        <main class="main">{body_html}</main>
    </div>
    <script>
        document.querySelector('a[data-page="{slug}"]')?.classList.add('active');
    </script>
</body>
</html>"""
        (output_dir / f"{slug}.html").write_text(page_html, encoding="utf-8")
        print(f"  Generated {slug}.html")

    # Copy README.md as index if no index.md exists
    if "index" not in pages:
        readme = Path("README.md")
        if readme.exists():
            body_html = converter.convert(readme.read_text(encoding="utf-8"))
            page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AppFlowy SDK</title>
    <style>{CSS}</style>
</head>
<body>
    <div class="layout">
        <aside class="sidebar">{nav_html}</aside>
        <main class="main">{body_html}</main>
    </div>
    <script>
        document.querySelector('a[data-page="index"]')?.classList.add('active');
    </script>
</body>
</html>"""
            (output_dir / "index.html").write_text(page_html, encoding="utf-8")
            print("  Generated index.html (from README.md)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build AppFlowy SDK documentation site"
    )
    parser.add_argument("--docs", default="docs", help="Source markdown directory")
    parser.add_argument("--output", default="site", help="Output HTML directory")
    args = parser.parse_args()

    docs_dir = Path(args.docs)
    output_dir = Path(args.output)

    if not docs_dir.exists():
        print(f"Error: docs directory '{docs_dir}' not found", file=sys.stderr)
        sys.exit(1)

    print(f"Building docs from {docs_dir}/ into {output_dir}/")
    build_site(docs_dir, output_dir)
    print(f"\nDone! {len(list(output_dir.glob('*.html')))} pages generated.")
    print(f"Open {output_dir}/index.html in a browser to view.")


if __name__ == "__main__":
    main()
