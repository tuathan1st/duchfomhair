"""Turn phone photos dropped in inbox/ into gallery-ready WebP files.

- A file named just a number (e.g. "5.jpg") becomes 5.webp (handy for
  swapping a piece).
- Anything else (e.g. "1000080851.jpg") becomes the next day's number.
- Several at once are numbered in filename order.
"""
import os
import re
from pathlib import Path
from PIL import Image, ImageOps

YEAR = os.environ.get("DUCH_YEAR", "2026")
MAX_SIDE = 2000
QUALITY = 78
OK = {".jpg", ".jpeg", ".png", ".webp"}

inbox = Path("inbox")
out = Path(YEAR)
out.mkdir(exist_ok=True)


def next_number():
    nums = [int(p.stem) for p in out.glob("*.webp") if p.stem.isdigit()]
    return max(nums, default=0) + 1


for src in sorted(p for p in inbox.iterdir() if p.suffix.lower() in OK):
    stem = src.stem.strip()
    n = int(stem) if re.fullmatch(r"\d{1,2}", stem) else next_number()
    im = ImageOps.exif_transpose(Image.open(src))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.getchannel("A"))
        im = bg
    else:
        im = im.convert("RGB")
    im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    dest = out / f"{n}.webp"
    im.save(dest, "WEBP", quality=QUALITY, method=6)
    print(f"{src.name} -> {dest} ({dest.stat().st_size // 1024} KB)")
    src.unlink()
