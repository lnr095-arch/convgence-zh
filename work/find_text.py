"""Locate the exact bytes of the PDA description text anywhere under the game folder."""
import os, re

ROOT = r"D:\steam\steamapps\common\CONVRGENCE"
NEEDLES = {
  "ЦЕНА": "ЦЕНА".encode("utf-8"),
  "НЕИЗВЕСТНА": "НЕИЗВЕСТНА".encode("utf-8"),
  "ПАТРОНОВ": "ПАТРОНОВ".encode("utf-8"),
  "ПРОДАЖА": "ПРОДАЖА".encode("utf-8"),
  "ТРЕБУЕТСЯ": "ТРЕБУЕТСЯ".encode("utf-8"),
  "ЦЕНA-u16": "ЦЕНА".encode("utf-16-le"),
  "ПАТРОНОВ-u16": "ПАТРОНОВ".encode("utf-16-le"),
}
CHUNK, OVER = 1 << 26, 4096
for dirpath, dirs, fs in os.walk(ROOT):
    for f in sorted(fs):
        p = os.path.join(dirpath, f)
        size = os.path.getsize(p)
        if size < 8:
            continue
        found = {}
        with open(p, "rb") as fh:
            base, carry = 0, b""
            while True:
                buf = fh.read(CHUNK)
                if not buf:
                    break
                data = carry + buf
                for name, nd in NEEDLES.items():
                    i = data.find(nd)
                    while i >= 0:
                        found.setdefault(name, []).append(base + i - (len(carry) if False else 0))
                        if len(found[name]) > 3:
                            break
                        i = data.find(nd, i + 1)
                carry = data[-OVER:]
                base += len(data) - len(carry)
        if found:
            print("%-58s %8.1f MB" % (os.path.relpath(p, ROOT), size / 1e6))
            for k, v in found.items():
                print("      %-14s x%-4d first at %s" % (k, len(v), ", ".join(hex(x) for x in v[:3])))
