#!/usr/bin/env python3
"""
Generate PDF from KIKI_EXECUTIVE_SUMMARY.md using markdown + weasyprint
"""
import markdown
from weasyprint import HTML, CSS
from pathlib import Path

def generate_pdf():
    # Read markdown file
    md_file = Path(__file__).parent / "KIKI_EXECUTIVE_SUMMARY.md"
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'nl2br']
    )
    
    # Enhanced CSS for professional executive summary
    css = CSS(string='''
        @page {
            size: Letter;
            margin: 0.75in;
            @top-center {
                content: "KIKI Agent™ Autonomous Revenue Engine";
                font-size: 9pt;
                color: #666;
            }
            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #1a1a1a;
        }
        
        h1 {
            color: #0066cc;
            font-size: 24pt;
            font-weight: 700;
            margin-top: 0;
            margin-bottom: 8pt;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 8pt;
        }
        
        h2 {
            color: #0066cc;
            font-size: 16pt;
            font-weight: 600;
            margin-top: 18pt;
            margin-bottom: 8pt;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4pt;
        }
        
        h3 {
            color: #333;
            font-size: 12pt;
            font-weight: 600;
            margin-top: 12pt;
            margin-bottom: 6pt;
        }
        
        p {
            margin: 6pt 0;
            text-align: justify;
        }
        
        strong {
            color: #000;
            font-weight: 600;
        }
        
        ul, ol {
            margin: 6pt 0;
            padding-left: 20pt;
        }
        
        li {
            margin: 3pt 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            font-size: 9pt;
        }
        
        th {
            background-color: #0066cc;
            color: white;
            font-weight: 600;
            padding: 6pt;
            text-align: left;
            border: 1px solid #0066cc;
        }
        
        td {
            padding: 6pt;
            border: 1px solid #ddd;
        }
        
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        code {
            background-color: #f4f4f4;
            padding: 2pt 4pt;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
        }
        
        pre {
            background-color: #f4f4f4;
            padding: 10pt;
            border-left: 4px solid #0066cc;
            overflow-x: auto;
            font-size: 8pt;
            line-height: 1.3;
        }
        
        hr {
            border: none;
            border-top: 2px solid #0066cc;
            margin: 12pt 0;
        }
        
        blockquote {
            border-left: 4px solid #0066cc;
            background-color: #f0f8ff;
            padding: 8pt 12pt;
            margin: 12pt 0;
            font-style: italic;
        }
        
        /* Highlight key metrics */
        strong:contains("30-50%"),
        strong:contains("20-40%"),
        strong:contains("Sub-millisecond"),
        strong:contains("24/7") {
            color: #0066cc;
        }
    ''')
    
    # Generate full HTML document
    full_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>KIKI Agent™ - Executive Summary</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    '''
    
    # Generate PDF
    output_file = Path(__file__).parent / "KIKI_EXECUTIVE_SUMMARY.pdf"
    HTML(string=full_html).write_pdf(output_file, stylesheets=[css])
    
    print(f"✅ PDF generated successfully: {output_file}")
    print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    generate_pdf()
