"""Self-QA over my own corrections: glossary violations, punctuation, residue."""
import json, os, re, collections

S = os.path.dirname(os.path.abspath(__file__))
DB = json.load(open(os.path.join(S, "db_zh_CONVRGENCE.json"), encoding="utf-8"))
fixes = json.load(open(os.path.join(S, "fixes.json"), encoding="utf-8"))
by_id = {}
for e in DB["translations"]:
    by_id.setdefault(e["_________id"], e["__from_text"])

CYR = re.compile(r"[А-Яа-яЁё]")
HALF = re.compile(r"([一-鿿])[,!?;:]")
HALF2 = re.compile(r"([,!?;:])([一-鿿])")
BAD = {
  "避难所": "庇护所", "兼容性": "适配", "声誉": "声望", "杂志": "弹匣?", "文物": "神器",
  "战利品": "货", "跟踪狂": "潜行者", "阿凡达": "角色", "化妆品": "外观", "汽车": "自动",
  "魔术师": "弹匣", "起重机": "菜鸟", "墨盒": "子弹", "快门": "枪机", "棕榈": "手掌",
  "流感": "Grip", "麻省理": "米佳伊", "赛加羚羊": "Saiga", "藏身处": "藏匿箱",
  "选项卡": "分页", "插槽": "格", "库存": "物品栏", "广场": "区块", "方格": "区块",
  "复合体": "建筑群", "纳霍德基": "拾获", "零日": "零点日", "变异区": "特异区",
  "弓弩": "十字弩", "十字弓": "十字弩", "手鼓": "弹鼓", "皮套": "枪套", "火把": "手电",
  "弹夹": "弹匣", "赃物": "货", "伏特~": "伏特加", "机器": "自动", "账户": "现金",
  "帐户": "现金", "标签": "分页", "土匪": "强盗", "匪徒": "强盗", "老板": "首领",
}
rows = []
for k, v in fixes.items():
    s = by_id.get(int(k), "")
    hits = [w for w in BAD if w in v]
    if CYR.search(v):
        hits.append("CYRILLIC")
    if HALF.search(v) or HALF2.search(v):
        hits.append("halfwidth-punct")
    if hits:
        rows.append((int(k), hits, s[:38].replace("\n", "/"), v[:52].replace("\n", "/")))
rows.sort(key=lambda r: -len(r[1]))
print("my corrections: %d | flagged: %d" % (len(fixes), len(rows)))
c = collections.Counter()
for r in rows:
    for h in r[1]:
        c[h] += 1
print("counts:", c.most_common(20))
for r in rows[:45]:
    print("#%-5d %-34s %r -> %r" % (r[0], ",".join(r[1])[:34], r[2], r[3]))
