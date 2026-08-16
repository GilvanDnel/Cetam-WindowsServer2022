# Manual Operacional e Guia de Execução Sênior - Grupo 3
## Administração, Segurança e Serviços Corporativos
**Projeto:** Implantação da Infraestrutura de TI do Instituto Esperança Digital  
**Sistema Operacional:** Windows Server 2022 Datacenter & Ubuntu Server 24.04 LTS  

---

### 🔑 Quadro de Credenciais e Parâmetros de Rede (Integração Grupos 1, 2 e 3)

| Parâmetro / Recurso | Valor / Configuração | Descrição / Observação Técnica |
|---|---|---|
| **Domínio Corporativo** | `esperancadigital.local` | FQDN do Active Directory Domain Services (Grupo 2) |
| **Controlador de Domínio (DC)** | `SRV-DC01` | Hostname do Windows Server 2022 |
| **IP Fixo Servidor Windows (DC/DNS)** | `192.168.10.2` (Máscara `255.255.255.0`) | IP estático do DC e Servidor DNS Principal |
| **IP Fixo Gateway Linux (Ubuntu)** | `192.168.10.1` | Interface LAN `enp1s0` do Ubuntu Server (Grupo 1 e 2) |
| **Faixa DHCP (Distribuída pelo Linux)** | `192.168.10.100` até `192.168.10.200` | Escopo dinâmico entregando DNS Primário `192.168.10.2` |
| **Login Administrador Windows** | `Administrator` (ou `administrator`) | Conta de Domínio com privilégios totais de gestão |
| **Senha Administrador Windows** | `Manaus@` | Credencial oficial do Administrador (Grupos 1 e 2) |
| **Login Servidor Linux (Ubuntu)** | `srv` | Usuário administrador com privilégios sudo / root |
| **Senha Servidor Linux** | `manaus` | Senha de acesso do servidor Ubuntu |
| **Padrão de Login dos Usuários** | `nome.sobrenome` (Ex: `joao.silva`, `sec.usuario`) | Contas cadastradas nas OUs departamentais |
| **Senha Padrão dos Usuários** | `@esperancadigital-2026` | Política de primeiro acesso dos colaboradores/alunos |
| **IP Impressora Geral (Corporativa)** | `192.168.10.20` (`IMP_Geral`) | Fila de impressão TCP/IP centralizada e publicada no AD DS para todos os setores |

---

## 🧰 SEÇÃO 0: Caixa de Ferramentas Administrativas e Matriz de Escopos

Um dos maiores desafios durante a implantação é a confusão entre ferramentas com nomes semelhantes ou escopos conflitantes. Utilize sempre o console correto para cada tarefa:

| Console / Comando | Nome da Ferramenta | Escopo de Atuação | Quando Utilizar no Grupo 3 |
|---|---|---|---|
| **`gpmc.msc`** | Gerenciamento de Diretiva de Grupo (GPMC) | **Todo o Domínio ou OUs** | Criar e editar GPOs de senha, papel de parede, bloqueio de painel e USB. |
| **`dsa.msc`** | Usuários e Computadores do AD (ADUC) | **Objetos do Domínio** | Gerenciar contas, grupos, OUs e configurar **Horário de Logon (Logon Hours)** individual. |
| **`secpol.msc`** | Diretiva de Segurança Local | **Apenas a Máquina Local** | ⚠️ *NÃO USAR PARA O DOMÍNIO*. Usada apenas em servidores fora de domínio. |
| **`printmanagement.msc`** | Gerenciamento de Impressão | **Servidor de Impressão** | Adicionar drivers, criar portas TCP/IP, compartilhar impressoras e implantar via GPO. |
| **`wf.msc`** | Windows Defender Firewall Avançado | **Segurança de Rede do Host** | Habilitar regras de entrada para compartilhamento SMB e ICMP Ping. |
| **`dnsmgmt.msc`** | Gerenciador DNS | **Resolução de Nomes** | Validar Zona Direta (`esperancadigital.local`) e Zona Reversa (`10.168.192.in-addr.arpa`). |

---

## 🛠️ ETAPA 1: Gestão de Identidade e Políticas de Grupo (GPO)

### 1.1. Política de Senhas e Bloqueio de Conta (Default Domain Policy)

> [!IMPORTANT]
> **Regra Arquitetural do Windows Server:**  
> Políticas de senha e bloqueio de conta para usuários de domínio **só entram em vigor globalmente quando editadas na `Default Domain Policy` localizada na RAIZ do domínio**. Configurar essas diretivas em GPOs vinculadas a OUs filhas (ex: `OU_Estacoes`) não surtirá efeito nas autenticações do Active Directory.

#### 📍 Árvore de Navegação e Clique a Clique:
1. No servidor `SRV-DC01`, pressione **`Win + R`**, digite **`gpmc.msc`** e pressione **Enter** (ou vá em `Server Manager` ➔ `Ferramentas` ➔ `Gerenciamento de Diretiva de Grupo`).
2. Expanda a árvore navegando em:  
   `Gerenciamento de Diretiva de Grupo` ➔ `Floresta: esperancadigital.local` ➔ `Domínios` ➔ `esperancadigital.local`.
3. Clique com o **botão direito do mouse** sobre **`Default Domain Policy`** ➔ selecione **`Editar...`**.
4. No menu esquerdo do *Editor de Gerenciamento de Diretiva de Grupo*, expanda:  
   `Configuração do Computador` ➔ `Diretivas` ➔ `Configurações do Windows` ➔ `Configurações de Segurança` ➔ `Políticas de Conta`.

```
Políticas de Conta (Account Policies)
 ├── 📂 Política de Senhas (Password Policy)           <--- Item A
 └── 📂 Política de Bloqueio de Conta (Account Lockout) <--- Item B (pasta logo abaixo)
```

#### ✍️ Configuração do Item A — 📂 Pasta `Política de Senhas`:
* Dê um clique simples na pasta **`Política de Senhas`** no painel esquerdo:
  1. **Tamanho mínimo da senha:** Duplo clique ➔ Marcar `Definir esta configuração` ➔ Digitar **`8`** caracteres ➔ `Aplicar` ➔ `OK`.
  2. **A senha deve satisfazer a requisitos de complexidade:** Duplo clique ➔ Marcar **`Habilitado`** ➔ `Aplicar` ➔ `OK`.
  3. **Exigir histórico de senhas:** Duplo clique ➔ Digitar **`5`** senhas memorizadas ➔ `Aplicar` ➔ `OK`.
  4. **Tempo máximo de vida da senha:** Duplo clique ➔ Digitar **`90`** dias ➔ `Aplicar` ➔ `OK`.

#### ✍️ Configuração do Item B — 📂 Pasta `Política de Bloqueio de Conta` (Pasta logo abaixo):
* Dê um clique simples na pasta **`Política de Bloqueio de Conta`** no painel esquerdo:
  1. **Limiar de bloqueio de conta:** Duplo clique ➔ Digitar **`5`** tentativas de logon incorretas ➔ `Aplicar`.
  2. *(O Windows exibirá um aviso ajustando automaticamente a Duração do Bloqueio para 30 min e Zerar Contador para 30 min. Clique em **`OK`**)*.
  3. Clique em **`OK`** para confirmar.

#### ✅ Validação e Confirmação:
* Abra o Prompt de Comando (`cmd`) no servidor ou estação e execute:
  ```cmd
  gpupdate /force
  net accounts
  ```
* **Resultado Esperado:** O terminal deve exibir:  
  - `Tamanho mínimo da senha: 8`  
  - `Histórico de senhas mantido: 5`  
  - `Limiar de Bloqueio: 5`  
  - `Duração do bloqueio (minutos): 30`

> [!CAUTION]
> **🚨 Incidente Real 01: O Mistério do `net accounts` desatualizado**  
> * **Sintoma:** O comando `net accounts` continua exibindo valores antigos padrão (42 dias, 7 caracteres).  
> * **Causa:** A edição foi feita em uma GPO vinculada a uma OU filha ou na *Default Domain Controllers Policy*.  
> * **Solução:** Certifique-se de editar exclusivamente a **`Default Domain Policy`** na raiz do domínio e execute `gpupdate /force`.

---

### 1.2. Desmistificando Mecanismos de Tempo (Inatividade vs Logoff vs Expediente)

É comum confundir o bloqueio de tela automático, o encerramento forçado de sessão e a janela de horário de trabalho:

| Mecanismo | O que faz na prática? | Onde se configura? | Escopo |
|---|---|---|---|
| **Limite de Inatividade da Máquina** | Bloqueia a tela (`Win + L`) após tempo ocioso sem mexer mouse/teclado. | GPMC ➔ Diretivas Locais ➔ Opções de Segurança | Computador / GPO |
| **Forçar Logoff ao Expirar Horário** | Desconecta a sessão quando o horário de expediente cadastrado termina. | GPMC ➔ Diretivas Locais ➔ Opções de Segurança | Computador / GPO |
| **Horário de Logon (Logon Hours)** | Define os dias da semana e horários em que o usuário tem permissão para logar. | **ADUC (`dsa.msc`)** ➔ Usuário ➔ Conta ➔ Horário de Logon | Objeto de Usuário |

#### ✍️ Configuração do Bloqueio Automático de Tela por Inatividade (GPO):
1. No console `gpmc.msc`, abra a **`Default Domain Policy`** ou crie na **`GPO_Seguranca_e_Padronizacao`**.
2. Navegue em: `Configuração do Computador` ➔ `Diretivas` ➔ `Configurações do Windows` ➔ `Configurações de Segurança` ➔ `Diretivas Locais` ➔ `Opções de Segurança`.
3. No painel direito, localize a política: **`Logon interativo: Limite de inatividade da máquina`**.
4. Habilite a diretiva e defina o valor como **`900`** segundos (15 minutos) ➔ `Aplicar` ➔ `OK`.

#### ✍️ Configuração do Horário de Expediente dos Usuários (ADUC `dsa.msc`):
1. Abra o console **`dsa.msc`** (`Active Directory Users and Computers`).
2. Expanda o domínio `esperancadigital.local` ➔ navegue até a OU desejada (ex: `OU_Secretaria`).
3. Clique com o botão direito sobre o usuário (ou selecione múltiplos usuários) ➔ **`Propriedades`**.
4. Clique na aba **`Conta`** (Account) ➔ clique no botão **`Horário de Logon...`** (Logon Hours).
5. Selecione os horários permitidos (ex: Segunda a Sexta, das 07:00 às 18:00) e marque **`Logon Permitido`** / **`Logon Negado`** ➔ `OK` ➔ `Aplicar`.

---

### 1.3. GPO de Segurança, Wallpaper Institucional e Bloqueio USB

#### 📍 Criação e Edição da GPO:
1. No console `gpmc.msc`, clique com o botão direito sobre a pasta **`Objetos de Diretiva de Grupo`** ➔ **`Novo`** ➔ Digite: **`GPO_Seguranca_e_Padronizacao`** ➔ `OK`.
2. Clique com o botão direito sobre `GPO_Seguranca_e_Padronizacao` ➔ **`Editar...`**.

#### ✍️ Item A: Bloqueio do Painel de Controle e Configurações
* Navegue em: `Configuração do Usuário` ➔ `Diretivas` ➔ `Modelos Administrativos` ➔ `Painel de Controle`.
* Dê duplo clique em **`Proibir acesso ao Painel de Controle e à configuração do PC`** ➔ Selecione **`Habilitado`** ➔ `Aplicar` ➔ `OK`.

#### ✍️ Item B: Papel de Parede Institucional (Desktop Wallpaper UNC)
* Navegue em: `Configuração do Usuário` ➔ `Diretivas` ➔ `Modelos Administrativos` ➔ `Trabalho de Mesa (Desktop)` ➔ `Trabalho de Mesa (Desktop)`.
* Dê duplo clique em **`Papel de Parede do Trabalho de Mesa`** ➔ Selecione **`Habilitado`**.
* No campo *Nome do papel de parede*, digite obrigatoriamente o caminho UNC de rede:  
  **`\\esperancadigital.local\Dados\Publico\wallpaper.jpg`**
* No campo *Estilo do papel de parede*, selecione **`Preencher`** (Fill) ➔ `Aplicar` ➔ `OK`.

#### ✍️ Item C: Bloqueio de Dispositivos Removíveis (Pendrives USB)
* Navegue em: `Configuração do Computador` ➔ `Diretivas` ➔ `Modelos Administrativos` ➔ `Sistema` ➔ `Acesso a Armazenamento Removível`.
* Dê duplo clique em **`Discos Removíveis: Negar acesso de gravação`** ➔ Selecione **`Habilitado`** ➔ `OK`.
* Dê duplo clique em **`Discos Removíveis: Negar acesso de leitura`** ➔ Selecione **`Habilitado`** ➔ `OK`.

---

### 1.4. Proteção contra "Fogo Amigo" e Vinculação às OUs

> [!WARNING]
> **🚨 Incidente Real 06: Fogo Amigo (Bloqueio de Ferramentas Administrativas para a TI)**  
> Se a GPO que restringe o Painel de Controle for aplicada globalmente sem filtros, os próprios administradores de TI (`Domain Admins`) perderão acesso às ferramentas de suporte nas estações.

#### 🛡️ Como Isolar a Equipe de TI da GPO Restritiva:
1. No console `gpmc.msc`, clique com o botão esquerdo sobre **`GPO_Seguranca_e_Padronizacao`** no painel esquerdo.
2. No painel direito, clique na aba **`Delegação`** (Delegation) ➔ clique no botão **`Avançadas...`** (no canto inferior direito).
3. Clique em **`Adicionar...`** ➔ digite **`Domain Admins`** ➔ `OK`.
4. Com `Domain Admins` selecionado na lista, procure na coluna de permissões a linha **`Aplicar diretiva de grupo`** (Apply group policy) e marque a caixinha na coluna **`Negar`** (Deny).
5. Clique em **`Aplicar`** ➔ confirme o aviso do Windows clicando em **`Sim`** ➔ `OK`.

#### 🔗 Como Vincular a GPO às OUs de Destino:
1. Para aplicar as restrições aos usuários:
   * Clique com o botão direito sobre **`OU_Alunos`** (e `OU_Secretaria`, `OU_Recepcao`) ➔ **`Vincular um GPO existente...`** ➔ Selecione `GPO_Seguranca_e_Padronizacao` ➔ `OK`.
2. Para aplicar o bloqueio de USB às máquinas:
   * Clique com o botão direito sobre **`OU_Estacoes`** (onde residem os computadores) ➔ **`Vincular um GPO existente...`** ➔ Selecione `GPO_Seguranca_e_Padronizacao` ➔ `OK`.

---

## 📁 ETAPA 2: Servidor de Arquivos, Permissões NTFS e ABE Blindado

### 2.1. Estrutura de Pastas e Compartilhamento SMB

1. No servidor `SRV-DC01`, crie a pasta raiz **`C:\Dados`** e dentro dela as 8 subpastas:  
   `Diretoria`, `Coordenacao`, `Secretaria`, `Biblioteca`, `Recepcao`, `Professores`, `Alunos`, `Publico`.
2. Clique com o botão direito em `C:\Dados` ➔ **`Propriedades`** ➔ aba **`Compartilhamento`** ➔ **`Compartilhamento Avançado...`**.
3. Marque **`Compartilhar esta pasta`** (Nome: `Dados`) ➔ clique no botão **`Permissões`**.
4. Conceda **`Controle Total`** para o grupo **`Todos` (Everyone)** ➔ `Aplicar` ➔ `OK` ➔ `OK`.
5. Abra o **PowerShell (Admin)** e ative o **Access-Based Enumeration (ABE)**:
   ```powershell
   Set-SmbShare -Name "Dados" -FolderEnumerationMode AccessBased -Confirm:$false
   ```

---

### 2.2. Blindagem contra o "Drive Vazio" no ABE e Permissões NTFS

> [!CAUTION]
> **🚨 Incidente Real 03: O Drive Vazio no ABE (Usuário não enxerga nenhuma pasta)**  
> * **Sintoma:** Ao habilitar o ABE, quando o usuário acessa `\\esperancadigital.local\Dados`, a pasta aparece totalmente vazia, mesmo que ele pertença ao grupo da Secretaria ou Diretoria.  
> * **Causa:** O usuário não possui permissão para ler o diretório raiz `C:\Dados`, o que impede o ABE de avaliar as permissões das subpastas filhas.  
> * **Solução:** Na pasta raiz `C:\Dados`, conceda a permissão **"Listar conteúdo da pasta"** (List folder / read data) para `Domain Users`, aplicando obrigatoriamente em **"Apenas a esta pasta"** (This folder only).

#### 📍 Passo a Passo para Configurar a Raiz `C:\Dados`:
1. Clique com o botão direito em `C:\Dados` ➔ **`Propriedades`** ➔ aba **`Segurança`** ➔ **`Avançadas`**.
2. Clique em **`Adicionar`** ➔ **`Selecionar um principal`** ➔ Digite: **`Domain Users`** ➔ `OK`.
3. No campo *Aplica-se a*, selecione: **`Apenas esta pasta`** (This folder only).
4. Marque as permissões básicas: **`Ler e Executar`**, **`Listar conteúdo da pasta`** e **`Leitura`** ➔ clique em `OK` ➔ `Aplicar` ➔ `OK`.

---

### 2.3. Permissões NTFS Cirúrgicas nas Subpastas Departamentais

Para cada subpasta departamental (ex: `C:\Dados\Secretaria`):
1. Botão direito na subpasta ➔ **`Propriedades`** ➔ aba **`Segurança`** ➔ **`Avançadas`**.
2. Clique em **`Desabilitar herança`** ➔ escolha **`Converter permissões herdadas em permissões explícitas neste objeto`**.
3. Selecione o grupo genérico **`Usuários (SRV-DC01\Users)`** ou **`Domain Users`** e clique em **`Remover`**.
4. Clique em **`Adicionar`** ➔ **`Selecionar um principal`** ➔ digite o grupo do setor: **`Secretaria`** (ou `GRP_Secretaria`) ➔ `OK`.
5. Marque a permissão **`Modificar`** ➔ clique em `OK`.
6. Garanta que **`Domain Admins`**, **`Administrators`** e **`SYSTEM`** estejam mantidos com **`Controle Total`**.
7. Clique em `Aplicar` ➔ `OK` ➔ `OK`.

#### 📌 Permissão Especial na Pasta `C:\Dados\Publico`:
* Na pasta `Publico`, mantenha a herança ou adicione os grupos **`Domain Users`** e **`Domain Computers`** com a permissão **`Ler e Executar`** (necessário para que tanto o usuário quanto o computador consigam carregar o arquivo `wallpaper.jpg` durante o boot/logon).

---

### 2.4. Execução Automatizada via Script PowerShell (`Configura_Grupo3_Servicos.ps1`)

Para executar toda a criação de pastas, permissões NTFS, ABE blindado e mitigação de impressoras de forma automática:
```powershell
# Executar no Windows PowerShell (Admin) do Servidor SRV-DC01
Set-ExecutionPolicy Unrestricted -Scope Process -Force
C:\Users\adm_b\OneDrive\Documentos\Cetam_Atividade\Configura_Grupo3_Servicos.ps1
```

---

## 🖨️ ETAPA 3: Servidor de Impressão e Mitigação PrintNightmare

### 3.1. Instalação e Criação da Impressora de Rede Centralizada

1. No `Server Manager`, vá em `Gerenciar` ➔ `Adicionar Funções e Recursos` ➔ Instale **`Serviços de Impressão e Documentos`** (`Print-Server`).
2. Abra o console **`printmanagement.msc`** (`Gerenciamento de Impressão`).
3. Expanda `Servidores de Impressão` ➔ `SRV-DC01 (Local)` ➔ clique com o botão direito em **`Impressoras`** ➔ **`Adicionar Impressora...`**.
4. Selecione: **`Adicionar impressora TCP/IP ou Web Services por IP ou nome`** ➔ `Avançar`.
5. Tipo: `Dispositivo TCP/IP` ➔ Endereço IP: **`192.168.10.20`** (Nome da Impressora: **`IMP_Geral`**).
6. Driver: Para ambiente de simulação/laboratório, selecione o driver padrão **`Generic / Text Only`** (ou `Microsoft Software Printer Driver`).
7. Compartilhamento: Marque **`Compartilhar esta impressora`** (Nome de Compartilhamento: `IMP_Geral`) e marque obrigatoriamente **`Listar no Active Directory`** ➔ `Concluir`.

---

### 3.2. Mitigação Cirúrgica do Erro RPC 0x8007011b (PrintNightmare)

> [!CAUTION]
> **🚨 Incidente Real 05: Erro RPC 0x8007011b no Cliente ao Conectar na Impressora**  
> * **Sintoma:** Ao tentar conectar a impressora compartilhada do servidor na estação cliente, o Windows retorna o erro `0x8007011b`.  
> * **Causa:** Atualizações de segurança recentes da Microsoft (PrintNightmare) exigem criptografia RPC estrita que bloqueia conexões de spoolers compartilhados.

#### 💉 Correção no Registro do Servidor Windows:
Abra o PowerShell (Admin) e execute o comando:
```powershell
New-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Print" -Name "RpcAuthnLevelPrivacyEnabled" -Value 0 -PropertyType DWORD -Force
Restart-Service -Name Spooler -Force
```

#### ✍️ Desativação de "Point and Print Restrictions" via GPO:
1. No console `gpmc.msc`, edite a `GPO_Seguranca_e_Padronizacao`.
2. Navegue em: `Configuração do Computador` ➔ `Diretivas` ➔ `Modelos Administrativos` ➔ `Impressoras`.
3. Localize: **`Restrições de Apontar e Imprimir`** (Point and Print Restrictions) ➔ Selecione **`Desabilitado`** ➔ `Aplicar` ➔ `OK`.

#### 🔗 Implantação Moderna via Group Policy Preferences (GPP):
No editor da GPO, navegue até: `Configuração do Usuário` ➔ `Preferências` ➔ `Configurações do Painel de Controle` ➔ `Impressoras` ➔ Botão direito ➔ `Novo` ➔ `Impressora de Rede` ➔ Ação: `Substituir` (Replace) ➔ Caminho: `\\SRV-DC01\IMP_Geral`.

---

## 🛡️ ETAPA 4: Windows Defender Firewall e Conectividade DNS

### 4.1. Configuração do Firewall com Segurança Avançada

1. Pressione **`Win + R`**, digite **`wf.msc`** e pressione Enter.
2. Certifique-se de que os perfis de **Domínio**, **Privado** e **Público** estejam **Ativados**.
3. No PowerShell (Admin), execute o comando de liberação segura:
   ```powershell
   # Libera tráfego SMB e RPC para arquivos e spooler de impressão
   Enable-NetFirewallRule -DisplayGroup "File and Printer Sharing"
   # Libera resposta a diagnósticos de Ping (ICMPv4)
   Enable-NetFirewallRule -Name "FPS-ICMP4-ERQ-In"
   ```

---

### 4.2. Validação da Zona de Pesquisa Inversa DNS (Incidente Real 04)

> [!NOTE]
> **🚨 Incidente Real 04: Falha na Autenticação Kerberos ao Acessar por Nome (`\\SRV-DC01`)**  
> * **Sintoma:** O acesso ao compartilhamento funciona por IP (`\\192.168.10.2\Dados`), mas falha ou pede senha repetidamente ao usar o nome NetBIOS/FQDN (`\\SRV-DC01\Dados`).  
> * **Causa:** O protocolo de autenticação Kerberos exige que o servidor possua resolução reversa (PTR) cadastrada no DNS.  
> * **Solução:** No console **`dnsmgmt.msc`**, crie a **Zona de Pesquisa Inversa** para a subrede `192.168.10.x` (`10.168.192.in-addr.arpa`) e certifique-se de que o registro PTR para `192.168.10.2` aponte para `SRV-DC01.esperancadigital.local`.

---

## 📊 ETAPA 5: Matriz de Testes Finais (Passagem de Bastão para o Grupo 4)

Execute esta bateria de testes para certificar que todos os requisitos do Grupo 3 estão 100% validados antes da auditoria do **Grupo 4**:

| # | Item de Teste | Procedimento / Comando no Cliente | Usuário / Credencial | Resultado Esperado | Status |
|---|---|---|---|---|---|
| **01** | **Resolução DNS** | Prompt: `nslookup esperancadigital.local` | Qualquer usuário | Retorna o IP do DC: `192.168.10.2` | [ ] Ok |
| **02** | **DNS Reverso** | Prompt: `nslookup 192.168.10.2` | Qualquer usuário | Retorna o nome: `SRV-DC01.esperancadigital.local` | [ ] Ok |
| **03** | **GPO Senha** | Ctrl+Alt+Del ➔ Alterar senha para `123` | `joao.silva` / `@esperancadigital-2026` | Recusado por requisitos de complexidade/tamanho | [ ] Ok |
| **04** | **GPO Painel** | Pressionar `Win + R` ➔ digite `control` | `joao.silva` / `@esperancadigital-2026` | Mensagem de restrição administrativa do sistema | [ ] Ok |
| **05** | **Fogo Amigo (TI)** | `Win + R` ➔ digite `control` | `Administrator` / `Manaus@` | Painel de Controle abre normalmente sem bloqueios | [ ] Ok |
| **06** | **GPO Wallpaper** | Logon na estação de trabalho | `joao.silva` / `@esperancadigital-2026` | Exibe imagem institucional sem tela preta | [ ] Ok |
| **07** | **GPO USB** | Conectar Pendrive USB e tentar abrir | `joao.silva` / `@esperancadigital-2026` | Janela de diálogo informando "Acesso Negado" | [ ] Ok |
| **08** | **Filtro ABE** | Acessar rede: `\\esperancadigital.local\Dados` | `sec.usuario` / `@esperancadigital-2026` | Exibe apenas as pastas `Secretaria` e `Publico` | [ ] Ok |
| **09** | **NTFS Permitido** | Criar arquivo em `\\SRV-DC01\Dados\Secretaria` | `sec.usuario` / `@esperancadigital-2026` | Permissão concedida para criar e editar arquivos | [ ] Ok |
| **10** | **NTFS Bloqueado** | Acessar caminho: `\\SRV-DC01\Dados\Diretoria` | `sec.usuario` / `@esperancadigital-2026` | Bloqueio imediato com aviso "Acesso Negado" | [ ] Ok |
| **11** | **Impressora GPO** | Disparar impressão de teste em `IMP_Geral` | `sec.usuario` / `@esperancadigital-2026` | Trabalho enviado com sucesso sem erro `0x8007011b` | [ ] Ok |
| **12** | **Firewall Ping** | Prompt: `ping 192.168.10.2` | Qualquer estação da LAN | 0% de perda de pacotes com latência <1ms | [ ] Ok |

---

## 🏁 Conclusão e Governança

Com a aplicação das diretivas e mitigações deste manual, a infraestrutura do **Instituto Esperança Digital** atinge conformidade total com as melhores práticas de governança e segurança do Microsoft Windows Server 2022. O ambiente está estável, auditável e pronto para a homologação técnica do **Grupo 4**.
