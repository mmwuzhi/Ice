#!/usr/bin/env python3
"""Regenerate Ice's DMG install-window background (dmg-background.tiff).

Run from anywhere; writes dmg-background.tiff next to this script. Requires
Pillow, numpy, and macOS `tiffutil`. Deps: `pip install pillow numpy`.

Layout matches Scripts/dmg-settings.py (icon centers at 150,235 / 450,235 in a
600x400 background). The TIFF carries a 600x400 @72dpi base + 1200x800 @144dpi
HiDPI rep; the 144dpi tag is essential or macOS treats the 2x image as a
1200x800-point background and the install window gains a scrollbar.
"""
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
SF = "/System/Library/Fonts/SFNS.ttf"

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))

def sf(size, weight="Regular"):
    f = ImageFont.truetype(SF, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f

def make_dmg_bg(scale=2):
    s = scale
    W, H = 600 * s, 400 * s
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    t0, t1 = hex2rgb("#FCFCFE"), hex2rgb("#ECECF0")
    for row in range(H):
        arr[row, :] = lerp(t0, t1, row / (H - 1))
    img = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(img)

    def ctext(txt, cy, font, color):
        b = d.textbbox((0, 0), txt, font=font)
        w, h = b[2] - b[0], b[3] - b[1]
        d.text(((W - w) // 2 - b[0], cy - h // 2 - b[1]), txt, font=font, fill=color)

    ctext("Ice", 58 * s, sf(30 * s, "Bold"), hex2rgb("#1D1D1F"))
    ctext("Powerful menu bar management", 100 * s,
          sf(15 * s, "Regular"), hex2rgb("#86868B"))

    # arrow between the icon slots (icon centers at x=150 / x=450, y=235)
    ay = 235 * s
    col = hex2rgb("#A1A1A8")
    th = 7 * s
    x1, x2 = 262 * s, 338 * s
    d.line([x1, ay, x2 - 12 * s, ay], fill=col, width=th)
    hh = 15 * s
    d.polygon([(x2, ay), (x2 - 19 * s, ay - hh), (x2 - 19 * s, ay + hh)], fill=col)

    ctext("Drag the app onto the Applications folder", 360 * s,
          sf(15 * s, "Regular"), hex2rgb("#6E6E73"))
    return img

def build_dmg_bg():
    p1, p2 = f"{OUT}/.bg1.png", f"{OUT}/.bg2.png"
    make_dmg_bg(1).save(p1, dpi=(72, 72))
    make_dmg_bg(2).save(p2, dpi=(144, 144))
    subprocess.run(["tiffutil", "-cathidpicheck", p1, p2,
                    "-out", f"{OUT}/dmg-background.tiff"], check=True)
    os.remove(p1)
    os.remove(p2)

if __name__ == "__main__":
    build_dmg_bg()
    print(f"wrote {OUT}/dmg-background.tiff")
