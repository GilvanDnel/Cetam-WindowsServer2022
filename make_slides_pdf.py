import os
import subprocess

def generate_slides_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, 'apresentacao_cetam.html')
    pdf_path = os.path.join(base_dir, 'Apresentacao_Grupo3_CETAM.pdf')

    if not os.path.exists(html_path):
        print(f"Erro: Arquivo HTML não encontrado: {html_path}")
        return

    edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    file_url = 'file:///' + html_path.replace('\\', '/')

    print(f"[*] Gerando PDF dos slides da apresentação...")
    cmd = [
        edge_exe,
        '--headless',
        '--disable-gpu',
        '--no-pdf-header-footer',
        '--print-to-pdf-no-header',
        f'--print-to-pdf={pdf_path}',
        file_url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"[+] Sucesso! PDF gerado em: {pdf_path} ({size_kb:.1f} KB)")
    else:
        print("[!] Erro ao gerar PDF:", result.stderr)

if __name__ == '__main__':
    generate_slides_pdf()
