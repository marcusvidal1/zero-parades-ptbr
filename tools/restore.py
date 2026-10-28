"""Desfaz a traducao: devolve o bundle e o catalog.bin originais. Uso: python -I restore.py <pasta_do_jogo> <pasta_backup>"""
import sys, os, shutil, glob
game, backup = sys.argv[1:3]
aa = os.path.join(game, "ZeroParades_Data", "StreamingAssets", "aa")
shutil.copy2(os.path.join(backup, "catalog.bin"), os.path.join(aa, "catalog.bin"))
for b in glob.glob(os.path.join(backup, "*.bundle")):
    shutil.copy2(b, os.path.join(aa, "StandaloneWindows64", os.path.basename(b)))
print("original restaurado")
