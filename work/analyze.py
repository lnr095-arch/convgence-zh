"""Exact parser + corpus table. Record layout in the log is:
   '>> <engine>;<file>;<0xoff>;  <DB|ONLINE>;<n1>;<n2>;<n3>;<n4>;' followed by
   exactly n1 bytes of source, ';', exactly n2 bytes of target, ';'  (may span lines).
n1 = source UTF-8 bytes == injection budget, n2 = padded target bytes (== n1)."""
import json, os, re, csv, collections

S = os.path.dirname(os.path.abspath(__file__))
raw = open(os.path.join(S, "translator.log"), "rb").read()
# The log was written in text mode, so every embedded \n inside a string became \r\n
# on disk. Undo that so n1/n2 byte counts line up with the payload slices.
raw = raw.replace(b"\r\n", b"\n")
DB = json.load(open(os.path.join(S, "db_zh_CONVRGENCE.json"), encoding="utf-8"))
HDR = re.compile(rb">> {1,2}(google|deepl);([^;]+);(0x[0-9a-f]+);\s*(DB|ONLINE)\s*;(\d+);(\d+);(\d+);(\d+);")

recs = []
pos, n = 0, len(raw)
while True:
    i = raw.find(b">> ", pos)
    if i < 0:
        break
    m = HDR.match(raw, i)
    if not m:
        pos = raw.find(b"\n", i) + 1
        continue
    eng, fpath, off, kind, n1, n2, n3, n4 = m.group(1), m.group(2).decode("utf-8", "replace"), \
        int(m.group(3), 16), m.group(4).decode(), *[int(x) for x in m.group(5, 6, 7, 8)]
    st = m.end()
    src = raw[st:st + n1]
    sep1 = raw[st + n1:st + n1 + 1]
    tgt = raw[st + n1 + 1:st + n1 + 1 + n2]
    sep2 = raw[st + n1 + n2 + 1:st + n1 + n2 + 2]
    if sep1 != b";" or sep2 != b";":
        pos = raw.find(b"\n", i) + 1
        continue
    recs.append(dict(eng=eng.decode(), base=os.path.basename(fpath.replace("\\", "/")),
                     path=fpath.replace("\\", "/"), off=off, kind=kind,
                     n1=n1, n2=n2, n3=n3, n4=n4,
                     src=src.decode("utf-8", "replace"), tgt=tgt.decode("utf-8", "replace")))
    pos = st + n1 + 1 + n2 + 1
print("records recovered:", len(recs), "(log claimed 7726 '>>' lines)")
print("kinds:", collections.Counter(r["kind"] for r in recs).most_common())
print("files:", sorted(set(r["base"] for r in recs)))
bad = [r for r in recs if len(r["src"].encode("utf-8")) != r["n1"]]
print("src byte mismatches:", len(bad))
print("slots:", len(set((r["base"], r["off"]) for r in recs)),
      "| multiline srcs:", sum("\n" in r["src"] for r in recs))

budget, occ = {}, collections.defaultdict(collections.Counter)
for r in recs:
    budget[r["src"]] = min(budget.get(r["src"], 1 << 30), r["n1"])
    occ[r["src"]][r["base"]] += 1

by_src = collections.defaultdict(list)
for e in DB["translations"]:
    by_src[e["__from_text"]].append(e)
print("DB unique:", len(by_src), "| DB sources absent from log:",
      sum(1 for s in by_src if s not in budget), "| log sources absent from DB:",
      sum(1 for s in budget if s not in by_src))

CYR = re.compile(r"[А-Яа-яЁё]")
out = []
for s in sorted(by_src, key=lambda k: by_src[k][0]["_________id"]):
    ents = by_src[s]
    e = ents[0]
    ovr = (e.get("_____peurKe") or "").strip()
    mt = (e.get("____to_text") or "").rstrip()
    cur = ovr or mt
    bud = budget.get(s)
    out.append(dict(
        id=e["_________id"], src=s, mt=mt, override=ovr,
        comment=";".join(v for k, v in sorted(e.items()) if k.startswith("_comment")) or (e.get("____comment") or ""),
        translators="/".join(sorted(set(x["_translator"] for x in ents))), n_rows=len(ents),
        slots=sum(occ.get(s, {}).values()),
        files=";".join("%s:%d" % (k, v) for k, v in sorted(occ.get(s, {}).items())),
        src_chars=len(s), budget=bud, cur_bytes=len(cur.encode("utf-8")),
        slack=(bud - len(cur.encode("utf-8"))) if bud else "",
        cyr=bool(CYR.search(cur)), trunc=mt.endswith("~"),
        multiline="\n" in s,
    ))
with open(os.path.join(S, "strings.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
json.dump(recs, open(os.path.join(S, "records.json"), "w", encoding="utf-8"), ensure_ascii=False)

print("== corpus ==")
print(" uniques:", len(out))
print(" untranslated (target still Cyrillic):", sum(1 for r in out if r["cyr"]))
print(" truncated mt ('~'):", sum(1 for r in out if r["trunc"]))
print(" zero slack (cannot gain a byte):", sum(1 for r in out if r["slack"] == 0))
print(" slack<0 (already over budget):", sum(1 for r in out if isinstance(r["slack"], int) and r["slack"] < 0))
print(" multi-line strings:", sum(1 for r in out if r["multiline"]))
print(" long lore (>=200 chars):", sum(1 for r in out if r["src_chars"] >= 200))
OPEN = ("level0", "level1", "level2", "level3", "sharedassets0.assets")
sub = [r for r in out if any(("%s:" % k) in r["files"] for k in OPEN)]
with open(os.path.join(S, "scope_opening.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(sub[0].keys())); w.writeheader(); w.writerows(sub)
print("== opening (level0-3 + sharedassets0) ==")
print(" strings:", len(sub), "src chars:", sum(r["src_chars"] for r in sub),
      "| untranslated:", sum(1 for r in sub if r["cyr"]),
      "| slots:", sum(r["slots"] for r in sub))
cnt = collections.Counter()
for r in sub:
    for k in r["files"].split(";"):
        cnt[k.split(":")[0]] += 1
print(" per-file uniques:", cnt.most_common())
