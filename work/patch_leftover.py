"""Patch the leftover strings the mod's extractor never saw (placeholders + legacy notes).

Same rule as patch.py: overwrite exactly n bytes in place, space-padded, so the int32
length prefix and the null terminator stay valid.
"""
import json, os, re, collections

S = os.path.dirname(os.path.abspath(__file__))
LIVE = r"D:\steam\steamapps\common\CONVRGENCE\CONVRGENCE_Data"
items = json.load(open(os.path.join(S, "leftover_strings.json"), encoding="utf-8"))

SKIP_HINT = ("_BaseColor", "_Roughness", ".001", ".002", "Кривая", "Цилиндр")
LEGACY = {
  "Привет, это Никита - разработчик Paradox of Hope. \nСпасибо за ваш интерес к моей игре!":
    "你好，我是尼基塔——《Paradox of Hope》的开发者。\n谢谢你对我游戏的关注！",
  "Спасибо за игру в Paradox of Hope Demo!\n":
    "感谢试玩《Paradox of Hope》Demo！\n",
}
plan, skipped = collections.defaultdict(list), collections.Counter()
for it in items:
    t, f, off, L = it["text"], it["file"], it["off"], it["len"]
    if any(h in t for h in SKIP_HINT):
        skipped[t] += 1
        continue
    m = re.fullmatch(r"НАЗВАНИЕ( \d+)?", t)
    if m:
        new = "标题" + (m.group(1) or "")
    elif t in LEGACY:
        new = LEGACY[t]
    else:
        skipped["UNRECOGNISED: " + t] += 1
        continue
    body = new.encode("utf-8")
    if len(body) > L:
        skipped["OVERFLOW: " + t] += 1
        continue
    plan[os.path.join(LIVE, f)].append((off, L, body + b" " * (L - len(body)), t, new))

print("to patch: %d slots | skipped (internal names etc.): %d" %
      (sum(len(v) for v in plan.values()), sum(skipped.values())))
for k, v in sorted(skipped.items(), key=lambda kv: -kv[1])[:8]:
    print("   keep  x%-4d %r" % (v, k[:60]))
for p, lst in sorted(plan.items()):
    before = os.path.getsize(p)
    with open(p, "r+b") as fh:
        for off, L, new, old, txt in lst:
            fh.seek(off)
            fh.write(new)
    bad = 0
    with open(p, "rb") as fh:
        for off, L, new, old, txt in lst:
            fh.seek(off)
            if fh.read(L) != new:
                bad += 1
    print("patched %-12s %3d slots  size %d -> %d  read-back bad=%d" %
          (os.path.basename(p), len(lst), before, os.path.getsize(p), bad))
    for off, L, new, old, txt in lst[:3]:
        print("     %s %r -> %r (%d/%d bytes)" % (hex(off), old, txt, len(new.rstrip()), L))
