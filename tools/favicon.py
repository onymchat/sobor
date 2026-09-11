#!/usr/bin/env python3
"""Render the sobor mark into favicon files.

The mark is the same geometry as the inline SVG in the nav: a rounded tile, two 90°
arcs of a broken ring rotated 45°, and eight dots on an inner circle. Everything is
expressed in the SVG's own 28-unit coordinate space and scaled up from there.

Tab strips come in both themes and a bare monochrome mark disappears on one of them,
so the raster icons are a solid near-black tile with a light mark — the same way the
mark reads against the site's own dark ground.

Needs Pillow (`pip install pillow`). Only to regenerate; the output is committed.
    python3 tools/favicon.py
"""
import math
import pathlib

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public"

U = 28.0          # the SVG viewBox is 0 0 28 28
C = 14.0          # centre
R_RING = 8.8      # arc radius
W_RING = 1.3      # arc stroke
R_DOTS = 4.6      # dots sit on this circle
R_DOT = 1.15
RX = 6.2          # tile corner radius
SS = 16           # supersample, then downsample for anti-aliasing

# ImageDraw overwrites pixels instead of compositing them, so anything the SVG draws
# semi-transparently is pre-blended against the tile here rather than given an alpha.
def over(rgb, alpha, bg):
    return tuple(round(alpha * c + (1 - alpha) * b) for c, b in zip(rgb, bg)) + (255,)


INK = (242, 242, 244, 255)                        # --on-text (dark theme)
TILE = (14, 14, 16, 255)                          # --on-surface
EDGE = over((255, 255, 255), 0.12, TILE[:3])      # --on-hairline-strong over the tile
DOT = over((242, 242, 244), 0.85, TILE[:3])       # the SVG's opacity=".85" on the dots


def draw_mark(size, rounded=True, pad=0.0, dots=8):
    """Render at size×size. `pad` insets the mark inside the tile, in 28-unit terms.

    At 16px eight dots on a 4.6-unit circle merge into a blob, so that size draws one
    centre dot instead. It is the same mark, simplified to the detail the pixels can
    actually carry — the usual favicon compromise.
    """
    px = size * SS
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # tile
    k = px / U
    if rounded:
        d.rounded_rectangle([0, 0, px - 1, px - 1], radius=RX * k, fill=TILE)
    else:
        d.rectangle([0, 0, px - 1, px - 1], fill=TILE)

    # everything below is drawn in a coordinate space inset by `pad`
    inner = U - 2 * pad
    s = px / inner

    def P(x, y):
        return ((x - pad) * s, (y - pad) * s)

    def circle(cx, cy, r, fill):
        x, y = P(cx, cy)
        rr = r * s
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fill)

    # hairline edge, matching the SVG's .5-inset stroke
    if rounded:
        e = 0.5 * s
        d.rounded_rectangle([e, e, px - 1 - e, px - 1 - e], radius=(RX - 0.5) * s,
                            outline=EDGE, width=max(1, int(round(1.0 * s))))

    # two 90° arcs, rotated 45° — drawn as thick arcs with round caps
    x0, y0 = P(C - R_RING, C - R_RING)
    x1, y1 = P(C + R_RING, C + R_RING)
    width = max(1, int(round(W_RING * s)))
    for start, end in ((-45, 45), (135, 225)):
        d.arc([x0, y0, x1, y1], start=start, end=end, fill=INK, width=width)
        # round caps — ImageDraw.arc butts its ends
        for a in (start, end):
            cx = C + R_RING * math.cos(math.radians(a))
            cy = C + R_RING * math.sin(math.radians(a))
            circle(cx, cy, W_RING / 2, INK)

    # the inner dots
    if dots >= 8:
        for i in range(8):
            a = math.radians(i * 45)
            circle(C + R_DOTS * math.cos(a), C + R_DOTS * math.sin(a), R_DOT, DOT)
    else:
        circle(C, C, R_DOT * 1.7, DOT)

    return img.resize((size, size), Image.LANCZOS)


def main():
    # .ico — 16 gets a touch more breathing room so the ring does not touch the edge
    layers = [draw_mark(s, rounded=True, pad=0.0) for s in (48, 32)]
    layers.append(draw_mark(16, rounded=True, pad=-0.8, dots=1))
    layers[0].save(OUT / "favicon.ico", format="ICO",
                   sizes=[(48, 48), (32, 32), (16, 16)], append_images=layers[1:])
    print("  wrote public/favicon.ico          48 · 32 · 16")

    # Apple squares its own corners, so hand it a full-bleed square
    draw_mark(180, rounded=False, pad=-2.2).save(OUT / "apple-touch-icon.png")
    print("  wrote public/apple-touch-icon.png 180")

    draw_mark(512, rounded=True).save(OUT / "icon-512.png")
    print("  wrote public/icon-512.png         512")


if __name__ == "__main__":
    main()
