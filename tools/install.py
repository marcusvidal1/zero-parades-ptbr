"""Instala bundles modificados no jogo e desliga a checagem de CRC deles no catalog.bin.
Uso: python -I install.py <pasta_do_jogo> <bundle> [<bundle> ...] <pasta_backup>
Passe TODOS os bundles modificados juntos: o catalogo e refeito a partir do backup a cada instalacao."""
import sys, os, shutil, struct
game, bundles, backup = sys.argv[1], sys.argv[2:-1], sys.argv[-1]
aa = os.path.join(game, "ZeroParades_Data", "StreamingAssets", "aa")
cat = os.path.join(aa, "catalog.bin")
os.makedirs(backup, exist_ok=True)
targets = [os.path.join(aa, "StandaloneWindows64", os.path.basename(b)) for b in bundles]
for f in targets + [cat]:
    b = os.path.join(backup, os.path.basename(f))
    if not os.path.exists(b):
        shutil.copy2(f, b); print("backup:", b)
data = bytearray(open(os.path.join(backup, "catalog.bin"), "rb").read())
for new_bundle in bundles:
    name = os.path.basename(new_bundle)
    p = struct.pack("<I", os.path.getsize(os.path.join(backup, name)))
    assert data.count(p) == 1, f"nao achei o registro de {name} no catalog (o jogo atualizou?)"
    i = data.find(p)
    print(name, "CRC antigo:", struct.unpack("<I", data[i-4:i])[0])
    data[i-4:i] = struct.pack("<I", 0)
    data[i:i+4] = struct.pack("<I", os.path.getsize(new_bundle))
open(cat, "wb").write(data)
for new_bundle, target in zip(bundles, targets):
    shutil.copy2(new_bundle, target)
    print("instalado:", target)
