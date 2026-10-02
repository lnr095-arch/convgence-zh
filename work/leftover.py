"""Verify which leftover Cyrillic byte-runs are REAL Unity serialized strings (int32 length prefix)."""
import os, re, struct, collections, json

LIVE = r"D:\steam\steamapps\common\CONVRGENCE\CONVRGENCE_Data"
S = os.path.dirname(os.path.abspath(__file__))
RUN = re.compile(rb"(?:[\xd0\xd1][\x80-\xbf]){3,}")
real = []
per = collections.Counter()
for f in sorted(os.listdir(LIVE)):
    p = os.path.join(LIVE, f)
    if not os.path.isfile(p) or f.endswith((".resS", ".resource", ".cfg", ".ini")):
        continue
    data = open(p, "rb").read()
    for m in RUN.finditer(data):
        s = m.start()
        for L in range(len(m.group(0)), len(m.group(0)) + 200):
            if s + L >= len(data) or data[s + L] != 0:
                continue
            if struct.unpack_from("<i", data, s - 4)[0] != L:
                continue
            raw = data[s:s + L]
            try:
                t = raw.decode("utf-8")
            except UnicodeDecodeError:
                break
            if not re.search(r"[а-яА-ЯёЁ]{3,}", t):
                break
            pad = (4 - (L + 1) % 4) % 4
            if data[s + L + 1:s + L + 1 + pad] != b"\x00" * pad:
                break
            real.append((f, s, L, t))
            per[f] += 1
            break
print("real serialized Russian strings still in the game files:", len(real))
print("per file:", per.most_common())
json.dump([{"file": f, "off": o, "len": L, "text": t} for f, o, L, t in real],
          open(os.path.join(S, "leftover_strings.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for f, o, L, t in sorted(real, key=lambda r: -r[2])[:35]:
    print("  %-22s %-10s len%-4d %r" % (f, hex(o), L, t[:150]))
