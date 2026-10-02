"""Translate the player-facing string literals baked into il2cpp global-metadata.dat.

Layout: Il2CppStringLiteral { uint32 byteLength; uint32 dataIndex } at
stringLiteralOffset + i*8; data lives at stringLiteralDataOffset + dataIndex.
We only ever shrink-or-equal, update the length field, and zero the tail, so no
offset moves. Any literal whose data range overlaps another is refused.
"""
import json, os, shutil, struct, sys

S = os.path.dirname(os.path.abspath(__file__))
META = r"D:\steam\steamapps\common\CONVRGENCE\CONVRGENCE_Data\il2cpp_data\Metadata\global-metadata.dat"
BAK = os.path.join(S, "meta_backup")
os.makedirs(BAK, exist_ok=True)

NEW = {
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
  8089: " 发子弹",
  9667: " 卢布", 9670: " - 需求上升", 9671: " (退换)", 9678: "保险", 9686: "价格: ",
  9783: "奖金 x{0} ({1:0})",
}

d = open(META, "rb").read()
sl_off, sl_sz, sd_off = struct.unpack_from("<3I", d, 8)
n = sl_sz // 8
regions = []
for i in range(n):
    ln, di = struct.unpack_from("<II", d, sl_off + i * 8)
    regions.append((sd_off + di, ln))

if not os.path.exists(os.path.join(BAK, "global-metadata.dat")):
    shutil.copy2(META, os.path.join(BAK, "global-metadata.dat"))
    print("backup written:", os.path.join(BAK, "global-metadata.dat"))

out, refused = [], []
for i, txt in NEW.items():
    ln, di = struct.unpack_from("<II", d, sl_off + i * 8)
    p = sd_off + di
    body = txt.encode("utf-8")
    if len(body) > ln:
        refused.append((i, "too long %d>%d" % (len(body), ln), txt))
        continue
    others = [j for j, (q, m) in enumerate(regions) if j != i and m and q < p + ln and p < q + m]
    if others:
        refused.append((i, "overlaps literals %s" % others[:6], txt))
        continue
    out.append((i, p, ln, di, body))

print("to write: %d | refused: %d" % (len(out), len(refused)))
for r in refused:
    print("   REFUSE #%d %s %r" % r)
if not out:
    sys.exit(0)
if "--apply" not in sys.argv:
    print("dry run; pass --apply")
    sys.exit(0)

buf = bytearray(d)
for i, p, ln, di, body in out:
    struct.pack_into("<I", buf, sl_off + i * 8, len(body))
    buf[p:p + len(body)] = body
    for q in range(p + len(body), p + ln):
        buf[q] = 0
open(META, "wb").write(bytes(buf))
print("written. size %d -> %d" % (len(d), os.path.getsize(META)))

chk = open(META, "rb").read()
bad = 0
for i, p, ln, di, body in out:
    l2, d2 = struct.unpack_from("<II", chk, sl_off + i * 8)
    got = chk[sd_off + d2:sd_off + d2 + l2].decode("utf-8", "replace")
    if got != NEW[i]:
        bad += 1
        print("   MISMATCH #%d %r" % (i, got[:40]))
print("read-back verification: %d mismatches" % bad)
for i, p, ln, di, body in out[:6]:
    print("   #%d %r -> %r (%d/%d bytes)" % (i, d[p:p + ln].decode("utf-8", "replace"), NEW[i], len(body), ln))
