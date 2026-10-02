"""READ-ONLY feasibility check for the metadata literal patch."""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
META = r"D:\steam\steamapps\common\CONVRGENCE\CONVRGENCE_Data\il2cpp_data\Metadata\global-metadata.dat"
import importlib.util
spec = importlib.util.spec_from_file_location("pm", os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch_meta.py"))
NEW = {
  3083: "无", 3085: "都市", 3087: "冬季", 3089: "磨损", 3091: "秋季", 3093: "现代",
  3095: "蝴蝶", 3097: "磁带", 3099: "南瓜", 3100: "小圣诞树", 3102: "绿色", 3103: "赭黄",
  3104: "犄角", 3106: "新年款", 3107: "新年款", 3108: "标准", 3109: "雕花",
  3111: "NKVD 芬卡", 3113: "万圣节", 3115: "夜视仪", 3117: "老兵款", 3119: "开荒款",
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
print("literals:", n, "| file:", len(d), "bytes")
ok = ref = 0
for i, txt in sorted(NEW.items()):
    ln, di = struct.unpack_from("<II", d, sl_off + i * 8)
    p = sd_off + di
    body = txt.encode("utf-8")
    old = d[p:p + ln].decode("utf-8", "replace")
    others = [j for j, (q, m) in enumerate(regions) if j != i and m and q < p + ln and p < q + m]
    if len(body) > ln:
        ref += 1
        print("  TOO LONG #%d %d>%d %r" % (i, len(body), ln, old[:40]))
    elif others:
        ref += 1
        print("  OVERLAP  #%d with %s %r" % (i, others[:5], old[:40]))
    else:
        ok += 1
        if ok <= 8:
            print("  ok  #%d %-34r -> %r  (%d/%d B)" % (i, old[:32].replace("\n", "/"), txt, len(body), ln))
print("feasible: %d | refused: %d" % (ok, ref))
