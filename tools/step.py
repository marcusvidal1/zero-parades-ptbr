"""Fluxo de traducao em lotes.
  python -I -X utf8 step.py next [palavras]   -> mostra o proximo lote (i|quem|texto)
  python -I -X utf8 step.py save <arquivo>    -> grava traducoes 'i<TAB>texto' do lote atual
  python -I -X utf8 step.py status            -> progresso
Quebras de linha aparecem como \n e devem ser escritas como \n."""
import sys, json, os, re, collections
W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work")
E = json.load(open(os.path.join(W, "english.json"), encoding="utf-8"))
english, meta, labels, fchunk = E["english"], E["meta"], E["flow_label"], E["flow_chunk"]
es = json.load(open(os.path.join(W, "es_mx_original.json"), encoding="utf-8"))
MAIN = os.path.join(W, "pt", "main.json"); CUR = os.path.join(W, "cur_batch.json")
main = json.load(open(MAIN, encoding="utf-8")) if os.path.exists(MAIN) else {}

def source(k):
    return (english[k], "en") if k in english else (es[k], "es")

def chunk_rank(c):
    order = ["Chunk-flow", "Chunk-dramatic-encounter", "Chunk-process-thought-flow", "Chunk-orb-flow", "Chunk-bark-flow"]
    for i, p in enumerate(order):
        if c.startswith(p + "-"): return (i, c)
    return (len(order), c)

def queue():
    flows = collections.defaultdict(list)
    for k, m in meta.items():
        flows[(chunk_rank(m["chunk"]) if m["chunk"] != "entities" else (90, ""), m["flow"])].append(k)
    q = []
    for fk in sorted(flows):
        q += sorted(flows[fk], key=lambda k: meta[k]["order"])
    q += sorted(k for k in es if k not in english)          # restante: fonte espanhol
    return q

TAG = re.compile(r"(?<!<)<(?!<)[^<>]*>|\{\d+\}")
def tags(s): return sorted(t for t in TAG.findall(s) if t != "<shy>")

def apply_tm():
    """Memoria de traducao: textos ingleses identicos recebem a mesma traducao."""
    tm = {}
    for k, v in main.items():
        if k in english: tm.setdefault(english[k], v)
    n = 0
    for k in english:
        if k not in main and english[k] in tm:
            main[k] = tm[english[k]]; n += 1
    return n

def save_main():
    tmp = MAIN + ".tmp"
    json.dump(main, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    os.replace(tmp, MAIN)

cmd = sys.argv[1]
if cmd == "next":
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    batch, seen, words, last_flow = [], {}, 0, None
    for k in queue():
        if k in main: continue
        txt, src = source(k)
        if src == "en" and txt in seen: continue            # duplicata dentro do lote
        f = meta.get(k, {}).get("flow")
        if words >= limit and f != last_flow: break
        if words >= limit * 1.6: break
        batch.append(k); seen[txt] = k; words += len(txt.split()); last_flow = f
    json.dump(batch, open(CUR, "w", encoding="utf-8"))
    cur_flow = object()
    for i, k in enumerate(batch):
        m = meta.get(k, {}); f = m.get("flow")
        if f != cur_flow:
            cur_flow = f
            print(f"## {labels.get(f, '') or m.get('chunk', 'restante (fonte: espanhol)' if k not in english else '')}")
        txt, src = source(k)
        who = m.get("speaker") or k.split("/")[-1]
        print(f"{i}|{who}{'|ES' if src == 'es' else ''}|{txt.replace(chr(10), chr(92) + 'n')}")
    print(f"-- {len(batch)} linhas, {words} palavras")
elif cmd == "save":
    batch = json.load(open(CUR, encoding="utf-8"))
    got, bad = {}, []
    for line in open(sys.argv[2], encoding="utf-8"):
        line = line.rstrip("\r\n")
        if not line.strip(): continue
        mm = re.match(r"\s*(\d+)[\t|](.*)$", line)
        if not mm: bad.append(f"linha sem indice: {line[:60]}"); continue
        got[int(mm.group(1))] = mm.group(2).replace("\\n", "\n")
    if got and max(got) + 1 != len(batch):
        sys.exit(f"ABORTADO: arquivo tem {max(got)+1} linhas, lote tem {len(batch)} (arquivo velho?)")
    for i, k in enumerate(batch):
        if i not in got: bad.append(f"{i} faltando"); continue
        src, _ = source(k); t = got[i]
        if tags(src) != tags(t): bad.append(f"{i} tags {tags(src)} != {tags(t)}"); continue
        if src.count("*") % 2 != t.count("*") % 2: bad.append(f"{i} asteriscos"); continue
        lead = src[:len(src) - len(src.lstrip())]; trail = src[len(src.rstrip()):]
        main[k] = lead + t.strip() + trail
    n = apply_tm(); save_main()
    print(f"salvas {len([1 for i in got if i < len(batch)])}, memoria +{n}, total {len(main)}/{len(es)}")
    for b in bad: print("PROBLEMA", b)
elif cmd == "status":
    tw = sum(len(source(k)[0].split()) for k in es); dw = sum(len(source(k)[0].split()) for k in main if k in es)
    print(f"{len(main)}/{len(es)} textos, {dw}/{tw} palavras ({100*dw/tw:.1f}%)")
elif cmd == "seed":
    for f in sys.argv[2:]: main.update(json.load(open(f, encoding="utf-8")))
    n = apply_tm(); save_main(); print("seed", len(main), "memoria", n)
