"""Gera um lote de trabalho (key, speaker, en) para uma lista de flows ou 'entities'.
Uso: python -I dump_batch.py english.json saida.jsonl <flowId|entities> [...]"""
import json, sys
d=json.load(open(sys.argv[1],encoding="utf-8")); out=open(sys.argv[2],"w",encoding="utf-8")
sel=set(sys.argv[3:]); n=0
for k,m in sorted(d["meta"].items(), key=lambda x:x[1]["order"]):
    if m["flow"] in sel or (m["chunk"]=="entities" and "entities" in sel):
        out.write(json.dumps({"key":k,"who":m["speaker"],"type":m["type"],"en":d["english"][k]},ensure_ascii=False)+"\n"); n+=1
print(n,"linhas")
