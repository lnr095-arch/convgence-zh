"""Parse global-metadata.dat string literals and list the untranslated Russian ones."""
import json, os, re, struct, sys

META = r"D:\steam\steamapps\common\CONVRGENCE\CONVRGENCE_Data\il2cpp_data\Metadata\global-metadata.dat"
S = os.path.dirname(os.path.abspath(__file__))
d = open(META, "rb").read()
magic, ver = struct.unpack_from("<II", d, 0)
print("magic=%#x version=%d filesize=%.1f MB" % (magic, ver, len(d) / 1e6))
sl_off, sl_sz, sd_off, sd_sz, st_off, st_sz = struct.unpack_from("<6I", d, 8)
print("stringLiteral table: off=%#x size=%d (n=%d)" % (sl_off, sl_sz, sl_sz // 8))
print("stringLiteralData : off=%#x size=%d" % (sd_off, sd_sz))
print("string table      : off=%#x size=%d" % (st_off, st_sz))

CYR = re.compile(rb"[\xd0\xd1][\x80-\xbf]")
lits, bad = [], 0
for i in range(sl_sz // 8):
    ln, di = struct.unpack_from("<II", d, sl_off + i * 8)
    p = sd_off + di
    if p + ln > len(d):
        bad += 1
        continue
    raw = d[p:p + ln]
    lits.append((i, p, ln, raw))
print("literals parsed:", len(lits), "out-of-range:", bad)
ru = [(i, p, ln, raw) for i, p, ln, raw in lits if CYR.search(raw) and len(CYR.findall(raw)) >= 2]
print("russian-ish literals:", len(ru), "bytes:", sum(x[2] for x in ru))
# sanity: does a known literal decode cleanly?
for i, p, ln, raw in ru:
    if b"\xd0\xa6\xd0\x95\xd0\x9d\xd0\x90" in raw:
        print("  #%d @%#s len=%d  %r" % (i, hex(p), ln, raw.decode("utf-8", "replace")[:120]))
texts = sorted(set(r[3].decode("utf-8", "replace") for r in ru))
print("distinct russian literals:", len(texts))
json.dump([{"i": i, "off": p, "len": ln, "text": raw.decode("utf-8", "replace")}
           for i, p, ln, raw in ru],
          open(os.path.join(S, "meta_lits.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(S, "meta_russian.txt"), "w", encoding="utf-8") as fh:
    for t in texts:
        fh.write(t.replace("\n", " ⏎ ") + "\n")
print("\nsample:")
for t in texts[:25]:
    print("   %r" % t[:110])
