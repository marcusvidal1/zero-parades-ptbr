# ZERO PARADES: Director's Cut — Tradução Português (Brasil)

Tradução de fã completa do jogo (73.708 textos): diálogos, pensamentos, missões, itens, menus e configurações. A tradução ocupa o lugar do idioma Espanhol (`es_mx`) no jogo.

Publicada no Nexus Mods: https://www.nexusmods.com/zeroparadesfordeadspies/mods/22

Tradução de fã, sem relação oficial com a ZA/UM. Feita com auxílio de IA (Claude e ChatGPT/Codex) e revisada. Este repositório **não** contém arquivos do jogo.

## O que tem aqui

| Caminho | Conteúdo |
|---|---|
| `work/pt/main.json` | a tradução: chave da tabela `es_mx` → texto em pt-BR |
| `GLOSSARIO.md` | termos e decisões de tradução |
| `tools/` | scripts de extração, tradução em lotes, build e instalação local |
| `pacote/` | instalador do Nexus (`instalador_ptbr.py`), atalhos `.cmd`, LEIA-ME e os textos finais (`dados/traducao-ptbr.json`) |
| `release/` | descrição da página do Nexus e tutorial de publicação |

## Fluxo de trabalho (requer Python 3.12 + UnityPy)

Os textos ficam no bundle `ZeroParades_Data/StreamingAssets/aa/StandaloneWindows64/g5ibkj7vdwf2g67g_assets_all_*.bundle` do jogo.

1. **Extrair o inglês** (gera `work/english.json`, não versionado): `python -I -X utf8 tools/extract.py <bundle_original> work`
2. **Traduzir em lotes**: `tools/step.py next 2300` mostra o próximo lote; a tradução vai em `work/pt/cur.txt` (`i|texto`) e entra no `main.json` com `tools/step.py save work/pt/cur.txt`.
3. **Montar o bundle**: `python -I -X utf8 tools/build.py <bundle_original> work/english.json work/build/<mesmo nome do bundle> work/pt/main.json` (valida tags, `{0}` e asteriscos contra o original).
4. **Instalar localmente**: `python -I tools/install.py "<pasta do jogo>" work/build/<bundle> backup` — copia o bundle e zera o CRC dele no `catalog.bin` (o jogo checa o CRC). `tools/restore.py` volta o original.

## Instalador para usuários (`pacote/`)

`instalador_ptbr.py` acha o jogo pelas bibliotecas da Steam, confere o SHA-256 do bundle original (recusa outra versão do jogo), faz backup em `%LOCALAPPDATA%\ZeroParades-Traducao-PTBR`, aplica `dados/traducao-ptbr.json` na tabela `es_mx` e zera o CRC no catálogo.

Desde a 1.0.1 o pacote do Nexus não leva Python nem `.exe` (a 1.0.0 tinha um `.exe` do PyInstaller e a 1.0 um Python portátil; os dois caíam na quarentena do Nexus). Ele leva:
- `payload\`: o bundle de textos e o `catalog.bin` já traduzidos, gerados pelo próprio `instalador_ptbr.py`;
- `manifest.json`: SHA-256 de cada arquivo original e traduzido;
- `scripts\instalar.ps1` / `remover.ps1` (+ `comum.ps1`), chamados pelos `.cmd`. Conferem os hashes, copiam e restauram com o mesmo backup e `estado.json` do instalador Python, então um desfaz o que o outro instalou.

Para gerar: `build_py\ZeroParades-Traducao-PTBR\runtime\python.exe -X utf8 tools\empacotar.py backup\build-<buildid>` (qualquer Python com UnityPy serve; a pasta tem o bundle e o `catalog.bin` originais daquele build). Sai em `build_ps\` e `release\ZeroParades-Traducao-PTBR-<versão>.zip`.

Quando a Steam atualizar o jogo: copie o bundle de textos e o `catalog.bin` originais para `backup\build-<buildid>\`, rode o `extract.py` no bundle novo e compare com o inglês anterior; ajuste `BUNDLE`, `BUNDLE_ORIGINAL_SHA256` e `BUILD_STEAM` no instalador e `VERSAO` no `empacotar.py`, e gere o pacote. Na atualização para o build 26138821 (versão 1.1.40910) a tabela `es_mx` não mudou, então o `traducao-ptbr.json` ficou igual.
