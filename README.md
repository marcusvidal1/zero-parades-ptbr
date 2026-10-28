# ZERO PARADES: Director's Cut — Tradução Português (Brasil)

Tradução de fã completa do jogo (73.708 textos): diálogos, pensamentos, missões, itens, menus e configurações. A tradução ocupa o lugar do idioma Espanhol (`es_mx`) no jogo.

Publicada no Nexus Mods: https://www.nexusmods.com/zeroparadesfordeadspies/mods/21

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

`instalador_ptbr.py` acha o jogo pelas bibliotecas da Steam, confere o SHA-256 do bundle original (recusa outra versão do jogo), faz backup em `%LOCALAPPDATA%\ZeroParades-Traducao-PTBR`, aplica `dados/traducao-ptbr.json` na tabela `es_mx` e zera o CRC no catálogo. Para gerar o `.exe`:

```
python -m PyInstaller --onefile --console --name Instalar-Traducao-PTBR --collect-all UnityPy pacote/instalador_ptbr.py
```

Quando a Steam atualizar o jogo: rode o `extract.py` no bundle novo, ajuste `BUNDLE`, `BUNDLE_ORIGINAL_SHA256` e `BUILD_STEAM` no instalador, refaça o build e exporte de novo `pacote/dados/traducao-ptbr.json` a partir do bundle montado.
