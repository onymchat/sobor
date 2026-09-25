#!/usr/bin/env python3
"""Render the Open Graph card for each locale.

Telegram, Slack and the rest show a text-only preview unless the page offers an
og:image, so this draws one per language: the hero, essentially, at 1200x630.

Pillow has no letter-spacing, and the site's look depends on it — tight negative
tracking on the headline, wide positive tracking on the mono eyebrow — so text is
drawn glyph by glyph with the spacing applied by hand.

    python3 tools/og.py

Needs Pillow. Output is committed; regenerate when a headline changes.
"""
import importlib.util
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
I18N = json.loads((ROOT / "content" / "i18n.json").read_text(encoding="utf-8"))

_spec = importlib.util.spec_from_file_location("favicon", ROOT / "tools" / "favicon.py")
_fav = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fav)

W, H = 1200, 630
PAD = 84
SS = 2                                   # supersample, for clean glyph edges

BG = (14, 14, 16)                        # --on-surface
INK = (242, 242, 244)                    # --on-text
DIM = (150, 150, 154)                    # ~ --on-text2 over BG
FAINT = (104, 104, 108)                  # ~ --on-text3 over BG
RULE = (44, 44, 48)                      # ~ --on-hairline-strong over BG

SANS = "/System/Library/Fonts/SFNS.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"


def sans(size, weight="Bold"):
    f = ImageFont.truetype(SANS, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def mono(size):
    return ImageFont.truetype(MONO, size)


def width(draw, text, font, track):
    """Advance width with per-glyph tracking folded in."""
    w = sum(draw.textlength(ch, font=font) for ch in text)
    return w + track * max(len(text) - 1, 0)


def write(draw, xy, text, font, fill, track=0.0):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track
    return x


def card(code):
    t = I18N[code]
    img = Image.new("RGB", (W * SS, H * SS), BG)
    d = ImageDraw.Draw(img)
    pad = PAD * SS
    inner = W * SS - pad * 2

    # mark + wordmark
    mark = _fav.draw_mark(64 * SS, rounded=True)
    img.paste(mark, (pad, pad), mark)
    f_word = sans(38 * SS, "Semibold")
    write(d, (pad + 64 * SS + 20 * SS, pad + 8 * SS), "sobor", f_word, INK, -1.2 * SS)

    # footer rule and the domain — drawn first, because the headline is fitted to
    # the space left between the wordmark and this rule
    ry = H * SS - pad - 52 * SS
    d.rectangle([pad, ry, W * SS - pad, ry + 1 * SS], fill=RULE)
    f_foot = mono(19 * SS)
    write(d, (pad, ry + 22 * SS), "sobor.io", f_foot, DIM, 1.6 * SS)

    # headline — the page's three lines, fitted to both the column and the gap above
    # the rule, then centred in that gap. Three lines is enough that height binds
    # before width does; the loop checks both so either can.
    lines = [t["hero"]["h1a"], t["hero"]["h1b"], t["hero"]["h1c"]]
    top, bottom = pad + 152 * SS, ry - 44 * SS
    room = bottom - top
    step = 0.96
    size = 92 * SS
    while size > 30 * SS:
        f = sans(size, "Bold")
        track = -0.055 * size
        fits_wide = max(width(d, ln, f, track) for ln in lines) <= inner
        fits_tall = size * step * (len(lines) - 1) + size <= room
        if fits_wide and fits_tall:
            break
        size -= 2 * SS
    f_head = sans(size, "Bold")
    track = -0.055 * size
    block = size * step * (len(lines) - 1) + size
    y = top + (room - block) / 2
    for i, ln in enumerate(lines):
        # the forward-looking line steps down, as it does on the page
        write(d, (pad, y), ln, f_head, FAINT if i == 2 else INK, track)
        y += size * step

    return img.resize((W, H), Image.LANCZOS)


def main():
    for code in ("en", "ru", "cnr"):
        out = ROOT / "public" / ("og.png" if code == "en" else "og-%s.png" % code)
        card(code).save(out, optimize=True)
        print("  wrote public/%s  (%d KB)" % (out.name, out.stat().st_size // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
