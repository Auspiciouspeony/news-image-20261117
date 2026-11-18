#!/usr/bin/env python3
"""Draw the 17 November 2026 world-news front page (1024x1024 PNG).

Flat newspaper illustration, drawn with PIL only. Reads nothing from the
network: every fact on the page was checked against 17 Nov 2026 reporting
(Algenom, Just Security Early Edition, Zark News, AP/TFI round-ups) before
drawing. Output: entry.png, 1024x1024, under the 1 MiB gate.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 26                      # outer margin
PAPER = (247, 242, 232)     # newsprint cream
INK = (18, 22, 38)          # near-black navy
NAVY = (22, 32, 64)
NAVY2 = (34, 48, 92)
GOLD = (198, 142, 38)
RED = (178, 34, 28)
GREY = (88, 88, 92)
LIGHT = (233, 226, 212)

SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def vgrad(img, box, top, bottom):
    """Vertical gradient fill inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    n = max(1, y1 - y0)
    strip = Image.new("RGB", (1, n))
    px = strip.load()
    for y in range(n):
        t = y / (n - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    img.paste(strip.resize((x1 - x0, n)), (x0, y0))


def headline(draw, text, fnt, box, fill=INK, leading=None):
    """Draw wrapped headline inside box; returns y just below last line."""
    x0, y0, x1, _ = box
    lh = leading or int(fnt.size * 1.08)
    y = y0
    for line in wrap(draw, text, fnt, x1 - x0):
        draw.text((x0, y), line, font=fnt, fill=fill)
        y += lh
    return y


def hero_bridge(draw, box):
    """Dusk scene: the Kerch bridge over the strait, one span collapsed,
    smoke and fire where the deck fell. Flat illustration, no photo."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    horizon = y0 + int(h * 0.62)
    # sky: indigo dusk down to a burnt-orange horizon
    vgrad(img, (x0, y0, x1, horizon), (24, 30, 66), (226, 110, 44))
    # low sun + glow, clear of the deck line
    sx, sy = x0 + int(w * 0.74), horizon - 58
    for r, c in ((64, (240, 140, 70)), (44, (246, 170, 96)), (28, (252, 214, 150))):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=c)
    # low distant shoreline along the horizon, left
    draw.polygon([(x0, horizon), (x0 + 150, horizon - 22),
                  (x0 + 300, horizon - 6), (x0 + 330, horizon)],
                 fill=(58, 48, 70))
    # sea
    draw.rectangle([x0, horizon, x1, y1], fill=(16, 30, 58))
    for i, yy in enumerate((horizon + 16, horizon + 42, horizon + 68)):
        draw.line([(x0 + 30 + i * 90, yy), (x1 - 60 - i * 40, yy)],
                  fill=(70, 104, 148), width=3)
    # bridge deck: left span, gap, right span (deck dips at the break)
    deck_y = horizon - 96
    cx = x0 + w // 2
    draw.line([(x0, deck_y), (cx - 74, deck_y)], fill=(232, 228, 216), width=10)
    draw.line([(cx - 74, deck_y), (cx - 30, deck_y + 34)], fill=(232, 228, 216), width=8)
    draw.line([(cx + 30, deck_y + 34), (cx + 74, deck_y)], fill=(232, 228, 216), width=8)
    draw.line([(cx + 74, deck_y), (x1, deck_y)], fill=(232, 228, 216), width=10)
    # smoke plumes rising from the broken span (small, tight, dark,
    # and kept inside the hero box)
    for ox, oy, r, c in ((-30, -28, 13, (96, 92, 88)),
                         (2, -46, 17, (118, 114, 110)),
                         (30, -30, 11, (96, 92, 88)),
                         (14, -62, 11, (138, 134, 128))):
        draw.ellipse([cx + ox - r, deck_y + oy - r,
                      cx + ox + r, deck_y + oy + r], fill=c)
    # flames licking from the break in the deck itself
    for pts, c in (
            ([(cx - 34, deck_y + 4), (cx - 12, deck_y - 30),
              (cx + 2, deck_y - 6), (cx + 18, deck_y - 26),
              (cx + 34, deck_y + 4)], (232, 120, 40)),
            ([(cx - 18, deck_y + 4), (cx - 6, deck_y - 18),
              (cx + 8, deck_y - 4), (cx + 18, deck_y + 4)], (252, 210, 110))):
        draw.polygon(pts, fill=c)
    # glow on the water under the break
    draw.ellipse([cx - 56, horizon - 6, cx + 56, horizon + 12], fill=(120, 70, 40))
    draw.ellipse([cx - 34, horizon - 4, cx + 34, horizon + 8], fill=(190, 110, 50))
    # pylons (A-frames, kept inside the hero box) and cables
    for px in (x0 + 168, x0 + w - 168):
        draw.line([(px - 40, deck_y), (px, deck_y - 64)], fill=(232, 228, 216), width=9)
        draw.line([(px + 40, deck_y), (px, deck_y - 64)], fill=(232, 228, 216), width=9)
        draw.line([(px - 40, deck_y - 26), (px + 40, deck_y - 26)],
                  fill=(232, 228, 216), width=5)
    for tx in (x0 + 60, x0 + 260, x0 + 420, x0 + 600, x0 + 760, x0 + 920):
        draw.line([(tx, deck_y), (tx + 48, deck_y - 56)], fill=(190, 186, 172), width=2)
    # small tanker, lower left, smoke from its funnel
    tx0, ty0 = x0 + 70, y1 - 58
    draw.polygon([(tx0, ty0), (tx0 + 150, ty0), (tx0 + 138, ty0 - 26),
                  (tx0 + 12, ty0 - 26)], fill=(12, 16, 30))
    draw.rectangle([tx0 + 96, ty0 - 52, tx0 + 122, ty0 - 26], fill=(12, 16, 30))
    draw.ellipse([tx0 + 104, ty0 - 64, tx0 + 118, ty0 - 50], fill=(140, 136, 130))
    draw.ellipse([tx0 + 109, ty0 - 76, tx0 + 119, ty0 - 66], fill=(150, 146, 140))
    # gulls
    for gx, gy in ((x0 + 700, y0 + 44), (x0 + 760, y0 + 66), (x0 + 640, y0 + 78)):
        draw.arc([gx, gy, gx + 26, gy + 12], 200, 340, fill=(232, 228, 216), width=3)
        draw.arc([gx + 26, gy, gx + 52, gy + 12], 200, 340, fill=(232, 228, 216), width=3)


def panel_hormuz(draw, box):
    """Tanker on a strait at dawn, smoke rising from its deck."""
    x0, y0, x1, y1 = box
    vgrad(img, (x0, y0, x1, y1), (250, 196, 130), (214, 128, 60))
    draw.rectangle([x0, y0 + 78, x1, y1], fill=(24, 52, 92))
    draw.line([(x0, y0 + 78), (x1, y0 + 78)], fill=(240, 220, 180), width=2)
    for i in range(3):
        yy = y0 + 96 + i * 14
        draw.line([(x0 + 12 + i * 22, yy), (x1 - 14 - i * 16, yy)],
                  fill=(96, 132, 172), width=2)
    # tanker hull + bridge + funnel; smoke rises from the funnel alone
    hx, hy = x0 + 34, y1 - 34
    draw.polygon([(hx, hy), (hx + 220, hy), (hx + 206, hy - 30),
                  (hx + 14, hy - 30)], fill=(16, 20, 36))
    draw.rectangle([hx + 150, hy - 58, hx + 182, hy - 30], fill=(16, 20, 36))
    draw.rectangle([hx + 44, hy - 48, hx + 62, hy - 30], fill=(178, 34, 28))
    for ox, oy, r in ((53, -60, 11), (58, -76, 13), (66, -90, 9)):
        draw.ellipse([hx + ox - r, hy + oy - r, hx + ox + r, hy + oy + r],
                     fill=(96, 92, 88))
    # small flame on the deck, mid-ship
    draw.polygon([(hx + 104, hy - 28), (hx + 112, hy - 48),
                  (hx + 120, hy - 28)], fill=(240, 140, 50))
    draw.polygon([(hx + 109, hy - 28), (hx + 113, hy - 40),
                  (hx + 117, hy - 28)], fill=(252, 210, 110))


def panel_summit(draw, box):
    """Three flags over a summit table: China, the US, Russia."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(30, 44, 86))
    # table
    draw.rectangle([x0 + 30, y1 - 34, x1 - 30, y1 - 22], fill=(198, 142, 38))
    draw.rectangle([x0 + 44, y1 - 22, x1 - 44, y1 - 8], fill=(120, 86, 30))
    # three flags on poles
    specs = [
        (x0 + 62, (198, 30, 30), "CN"),   # red
        (x0 + 142, (40, 60, 160), "US"),  # blue field
        (x0 + 222, (240, 240, 240), "RU"),  # white
    ]
    for fx, colour, _ in specs:
        draw.line([(fx, y0 + 18), (fx, y1 - 34)], fill=(232, 228, 216), width=4)
        draw.rectangle([fx, y0 + 18, fx + 62, y0 + 52], fill=colour)
    # US flag stripes + stars hint
    fx = x0 + 142
    for i in range(3):
        draw.rectangle([fx, y0 + 18 + i * 12, fx + 62, y0 + 24 + i * 12],
                       fill=(240, 240, 240))
    draw.rectangle([fx, y0 + 18, fx + 26, y0 + 34], fill=(40, 60, 160))
    # Russia flag stripes
    fx = x0 + 222
    draw.rectangle([fx, y0 + 29, fx + 62, y0 + 41], fill=(40, 90, 200))
    draw.rectangle([fx, y0 + 41, fx + 62, y0 + 52], fill=(198, 30, 30))
    # China flag stars hint
    fx = x0 + 62
    for sx, sy in ((fx + 12, y0 + 28), (fx + 26, y0 + 24), (fx + 24, y0 + 38)):
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(252, 220, 90))


def panel_pentagon(draw, box):
    """The Pentagon, grey on a pale sky, with a red AUDIT FAILED stamp
    below it — nothing overlaps the building."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(214, 206, 188))
    cx, cy = (x0 + x1) // 2, y0 + 46
    r = 40
    pts = []
    import math
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=(96, 100, 108))
    draw.polygon([(cx + r * 0.55 * math.cos(-math.pi / 2 + i * 2 * math.pi / 5),
                   cy + r * 0.55 * math.sin(-math.pi / 2 + i * 2 * math.pi / 5))
                  for i in range(5)], fill=(214, 206, 188))
    # stamp, clear of the building
    draw.rectangle([x0 + 40, y1 - 30, x1 - 40, y1 - 6], outline=RED, width=3)
    f = font(SANS_B, 21)
    draw.text(((x0 + x1) / 2, y1 - 18), "AUDIT FAILED",
              font=f, fill=RED, anchor="mm")


def build():
    global img
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    x0, x1 = M, W - M

    # ---- masthead ------------------------------------------------------
    draw.rectangle([x0, M, x1, 118], fill=NAVY)
    f_mast = font(SERIF_B, 58)
    draw.text((W // 2, 52), "THE WORLD IN ONE DAY", font=f_mast,
              fill=(247, 242, 232), anchor="mm")
    f_date = font(SANS_B, 27)
    draw.text((W // 2, 94), "TUESDAY  17  NOVEMBER  2026",
              font=f_date, fill=(226, 182, 90), anchor="mm")
    draw.rectangle([x0, 122, x1, 126], fill=GOLD)

    # ---- hero ----------------------------------------------------------
    hy0, hy1 = 138, 380
    hero_bridge(draw, (x0, hy0, x1, hy1))
    draw.rectangle([x0, hy1, x1, hy1 + 4], fill=GOLD)
    y = headline(draw, "UKRAINE HITS CRIMEA BRIDGE AGAIN",
                 font(SERIF_B, 46), (x0, hy1 + 14, x1, 0), fill=INK)
    y = headline(draw,
                 "Second strike in 24 hours collapses a span of the Kerch "
                 "crossing.",
                 font(SANS, 22), (x0, y + 4, x1, 0), fill=(52, 52, 58),
                 leading=28)
    y = headline(draw,
                 "Russian missiles hit Kyiv\u2019s bridges \u2014 Zelenskyy "
                 "hails \u201can unprecedented operation\u201d.",
                 font(SANS, 22), (x0, y, x1, 0), fill=(52, 52, 58),
                 leading=28)
    draw.rectangle([x0, y + 12, x1, y + 14], fill=INK)

    # ---- three panels --------------------------------------------------
    # Measured, not guessed: panel block height follows its real text.
    py0 = y + 20
    ill_h = 92
    panels = [
        (panel_hormuz, "TANKERS HIT BY MINES OFF HORMUZ",
         "Iran says mines struck ships near the strait; a tanker is left "
         "disabled off Oman as a third US carrier reaches the Gulf."),
        (panel_summit, "XI, TRUMP AND PUTIN TO MEET THURSDAY",
         "China confirms the first three-way summit of the three leaders, "
         "on the sidelines of APEC in Shenzhen."),
        (panel_pentagon, "PENTAGON FAILS ITS AUDIT \u2014 9TH YEAR",
         "Auditors again cannot verify the books, covering more than "
         "$4.8 trillion in assets."),
    ]
    pw = (x1 - x0 - 2 * 18) // 3
    f_head, f_body = font(SANS_B, 25), font(SANS, 19)
    panel_bottom = py0
    for i, (fn, head, body) in enumerate(panels):
        px0 = x0 + i * (pw + 18)
        px1 = px0 + pw
        fn(draw, (px0, py0, px1, py0 + ill_h))
        draw.rectangle([px0, py0 + ill_h, px1, py0 + ill_h + 2], fill=GOLD)
        yy = headline(draw, head, f_head, (px0, py0 + ill_h + 12, px1, 0),
                      leading=29)
        yy = headline(draw, body, f_body, (px0, yy + 4, px1, 0),
                      fill=(52, 52, 58), leading=23)
        panel_bottom = max(panel_bottom, yy)

    # ---- also-on strip -------------------------------------------------
    sy0 = panel_bottom + 18
    draw.rectangle([x0, sy0, x1, sy0 + 4], fill=INK)
    f_lab = font(SANS_B, 22)
    draw.text((x0, sy0 + 16), "ALSO ON 17 NOVEMBER", font=f_lab, fill=RED)
    items = [
        "Japan scrambles jets as suspected Russian planes enter its airspace",
        "US measles cases hit their highest since 1991; 13 babies born with the virus",
        "UK sanctions firms building settlements in the occupied West Bank",
        "Xi and Canada\u2019s Carney agree tariff cuts and deeper ties",
    ]
    f_item = font(SANS, 19)
    col_w = (x1 - x0 - 24) // 2
    strip_bottom = sy0 + 50
    for i, item in enumerate(items):
        ix = x0 + (i % 2) * (col_w + 24)
        iy = sy0 + 50 + (i // 2) * 46
        lines = wrap(draw, item, f_item, col_w - 20)
        yy = iy
        for line in lines[:2]:
            draw.text((ix + 20, yy), line, font=f_item, fill=INK)
            yy += 24
        draw.rectangle([ix, iy + 6, ix + 10, iy + 16], fill=GOLD)
        strip_bottom = max(strip_bottom, yy)

    # ---- bottom rule ---------------------------------------------------
    fy = strip_bottom + 12
    assert fy + 4 <= H - M, "layout overflow: %d > %d" % (fy, H - M)
    draw.rectangle([x0, fy, x1, fy + 2], fill=GOLD)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    build()
