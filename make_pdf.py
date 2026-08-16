import re
import os
import subprocess

def md_to_html(md_text):
    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    code_lang = ""
    in_table = False
    in_blockquote = False
    blockquote_type = ""
    blockquote_content = []
    
    def flush_blockquote():
        nonlocal in_blockquote, blockquote_type, blockquote_content
        if in_blockquote:
            content_html = "<br/>".join(blockquote_content)
            if blockquote_type:
                title_map = {
                    'NOTE': '📌 NOTA',
                    'TIP': '💡 DICA',
                    'IMPORTANT': '⭐ IMPORTANTE',
                    'WARNING': '⚠️ ATENÇÃO / AVISO',
                    'CAUTION': '🚨 ALERTA CRÍTICO / INCIDENTE REAL'
                }
                title = title_map.get(blockquote_type, blockquote_type)
                html_lines.append(f'<div class="callout callout-{blockquote_type.lower()}"><div class="callout-title">{title}</div><div class="callout-body">{content_html}</div></div>')
            else:
                html_lines.append(f'<blockquote>{content_html}</blockquote>')
            in_blockquote = False
            blockquote_type = ""
            blockquote_content = []

    for line in lines:
        # Code block handling
        if line.startswith('```'):
            flush_blockquote()
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
            else:
                code_lang = line[3:].strip()
                html_lines.append(f'<pre><code class="language-{code_lang}">')
                in_code_block = True
            continue
        
        if in_code_block:
            escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_lines.append(escaped)
            continue

        # Blockquote / Alert handling
        if line.strip().startswith('>'):
            raw_quote = line.strip()[1:].strip()
            alert_match = re.match(r'^\[\!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', raw_quote)
            if alert_match:
                flush_blockquote()
                in_blockquote = True
                blockquote_type = alert_match.group(1)
                continue
            
            if not in_blockquote:
                in_blockquote = True
                blockquote_type = ""
            
            if raw_quote:
                blockquote_content.append(raw_quote)
            continue
        else:
            flush_blockquote()
            
        # Table handling
        if '|' in line and not line.strip().startswith('```'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if not parts:
                continue
            if all(set(p) <= set(':- ') for p in parts):
                continue
            if not in_table:
                in_table = True
                html_lines.append('<table><thead><tr>')
                for p in parts:
                    html_lines.append(f'<th>{p}</th>')
                html_lines.append('</tr></thead><tbody>')
            else:
                html_lines.append('<tr>')
                for p in parts:
                    html_lines.append(f'<td>{p}</td>')
                html_lines.append('</tr>')
            continue
        else:
            if in_table:
                html_lines.append('</tbody></table>')
                in_table = False

        # Headers
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
            continue
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
            continue
        elif line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
            continue
        elif line.startswith('#### '):
            html_lines.append(f'<h4>{line[5:]}</h4>')
            continue

        # Horizontal rule
        if line.strip() in ['---', '***', '___']:
            html_lines.append('<hr/>')
            continue

        # Unordered list items
        if line.strip().startswith('* ') or line.strip().startswith('- '):
            item_text = line.strip()[2:]
            html_lines.append(f'<ul><li>{item_text}</li></ul>')
            continue

        # Ordered list items
        num_match = re.match(r'^(\d+)\.\s+(.*)', line.strip())
        if num_match:
            item_text = num_match.group(2)
            html_lines.append(f'<ol start="{num_match.group(1)}"><li>{item_text}</li></ol>')
            continue

        # Blank line
        if not line.strip():
            html_lines.append('<br/>')
            continue

        # Paragraph
        html_lines.append(f'<p>{line}</p>')

    flush_blockquote()

    if in_table:
        html_lines.append('</tbody></table>')

    html_content = '\n'.join(html_lines)

    # Clean consecutive list tags
    html_content = re.sub(r'</ul>\s*<ul>', '', html_content)
    html_content = re.sub(r'</ol>\s*<ol[^>]*>', '', html_content)

    # Inline formatting: **bold**, `code`, *italic*
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
    html_content = re.sub(r'`(.*?)`', r'<code>\1</code>', html_content)
    html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
    
    return html_content

def build_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_path = os.path.join(base_dir, 'Grupo3_Guia_Execucao.md')
    html_path = os.path.join(base_dir, 'Grupo3_Guia_Execucao.html')
    pdf_path = os.path.join(base_dir, 'Grupo3_Guia_Execucao.pdf')

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    body_html = md_to_html(md_text)

    full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Manual Operacional Grupo 3 - Windows Server 2022</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
    
    @page {{
        size: A4;
        margin: 15mm 15mm 15mm 15mm;
    }}
    
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1e293b;
        background-color: #ffffff;
        line-height: 1.5;
        font-size: 11.5px;
        margin: 0;
        padding: 0;
    }}
    
    h1 {{
        color: #0f172a;
        font-size: 19px;
        border-bottom: 3px solid #2563eb;
        padding-bottom: 6px;
        margin-top: 0;
        margin-bottom: 10px;
    }}
    
    h2 {{
        color: #1e3a8a;
        font-size: 14.5px;
        background-color: #f1f5f9;
        padding: 6px 10px;
        border-left: 4px solid #2563eb;
        margin-top: 20px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }}
    
    h3 {{
        color: #0369a1;
        font-size: 13px;
        margin-top: 14px;
        margin-bottom: 6px;
        page-break-after: avoid;
    }}
    
    h4 {{
        color: #0f766e;
        font-size: 12px;
        margin-top: 10px;
        margin-bottom: 4px;
        page-break-after: avoid;
    }}
    
    p {{
        margin-top: 3px;
        margin-bottom: 6px;
    }}
    
    strong {{
        color: #0f172a;
    }}
    
    code {{
        font-family: 'Consolas', 'Courier New', monospace;
        background-color: #f1f5f9;
        color: #0f172a;
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 10.5px;
        border: 1px solid #cbd5e1;
    }}
    
    pre {{
        background-color: #0f172a;
        color: #f8fafc;
        padding: 10px 12px;
        border-radius: 6px;
        overflow-x: auto;
        font-size: 10.5px;
        line-height: 1.45;
        margin: 8px 0;
        page-break-inside: avoid;
    }}
    
    pre code {{
        background-color: transparent;
        color: inherit;
        padding: 0;
        border: none;
    }}
    
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        font-size: 10.5px;
        page-break-inside: avoid;
    }}
    
    th {{
        background-color: #1e293b;
        color: #ffffff;
        text-align: left;
        padding: 6px 8px;
        font-weight: 600;
        border: 1px solid #334155;
    }}
    
    td {{
        padding: 6px 8px;
        border: 1px solid #cbd5e1;
    }}
    
    tr:nth-child(even) {{
        background-color: #f8fafc;
    }}
    
    ul, ol {{
        margin-top: 3px;
        margin-bottom: 8px;
        padding-left: 20px;
    }}
    
    li {{
        margin-bottom: 3px;
    }}
    
    hr {{
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 16px 0;
    }}

    /* Callout & Alert Box Styles */
    .callout {{
        border-left: 4px solid #3b82f6;
        background-color: #f8fafc;
        padding: 10px 14px;
        margin: 12px 0;
        border-radius: 0 6px 6px 0;
        page-break-inside: avoid;
    }}
    
    .callout-title {{
        font-weight: bold;
        font-size: 11.5px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
    }}
    
    .callout-body {{
        font-size: 11px;
        line-height: 1.45;
    }}
    
    .callout-note {{
        border-left-color: #3b82f6;
        background-color: #eff6ff;
    }}
    .callout-note .callout-title {{ color: #1d4ed8; }}
    
    .callout-important {{
        border-left-color: #6366f1;
        background-color: #eef2ff;
    }}
    .callout-important .callout-title {{ color: #4338ca; }}
    
    .callout-warning {{
        border-left-color: #f59e0b;
        background-color: #fffbeb;
    }}
    .callout-warning .callout-title {{ color: #b45309; }}
    
    .callout-caution {{
        border-left-color: #ef4444;
        background-color: #fef2f2;
    }}
    .callout-caution .callout-title {{ color: #b91c1c; }}

    blockquote {{
        border-left: 4px solid #94a3b8;
        background-color: #f8fafc;
        margin: 8px 0;
        padding: 6px 12px;
        color: #475569;
        font-style: italic;
    }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"HTML gerado com sucesso: {html_path}")

    edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    file_url = 'file:///' + html_path.replace('\\', '/')
    cmd = [
        edge_exe,
        '--headless',
        '--disable-gpu',
        '--no-pdf-header-footer',
        f'--print-to-pdf={pdf_path}',
        file_url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_path):
        print(f"PDF gerado com sucesso: {pdf_path}")
    else:
        print("Erro ao gerar PDF:", result.stderr)

if __name__ == '__main__':
    build_pdf()
