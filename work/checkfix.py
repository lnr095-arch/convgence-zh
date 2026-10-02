"""Validate fixes.json against the per-string byte budget and line structure."""
import json, os, collections

S = os.path.dirname(os.path.abspath(__file__))
recs = json.load(open(os.path.join(S, "records.json"), encoding="utf-8"))
DB = json.load(open(os.path.join(S, "db_zh_CONVRGENCE.json"), encoding="utf-8"))
fixes = json.load(open(os.path.join(S, "fixes.json"), encoding="utf-8"))

budget = {}
for r in recs:
    budget[r["src"]] = min(budget.get(r["src"], 1 << 30), r["n1"])
by_id = {}
for e in DB["translations"]:
    by_id.setdefault(e["_________id"], e["__from_text"])

slots = collections.Counter()
for r in recs:
    slots[r["src"]] += 1

bad = []
nl = []
over = []
tot_slots = 0
for k, v in fixes.items():
    i = int(k)
    src = by_id.get(i)
    if src is None:
        bad.append((k, "no such db id"))
        continue
    b = budget.get(src)
    if b is None:
        bad.append((k, "no log slot for %r" % src[:30]))
        continue
    n = len(v.encode("utf-8"))
    tot_slots += slots[src]
    if n > b:
        over.append((i, src[:46], b, n, v[:40]))
    if src.count("\n") != v.count("\n"):
        nl.append((i, src.count("\n"), v.count("\n"), src[:34].replace("\n", "/")))
print("fixes: %d | ids ok: %d | game slots touched: %d" % (len(fixes), len(fixes) - len(bad), tot_slots))
print("OVER BUDGET (would truncate to '~'): %d" % len(over))
for o in over:
    print("   #%d bud=%d mine=%d | %r -> %r" % (o[0], o[2], o[3], o[1], o[4]))
print("newline count differs: %d" % len(nl))
for x in nl[:12]:
    print("   #%d src %d nl vs mine %d nl | %r" % x)
for x in bad:
    print("   BAD", x)
