"""Zip the release folder into a single portable archive and report sizes."""
import os, zipfile

S = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(S, "release", "CONVRGENCE_ZH")
OUT = os.path.join(S, "release", "CONVRGENCE_中文汉化包_人工校对_v1.0.zip")
if os.path.exists(OUT):
    os.remove(OUT)
raw = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for dp, _, fs in os.walk(SRC):
        for f in sorted(fs):
            p = os.path.join(dp, f)
            if f == "global-metadata.dat.orig":
                continue
            raw += os.path.getsize(p)
            z.write(p, os.path.relpath(p, SRC))
print("files: %d | uncompressed %.2f MB | zip %.2f MB" %
      (len(z.namelist()), raw / 1e6, os.path.getsize(OUT) / 1e6))
for n in sorted(z.namelist()):
    print("   ", n)
