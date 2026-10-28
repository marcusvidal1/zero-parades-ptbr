import json, sys, collections
d=json.load(open(sys.argv[1],encoding="utf-8"))
cnt=collections.Counter(); words=collections.Counter()
for k,m in d["meta"].items():
    cnt[m["flow"]]+=1; words[m["flow"]]+=len(d["english"][k].split())
ent=[k for k,m in d["meta"].items() if m["chunk"]=="entities"]
print("entidades:",len(ent),"palavras:",sum(len(d["english"][k].split()) for k in ent))
rows=sorted(((d["flow_chunk"].get(f,""),f,d["flow_label"].get(f,""),cnt[f],words[f]) for f in cnt if f))
for r in rows:
    if any(x in r[2].lower() for x in ("intro","open","start","prologue","wake","tutorial","begin","dream","0a","1a")) or r[0] in ("Chunk-flow-0000","Chunk-flow-0001","Chunk-dramatic-encounter-0000"):
        print(r)
