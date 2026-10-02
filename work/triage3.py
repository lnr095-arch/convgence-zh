"""Triage tier 3: flag already-translated strings whose Chinese breaks the glossary
or carries an obvious machine-translation failure. Output t3_flags.txt."""
import json, os, re, collections

S = os.path.dirname(os.path.abspath(__file__))
recs = json.load(open(os.path.join(S, "records.json"), encoding="utf-8"))
DB = json.load(open(os.path.join(S, "db_zh_CONVRGENCE.json"), encoding="utf-8"))
fixes = json.load(open(os.path.join(S, "fixes.json"), encoding="utf-8"))
by_id, cur = {}, {}
for e in DB["translations"]:
    by_id.setdefault(e["_________id"], e["__from_text"])
    s = e["__from_text"]
    o = (e.get("_____peurKe") or "").strip()
    if o or s not in cur:
        cur[s] = o or (e.get("____to_text") or "").rstrip()
slots = collections.Counter(r["src"] for r in recs)
bud = {}
for r in recs:
    bud[r["src"]] = min(bud.get(r["src"], 1 << 30), r["n1"])
fixed = {by_id[int(k)] for k in fixes}

BAD = ["杂志", "商店", "倾销", "快门", "阿凡达", "化妆品", "汽车", "风笛", "魔术师", "跟踪",
       "棕榈", "墨盒", "火炬", "总容量", "普通卷", "开幕", "赛加羚羊", "学究", "舞台", "教育",
       "阴谋", "颤动", "流感", "库存", "选项卡", "插槽", "汉斯托", "光滑", "锋利", "机器",
       "圣域", "避难所", "综合体", "纳霍德基", "麻省理", "零日", "声誉", "余额", "兼容",
       "帐户", "赞助人", "公文包", "突击步枪弹夹", "内鬼", "格雷", "马格", "捕获 ", "紧迫"]
GLOSS = ["文物", "变异区", "禁区", "弹夹", "弓套", "虎钳", "战利品", "长矛", "藏身处", "能量"]
TRAD = re.compile(r"[個裏面們單發語說車灣點聽覺關開處學習國時種樣讓還對]")
CYR = re.compile(r"[А-Яа-яЁё]")

hits = []
ids = {}
for e in DB["translations"]:
    ids.setdefault(e["__from_text"], e["_________id"])
for s, n in slots.items():
    if s in fixed:
        continue
    t = cur.get(s, "")
    why = []
    if CYR.search(t):
        why.append("still-Russian")
    if t.endswith("~"):
        why.append("truncated")
    if TRAD.search(t):
        why.append("traditional")
    for w in BAD:
        if w in t:
            why.append("bad:" + w)
    for w in GLOSS:
        if w in t:
            why.append("gloss:" + w)
    if why:
        hits.append((n, len(s), s, t, ";".join(why[:4])))
hits.sort(reverse=True)
with open(os.path.join(S, "t3_flags.txt"), "w", encoding="utf-8") as fh:
    for n, ln, s, t, why in hits:
        fh.write("x%d #%d b%d %s\n  RU %s\n  ZH %s\n" % (n, ids[s], bud[s], why, s.replace("\n", " / ")[:230], t.replace("\n", " / ")[:230]))
print("unfixed uniques: %d | flagged: %d | flagged slots: %d" %
      (len(slots) - len(fixed & set(slots)), len(hits), sum(h[0] for h in hits)))
c = collections.Counter()
for h in hits:
    for w in h[4].split(";"):
        c[w.split(":")[0] if w.startswith(("bad", "gloss")) else w] += 1
print("reasons:", c.most_common(14))
for h in hits[:12]:
    print("x%d %-28s %s -> %s" % (h[0], h[4][:28], h[2][:44].replace("\n", "/"), h[3][:44].replace("\n", "/")))
