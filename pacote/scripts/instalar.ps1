# Instala a traducao: confere os arquivos originais do jogo, faz backup e copia os de payload\.
# Uso: powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1 [-Jogo "D:\...\Zero Parades"] [-Interativo]
param([string]$Jogo, [switch]$Interativo)
. (Join-Path $PSScriptRoot 'comum.ps1')

function Instalar {
    $m = Ler-Manifesto
    Write-Host "ZERO PARADES - Traducao Portugues (Brasil) v$($m.versao)`n"
    $pasta = Achar-Jogo $Jogo ([bool]$Interativo)
    Write-Host "Jogo encontrado em: $pasta`n"
    Conferir-JogoFechado

    $arquivos = @(Arquivos $m $pasta)
    foreach ($a in $arquivos) {
        if (-not (Test-Path -LiteralPath $a.payload -PathType Leaf) -or (Sha256 $a.payload) -ne $a.novo) {
            throw "O pacote esta incompleto ou corrompido ($($a.nome)). Extraia o ZIP inteiro de novo antes de instalar."
        }
        if (-not (Test-Path -LiteralPath $a.alvo -PathType Leaf)) {
            throw "O arquivo $($a.nome) do jogo nao existe. Provavelmente o jogo foi atualizado e esta versao da " +
                  'traducao ainda nao e compativel.'
        }
        $a | Add-Member -NotePropertyName atual -NotePropertyValue (Sha256 $a.alvo)
    }
    if (@($arquivos | Where-Object { $_.atual -ne $_.novo }).Count -eq 0) {
        Write-Host 'A traducao ja esta instalada.' -ForegroundColor Green
        return
    }
    if (@($arquivos | Where-Object { $_.atual -ne $_.origem }).Count -gt 0) {
        throw "Os arquivos do jogo nao sao os originais desta versao (o jogo atualizou ou ha outro mod instalado). " +
              "Nada foi alterado.`nNa Steam: Propriedades > Arquivos instalados > Verificar integridade, e tente de novo."
    }

    Write-Host 'Fazendo backup...'
    New-Item -ItemType Directory -Force -Path $PastaBackup | Out-Null
    foreach ($a in $arquivos) { Copiar-Verificado $a.alvo $a.backup $a.origem }

    Write-Host 'Aplicando a traducao...'
    try {
        foreach ($a in $arquivos) { Copiar-Verificado $a.payload $a.alvo $a.novo }
    }
    catch {
        Write-Host 'Falhou; voltando os arquivos originais...' -ForegroundColor Yellow
        foreach ($a in $arquivos) { Copiar-Verificado $a.backup $a.alvo $a.origem }
        throw
    }
    $bundle = $arquivos | Where-Object { $_.nome -eq 'textos' }
    Gravar-Estado ([ordered]@{ versao_pacote = $m.versao; jogo = $pasta; bundle_instalado_sha256 = $bundle.novo })

    Write-Host "`nINSTALACAO CONCLUIDA." -ForegroundColor Green
    Write-Host 'No jogo, va em Configuracoes > Idioma e escolha a opcao Espanhol (depois de escolhida, ela aparece como "Portugues (BR)").'
}

Executar { Instalar } ([bool]$Interativo)
