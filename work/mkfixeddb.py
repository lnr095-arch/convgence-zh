"""Write the human corrections into the tool's translation memory.

The tool reads fix_list keys (_____peurKe) in preference to ____to_text, so a human
override survives a re-run and never costs a network call. We write BOTH places:
  DB/json/zh_CONVRGENCE.json            - the DB the run just used
  apocalyptic_translatorZ.FIXED_DB/...  - checked first, meant for edited DBs
Every row sharing a source gets the override, because lookup prefers the deepl row
when both deepl and google rows exist.
"""
import json, os, collections

S = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\steam\steamapps\common\CONVRGENCE\apocalyptic_translatorZ"
fixes = json.load(open(os.path.join(S, "fixes.json"), encoding="utf-8"))
pristine = json.load(open(os.path.join(S, "db_zh_CONVRGENCE.json"), encoding="utf-8"))

live_path = os.path.join(ROOT, "DB", "json", "zh_CONVRGENCE.json")
db = json.load(open(live_path, encoding="utf-8"))
print("DB rows: %d, next_id: %s, state: %s" % (len(db["translations"]), db.get("next_id"), db.get("state")))

by_id = {}
for e in db["translations"]:
    by_id.setdefault(e["_________id"], e["__from_text"])
target = {}
missing = []
for k, v in fixes.items():
    s = by_id.get(int(k))
    if s is None:
        missing.append(k)
    else:
        target[s] = v
print("mapped sources: %d, ids not in live DB: %d" % (len(target), len(missing)))

touched = collections.Counter()
for e in db["translations"]:
    v = target.get(e["__from_text"])
    if v is not None:
        e["_____peurKe"] = v
        touched[e["_translator"]] += 1
# The same sentence can exist twice in the DB with \r\n vs \n line endings; the lookup
# takes whichever row matches the asset byte-for-byte, so stamp the sibling variants too.
norm = {}
for s, v in target.items():
    norm.setdefault(s.replace("\r\n", "\n"), v)
extra = 0
for e in db["translations"]:
    s = e["__from_text"]
    if s in target:
        continue
    v = norm.get(s.replace("\r\n", "\n"))
    if v is not None:
        e["_____peurKe"] = v
        extra += 1
print("rows stamped with override:", dict(touched), "| line-ending variants also stamped:", extra)
if "_____peurKe" not in db["fix_list"]:
    db["fix_list"].append("_____peurKe")

with open(live_path, "w", encoding="utf-8") as fh:
    json.dump(db, fh, ensure_ascii=False, indent=2)
fixed_db = os.path.join(ROOT, "FIXED_DB")
os.makedirs(fixed_db, exist_ok=True)
with open(os.path.join(fixed_db, "zh_CONVRGENCE.json"), "w", encoding="utf-8") as fh:
    json.dump(db, fh, ensure_ascii=False, indent=2)
print("wrote:", live_path)
print("wrote:", os.path.join(fixed_db, "zh_CONVRGENCE.json"))
print("pristine copy kept at:", os.path.join(S, "db_zh_CONVRGENCE.json"))
