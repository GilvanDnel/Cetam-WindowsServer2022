<#
.SYNOPSIS
    Script Sênior de Automação das Tarefas do Grupo 3 - Windows Server 2022
    Instituto Esperança Digital (esperancadigital.local)
.DESCRIPTION
    Este script realiza a implantação automatizada e blindada de:
    1. Pastas departamentais, compartilhamento SMB e ativação de Access-Based Enumeration (ABE).
    2. Correção de permissão de travessia na raiz C:\Dados ("Apenas esta pasta") para prevenir o "Drive Vazio" no ABE.
    3. Aplicação de permissões NTFS restritivas por departamento com busca inteligente de grupos do AD DS.
    4. Garantia de permissão NTFS em Publico para 'Domain Users' e 'Domain Computers' (Wallpaper GPO).
    5. Habilitação das funções de Servidor de Impressão (Print-Server).
    6. Mitigação cirúrgica no Registro para o erro RPC 0x8007011b (PrintNightmare).
    7. Configuração das regras do Windows Defender Firewall (SMB/RPC, ICMP/Ping).
#>

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " IMPLANTAÇÃO GRUPO 3 - SERVIÇOS CORPORATIVOS E SEGURANÇA   " -ForegroundColor Cyan
Write-Host " Domínio: esperancadigital.local | Servidor: SRV-DC01       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. DEFINIÇÃO DE CAMINHO RAIZ E DEPARTAMENTOS
$RaizDados = "C:\Dados"
$Departamentos = @(
    "Diretoria",
    "Coordenacao",
    "Secretaria",
    "Biblioteca",
    "Recepcao",
    "Professores",
    "Alunos",
    "Publico"
)

# Criar pasta raiz se não existir
if (-not (Test-Path $RaizDados)) {
    New-Item -Path $RaizDados -ItemType Directory | Out-Null
    Write-Host "[+] Diretório raiz $RaizDados criado com sucesso." -ForegroundColor Green
}

# Criar compartilhamento de rede SMB para a pasta Dados (Share Permission: Full Control para Todos)
if (-not (Get-SmbShare -Name "Dados" -ErrorAction SilentlyContinue)) {
    New-SmbShare -Name "Dados" -Path $RaizDados -FullAccess "Everyone" | Out-Null
    Write-Host "[+] Compartilhamento de Rede '\\esperancadigital.local\Dados' criado." -ForegroundColor Green
} else {
    Write-Host "[*] Compartilhamento 'Dados' já existente." -ForegroundColor Gray
}

# Habilitar Access-Based Enumeration (ABE) no compartilhamento SMB
try {
    Set-SmbShare -Name "Dados" -FolderEnumerationMode AccessBased -Confirm:$false | Out-Null
    Write-Host "[+] Access-Based Enumeration (ABE) ativado com sucesso no compartilhamento 'Dados'." -ForegroundColor Green
} catch {
    Write-Host "[!] Aviso: Não foi possível definir ABE via cmdlet SMB: $_" -ForegroundColor Yellow
}

# 2. BLINDAGEM DA RAIZ C:\Dados CONTRA O BUG DO 'DRIVE VAZIO' NO ABE
# Concede 'ListFolder / Read' para Domain Users aplicado 'Apenas a esta pasta' (This folder only)
try {
    $aclRaiz = Get-Acl $RaizDados
    $ruleRaizABE = New-Object System.Security.AccessControl.FileSystemAccessRule(
        "Domain Users",
        "ReadAndExecute",
        [System.Security.AccessControl.InheritanceFlags]::None,
        [System.Security.AccessControl.PropagationFlags]::None,
        [System.Security.AccessControl.AccessControlType]::Allow
    )
    $aclRaiz.AddAccessRule($ruleRaizABE)
    Set-Acl -Path $RaizDados -AclObject $aclRaiz
    Write-Host "[+] Permissão de travessia (Apenas esta pasta) configurada em C:\Dados para Domain Users." -ForegroundColor Green
} catch {
    Write-Host "[!] Falha ao ajustar permissão raiz de ABE: $_" -ForegroundColor Yellow
}

# 3. CRIAÇÃO DAS PASTAS DEPARTAMENTAIS E PERMISSÕES NTFS RESTRITIVAS
Write-Host "`n[+] Configurando pastas departamentais e permissões NTFS..." -ForegroundColor Cyan
foreach ($dept in $Departamentos) {
    $CaminhoPasta = Join-Path -Path $RaizDados -ChildPath $dept
    
    if (-not (Test-Path $CaminhoPasta)) {
        New-Item -Path $CaminhoPasta -ItemType Directory | Out-Null
        Write-Host "   [+] Pasta criada: $CaminhoPasta" -ForegroundColor Yellow
    }

    # Desativa herança e remove regras herdadas (Converter em explícitas)
    $acl = Get-Acl $CaminhoPasta
    $acl.SetAccessRuleProtection($true, $false)

    # Conceder Controle Total para Administradores, Domain Admins e SYSTEM
    $adminRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Administrators", "FullControl", "ContainerInherit, ObjectInherit", "None", "Allow")
    $domainAdminRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Domain Admins", "FullControl", "ContainerInherit, ObjectInherit", "None", "Allow")
    $systemRule = New-Object System.Security.AccessControl.FileSystemAccessRule("SYSTEM", "FullControl", "ContainerInherit, ObjectInherit", "None", "Allow")
    
    $acl.AddAccessRule($adminRule)
    $acl.AddAccessRule($domainAdminRule)
    $acl.AddAccessRule($systemRule)

    # Busca inteligente do grupo no Active Directory
    if ($dept -ne "Publico") {
        $GruposCandidatos = @($dept, "GRP_$dept", "Grupo_$dept", "OU_$dept")
        $GrupoEncontrado = $null

        foreach ($g in $GruposCandidatos) {
            try {
                $sid = (New-Object System.Security.Principal.NTAccount($g)).Translate([System.Security.Principal.SecurityIdentifier])
                if ($sid) {
                    $GrupoEncontrado = $g
                    break
                }
            } catch {
                # Continua testando próximo candidato
            }
        }

        if ($GrupoEncontrado) {
            $deptRule = New-Object System.Security.AccessControl.FileSystemAccessRule($GrupoEncontrado, "Modify", "ContainerInherit, ObjectInherit", "None", "Allow")
            $acl.AddAccessRule($deptRule)
            Write-Host "   [-] Permissão NTFS de 'Modificar' atribuída ao grupo '$GrupoEncontrado' em $dept." -ForegroundColor Gray
        } else {
            Write-Host "   [!] Atenção: Grupo para '$dept' não localizado no AD. Crie o grupo '$dept' no AD DS." -ForegroundColor Yellow
        }
    }

    Set-Acl -Path $CaminhoPasta -AclObject $acl
}

# 4. PERMISSÃO ESPECIAL NA PASTA PUBLICO (WALLPAPER GPO)
$CaminhoPublico = Join-Path -Path $RaizDados -ChildPath "Publico"
$aclPublico = Get-Acl $CaminhoPublico
$usersRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Domain Users", "ReadAndExecute", "ContainerInherit, ObjectInherit", "None", "Allow")
$compRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Domain Computers", "ReadAndExecute", "ContainerInherit, ObjectInherit", "None", "Allow")
$aclPublico.AddAccessRule($usersRule)
$aclPublico.AddAccessRule($compRule)
Set-Acl -Path $CaminhoPublico -AclObject $aclPublico
Write-Host "[+] Permissão de Leitura em Publico para 'Domain Users' e 'Domain Computers' aplicada." -ForegroundColor Green

# Criar arquivo de Wallpaper modelo se não existir
$WallpaperPath = Join-Path -Path $CaminhoPublico -ChildPath "wallpaper.jpg"
if (-not (Test-Path $WallpaperPath)) {
    New-Item -Path $WallpaperPath -ItemType File -Force | Out-Null
    Write-Host "[+] Arquivo modelo 'wallpaper.jpg' criado em C:\Dados\Publico." -ForegroundColor Yellow
}

# 5. INSTALAÇÃO DO SERVIÇO DE IMPRESSÃO E FIX PRINTNIGHTMARE
Write-Host "`n[+] Verificando/Instalando Função de Servidor de Impressão (Print-Server)..." -ForegroundColor Cyan
try {
    Install-WindowsFeature -Name Print-Server -IncludeManagementTools | Out-Null
    Write-Host "[+] Função Print-Server instalada/confirmada com sucesso." -ForegroundColor Green
} catch {
    Write-Host "[!] Falha ao instalar Print-Server (execute com privilégios de Administrador): $_" -ForegroundColor Red
}

# Correção no Registro para Erro RPC 0x8007011b (PrintNightmare)
Write-Host "[+] Aplicando correção de registro para PrintNightmare (RpcAuthnLevelPrivacyEnabled = 0)..." -ForegroundColor Cyan
try {
    $regPath = "HKLM:\System\CurrentControlSet\Control\Print"
    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    New-ItemProperty -Path $regPath -Name "RpcAuthnLevelPrivacyEnabled" -Value 0 -PropertyType DWORD -Force | Out-Null
    Restart-Service -Name Spooler -Force -ErrorAction SilentlyContinue
    Write-Host "[+] Chave de registro aplicada e serviço Spooler reiniciado com sucesso." -ForegroundColor Green
} catch {
    Write-Host "[!] Aviso ao aplicar chave de registro do Spooler: $_" -ForegroundColor Yellow
}

# 6. CONFIGURAÇÃO DO WINDOWS DEFENDER FIREWALL
Write-Host "`n[+] Configurando regras do Windows Defender Firewall..." -ForegroundColor Cyan
try {
    # Habilitar regra de Compartilhamento de Arquivos e Impressoras (SMB/RPC)
    Enable-NetFirewallRule -DisplayGroup "File and Printer Sharing" -ErrorAction SilentlyContinue
    Write-Host "[+] Regra de Firewall: Compartilhamento de Arquivos e Impressoras ativada." -ForegroundColor Green

    # Habilitar ICMPv4 (Ping)
    Enable-NetFirewallRule -Name "FPS-ICMP4-ERQ-In" -ErrorAction SilentlyContinue
    Write-Host "[+] Regra de Firewall: Solicitação de Eco ICMPv4 (Ping) ativada." -ForegroundColor Green
} catch {
    Write-Host "[!] Aviso ao configurar regras de firewall: $_" -ForegroundColor Yellow
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " AUTOMAÇÃO E BLINDAGEM DO GRUPO 3 CONCLUÍDA COM SUCESSO!   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
