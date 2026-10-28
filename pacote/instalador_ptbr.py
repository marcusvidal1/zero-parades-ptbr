"""Instalador da traducao pt-BR de ZERO PARADES: Director's Cut.

Aplica o texto traduzido (dados/traducao-ptbr.json) no arquivo de textos do proprio jogo, no lugar do
Espanhol. Faz backup antes e permite remover. Nao baixa nada nem usa internet.

Uso: runtime\\python.exe -X utf8 instalador_ptbr.py [instalar|remover] [--jogo "C:\\...\\Zero Parades"]
Os atalhos INSTALAR-TRADUCAO.cmd e REMOVER-TRADUCAO.cmd fazem isso. runtime\\ e o Python portatil oficial
(python.org, assinado pela Python Software Foundation) com as bibliotecas UnityPy, Pillow, lz4, brotli, fsspec e attrs.
Sem argumentos, mostra um menu."""
import hashlib, json, os, shutil, struct, sys, traceback

VERSAO_PACOTE = "1.0.1"
BUILD_STEAM = "25778956"  # buildid da Steam em que a traducao foi testada
BUNDLE = "g5ibkj7vdwf2g67g_assets_all_7de35702cafaf3b47f772481acd859f2.bundle"
BUNDLE_ORIGINAL_SHA256 = "dcca208d631a088d3afcc0c94f77c0e7aabab866aa7fc181ea967dd63de2a88d"
TABELA = "es_mxLocalizationTable"
PASTA_APP = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ZeroParades-Traducao-PTBR")
PASTA_BACKUP = os.path.join(PASTA_APP, "backup")
ESTADO = os.path.join(PASTA_APP, "estado.json")


def base_dir():
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def bibliotecas_steam():
    pastas = []
    try:
        import winreg
        for raiz, chave, valor in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
                                   (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath")):
            try:
                with winreg.OpenKey(raiz, chave) as k:
                    pastas.append(winreg.QueryValueEx(k, valor)[0])
            except OSError:
                pass
    except ImportError:
        pass
    pastas.append(r"C:\Program Files (x86)\Steam")
    libs = []
    for steam in pastas:
        libs.append(steam)
        vdf = os.path.join(steam, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf):
            for linha in open(vdf, encoding="utf-8", errors="ignore"):
                partes = linha.strip().split('"')
                if len(partes) >= 4 and partes[1] == "path":
                    libs.append(partes[3].replace("\\\\", "\\"))
    vistos, saida = set(), []
    for l in libs:
        n = os.path.normcase(os.path.normpath(l))
        if n not in vistos:
            vistos.add(n); saida.append(l)
    return saida


def achar_jogo(arg):
    candidatos = [arg] if arg else [os.path.join(l, "steamapps", "common", "Zero Parades") for l in bibliotecas_steam()]
    for c in candidatos:
        if c and os.path.exists(os.path.join(c, "ZeroParades_Data")):
            return c
    if arg:
        raise SystemExit(f"Nao achei o jogo em: {arg}")
    print("Nao encontrei ZERO PARADES nas bibliotecas da Steam.")
    c = input("Cole aqui a pasta do jogo (a que contem ZeroParades_Data): ").strip().strip('"')
    if not os.path.exists(os.path.join(c, "ZeroParades_Data")):
        raise SystemExit("Pasta invalida.")
    return c


def caminhos(jogo):
    aa = os.path.join(jogo, "ZeroParades_Data", "StreamingAssets", "aa")
    return os.path.join(aa, "StandaloneWindows64", BUNDLE), os.path.join(aa, "catalog.bin")


def ler_estado():
    try:
        return json.load(open(ESTADO, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def gravar_atomico(destino, dados):
    tmp = destino + ".ptbr-tmp"
    with open(tmp, "wb") as f:
        f.write(dados)
    os.replace(tmp, destino)


def montar_bundle(origem):
    import UnityPy
    traducao = json.load(open(os.path.join(base_dir(), "dados", "traducao-ptbr.json"), encoding="utf-8"))
    env = UnityPy.load(origem)
    for o in env.objects:
        if o.type.name == "MonoBehaviour" and o.read().m_Name == TABELA:
            tt = o.read_typetree()
            d = tt["m_data"]
            pos = {k: i for i, k in enumerate(d["m_keys"])}
            faltando = [k for k in traducao if k not in pos]
            if faltando:
                raise SystemExit(f"O arquivo do jogo nao tem {len(faltando)} textos esperados. O jogo mudou de versao?")
            for k, v in traducao.items():
                d["m_values"][pos[k]] = v
            o.save_typetree(tt)
            print(f"  {len(traducao)} textos traduzidos aplicados.")
            return env.file.save(packer="lz4")
    raise SystemExit("Tabela de textos nao encontrada no arquivo do jogo.")


def instalar(jogo):
    bundle, catalogo = caminhos(jogo)
    if not os.path.exists(bundle):
        raise SystemExit("O arquivo de textos esperado nao existe. Provavelmente o jogo foi atualizado e esta "
                         "versao da traducao ainda nao e compativel.")
    atual = sha256(bundle)
    estado = ler_estado()
    if estado and atual == estado.get("bundle_instalado_sha256"):
        print("A traducao ja esta instalada.")
        return
    if atual != BUNDLE_ORIGINAL_SHA256:
        raise SystemExit("O arquivo de textos do jogo nao e o original desta versao (o jogo atualizou ou ha outro "
                         "mod instalado). Nada foi alterado.\nNa Steam: Propriedades > Arquivos instalados > "
                         "Verificar integridade, e tente de novo.")
    tamanho_original = os.path.getsize(bundle)
    cat = bytearray(open(catalogo, "rb").read())
    marca = struct.pack("<I", tamanho_original)
    if cat.count(marca) != 1:
        raise SystemExit("Nao reconheci o catalogo do jogo. Nada foi alterado.")

    print("Fazendo backup...")
    os.makedirs(PASTA_BACKUP, exist_ok=True)
    shutil.copy2(bundle, os.path.join(PASTA_BACKUP, BUNDLE))
    shutil.copy2(catalogo, os.path.join(PASTA_BACKUP, "catalog.bin"))

    print("Aplicando a traducao (pode levar 1 ou 2 minutos)...")
    novo = montar_bundle(bundle)
    i = cat.find(marca)
    cat[i - 4:i] = struct.pack("<I", 0)  # desliga a checagem de CRC deste arquivo
    cat[i:i + 4] = struct.pack("<I", len(novo))
    try:
        gravar_atomico(bundle, novo)
        gravar_atomico(catalogo, bytes(cat))
    except Exception:
        shutil.copy2(os.path.join(PASTA_BACKUP, BUNDLE), bundle)
        shutil.copy2(os.path.join(PASTA_BACKUP, "catalog.bin"), catalogo)
        raise
    json.dump({"versao_pacote": VERSAO_PACOTE, "jogo": jogo, "bundle_instalado_sha256": hashlib.sha256(novo).hexdigest()},
              open(ESTADO, "w", encoding="utf-8"), indent=1)
    print("\nINSTALACAO CONCLUIDA.\nNo jogo, va em Configuracoes > Idioma e escolha a opcao Espanhol "
          "(depois de escolhida, ela aparece como \"Portugues (BR)\").")


def remover(jogo):
    bundle, catalogo = caminhos(jogo)
    b_bundle, b_cat = os.path.join(PASTA_BACKUP, BUNDLE), os.path.join(PASTA_BACKUP, "catalog.bin")
    if not (os.path.exists(b_bundle) and os.path.exists(b_cat)):
        raise SystemExit("Nao achei o backup da instalacao. Para voltar ao original, use na Steam: "
                         "Propriedades > Arquivos instalados > Verificar integridade.")
    estado = ler_estado() or {}
    if os.path.exists(bundle) and sha256(bundle) not in (estado.get("bundle_instalado_sha256"), BUNDLE_ORIGINAL_SHA256):
        raise SystemExit("O arquivo do jogo mudou desde a instalacao (provavelmente a Steam atualizou o jogo). "
                         "Nada foi alterado; a Steam ja deve ter colocado os arquivos originais.")
    shutil.copy2(b_bundle, bundle)
    shutil.copy2(b_cat, catalogo)
    if sha256(bundle) != BUNDLE_ORIGINAL_SHA256:
        raise SystemExit("A restauracao nao conferiu. Use a verificacao de integridade da Steam.")
    try:
        os.remove(ESTADO)
    except OSError:
        pass
    print("\nREMOCAO CONCLUIDA. O jogo voltou aos arquivos originais.")


def main():
    args = [a for a in sys.argv[1:] if a != "--sem-pausa"]
    jogo_arg = None
    if "--jogo" in args:
        i = args.index("--jogo"); jogo_arg = args[i + 1]; del args[i:i + 2]
    acao = args[0].lower() if args else None
    print(f"ZERO PARADES - Traducao Portugues (Brasil) v{VERSAO_PACOTE}\n")
    if acao not in ("instalar", "remover"):
        print("1) Instalar a traducao\n2) Remover a traducao\n")
        acao = {"1": "instalar", "2": "remover"}.get(input("Escolha 1 ou 2: ").strip())
        if not acao:
            raise SystemExit("Opcao invalida.")
    jogo = achar_jogo(jogo_arg)
    print(f"Jogo encontrado em: {jogo}\nFeche o jogo antes de continuar.\n")
    try:
        instalar(jogo) if acao == "instalar" else remover(jogo)
    except PermissionError:
        raise SystemExit("Sem permissao para alterar os arquivos do jogo. Feche o jogo e tente de novo; se "
                         "persistir, execute como administrador (botao direito > Executar como administrador).")


if __name__ == "__main__":
    codigo = 0
    try:
        main()
    except SystemExit as e:
        if e.code not in (None, 0):
            print(f"\nERRO: {e.code}" if isinstance(e.code, str) else "")
            codigo = 1
    except Exception:
        traceback.print_exc(); codigo = 1
    if "--sem-pausa" not in sys.argv:
        input("\nPressione Enter para fechar...")
    sys.exit(codigo)
