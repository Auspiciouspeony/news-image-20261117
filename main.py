#!/usr/bin/env python3
"""news-image-20261117 entry (Python 3.13, standard library only).

The front page for Tuesday 17 November 2026 is drawn at build time by
draw.py and committed as entry.png beside this file (1024x1024 PNG, under
the 1 MiB gate). The grader runs this program with no network, so all it
does is copy that image to /output/entry.png. The judge sees exactly the
bytes copied.

Local run:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil
import struct
import sys

MAX_BYTES = 1048576
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_dimensions(head):
    """Width and height from a PNG IHDR chunk, else (None, None)."""
    if len(head) >= 24 and head[12:16] == b"IHDR":
        return struct.unpack(">II", head[16:24])
    return None, None


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.exists(src):
        sys.exit("entry.png missing beside main.py")
    with open(src, "rb") as fh:
        head = fh.read(24)
        fh.seek(0, os.SEEK_END)
        size = fh.tell()
    is_png = head[:8] == PNG_MAGIC
    is_jpeg = head[:2] == b"\xff\xd8"
    if not (is_png or is_jpeg):
        sys.exit("entry.png is neither a whole PNG nor a whole JPEG")
    if size > MAX_BYTES:
        sys.exit("entry.png is %d bytes, over the 1 MiB limit" % size)
    if is_png:
        width, height = png_dimensions(head)
        if width is not None and (width > MAX_DIM or height > MAX_DIM):
            sys.exit("entry.png is %dx%d, over the 1024x1024 limit"
                     % (width, height))
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
