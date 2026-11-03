# Remove a traducao: volta os arquivos originais a partir do backup feito na instalacao.
# Uso: powershell -ExecutionPolicy Bypass -File scripts\remover.ps1 [-Jogo "D:\...\Zero Parades"] [-Interativo]
param([string]$Jogo, [switch]$Interativo)
. (Join-Path $PSScriptRoot 'comum.ps1')

function Remover {
    $m = Ler-Manifesto
    Write-Host "ZERO PARADES - Traducao Portugues (Brasil) v$($m.versao)`n"
    $pasta = Achar-Jogo $Jogo ([bool]$Interativo)
    Write-Host "Jogo encontrado em: $pasta`n"
    Conferir-JogoFechado

    $arquivos = @(Arquivos $m $pasta)
    foreach ($a in $arquivos) {
        if (-not (Test-Path -LiteralPath $a.backup -PathType Leaf) -or (Sha256 $a.backup) -ne $a.origem) {
            throw 'Nao achei um backup valido da instalacao. Para voltar ao original, use na Steam: ' +
                  'Propriedades > Arquivos instalados > Verificar integridade.'
        }
        if ((Test-Path -LiteralPath $a.alvo -PathType Leaf) -and (Sha256 $a.alvo) -notin @($a.novo, $a.origem)) {
            throw 'Os arquivos do jogo mudaram desde a instalacao (provavelmente a Steam atualizou o jogo). ' +
                  'Nada foi alterado; a Steam ja deve ter colocado os arquivos originais.'
        }
    }
    foreach ($a in $arquivos) { Copiar-Verificado $a.backup $a.alvo $a.origem }
    if (Test-Path -LiteralPath $Estado) { Remove-Item -LiteralPath $Estado -Force }

    Write-Host "`nREMOCAO CONCLUIDA. O jogo voltou aos arquivos originais." -ForegroundColor Green
}

Executar { Remover } ([bool]$Interativo)
