# Funcoes usadas por instalar.ps1 e remover.ps1.
# Backup e estado ficam no mesmo lugar e formato do instalador 1.0 (Python), para que um remova o que o outro instalou.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PacoteDir = Split-Path -Parent $PSScriptRoot
$PastaApp = Join-Path $env:LOCALAPPDATA 'ZeroParades-Traducao-PTBR'
$PastaBackup = Join-Path $PastaApp 'backup'
$Estado = Join-Path $PastaApp 'estado.json'

function Sha256([string]$Caminho) {
    return (Get-FileHash -LiteralPath $Caminho -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Ler-Manifesto {
    return Get-Content -LiteralPath (Join-Path $PacoteDir 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Bibliotecas-Steam {
    $steams = @()
    foreach ($c in @(@('HKCU:\Software\Valve\Steam', 'SteamPath'), @('HKLM:\SOFTWARE\WOW6432Node\Valve\Steam', 'InstallPath'))) {
        try { $steams += [string](Get-ItemProperty -LiteralPath $c[0] -Name $c[1] -ErrorAction Stop).($c[1]) } catch { }
    }
    $steams += 'C:\Program Files (x86)\Steam'
    $libs = @()
    foreach ($steam in $steams) {
        if (-not $steam) { continue }
        $libs += $steam
        $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf -PathType Leaf) {
            foreach ($m in [regex]::Matches((Get-Content -LiteralPath $vdf -Raw), '"path"\s+"([^"]+)"')) {
                $libs += $m.Groups[1].Value.Replace('\\', '\')
            }
        }
    }
    return $libs | Select-Object -Unique
}

function Achar-Jogo([string]$Jogo, [bool]$Interativo) {
    if ($Jogo) {
        if (-not (Test-Path -LiteralPath (Join-Path $Jogo 'ZeroParades_Data'))) { throw "Nao achei o jogo em: $Jogo" }
        return $Jogo
    }
    foreach ($lib in Bibliotecas-Steam) {
        $c = Join-Path $lib 'steamapps\common\Zero Parades'
        if (Test-Path -LiteralPath (Join-Path $c 'ZeroParades_Data')) { return $c }
    }
    if (-not $Interativo) { throw 'Nao encontrei ZERO PARADES nas bibliotecas da Steam. Informe a pasta com -Jogo.' }
    Write-Host 'Nao encontrei ZERO PARADES nas bibliotecas da Steam.'
    $c = (Read-Host 'Cole aqui a pasta do jogo (a que contem ZeroParades_Data)').Trim().Trim('"')
    if (-not $c -or -not (Test-Path -LiteralPath (Join-Path $c 'ZeroParades_Data'))) { throw 'Pasta invalida.' }
    return $c
}

function Conferir-JogoFechado {
    if (@(Get-Process -Name 'ZeroParades' -ErrorAction SilentlyContinue).Count -gt 0) {
        throw 'ZERO PARADES esta aberto. Feche o jogo e tente de novo. Nada foi alterado.'
    }
}

# Lista os arquivos do manifesto com o caminho do payload, o do jogo e o do backup.
function Arquivos($Manifesto, [string]$Jogo) {
    foreach ($a in $Manifesto.arquivos) {
        [pscustomobject]@{
            nome    = $a.nome
            payload = Join-Path (Join-Path $PacoteDir 'payload') $a.payload
            alvo    = Join-Path $Jogo $a.alvo
            backup  = Join-Path $PastaBackup $a.payload
            origem  = $a.origem_sha256
            novo    = $a.payload_sha256
        }
    }
}

# Copia por um temporario na mesma pasta, confere o hash e so entao troca o arquivo de destino.
function Copiar-Verificado([string]$Origem, [string]$Destino, [string]$Esperado) {
    $tmp = "$Destino.ptbr-tmp"
    try {
        Copy-Item -LiteralPath $Origem -Destination $tmp -Force
        if ((Sha256 $tmp) -ne $Esperado) { throw "A copia nao conferiu: $Destino" }
        if (Test-Path -LiteralPath $Destino) { [System.IO.File]::Replace($tmp, $Destino, [NullString]::Value) }
        else { Move-Item -LiteralPath $tmp -Destination $Destino }
    }
    finally {
        if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force }
    }
    if ((Sha256 $Destino) -ne $Esperado) { throw "O arquivo gravado nao conferiu: $Destino" }
}

function Gravar-Estado($Valor) {
    New-Item -ItemType Directory -Force -Path $PastaApp | Out-Null
    [System.IO.File]::WriteAllText($Estado, ($Valor | ConvertTo-Json), (New-Object System.Text.UTF8Encoding($false)))
}

function Mensagem-Erro($Erro) {
    for ($e = $Erro.Exception; $e; $e = $e.InnerException) {
        if ($e -is [System.UnauthorizedAccessException]) {
            return 'Sem permissao para alterar os arquivos do jogo. Feche o jogo e tente de novo; se persistir, ' +
                   'execute como administrador (botao direito > Executar como administrador).'
        }
    }
    return $Erro.Exception.Message
}

# Roda a acao, mostra o erro de forma simples e segura a janela aberta quando veio do .cmd.
function Executar([scriptblock]$Acao, [bool]$Interativo) {
    $codigo = 0
    try { & $Acao }
    catch {
        $codigo = 1
        Write-Host ''
        Write-Host "ERRO: $(Mensagem-Erro $_)" -ForegroundColor Red
    }
    if ($Interativo) { Read-Host "`nPressione Enter para fechar" | Out-Null }
    exit $codigo
}
