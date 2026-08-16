# 🏛️ Apresentação Técnica CETAM • Infraestrutura Windows Server 2022
**Projeto:** Administração, Segurança e Serviços Corporativos no Windows Server 2022  
**Instituição:** Centro de Educação Tecnológica do Amazonas (CETAM)  
**Equipe 3:** Elizandra, Gilvan, Mariane, Edmar e Adler  

---

## 📂 Estrutura Modular do Projeto

```text
Cetam_Atividade/
├── apresentacao_cetam.html     # Aplicação Web interativa dos slides
├── index.html                  # Ponto de entrada padrão
├── Apresentacao_Grupo3_CETAM.pdf # Exportação dos slides em PDF (16:9)
├── Grupo3_Guia_Execucao.md     # Manual Operacional Completo (317 linhas)
├── Grupo3_Guia_Execucao.pdf    # Manual Operacional em PDF para auditoria
├── Configura_Grupo3_Servicos.ps1 # Script de automação PowerShell
│
├── assets/
│   └── images/                 # Vetores SVG da identidade CETAM e fauna amazônica
│       ├── cetam-logo.svg      # Logo oficial vetorizado
│       ├── onca.svg            # Silhueta da Onça-pintada (GPO & Hardening)
│       ├── boto.svg            # Silhueta do Boto-cor-de-rosa (Arquivos & NTFS)
│       ├── harpia.svg          # Silhueta da Harpia / Gavião-real (Impressão & Firewall)
│       └── arara.svg           # Silhueta da Arara-vermelha (Fechamento)
│
├── css/                        # Módulos de Estilo Particionados
│   ├── style.css               # Hub principal de importação
│   ├── variables.css           # Tokens de cor CETAM, fontes e sombras
│   ├── layout.css              # Estrutura geral, header, footer e @media print
│   ├── components.css          # Cards em 3 níveis (DrawIO), botões e chips
│   ├── watermarks.css          # Marcas d'água translúcidas dos animais
│   └── responsive.css          # Adaptação para celulares, tablets e projetores
│
└── js/                         # Módulos de Lógica e Interatividade
    ├── particles.js            # Canvas animado de partículas em rede
    └── presentation.js         # Controle de navegação, teclado, swipe e clipboard
```

---

## 🎨 Padrão Visual dos Slides (Modelo DrawIO)

Cada slide técnico segue rigorosamente a estrutura tripla de 3 níveis:

```
┌──────────────────────────────────────────────────────────┐
│ 👤 1. Precisa ser feito    (Requisito e escopo claro)    │
└────────────────────────────┬─────────────────────────────┘
                             │ ↓
┌────────────────────────────┴─────────────────────────────┐
│ ⚙️ 2. Como fazer            (Console / Ação no Windows)   │
└────────────────────────────┬─────────────────────────────┘
                             │ ↓
┌────────────────────────────┴─────────────────────────────┐
│ ✉️ 3. Como testar se deu   (Comando com botão de cópia   │
│       certo                 e resultado esperado)        │
└──────────────────────────────────────────────────────────┘
```

---

## 👥 Divisão Oficial dos 6 Slides

1. **Slide 1 — Capa & Equipe (Elizandra / Todos):** Abertura oficial e apresentação dos 5 integrantes.
2. **Slide 2 — Gilvan (Etapa 1 • GPO):** Políticas de Senhas, Bloqueio de USB, Bloqueio de CMD/PowerShell e Isenção da TI (`Domain Admins`).
3. **Slide 3 — Mariane (Etapa 2 • Arquivos):** 8 Pastas Departamentais em `C:\Dados`, Permissões NTFS do Setor e Pop-up de Acesso Negado (sem ABE).
4. **Slide 4 — Edmar (Etapa 3 • Impressão):** Função Print-Server, Fila Central `IMP_Geral` (`192.168.10.20`) no AD e Correção RPC `0x8007011b`.
5. **Slide 5 — Adler (Etapa 4 • Firewall/DNS):** Perfis Ativos no `wf.msc`, Liberação SMB/Ping e DNS Reverso `10.168.192.in-addr.arpa`.
6. **Slide 6 — Elizandra & Equipe (Encerramento):** Agradecimentos, citação dos integrantes e Referências Técnicas Oficiais da Microsoft.

---

## ⌨️ Atalhos de Teclado e Navegação

* <kbd>→</kbd> / <kbd>Espaço</kbd> / <kbd>PageDown</kbd>: Avançar slide
* <kbd>←</kbd> / <kbd>PageUp</kbd>: Voltar slide
* <kbd>1</kbd> até <kbd>6</kbd>: Ir direto ao slide correspondente
* <kbd>H</kbd> ou <kbd>Home</kbd>: Voltar para a Capa (Slide 1)
* <kbd>F</kbd>: Alternar modo Tela Cheia
* **Dispositivos Móveis:** Suporte a toque com deslizamento (*swipe*) para a esquerda/direita.

---

## 🖨️ Como Recompilar o PDF dos Slides

Para gerar uma nova versão do PDF de slides em alta resolução:
```bash
python make_slides_pdf.py
```
