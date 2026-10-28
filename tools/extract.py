"""Extrai o texto em ingles do bundle do Zero Parades e casa com as chaves da tabela es_mx.
Uso: python -I extract.py <bundle> <saida_dir>"""
import sys, json, os, collections, UnityPy

bundle, out = sys.argv[1], sys.argv[2]
env = UnityPy.load(bundle)
objs = {}
for o in env.objects:
    if o.type.name == "MonoBehaviour":
        objs[o.read().m_Name] = o

table = objs["es_mxLocalizationTable"].read_typetree()["m_data"]
es = dict(zip(table["m_keys"], table["m_values"]))

english = {}   # chave -> texto ingles
meta = {}      # chave -> {chunk, flow, speaker, order}

def walk_props(refs, cd, prefix):
    """Percorre m_cardData / m_entityData devolvendo (nome, valor) de propriedades string."""
    for k, v in zip(cd.get("m_keys", []), cd.get("m_values", [])):
        r = refs.get(v.get("rid")) if isinstance(v, dict) else None
        if not r: continue
        d = r.get("data") or {}
        if isinstance(d.get("m_value"), str):
            yield prefix + k, d["m_value"]
        for sub in ("m_properties", "m_data", "m_group"):
            if isinstance(d.get(sub), dict) and "m_keys" in d[sub]:
                yield from walk_props(refs, d[sub], prefix + k + ".")
        if isinstance(d.get("m_childProperties"), list):
            yield from walk_group(refs, d["m_childProperties"], k)

def walk_group(refs, children, path):
    """Grupos de propriedades (ex.: modificadores de testes): gera 'modifier[1]/explanation'."""
    kids = [refs.get(c.get("rid")) for c in children if isinstance(c, dict)]
    kids = [r for r in kids if r]
    names = [(r.get("data") or {}).get("m_name") for r in kids]
    indexed = len(set(names)) == 1 and len(kids) > 0 and isinstance((kids[0].get("data") or {}).get("m_childProperties"), list)
    for i, r in enumerate(kids):
        d = r.get("data") or {}
        nm = d.get("m_name", "")
        if isinstance(d.get("m_childProperties"), list):
            yield from walk_group(refs, d["m_childProperties"], f"{path}[{i}]" if indexed else f"{path}.{nm}")
        elif isinstance(d.get("m_value"), str):
            yield f"{path}/{nm}", d["m_value"]

flow_label = {}
db = objs["DialogueDatabase"].read_typetree()
dbrefs = {r["rid"]: r for r in db["references"]["RefIds"]}
for fid, v in zip(db["m_flows"]["m_keys"], db["m_flows"]["m_values"]):
    flow_label[fid] = (dbrefs[v["rid"]].get("data") or {}).get("m_label", "")
flow_chunk = dict(zip(db["m_flowToChunkId"]["m_keys"], db["m_flowToChunkId"]["m_values"]))

order = 0
for name, o in objs.items():
    tt = o.read_typetree()
    if "references" not in tt: continue
    refs = {r["rid"]: r for r in tt["references"]["RefIds"]}
    for r in tt["references"]["RefIds"]:
        d = r.get("data") or {}
        cid = d.get("m_cardId")
        if cid and "m_cardData" in d:
            props = dict(walk_props(refs, d["m_cardData"], ""))
            for pn, val in props.items():
                key = f"{cid}.{pn}" if "/" in pn else f"{cid}/{pn}"
                if key in es:
                    english[key] = val; order += 1
                    meta[key] = {"chunk": name, "flow": d.get("m_flowId", ""), "speaker": props.get("character_short_name", ""), "order": order, "type": d.get("m_cardType", "")}

# entidades (itens, personagens, pensamentos...)
for eid, v in zip(db["m_entities"]["m_keys"], db["m_entities"]["m_values"]):
    d = dbrefs[v["rid"]].get("data") or {}
    cand = {"character_full_name": d.get("m_fullName"), "fullDescription": d.get("m_description"),
            "shortDescription": d.get("m_shortDescription")}
    for pn, val in walk_props(dbrefs, d.get("m_entityData", {}), ""):
        cand[pn] = val
    for k2, val in list(cand.items()):
        key = f"{eid}/{k2}"
        if isinstance(val, str) and key in es and key not in english:
            english[key] = val; order += 1; meta[key] = {"chunk": "entities", "flow": "", "speaker": "", "order": order, "type": d.get("m_entityType", "")}
    lc = lambda f: f[2].lower() + f[3:]
    for f, val in d.items():
        if isinstance(val, str) and f.startswith("m_"):
            cand.setdefault(lc(f), val)
    if d.get("m_description"): cand.setdefault("description", d["m_description"])
    for i, val in enumerate(d.get("m_alternativeNames") or []):
        cand[f"alternativeNames_{i}"] = val
    for sid, st in zip((d.get("m_subTasks") or {}).get("m_keys", []), (d.get("m_subTasks") or {}).get("m_values", [])):
        cand[f"__sub__{sid}"] = None
        for k2, v2 in (("name", st.get("Name")), ("description", st.get("Description"))):
            if isinstance(v2, str): cand[f"subTasks{{{sid}}}/{k2}"] = v2
        for uid, up in zip(st.get("Updates", {}).get("m_keys", []), st.get("Updates", {}).get("m_values", [])):
            if isinstance(up.get("Entry"), str): cand[f"subTasks{{{sid}}}.updates{{{uid}}}/entry"] = up["Entry"]
    for k2, val in list(cand.items()):
        key = f"{eid}.{k2}" if "/" in k2 else f"{eid}/{k2}"
        if isinstance(val, str) and key in es and key not in english:
            english[key] = val; order += 1; meta[key] = {"chunk": "entities", "flow": "", "speaker": "", "order": order, "type": d.get("m_entityType", "")}
    gm = d.get("m_gearModifiersCollection") or {}
    for lst in gm.values():
        if isinstance(lst, list):
            for m in lst:
                if isinstance(m, dict) and m.get("SourcePropertyPath") and "Description" in m:
                    p = m["SourcePropertyPath"]; p = p[0].lower() + p[1:]
                    key = f"{m.get('SourceEntityId', eid)}.{p}/description"
                    if key in es and key not in english:
                        english[key] = m["Description"]; order += 1; meta[key] = {"chunk": "entities", "flow": "", "speaker": "", "order": order, "type": "modifier"}

os.makedirs(out, exist_ok=True)
json.dump({"english": english, "meta": meta, "flow_label": flow_label, "flow_chunk": flow_chunk},
          open(os.path.join(out, "english.json"), "w", encoding="utf-8"), ensure_ascii=False)
missing = [k for k in es if k not in english]
json.dump(missing, open(os.path.join(out, "missing_keys.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("tabela:", len(es), "casadas:", len(english), "faltando:", len(missing))
print(collections.Counter(k.split("/")[-1].split(".")[0][:25] for k in missing).most_common(20))
print(missing[:30])
