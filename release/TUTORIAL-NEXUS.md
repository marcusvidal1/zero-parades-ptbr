# Como publicar a tradução no Nexus Mods

Tudo que você vai precisar está na pasta `ZeroParades-PTBR\release`:

| Arquivo | Para quê |
|---|---|
| `ZeroParades-Traducao-PTBR-1.0.0.zip` | o arquivo que as pessoas vão baixar |
| `DESCRICAO-NEXUS-BBCODE.txt` | o texto da página (já formatado pro editor do Nexus) |
| `DESCRICAO-NEXUS.txt` | o mesmo texto, sem formatação, e o resumo curto |

> A tela do Nexus muda de vez em quando. Se algum nome de botão estiver diferente, procure algo parecido — os passos são sempre esses.

---

## Antes de começar (5 minutos)

1. **Conta no Nexus**: entre em [nexusmods.com](https://www.nexusmods.com) e faça login (ou crie a conta). Não precisa ser Premium.
2. **Tire 3 a 5 prints do jogo em português** (tecla F12 na Steam, ou Win+Shift+S). Boas ideias:
   - uma tela de diálogo com escolhas;
   - o Dossiê com as habilidades;
   - o Diário com uma missão;
   - o menu de Configurações com "Português (BR)".
   Escolha o melhor como **imagem principal** (é a que aparece na lista de mods).

---

## Passo 1 — Criar a página do mod

1. No site, abra o menu do seu perfil (canto superior direito) e clique em **Upload mod** (ou vá em *Mods > Upload a mod*).
2. **Jogo**: digite e escolha **ZERO PARADES** (é a mesma página de jogo onde estava o mod PT-BR antigo).
3. Preencha:
   - **Mod name**: `ZERO PARADES - Tradução Português (Brasil)`
   - **Language**: `Portuguese` (ou "Brazilian Portuguese", se existir).
   - **Version**: `1.0.0`
   - **Category**: `Translations` / `Language` (se não houver, use "Miscellaneous" ou "Utilities").
   - **Author**: seu nome de usuário.
   - **Brief overview / Summary**: copie o **RESUMO** do `DESCRICAO-NEXUS.txt`:
     > Tradução completa de ZERO PARADES: Director's Cut para português do Brasil, com instalador automático e remoção em um clique.
4. **Description**: no editor, mude para o modo de código (o botão `[BBCode]` ou `</>` na barra do editor), apague o que tiver e cole **tudo** do `DESCRICAO-NEXUS-BBCODE.txt`. Volte pro modo visual pra conferir.
5. **Tags / conteúdo com IA** — **importante**: o Nexus pede que mods com tradução feita por IA sejam marcados. Marque **"AI-Generated Content"** (é a categoria que cobre traduções feitas com IA). Se você mesmo for usar imagem de capa gerada por IA, marque também "AI Media". Marcar errado pode fazer a moderação esconder o mod.
6. Salve e avance (**Save & continue** / **Next**).

## Passo 2 — Imagens

1. Na aba **Media / Images**, envie os prints.
2. Defina o melhor como **Primary image** (imagem principal).
3. Salve.

## Passo 3 — Enviar o arquivo

1. Vá na aba **Files**.
2. Clique em **Add a file** (ou "Upload file") e escolha `ZeroParades-Traducao-PTBR-1.0.0.zip`.
3. Preencha:
   - **File name**: `Tradução PT-BR - Instalador`
   - **Version**: `1.0.0`
   - **Category**: **Main files**
   - **Description**: `Instalador automático. Extraia, feche o jogo e rode INSTALAR-TRADUCAO.cmd. Compatível com o build Steam 25778956.`
   - **Remove/replace older files**: deixe desmarcado (é o primeiro arquivo).
4. Espere o upload chegar a 100% e salve.
5. Se o Nexus perguntar sobre o gerenciador de mods (Vortex/"mod manager download"): **desative** o botão de mod manager — esse mod se instala pelo próprio instalador, não pelo Vortex.

## Passo 4 — Permissões e requisitos

1. **Permissions**: sugestão:
   - Upload em outros sites: **não** (sem pedir antes).
   - Modificar/reaproveitar: **com permissão**.
   - Conversão para outros jogos: **não**.
   - Uso de assets em mods pagos: **não**.
2. **Requirements**: nenhum (o instalador já leva tudo que precisa).
3. Salve.

## Passo 5 — Publicar

1. Confira a página em **Preview**.
2. Clique em **Publish**. O mod pode ficar alguns minutos (às vezes horas) em análise antes de aparecer pra todo mundo — o `.exe` passa por verificação de vírus do Nexus.

---

## Depois de publicado

- **Comentários (aba Posts)**: as pessoas vão avisar de erros de tradução. Me mande o print e o trecho, que eu corrijo no `main.json` e gero uma versão nova.
- **Quando a Steam atualizar o jogo**: esta versão vai recusar a instalação (de propósito). Me chame pra gerar a **1.0.1**. Pra atualizar a página:
  1. aba **Files** > **Add a file** com o zip novo;
  2. versão `1.0.1`, categoria **Main files**;
  3. marque pra mover o arquivo antigo para **Old files**;
  4. atualize a **Version** da página e o build citado na descrição;
  5. escreva o que mudou na aba **Changelogs**.
- **Aviso do SmartScreen / antivírus**: é comum em `.exe` sem assinatura digital. A descrição já explica como passar. Se algum antivírus reclamar, responda que o instalador não baixa nada e que a remoção volta os originais.

## Bom saber

- Já existe (ou existiu) outro mod PT-BR desse jogo no Nexus, de outro autor, feito pra uma versão antiga. Não tem problema publicar o seu, mas vale deixar claro no título/descrição que este é compatível com o **Director's Cut atual** — isso ajuda quem chega procurando.
- Leia uma vez as regras de envio do Nexus e a política de mods da ZA/UM, só pra garantir. A sua tradução não redistribui arquivos do jogo, que é o ponto mais sensível.
