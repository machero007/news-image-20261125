#!/usr/bin/env python3
"""Entry point for make.fun news-image-20261125.

Copies the bundled entry.png to /output/entry.png (creating /output
if needed). Standard library only; no network, no timestamps.
"""

import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST_DIR = "/output"
DST = os.path.join(DST_DIR, "entry.png")
# sha256 of the bundled entry.png, recorded at build time so a
# corrupted or swapped copy is caught instead of shipped silently.
EXPECTED_SHA256 = "9b0c59a772f788f494438af6115b8cddf1bbcef495d5dc46cac64d7f574fd7e2"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if os.path.abspath(SRC) == os.path.abspath(DST):
        raise SystemExit("source and destination are the same file")
    digest = _sha256(SRC)
    if digest != EXPECTED_SHA256:
        raise SystemExit("entry.png sha256 mismatch: %s" % digest)
    os.makedirs(DST_DIR, exist_ok=True)
    shutil.copyfile(SRC, DST)
    if _sha256(DST) != EXPECTED_SHA256:
        raise SystemExit("copied entry.png sha256 mismatch")
    print("copied", SRC, "->", DST, "sha256", digest)


if __name__ == "__main__":
    main()
