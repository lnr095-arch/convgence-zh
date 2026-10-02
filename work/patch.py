"""Byte-exact in-place patcher for apocalyptic_translatorZ output.

Every translated slot was written over the original string at the same offset,
occupying exactly n1 bytes (space padded), and the int32 length prefix in front of
it was left untouched. So a correction is: seek(off); write(zh.encode() padded to n1).

  python patch.py                # dry run: what would change, any overflow
  python patch.py --apply        # write into CONVRGENCE_Data (game files)
  python patch.py --revert       # put the machine translation back from the log
"""
import json, os, sys, collections

S = os.path.dirname(os.path.abspath(__file__))
LIVE = r"D:\steam\steamapps\common\CONVRGENCE\CONVRGENCE_Data"
recs = json.load(open(os.path.join(S, "records.json"), encoding="utf-8"))
DB = json.load(open(os.path.join(S, "db_zh_CONVRGENCE.json"), encoding="utf-8"))
fixes = json.load(open(os.path.join(S, "fixes.json"), encoding="utf-8"))

by_id = {}
for e in DB["translations"]:
    by_id.setdefault(e["_________id"], e["__from_text"])
zh = {by_id[int(k)]: v for k, v in fixes.items() if int(k) in by_id}
print("fixes loaded: %d, resolvable sources: %d" % (len(fixes), len(zh)))

plan = collections.defaultdict(list)
over, changed, same = [], 0, 0
for r in recs:
    t = zh.get(r["src"])
    if t is None:
        continue
    body = t.encode("utf-8")
    if len(body) > r["n1"]:
        over.append((r["base"], hex(r["off"]), r["n1"], len(body), t[:34]))
        continue
    new = body + b" " * (r["n1"] - len(body))
    if new == r["tgt"].encode("utf-8"):
        same += 1
        continue
    changed += 1
    plan[os.path.join(LIVE, r["base"])].append((r["off"], new, r["tgt"].encode("utf-8")))

print("slots to rewrite: %d | already identical: %d | overflow(skipped): %d" % (changed, same, len(over)))
for o in over[:10]:
    print("   OVER %s %s bud=%d mine=%d %r" % o)
print("files touched: %d" % len(plan))
for p, lst in sorted(plan.items()):
    print("   %-26s %d slots" % (os.path.basename(p), len(lst)))

if "--apply" not in sys.argv and "--revert" not in sys.argv:
    print("\ndry run only; pass --apply to write, --revert to undo")
    sys.exit(0)

for p, lst in sorted(plan.items()):
    if not os.path.exists(p):
        print("MISSING", p)
        continue
    before = os.path.getsize(p)
    with open(p, "r+b") as fh:
        for off, new, old in lst:
            fh.seek(off)
            fh.write(old if "--revert" in sys.argv else new)
    after = os.path.getsize(p)
    if after != before:
        print("!! SIZE CHANGED %s %d->%d" % (p, before, after))
    print("%-10s %-26s %4d slots  size %d -> %d" % (
        "reverted" if "--revert" in sys.argv else "patched", os.path.basename(p), len(lst), before, after))

# verify by reading back
bad = 0
for p, lst in sorted(plan.items()):
    with open(p, "rb") as fh:
        for off, new, old in lst:
            fh.seek(off)
            got = fh.read(len(new))
            want = old if "--revert" in sys.argv else new
            if got != want:
                bad += 1
print("read-back verification: %d mismatches" % bad)
