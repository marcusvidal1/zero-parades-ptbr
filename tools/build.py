"""Valida as traducoes e gera o bundle com o portugues no lugar do espanhol (es_mx).
Uso: python -I -X utf8 build.py <bundle_original> <english.json> <saida.bundle> pt1.json [pt2.json ...]"""
import sys, json, re, UnityPy

src, eng_path, out = sys.argv[1:4]
english = json.load(open(eng_path, encoding="utf-8"))["english"]
pt = {}
for f in sys.argv[4:]:
    pt.update(json.load(open(f, encoding="utf-8")))

TAG = re.compile(r"(?<!<)<(?!<)[^<>]*>|\{\d+\}")
def tags(s):
    return sorted(t for t in TAG.findall(s) if t != "<shy>")

env = UnityPy.load(src)
table = next(o for o in env.objects if o.type.name == "MonoBehaviour" and o.read().m_Name == "es_mxLocalizationTable")
tt = table.read_typetree()
d = tt["m_data"]; pos = {k: i for i, k in enumerate(d["m_keys"])}

problems = []
for k, v in list(pt.items()):
    en = english.get(k)
    if en is None and k in pos:
        en = d["m_values"][pos[k]]  # sem ingles: valida contra o espanhol original
    if en is None:
        problems.append((k, "chave nao existe no ingles")); continue
    if tags(en) != tags(v):
        problems.append((k, f"tags diferentes: {tags(en)} vs {tags(v)}"))
    if en.count("*") % 2 != v.count("*") % 2:
        problems.append((k, "asteriscos (*enfase*) desbalanceados"))
    # preserva espacos/quebras de linha nas pontas, como no original
    lead = en[:len(en) - len(en.lstrip())]; trail = en[len(en.rstrip()):]
    pt[k] = lead + v.strip() + trail
if problems:
    for p in problems: print("PROBLEMA", *p)
    sys.exit(1)

for k, v in pt.items():
    d["m_values"][pos[k]] = v
table.save_typetree(tt)
open(out, "wb").write(env.file.save(packer="lz4"))
print("traduzidas:", len(pt), "-> gravado", out)
