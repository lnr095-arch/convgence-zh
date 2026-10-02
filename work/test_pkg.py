"""End-to-end test of the portable package against a simulated fresh install."""
import json, os, shutil, struct, subprocess, sys

S = os.path.dirname(os.path.abspath(__file__))
GAME = r"D:\steam\steamapps\common\CONVRGENCE"
BACKUP = os.path.join(GAME, r"apocalyptic_translatorZ\25630966\BACKUP")
LIVE = os.path.join(GAME, "CONVRGENCE_Data")
PKG = os.path.join(S, "release", "CONVRGENCE_ZH")
ST = os.path.join(S, "release", "_staging")

ph = json.load(open(os.path.join(PKG, "tools", "data", "placeholders.json"), encoding="utf-8"))
mt = json.load(open(os.path.join(PKG, "tools", "data", "meta_literals.json"), encoding="utf-8"))

if os.path.exists(ST):
    shutil.rmtree(ST)
os.makedirs(os.path.join(ST, "CONVRGENCE_Data", "il2cpp_data", "Metadata"))
os.makedirs(os.path.join(ST, "tools", "data"))
open(os.path.join(ST, "CONVRGENCE.exe"), "wb").close()
files = sorted(set(p["file"] for p in ph))
tot = 0
for f in files:
    shutil.copy2(os.path.join(BACKUP, f), os.path.join(ST, "CONVRGENCE_Data", f))
    tot += os.path.getsize(os.path.join(BACKUP, f))
shutil.copy2(os.path.join(S, "meta_backup", "global-metadata.dat"),
             os.path.join(ST, "CONVRGENCE_Data", "il2cpp_data", "Metadata", "global-metadata.dat"))
shutil.copy2(os.path.join(PKG, "tools", "apply_extra.ps1"), os.path.join(ST, "tools", "apply_extra.ps1"))
for d in ("placeholders.json", "meta_literals.json"):
    shutil.copy2(os.path.join(PKG, "tools", "data", d), os.path.join(ST, "tools", "data", d))
print("staging: %d scene files (%.1f MB) + metadata, all PRISTINE" % (len(files), tot / 1e6))


def run(mode):
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-File", os.path.join(ST, "tools", "apply_extra.ps1"), "-Mode", mode],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("--- mode=%s rc=%d" % (mode, r.returncode))
    for ln in (r.stdout or "").splitlines():
        if ln.strip():
            print("   ", ln[:150])
    for ln in (r.stderr or "").splitlines()[:6]:
        print("  ERR", ln[:150])
    return r


def region(path, off, ln):
    with open(path, "rb") as fh:
        fh.seek(off)
        return fh.read(ln)


run("check")
run("apply")

bad = same_as_live = 0
for e in ph:
    got = region(os.path.join(ST, "CONVRGENCE_Data", e["file"]), e["off"], e["len"])
    want = e["zh"].encode("utf-8").ljust(e["len"], b" ")
    if got != want:
        bad += 1
        if bad < 4:
            print("   MISMATCH", e["file"], hex(e["off"]), got[:30], "want", want[:30])
        continue
    try:
        if got == region(os.path.join(LIVE, e["file"]), e["off"], e["len"]):
            same_as_live += 1
    except OSError:
        pass
print("placeholders: correct=%d/%d, byte-identical to the live patched game: %d" %
      (len(ph) - bad, len(ph), same_as_live))

d = open(os.path.join(ST, "CONVRGENCE_Data", "il2cpp_data", "Metadata", "global-metadata.dat"), "rb").read()
sl, ssz, sd = struct.unpack_from("<3I", d, 8)
found = 0
undec = 0
for i in range(ssz // 8):
    ln, di = struct.unpack_from("<II", d, sl + i * 8)
    try:
        t = d[sd + di:sd + di + ln].decode("utf-8")
    except UnicodeDecodeError:
        undec += 1
        continue
    if any(t == m["zh"] for m in mt):
        found += 1
print("metadata: chinese literals present=%d/%d, undecodable literals=%d" % (found, len(mt), undec))

run("apply")          # idempotency: second run must report already=175/58
run("restore")


def meta_texts(path):
    b = open(path, "rb").read()
    a, c, e = struct.unpack_from("<3I", b, 8)
    out = set()
    for i in range(c // 8):
        ln, di = struct.unpack_from("<II", b, a + i * 8)
        try:
            out.add(b[e + di:e + di + ln].decode("utf-8"))
        except UnicodeDecodeError:
            pass
    return out


MP = os.path.join(ST, "CONVRGENCE_Data", "il2cpp_data", "Metadata", "global-metadata.dat")
ru_set = {m["ru"] for m in mt}
zh_set = {m["zh"] for m in mt}
after_restore = meta_texts(MP)
back = sum(1 for e in ph if region(os.path.join(ST, "CONVRGENCE_Data", e["file"]), e["off"], e["len"])
           == e["ru"].encode("utf-8").ljust(e["len"], b" "))
print("after restore: ru back in %d/%d slots | ru literals back %d/%d | zh gone: %s" %
      (back, len(ph), len(ru_set & after_restore), len(ru_set), not (zh_set & after_restore)))
run("apply")
again = meta_texts(MP)
print("re-apply after restore: zh literals %d/%d, scene slots correct %d/%d" %
      (len(zh_set & again), len(zh_set),
       sum(1 for e in ph if region(os.path.join(ST, "CONVRGENCE_Data", e["file"]), e["off"], e["len"])
           == e["zh"].encode("utf-8").ljust(e["len"], b" ")), len(ph)))
print("staging file sizes unchanged:",
      all(os.path.getsize(os.path.join(ST, "CONVRGENCE_Data", f)) ==
          os.path.getsize(os.path.join(BACKUP, f)) for f in files))

