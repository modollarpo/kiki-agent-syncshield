#!/usr/bin/env python3
"""
Convert HOW_KIKI_WORKS.md to PDF with styling
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path

def convert_markdown_to_pdf(md_file: str, pdf_file: str):
    """
    Convert markdown file to PDF with custom styling
    """
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'extra',           # Tables, code blocks, etc.
            'codehilite',      # Syntax highlighting
            'toc',             # Table of contents
            'nl2br',           # Line breaks
            'sane_lists'       # Better list handling
        ]
    )
    
    # Add CSS styling for better PDF appearance
    css_style = """
        @page {
            size: A4;
            margin: 2cm;
            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
        }
        
        h1 {
            color: #1a1a1a;
            font-size: 28pt;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
            margin-top: 20px;
            page-break-before: always;
        }
        
        h1:first-of-type {
            page-break-before: avoid;
        }
        
        h2 {
            color: #2c3e50;
            font-size: 20pt;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
            margin-top: 25px;
            page-break-after: avoid;
        }
        
        h3 {
            color: #34495e;
            font-size: 16pt;
            margin-top: 20px;
            page-break-after: avoid;
        }
        
        h4 {
            color: #555;
            font-size: 14pt;
            margin-top: 15px;
            page-break-after: avoid;
        }
        
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            color: #d14;
        }
        
        pre {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            overflow-x: auto;
            border-radius: 4px;
            page-break-inside: avoid;
        }
        
        pre code {
            background-color: transparent;
            padding: 0;
            color: #333;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        th {
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        
        td {
            border: 1px solid #ddd;
            padding: 10px;
        }
        
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #555;
            font-style: italic;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        ul, ol {
            margin: 10px 0;
            padding-left: 30px;
        }
        
        li {
            margin: 5px 0;
        }
        
        hr {
            border: none;
            border-top: 2px solid #e0e0e0;
            margin: 30px 0;
        }
        
        .toc {
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            page-break-after: always;
        }
        
        img {
            max-width: 100%;
            height: auto;
        }
        
        strong {
            color: #2c3e50;
            font-weight: 600;
        }
        
        em {
            color: #555;
        }
    """
    
    # Create full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>How KIKI Agent Works</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    print(f"Converting {md_file} to PDF...")
    HTML(string=full_html).write_pdf(
        pdf_file,
        stylesheets=[CSS(string=css_style)]
    )
    print(f"✅ PDF created successfully: {pdf_file}")
    
    # Get file size
    size_mb = Path(pdf_file).stat().st_size / (1024 * 1024)
    print(f"📄 File size: {size_mb:.2f} MB")


if __name__ == "__main__":
    md_file = "/workspaces/kiki-agent-syncshield/docs/HOW_KIKI_WORKS.md"
    pdf_file = "/workspaces/kiki-agent-syncshield/docs/HOW_KIKI_WORKS.pdf"
    
    convert_markdown_to_pdf(md_file, pdf_file)
