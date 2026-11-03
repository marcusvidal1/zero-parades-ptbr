"""Monta o pacote da traducao para o Nexus: scripts PowerShell + arquivos do jogo ja traduzidos (sem Python nem .exe).

Os arquivos traduzidos saem do proprio instalador_ptbr.py, rodado numa copia temporaria dos originais.
Precisa de um Python com UnityPy, por exemplo o runtime do build Python:
  build_py\\ZeroParades-Traducao-PTBR\\runtime\\python.exe -X utf8 tools\\empacotar.py backup
(backup\\ = pasta com o bundle e o catalog.bin originais do jogo).
Gera build_ps\\ZeroParades-Traducao-PTBR\\ e release\\ZeroParades-Traducao-PTBR-<VERSAO>.zip."""
import hashlib, importlib.util, json, os, shutil, sys, zipfile

VERSAO = "1.1.1"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACOTE = os.path.join(RAIZ, "pacote")
NOME = "ZeroParades-Traducao-PTBR"
SAIDA = os.path.join(RAIZ, "build_ps", NOME)
ZIP = os.path.join(RAIZ, "release", f"{NOME}-{VERSAO}.zip")
AA = os.path.join("ZeroParades_Data", "StreamingAssets", "aa")
# Arquivos de texto do pacote; vao com CRLF para abrir certo no Bloco de Notas e no cmd.
TEXTOS = ["INSTALAR-TRADUCAO.cmd", "REMOVER-TRADUCAO.cmd", "LEIA-ME.txt",
          os.path.join("scripts", "comum.ps1"), os.path.join("scripts", "instalar.ps1"), os.path.join("scripts", "remover.ps1")]


def sha256(dados):
    return hashlib.sha256(dados).hexdigest()


def carregar_instalador():
    spec = importlib.util.spec_from_file_location("instalador_ptbr", os.path.join(PACOTE, "instalador_ptbr.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def traduzir(inst, originais):
    """Roda inst.instalar() num jogo falso em build_ps\\_tmp e devolve {caminho relativo: (original, traduzido)}."""
    alvos = [os.path.join(AA, "StandaloneWindows64", inst.BUNDLE), os.path.join(AA, "catalog.bin")]
    tmp = os.path.join(RAIZ, "build_ps", "_tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    jogo = os.path.join(tmp, "jogo")
    for rel in alvos:
        os.makedirs(os.path.dirname(os.path.join(jogo, rel)), exist_ok=True)
        shutil.copy2(os.path.join(originais, os.path.basename(rel)), os.path.join(jogo, rel))
    antes = {rel: open(os.path.join(jogo, rel), "rb").read() for rel in alvos}
    inst.PASTA_BACKUP = os.path.join(tmp, "backup")
    inst.ESTADO = os.path.join(tmp, "estado.json")
    os.makedirs(inst.PASTA_BACKUP)
    inst.instalar(jogo)
    saida = {rel: (antes[rel], open(os.path.join(jogo, rel), "rb").read()) for rel in alvos}
    shutil.rmtree(tmp)
    return saida


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    inst = carregar_instalador()
    arquivos = traduzir(inst, sys.argv[1])
    shutil.rmtree(SAIDA, ignore_errors=True)
    os.makedirs(os.path.join(SAIDA, "payload"))
    manifesto = {"versao": VERSAO, "build_steam": inst.BUILD_STEAM, "arquivos": []}
    for rel, (original, traduzido) in arquivos.items():
        nome = os.path.basename(rel)
        if nome == inst.BUNDLE and sha256(original) != inst.BUNDLE_ORIGINAL_SHA256:
            raise SystemExit("O bundle informado nao e o original desta versao do jogo.")
        open(os.path.join(SAIDA, "payload", nome), "wb").write(traduzido)
        manifesto["arquivos"].append({
            "nome": "textos" if nome == inst.BUNDLE else "catalogo", "alvo": rel, "payload": nome,
            "origem_sha256": sha256(original), "payload_sha256": sha256(traduzido), "payload_bytes": len(traduzido)})
    json.dump(manifesto, open(os.path.join(SAIDA, "manifest.json"), "w", encoding="utf-8", newline="\r\n"), indent=2)
    for rel in TEXTOS:
        texto = open(os.path.join(PACOTE, rel), encoding="utf-8").read()
        os.makedirs(os.path.dirname(os.path.join(SAIDA, rel)), exist_ok=True)
        open(os.path.join(SAIDA, rel), "w", encoding="utf-8", newline="\r\n").write(texto)

    os.makedirs(os.path.dirname(ZIP), exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for pasta, _, nomes in os.walk(SAIDA):
            for n in sorted(nomes):
                caminho = os.path.join(pasta, n)
                z.write(caminho, os.path.join(NOME, os.path.relpath(caminho, SAIDA)).replace(os.sep, "/"))
    print(json.dumps(manifesto, indent=2))
    print(f"{ZIP}: {os.path.getsize(ZIP)} bytes, sha256 {sha256(open(ZIP, 'rb').read())}")


if __name__ == "__main__":
    main()
