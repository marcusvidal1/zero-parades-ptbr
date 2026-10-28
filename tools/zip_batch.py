"""Junta uma lista de traducoes (na ordem do lote) com as chaves. Uso: zip_batch.py lote.jsonl traducoes.json saida.json"""
import json, sys
rows=[json.loads(l) for l in open(sys.argv[1],encoding="utf-8")]
pt=json.load(open(sys.argv[2],encoding="utf-8"))
assert len(rows)==len(pt), f"{len(rows)} linhas no lote vs {len(pt)} traducoes"
json.dump({r["key"]:t for r,t in zip(rows,pt)}, open(sys.argv[3],"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(pt))
