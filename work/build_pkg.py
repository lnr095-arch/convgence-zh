"""Build the portable release package: copy the tool + merged DB, derive the two
extra patch tables from the PRISTINE game files, and emit the data files.
"""
import json, os, re, shutil, struct, subprocess

GAME = r"D:\steam\steamapps\common\CONVRGENCE"
BACKUP = os.path.join(GAME, r"apocalyptic_translatorZ\25630966\BACKUP")
DB = os.path.join(GAME, r"apocalyptic_translatorZ\DB\json\zh_CONVRGENCE.json")
META_BAK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta_backup", "global-metadata.dat")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "release", "CONVRGENCE_ZH")

LEGACY = {
  "Привет, это Никита - разработчик Paradox of Hope. \nСпасибо за ваш интерес к моей игре!":
    "你好，我是尼基塔——《Paradox of Hope》的开发者。\n谢谢你对我游戏的关注！",
  "Спасибо за игру в Paradox of Hope Demo!\n": "感谢试玩《Paradox of Hope》Demo！\n",
}
META_NEW = {
  3083: "无", 3085: "都市", 3087: "冬季", 3089: "磨损", 3091: "秋季", 3093: "现代",
  3095: "蝴蝶", 3097: "磁带", 3099: "南瓜", 3100: "小圣诞树", 3102: "绿色", 3103: "赭黄",
  3104: "犄角", 3106: "新年款", 3107: "新年款", 3108: "标准", 3109: "雕花",
  3111: "NKVD 芬卡", 3113: "万圣节", 3115: "夜视", 3117: "老兵款", 3119: "开荒款",
  3121: "RSh-12", 3123: "MPL-50", 3125: "标准", 3126: "战术", 3128: "Taiga-1",
  3130: "战斧", 3132: "护耳帽",
  3766: "上次你\n撑了:\n", 3767: " 分 ", 3768: " 秒", 3769: "最佳时间:\n", 3770: " 秒 ",
  8056: " 卢布", 8058: "价格:偏高", 8060: "价格:偏低", 8062: "价格:中等",
  8064: "价格未知。\n需要先\n卖出一次", 8065: "左轮手枪", 8067: "价格未知",
  8068: "十字弩", 8069: "喷火器", 8071: "能量步枪", 8072: "匕首", 8075: "锋利度 ",
  8078: "手电", 8081: "刷子", 8083: "磨刀石", 8085: "污染度 ", 8087: "污染度 0%",
  8089: " 发子弹", 9667: " 卢布", 9670: " - 需求上升", 9671: " (退换)",
  9678: "保险", 9686: "价格: ", 9783: "奖金 x{0} ({1:0})",
}

for d in ("", "tools", "tools\\data", "apocalyptic_translatorZ\\DB\\json"):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

# 1. tool + merged DB
shutil.copy2(os.path.join(GAME, "apocalyptic_translatorZ.exe"), os.path.join(OUT, "apocalyptic_translatorZ.exe"))
shutil.copy2(DB, os.path.join(OUT, "apocalyptic_translatorZ", "DB", "json", "zh_CONVRGENCE.json"))
print("copied tool + merged DB")

# 2. placeholder table, derived from the PRISTINE backups
RUN = re.compile(rb"(?:[\xd0\xd1][\x80-\xbf]){3,}")
ph = []
for f in sorted(os.listdir(BACKUP)):
    p = os.path.join(BACKUP, f)
    if not os.path.isfile(p) or f.endswith((".resS", ".resource")):
        continue
    d = open(p, "rb").read()
    for m in RUN.finditer(d):
        s = m.start()
        for L in range(len(m.group(0)), len(m.group(0)) + 220):
            if s + L >= len(d) or d[s + L] != 0 or struct.unpack_from("<i", d, s - 4)[0] != L:
                continue
            raw = d[s:s + L]
            try:
                t = raw.decode("utf-8")
            except UnicodeDecodeError:
                break
            if not re.search(r"[а-яА-ЯёЁ]{3,}", t):
                break
            mm = re.fullmatch(r"НАЗВАНИЕ( \d+)?", t)
            zh = ("标题" + (mm.group(1) or "")) if mm else LEGACY.get(t)
            if zh and len(zh.encode("utf-8")) <= L:
                ph.append({"file": f, "off": s, "len": L, "ru": t, "zh": zh})
            break
json.dump(ph, open(os.path.join(OUT, "tools", "data", "placeholders.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)
print("placeholders:", len(ph))

# 3. metadata literals, keyed by Russian text so a game update can still be matched
d = open(META_BAK, "rb").read()
sl_off, sl_sz, sd_off = struct.unpack_from("<3I", d, 8)
lit = {}
for i in range(sl_sz // 8):
    ln, di = struct.unpack_from("<II", d, sl_off + i * 8)
    try:
        t = d[sd_off + di:sd_off + di + ln].decode("utf-8")
    except UnicodeDecodeError:
        continue
    lit.setdefault(t, ln)
meta = []
miss = []
for i, zh in sorted(META_NEW.items()):
    ln, di = struct.unpack_from("<II", d, sl_off + i * 8)
    ru = d[sd_off + di:sd_off + di + ln].decode("utf-8", "replace")
    if ru in lit and len(zh.encode("utf-8")) <= lit[ru]:
        meta.append({"idx": i, "ru": ru, "zh": zh, "maxlen": lit[ru]})
    else:
        miss.append((i, ru, zh))
json.dump(meta, open(os.path.join(OUT, "tools", "data", "meta_literals.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)
print("meta literals:", len(meta), "refused:", miss)
for f in sorted(os.listdir(os.path.join(OUT))):
    print("   ", f)
