#!/usr/bin/env python3
"""Draw the 17 November 2026 world-news front page (1024x1024 PNG).

A one-page newspaper front page: masthead, three hero stories, ten
illustrated stories, a world map and a numbered list of thirty more --
43 stories from six continents, every one of them an event that happened
or was first reported on Tuesday 17 November 2026. Flat PIL drawings
only; no network, no photos. Facts were cross-checked against the
17 Nov 2026 reporting (Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN
round-ups) and against the day's other front pages; contested claims
are attributed in the text, never stated as settled fact.
Output: entry.png, 1024x1024, under the 1 MiB gate.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 20
X0, X1 = M, W - M
PAPER = (247, 242, 232)
INK = (18, 22, 38)
NAVY = (22, 32, 64)
GOLD = (198, 142, 38)
RED = (178, 34, 28)
GREY = (88, 88, 92)
BODY = (52, 52, 58)
LIGHT = (233, 226, 212)
SEA = (196, 216, 228)
LAND = (232, 214, 170)

SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
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
    x0, y0, x1, y1 = box
    n = max(1, y1 - y0)
    strip = Image.new("RGB", (1, n))
    px = strip.load()
    for y in range(n):
        t = y / (n - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t)
                         for i in range(3))
    img.paste(strip.resize((x1 - x0, n)), (x0, y0))


def headline(draw, text, fnt, box, fill=INK, leading=None):
    x0, y0, x1, _ = box
    lh = leading or int(fnt.size * 1.1)
    y = y0
    for line in wrap(draw, text, fnt, x1 - x0):
        draw.text((x0, y), line, font=fnt, fill=fill)
        y += lh
    return y


def kicker(draw, text, x, y, color, size=13):
    f = font(SANS_B, size)
    draw.text((x, y), text, font=f, fill=color)
    return y + size + 5


def fit_font(draw, text, path, size, max_w):
    """Largest font size (down to 8) whose text fits max_w pixels."""
    while size > 8:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, 8)


def clipped(fn, box):
    """Render an illustration onto a throwaway layer the size of its
    box, then paste it: no illustration element can ever bleed into
    the masthead, a headline or a neighbouring panel."""
    global img
    x0, y0, x1, y1 = box
    tmp = Image.new("RGB", (x1 - x0, y1 - y0), PAPER)
    old = img
    img = tmp
    try:
        fn(ImageDraw.Draw(tmp), (0, 0, x1 - x0, y1 - y0))
    finally:
        img = old
    img.paste(tmp, (x0, y0))


def caption_bar(draw, box, text, fill):
    """Dark strip with a white label across the bottom of an
    illustration; the label shrinks until it fits the box."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y1 - 22, x1, y1], fill=fill)
    f = fit_font(draw, text, SANS_B, 13, (x1 - x0) - 12)
    draw.text(((x0 + x1) // 2, y1 - 11), text, font=f,
              fill=(247, 242, 232), anchor="mm")


# ---------------------------------------------------------------- heroes

def ill_bridge(draw, box):
    """Kerch Strait at dusk: the bridge, one road span dropped into the
    sea, smoke over the break, a patrol boat below."""
    x0, y0, x1, y1 = box
    w = x1 - x0
    strip = 22
    horizon = y0 + int((y1 - y0 - strip) * 0.62)
    vgrad(img, (x0, y0, x1, horizon), (28, 34, 70), (228, 116, 48))
    # low sun, fully inside the sky
    sx, sy = x0 + int(w * 0.74), horizon - 20
    for r, c in ((15, (240, 140, 70)), (10, (246, 170, 96)),
                 (6, (252, 214, 150))):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=c)
    # sea
    draw.rectangle([x0, horizon, x1, y1 - strip], fill=(16, 30, 58))
    for i, yy in enumerate((horizon + 12, horizon + 26)):
        draw.line([(x0 + 24 + i * 60, yy), (x1 - 40 - i * 30, yy)],
                  fill=(70, 104, 148), width=3)
    deck_y = y0 + 34
    cx = x0 + w // 2
    # left span, then a broken stub diving down and the dropped span
    # tilted into the strait, then the right span
    draw.line([(x0, deck_y), (cx - 70, deck_y)], fill=(232, 228, 216),
              width=10)
    draw.line([(cx - 70, deck_y), (cx - 28, deck_y + 18)],
              fill=(232, 228, 216), width=8)
    draw.line([(cx - 28, deck_y + 18), (cx + 22, deck_y + 30)],
              fill=(200, 196, 184), width=8)
    draw.line([(cx + 32, deck_y + 18), (cx + 70, deck_y)],
              fill=(232, 228, 216), width=8)
    draw.line([(cx + 70, deck_y), (x1, deck_y)], fill=(232, 228, 216),
              width=10)
    # pylons, apexes well inside the box
    for px in (x0 + 64, x1 - 64):
        draw.line([(px - 26, deck_y), (px, deck_y - 28)],
                  fill=(232, 228, 216), width=7)
        draw.line([(px + 26, deck_y), (px, deck_y - 28)],
                  fill=(232, 228, 216), width=7)
        draw.line([(px - 26, deck_y - 14), (px + 26, deck_y - 14)],
                  fill=(232, 228, 216), width=4)
    # smoke plumes rising from the broken span, kept low
    for ox, oy, r, c in ((-26, -6, 11, (96, 92, 88)),
                         (0, -20, 14, (118, 114, 110)),
                         (26, -8, 10, (96, 92, 88))):
        draw.ellipse([cx + ox - r, deck_y + oy - r,
                      cx + ox + r, deck_y + oy + r], fill=c)
    # flames licking from the break in the deck itself
    draw.polygon([(cx - 30, deck_y + 3), (cx - 12, deck_y - 20),
                  (cx + 2, deck_y - 5), (cx + 18, deck_y - 17),
                  (cx + 30, deck_y + 3)], fill=(232, 120, 40))
    draw.polygon([(cx - 16, deck_y + 3), (cx - 6, deck_y - 11),
                  (cx + 8, deck_y - 4), (cx + 16, deck_y + 3)],
                 fill=(252, 210, 110))
    # glow on the water under the break
    draw.ellipse([cx - 40, horizon - 4, cx + 40, horizon + 8],
                 fill=(120, 70, 40))
    draw.ellipse([cx - 26, horizon - 2, cx + 26, horizon + 6],
                 fill=(190, 110, 50))
    # patrol boat, lower left, clear of the caption strip
    bx, by = x0 + 30, y1 - strip - 8
    draw.polygon([(bx, by), (bx + 84, by), (bx + 76, by - 16),
                  (bx + 8, by - 16)], fill=(12, 16, 30))
    draw.rectangle([bx + 52, by - 30, bx + 66, by - 16], fill=(12, 16, 30))
    for gx, gy in ((x0 + 200, y0 + 8), (x0 + 236, y0 + 18)):
        draw.arc([gx, gy, gx + 18, gy + 9], 200, 340,
                 fill=(232, 228, 216), width=2)
        draw.arc([gx + 18, gy, gx + 36, gy + 9], 200, 340,
                 fill=(232, 228, 216), width=2)
    caption_bar(draw, box, "KERCH STRAIT · STRUCK FOR A 2ND DAY", NAVY)


def ill_gulf(draw, box):
    """Schematic of the Gulf: Bahrain and the US radar, the drone
    tracks, the Qeshm strike and a tanker at Hormuz."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(214, 228, 232))
    # land: Iran across the top, Arabia below
    draw.polygon([(x0, y0), (x1, y0), (x1, y0 + 34), (x0 + 190, y0 + 44),
                  (x0 + 120, y0 + 30), (x0, y0 + 40)], fill=LAND)
    draw.polygon([(x0, y1), (x1, y1), (x1, y1 - 30), (x0 + 210, y1 - 38),
                  (x0 + 90, y1 - 26), (x0, y1 - 34)], fill=LAND)
    f = font(SANS_B, 12)
    draw.text((x0 + 10, y0 + 6), "IRAN", font=f, fill=INK)
    draw.text((x0 + 150, y1 - 16), "ARABIA", font=f, fill=GREY)
    # Bahrain radar dome on the lower shore
    bx, by = x0 + 108, y1 - 44
    draw.ellipse([bx - 13, by - 13, bx + 13, by + 2], fill=(240, 240, 240),
                 outline=INK, width=2)
    draw.rectangle([bx - 13, by, bx + 13, by + 6], fill=INK)
    draw.text((bx - 26, by + 10), "BAHRAIN", font=f, fill=INK)
    # drone tracks: dashed red arcs from Iran to Bahrain, blue intercept
    for i in range(6):
        t = i / 5
        px = int(x0 + 210 + t * (bx - x0 - 210))
        py = int(y0 + 34 - 26 * math.sin(t * math.pi) + t * (by - y0 - 34))
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    draw.ellipse([bx - 5, by - 18, bx + 5, by - 8], fill=(40, 90, 200))
    # Qeshm: burst and label
    qx, qy = x1 - 52, y0 + 52
    for a in range(8):
        ang = a * math.pi / 4
        draw.line([(qx, qy), (qx + 16 * math.cos(ang),
                              qy + 16 * math.sin(ang))],
                  fill=(232, 120, 40), width=3)
    draw.ellipse([qx - 6, qy - 6, qx + 6, qy + 6], fill=(252, 210, 110))
    draw.text((qx - 30, qy + 20), "QESHM", font=f, fill=INK)
    # tanker at Hormuz, lower right
    tx, ty = x1 - 96, y1 - 30
    draw.polygon([(tx, ty), (tx + 70, ty), (tx + 62, ty - 14),
                  (tx + 6, ty - 14)], fill=(16, 20, 36))
    draw.rectangle([tx + 44, ty - 26, tx + 56, ty - 14], fill=(16, 20, 36))
    draw.text((tx - 6, ty - 44), "HORMUZ", font=f, fill=INK)
    caption_bar(draw, box, "STRAIT OF HORMUZ · CLAIM UNVERIFIED", NAVY)


def ill_quad(draw, box):
    """Summit table with the four Quad flags: US, India, Japan,
    Australia."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(232, 226, 244))
    draw.rectangle([x0 + 16, y1 - 34, x1 - 16, y1 - 22], fill=GOLD)
    draw.rectangle([x0 + 30, y1 - 22, x1 - 30, y1 - 10], fill=(120, 86, 30))
    specs = [
        ((40, 60, 160), "US", "stripes"),
        ((255, 136, 0), "IN", "wheel"),
        ((240, 240, 240), "JP", "disc"),
        ((0, 40, 120), "AU", "stars"),
    ]
    fw = 58
    gap = (x1 - x0 - 4 * fw - 2 * 20) // 3
    for i, (colour, code, kind) in enumerate(specs):
        fx = x0 + 20 + i * (fw + gap)
        draw.line([(fx + fw // 2, y0 + 12), (fx + fw // 2, y1 - 34)],
                  fill=(120, 110, 100), width=3)
        draw.rectangle([fx, y0 + 12, fx + fw, y0 + 44], fill=colour,
                       outline=INK, width=1)
        if kind == "stripes":
            for s in range(3):
                draw.rectangle([fx, y0 + 12 + s * 11, fx + fw,
                                y0 + 17 + s * 11], fill=(240, 240, 240))
            draw.rectangle([fx, y0 + 12, fx + 24, y0 + 24],
                           fill=(40, 60, 160))
        elif kind == "wheel":
            draw.rectangle([fx, y0 + 12, fx + fw, y0 + 22],
                           fill=(255, 136, 0))
            draw.rectangle([fx, y0 + 34, fx + fw, y0 + 44],
                           fill=(19, 136, 8))
            draw.ellipse([fx + 24, y0 + 22, fx + 34, y0 + 32],
                         outline=(0, 0, 128), width=2)
        elif kind == "disc":
            draw.ellipse([fx + 21, y0 + 20, fx + 37, y0 + 36],
                         fill=(188, 0, 45))
        else:
            draw.rectangle([fx, y0 + 12, fx + 28, y0 + 28],
                           fill=(0, 40, 120))
            for sx, sy in ((fx + 44, y0 + 20), (fx + 48, y0 + 34),
                           (fx + 36, y0 + 30)):
                draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2],
                             fill=(240, 240, 240))
        f = font(SANS_B, 11)
        draw.text((fx + fw // 2, y0 + 50), code, font=f, fill=INK,
                  anchor="mt")
    caption_bar(draw, box, "QUAD SUMMIT · MANILA", (74, 44, 120))


# ------------------------------------------------------- small panels

def ill_nvidia(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(10, 26, 18))
    # chip
    cx, cy = x0 + 42, y0 + 32
    draw.rectangle([cx - 22, cy - 22, cx + 22, cy + 22], fill=(22, 120, 60),
                   outline=(120, 220, 140), width=2)
    draw.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], fill=(10, 26, 18))
    for dx in (-28, 28):
        for dy in (-14, 0, 14):
            draw.line([(cx + dx, cy + dy), (cx + dx + (8 if dx > 0 else -8),
                                             cy + dy)], fill=(120, 220, 140),
                      width=2)
    # rising bars along the bottom, clear of the labels above them
    bx = x0 + 88
    for i, h in enumerate((10, 15, 20, 26)):
        draw.rectangle([bx + i * 20, y1 - 6 - h, bx + i * 20 + 13, y1 - 6],
                       fill=(64, 200, 110))
    f = fit_font(draw, "$115.8bn", SANS_B, 14, (x1 - x0) - 92)
    draw.text((x0 + 88, y0 + 4), "$115.8bn", font=f, fill=(120, 230, 150))
    f2 = font(SANS_B, 11)
    draw.text((x0 + 88, y0 + 20), "DOW -849", font=f2, fill=(240, 120, 100))


def ill_ebola(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(238, 228, 208))
    # headline figure across the top, fitted to the box
    f = fit_font(draw, "11,000+ CASES", SANS_B, 15, (x1 - x0) - 8)
    draw.text(((x0 + x1) // 2, y0 + 3), "11,000+ CASES", font=f, fill=RED,
              anchor="ma")
    # clinic tent + red cross, bottom left
    tx, ty = x0 + 18, y1 - 6
    draw.polygon([(tx, ty), (tx + 72, ty), (tx + 55, ty - 26),
                  (tx + 17, ty - 26)], fill=(247, 242, 232),
                 outline=INK, width=2)
    draw.rectangle([tx + 30, ty - 22, tx + 42, ty - 6], fill=RED)
    draw.rectangle([tx + 24, ty - 17, tx + 48, ty - 11], fill=RED)
    # case-count bars: August (grey, short) vs November (red, tall)
    for i, h in enumerate((12, 26)):
        bx = x0 + 110 + i * 34
        draw.rectangle([bx, y1 - 6 - h, bx + 24, y1 - 6],
                       fill=(178, 34, 28) if i else (150, 140, 120))


def ill_measles(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(250, 238, 226))
    # three small flags: US, Mexico, Bolivia
    flags = [((40, 60, 160), "US"), ((0, 104, 71), "MX"),
             ((214, 0, 28), "BO")]
    for i, (c, code) in enumerate(flags):
        fx = x0 + 14 + i * 58
        draw.rectangle([fx, y0 + 10, fx + 46, y0 + 34], fill=c,
                       outline=INK, width=1)
        draw.rectangle([fx, y0 + 10, fx + 18, y0 + 22], fill=(240, 240, 240))
        f = font(SANS_B, 10)
        draw.text((fx + 23, y0 + 40), code, font=f, fill=INK, anchor="ma")
    # virus: spiked circle, clear of the flags above it
    vx, vy = x0 + 150, y0 + 45
    for a in range(8):
        ang = a * math.pi / 4
        draw.line([(vx + 8 * math.cos(ang), vy + 8 * math.sin(ang)),
                   (vx + 11 * math.cos(ang), vy + 11 * math.sin(ang))],
                  fill=RED, width=2)
    draw.ellipse([vx - 8, vy - 8, vx + 8, vy + 8], fill=RED)


def ill_cop(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(214, 232, 226))
    # globe
    gx, gy = x0 + 40, y0 + 28
    draw.ellipse([gx - 24, gy - 24, gx + 24, gy + 24], fill=(70, 130, 190),
                 outline=INK, width=2)
    draw.arc([gx - 24, gy - 11, gx + 24, gy + 11], 0, 360, fill=(240, 240,
              240), width=1)
    draw.line([(gx, gy - 24), (gx, gy + 24)], fill=(240, 240, 240), width=1)
    draw.ellipse([gx - 11, gy - 17, gx + 2, gy - 6], fill=(90, 170, 90))
    draw.ellipse([gx + 2, gy + 7, gx + 15, gy + 19], fill=(90, 170, 90))
    # draft document with a red question mark
    dx = x0 + 92
    draw.rectangle([dx, y0 + 6, dx + 76, y0 + 52], fill=(247, 242, 232),
                   outline=INK, width=2)
    for i in range(3):
        draw.line([(dx + 10, y0 + 17 + i * 9), (dx + 66, y0 + 17 + i * 9)],
                  fill=GREY, width=2)
    f = font(SANS_B, 13)
    draw.text((dx + 38, y0 + 44), "DRAFT", font=f, fill=RED, anchor="ma")


def ill_gaza(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(226, 214, 188))
    # tents, bottom
    for i, tx in enumerate((x0 + 14, x0 + 74, x0 + 134)):
        ty = y1 - 10
        draw.polygon([(tx, ty), (tx + 44, ty), (tx + 22, ty - 22)],
                     fill=(247, 242, 232), outline=INK, width=2)
    # aid truck, bottom right
    draw.rectangle([x0 + 96, y1 - 36, x0 + 150, y1 - 10], fill=(240, 240,
                   240), outline=INK, width=2)
    draw.rectangle([x0 + 150, y1 - 30, x0 + 168, y1 - 10], fill=(200, 60,
                   40), outline=INK, width=2)
    f = fit_font(draw, "1.4M FACE ACUTE HUNGER", SANS_B, 14, (x1 - x0) - 8)
    draw.text(((x0 + x1) // 2, y0 + 3), "1.4M FACE ACUTE HUNGER", font=f,
              fill=RED, anchor="ma")


def ill_mongolia(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(238, 232, 220))
    # flag: red-blue-red with yellow soyombo hint
    fx, fy = x0 + 14, y0 + 10
    draw.rectangle([fx, fy, fx + 20, fy + 30], fill=(200, 40, 40))
    draw.rectangle([fx + 20, fy, fx + 46, fy + 30], fill=(0, 80, 160))
    draw.rectangle([fx + 46, fy, fx + 66, fy + 30], fill=(200, 40, 40))
    draw.ellipse([fx + 28, fy + 8, fx + 38, fy + 18], fill=(252, 220, 90))
    # resignation letter
    dx = x0 + 92
    draw.rectangle([dx, y0 + 6, dx + 80, y0 + 52], fill=(247, 242, 232),
                   outline=INK, width=2)
    for i in range(3):
        draw.line([(dx + 10, y0 + 16 + i * 8), (dx + 70, y0 + 16 + i * 8)],
                  fill=GREY, width=2)
    draw.line([(dx + 48, y0 + 44), (dx + 70, y0 + 44)], fill=INK, width=2)
    f = fit_font(draw, "RESIGNATION", SANS_B, 11, 76)
    draw.text((dx + 40, y0 + 38), "RESIGNATION", font=f, fill=RED,
              anchor="ma")


def ill_serbia(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(226, 232, 244))
    # parliament semicircle: red seats 140, blue 103
    cx, cy = x0 + 94, y1 - 8
    for i in range(12):
        ang = math.pi + i * math.pi / 11
        px = cx + 56 * math.cos(ang)
        py = cy + 36 * math.sin(ang)
        col = RED if i < 7 else (40, 60, 160)
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=col)
    f = font(SANS_B, 15)
    draw.text((x0 + 12, y0 + 2), "140", font=f, fill=RED)
    draw.text((x1 - 12, y0 + 2), "103", font=f, fill=(40, 60, 160),
              anchor="ra")
    f2 = font(SANS_B, 10)
    draw.text((x0 + 12, y0 + 20), "STUDENTS", font=f2, fill=GREY)
    draw.text((x1 - 12, y0 + 20), "VUCIC BLOC", font=f2, fill=GREY,
              anchor="ra")


def ill_dhaka(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(232, 226, 210))
    # factory + chimney
    draw.rectangle([x0 + 14, y1 - 40, x0 + 96, y1 - 10], fill=(120, 110,
                   100), outline=INK, width=2)
    draw.rectangle([x0 + 80, y1 - 56, x0 + 94, y1 - 40], fill=(120, 110,
                   100), outline=INK, width=2)
    for i in range(3):
        draw.rectangle([x0 + 24 + i * 22, y1 - 34, x0 + 38 + i * 22,
                        y1 - 20], fill=(252, 220, 90))
    # workers + placard
    for wx in (x0 + 116, x0 + 136, x0 + 156):
        draw.ellipse([wx - 5, y1 - 40, wx + 5, y1 - 30], fill=(90, 60, 40))
        draw.rectangle([wx - 6, y1 - 30, wx + 6, y1 - 10], fill=(40, 90,
                       60))
    draw.rectangle([x0 + 104, y0 + 8, x0 + 176, y0 + 30], fill=(247, 242,
                   232), outline=INK, width=2)
    f = font(SANS_B, 12)
    draw.text((x0 + 140, y0 + 19), "TK 30,000", font=f, fill=INK,
              anchor="mm")


def ill_crash(draw, box):
    x0, y0, x1, y1 = box
    vgrad(img, (x0, y0, x1, y1), (200, 210, 220), (150, 160, 170))
    # mountains
    draw.polygon([(x0, y1), (x0 + 60, y0 + 34), (x0 + 120, y1)],
                 fill=(110, 120, 130))
    draw.polygon([(x0 + 90, y1), (x0 + 150, y0 + 44), (x1, y1)],
                 fill=(90, 100, 112))
    # plane diving, nose down
    px, py = x0 + 96, y0 + 22
    draw.polygon([(px - 34, py + 8), (px + 34, py - 8), (px + 40, py - 2),
                  (px - 28, py + 14)], fill=(30, 34, 44))
    draw.polygon([(px - 6, py - 2), (px + 2, py - 16), (px + 10, py - 2)],
                 fill=(30, 34, 44))
    for ox, oy, r in ((px + 30, py + 12, 7), (px + 40, py + 20, 9),
                      (px + 50, py + 28, 7)):
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=(96, 92, 88))


def ill_trial(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(232, 226, 208))
    # courthouse columns
    draw.polygon([(x0 + 24, y0 + 16), (x0 + 164, y0 + 16), (x0 + 94,
                  y0 + 2)], fill=(150, 140, 120))
    for cx in (x0 + 40, x0 + 80, x0 + 120, x0 + 156):
        draw.rectangle([cx - 6, y0 + 18, cx + 6, y1 - 10], fill=(247, 242,
                       232), outline=INK, width=1)
    draw.rectangle([x0 + 24, y1 - 10, x0 + 164, y1 - 4], fill=(150, 140,
                   120))
    # gavel
    gx, gy = x0 + 150, y0 + 44
    draw.rectangle([gx - 4, gy - 16, gx + 22, gy - 4], fill=(120, 80, 40))
    draw.line([(gx + 8, gy - 4), (gx - 6, gy + 12)], fill=(120, 80, 40),
              width=5)
    f = font(SANS_B, 12)
    draw.text((x0 + 14, y0 + 44), "5 CHARGES", font=f, fill=RED)


# ------------------------------------------------------------------- map

def ill_map(draw, box):
    """Simplified world map: numbered pins for stories 1-13, dots for
    the rest. Rough flat continents on a faint graticule, not a survey.
    Pins are spread so neighbours in crowded Europe do not cover each
    other."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=SEA)
    # faint graticule
    for gx in range(x0 + 40, x1, 40):
        draw.line([(gx, y0), (gx, y1)], fill=(178, 200, 214), width=1)
    for gy in range(y0 + 36, y1, 36):
        draw.line([(x0, gy), (x1, gy)], fill=(178, 200, 214), width=1)
    # continents, in map-local coordinates (map is ~330 x ~160)
    land_polys = [
        # North America
        [(14, 14), (58, 6), (104, 12), (114, 32), (94, 50), (78, 42),
         (68, 60), (48, 54), (28, 42), (10, 30)],
        # South America
        [(70, 80), (96, 74), (112, 92), (104, 122), (90, 146),
         (78, 126), (66, 100)],
        # Europe
        [(148, 18), (178, 8), (200, 18), (194, 38), (172, 44),
         (154, 34)],
        # Africa
        [(150, 52), (186, 46), (206, 62), (200, 92), (186, 118),
         (168, 104), (152, 78)],
        # Asia
        [(204, 10), (264, 4), (314, 12), (320, 36), (294, 52),
         (270, 40), (246, 58), (224, 48), (208, 30)],
        # Australia
        [(268, 124), (300, 118), (314, 132), (298, 144), (272, 138)],
    ]
    for poly in land_polys:
        draw.polygon([(x0 + px, y0 + py) for px, py in poly], fill=LAND,
                     outline=(200, 180, 140))
    pins = {  # story -> (map-local x, y, colour)
        1: (202, 32, (40, 60, 160)), 2: (236, 56, (214, 120, 0)),
        3: (300, 58, (120, 40, 140)), 4: (50, 28, (178, 34, 28)),
        5: (176, 88, (30, 120, 60)), 6: (56, 44, (178, 34, 28)),
        7: (190, 44, (30, 120, 60)), 8: (214, 52, (214, 120, 0)),
        9: (274, 26, (120, 40, 140)), 10: (178, 26, (40, 60, 160)),
        11: (256, 52, (120, 40, 140)), 12: (262, 12, (40, 60, 160)),
        13: (190, 112, (30, 120, 60)),
    }
    f = font(SANS_B, 10)
    for n, (px, py, col) in pins.items():
        draw.ellipse([x0 + px - 8, y0 + py - 8, x0 + px + 8, y0 + py + 8],
                     fill=col, outline=(255, 255, 255), width=1)
        draw.text((x0 + px, y0 + py), str(n), font=f,
                  fill=(255, 255, 255), anchor="mm")
    dots = [(38, 38), (86, 58), (94, 114), (118, 28), (158, 58),
            (212, 58), (242, 38), (272, 66), (292, 86), (302, 132),
            (182, 66), (222, 28), (58, 86), (148, 26), (282, 26),
            (98, 38), (232, 66), (172, 106), (262, 86), (312, 56)]
    for px, py in dots:
        draw.ellipse([x0 + px - 3, y0 + py - 3, x0 + px + 3, y0 + py + 3],
                     fill=(90, 90, 96))


# ------------------------------------------------------------------ build

HEROES = [
    (ill_bridge, "1  EUROPE · UKRAINE WAR", (40, 60, 160),
     "Ukraine says a Crimea Bridge road span fell into the sea",
     "Second strike in two days; Zelenskyy hails an \u201cunprecedented "
     "operation\u201d. The Kremlin vows to rebuild."),
    (ill_gulf, "2  MIDDLE EAST · IRAN WAR", (214, 120, 0),
     "Iran sends drones at a US radar in Bahrain; US hits back",
     "Bahrain and the US say all were downed; US jets then strike "
     "Qeshm. Iran says tankers hit mines in Hormuz."),
    (ill_quad, "3  ASIA · DIPLOMACY", (120, 40, 140),
     "Trump holds his first Quad summit, in Manila",
     "The four unveil critical-minerals deals; Trump is due in "
     "Shenzhen for Thursday\u2019s talks with Xi and Putin."),
]

SMALL = [
    (ill_nvidia, "4  US · BUSINESS", (30, 90, 50),
     "Nvidia sales double to $115.8bn",
     "Reported after the close. Earlier the Dow fell 849 points."),
    (ill_ebola, "5  AFRICA · HEALTH", (30, 120, 60),
     "Ebola cases in DR Congo top 11,000",
     "Cases doubled in three months; about 5,400 have died."),
    (ill_measles, "6  AMERICAS · HEALTH", (178, 34, 28),
     "US, Mexico, Bolivia lose measles-free status",
     "PAHO cites a year of spread; US cases top 5,700."),
    (ill_cop, "7  GLOBAL · CLIMATE", (30, 80, 60),
     "COP31 split over fossil-fuel phase-out",
     "Nations weigh the first draft; the Antalya talks end Friday."),
    (ill_gaza, "8  MIDDLE EAST · GAZA", (140, 40, 30),
     "Gaza truce at risk of collapse",
     "UN agencies say 1.4m face acute hunger as winter aid stalls."),
    (ill_mongolia, "9  ASIA · POLITICS", (120, 40, 140),
     "Mongolia\u2019s president says he will resign",
     "He denies a $25m bribe claim; parliament must accept."),
    (ill_serbia, "10  EUROPE · POLITICS", (40, 60, 160),
     "Serbia\u2019s student-led majority takes seats",
     "Student List holds 140 of 250 seats; Vu\u010di\u0107\u2019s party is out."),
    (ill_dhaka, "11  ASIA · LABOUR", (120, 40, 140),
     "Bangladesh police tear-gas garment workers",
     "They want Tk 30,000 a month, up from 12,500."),
    (ill_crash, "12  RUSSIA · AIR CRASH", (40, 60, 160),
     "An-12 crash in Siberia kills all 19",
     "It came down near Kemerovo; a fault is suspected."),
    (ill_trial, "13  AFRICA · JUSTICE", (30, 120, 60),
     "Mozambique puts opposition leader on trial",
     "Ven\u00e2ncio Mondlane faces 5 charges over deadly 2024 protests."),
]

ALSO = [
    (14, "Kyiv: Russia hits two Dnipro bridges"),
    (15, "Russia says it downed a record 1,441 drones"),
    (16, "UN: Ukraine civilian deaths top all of 2025"),
    (17, "Prague: two trains collide; 46 injured"),
    (18, "France: public-sector strike; 146,000 march"),
    (19, "Poland: Tusk survives no-confidence vote"),
    (20, "Turkey: police seize opposition TV channel"),
    (21, "Moldova shuts airspace over a Russian drone"),
    (22, "Germany: Deutsche Bank falls on data leak"),
    (23, "Japan: jets scramble over Russian planes"),
    (24, "UK sanctions 8 settlement firms in West Bank"),
    (25, "Israel: Kahana elected Knesset speaker, 66\u201352"),
    (26, "West Bank: settlers kill a woman, 72"),
    (27, "Ukraine: Europeans join peace talks"),
    (28, "Apple: Pay, iCloud, App Store outage"),
    (29, "JPMorgan outage cuts off Zelle users"),
    (30, "Darwin: M6.6 quake felt; no tsunami"),
    (31, "India: Cyclone Akvan nears; Odisha evacuates"),
    (32, "China\u2013Canada: Xi and Carney cut tariffs"),
    (33, "Thailand to scrap tariffs on US goods"),
    (34, "South Korea: IMF lifts 2026 forecast to 3.9%"),
    (35, "Football: Norway 3\u20132 Denmark; Haaland scores 2"),
    (36, "Football: Togo 3\u20130 Algeria, AFCON qualifier"),
    (37, "Vatican: Pope Leo XIV back from South America"),
    (38, "Sudan: UN verifies 2,230 civilian deaths"),
    (39, "Five EU states plan Rwanda asylum hub"),
    (40, "Haiti: Aristide\u2019s party fields no candidates"),
    (41, "Pentagon fails its audit, ninth year"),
    (42, "Malaysia: Macron visit seals partnership"),
    (43, "Voyager 1 nears one light-day from Earth"),
]

ALSO_COLOURS = [(178, 34, 28), (40, 60, 160), (214, 120, 0),
                (120, 40, 140), (30, 120, 60)]


def build():
    global img
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- kicker + masthead ------------------------------------------
    f_kick = font(SANS_B, 13)
    draw.text((X0, 12), "THE WORLD\u2019S NEWS IN ONE PICTURE", font=f_kick,
              fill=RED)
    rtxt = "43 STORIES  ·  6 CONTINENTS  ·  ALL FROM TUESDAY"
    draw.text((X1, 12), rtxt, font=f_kick, fill=GREY, anchor="ra")
    f_mast = font(SERIF_B, 62)
    draw.text((W // 2, 62), "Tuesday 17 November 2026", font=f_mast,
              fill=INK, anchor="mm")
    draw.rectangle([X0, 100, X1, 103], fill=INK)
    draw.rectangle([X0, 106, X1, 108], fill=GOLD)

    # ---- hero row ----------------------------------------------------
    hy0, ill_h = 116, 94
    hgap = 12
    hw = (X1 - X0 - 2 * hgap) // 3
    hero_bottom = hy0
    f_hhead, f_hbody = font(SANS_B, 23), font(SANS, 15)
    for i, (fn, kick, col, head, body) in enumerate(HEROES):
        hx0 = X0 + i * (hw + hgap)
        hx1 = hx0 + hw
        clipped(fn, (hx0, hy0, hx1, hy0 + ill_h))
        y = kicker(draw, kick, hx0, hy0 + ill_h + 8, col, size=13)
        y = headline(draw, head, f_hhead, (hx0, y, hx1, 0), leading=26)
        y = headline(draw, body, f_hbody, (hx0, y + 3, hx1, 0), fill=BODY,
                     leading=19)
        hero_bottom = max(hero_bottom, y)
    draw.rectangle([X0, hero_bottom + 8, X1, hero_bottom + 10], fill=INK)

    # ---- small rows --------------------------------------------------
    sgap = 10
    sw = (X1 - X0 - 4 * sgap) // 5
    sill_h = 58
    f_shead, f_sbody = font(SANS_B, 16), font(SANS, 12)
    row_bottom = hero_bottom + 10
    for row in range(2):
        ry0 = row_bottom + 12 if row == 0 else row_bottom + 10
        rb = ry0
        for j in range(5):
            fn, kick, col, head, body = SMALL[row * 5 + j]
            sx0 = X0 + j * (sw + sgap)
            sx1 = sx0 + sw
            clipped(fn, (sx0, ry0, sx1, ry0 + sill_h))
            y = kicker(draw, kick, sx0, ry0 + sill_h + 6, col, size=11)
            y = headline(draw, head, f_shead, (sx0, y, sx1, 0), leading=18)
            y = headline(draw, body, f_sbody, (sx0, y + 2, sx1, 0),
                         fill=BODY, leading=15)
            rb = max(rb, y)
        row_bottom = rb
    draw.rectangle([X0, row_bottom + 8, X1, row_bottom + 10], fill=INK)

    # ---- map + also-on list ------------------------------------------
    by0 = row_bottom + 14
    map_w, map_h = 330, 160
    clipped(ill_map, (X0, by0 + 22, X0 + map_w, by0 + 22 + map_h))
    f_lab = font(SANS_B, 15)
    draw.text((X0, by0), "WHERE IT HAPPENED", font=f_lab, fill=RED)
    draw.text((X0 + map_w + 16, by0), "ALSO ON TUESDAY 17 NOVEMBER",
              font=f_lab, fill=RED)
    f_leg = font(SANS, 10)
    draw.text((X0, by0 + 22 + map_h + 4),
              "Pins: stories 1\u201313  ·  dots: 14\u201343", font=f_leg,
              fill=GREY)
    f_item = font(SANS, 12)
    lx0 = X0 + map_w + 16
    col_w = (X1 - lx0 - 12) // 2
    for i, (n, text) in enumerate(ALSO):
        ix = lx0 + (i // 15) * (col_w + 12)
        iy = by0 + 22 + (i % 15) * 11
        col = ALSO_COLOURS[i % len(ALSO_COLOURS)]
        draw.ellipse([ix, iy + 1, ix + 11, iy + 12], fill=col)
        f_num = font(SANS_B, 8)
        draw.text((ix + 5.5, iy + 6.5), str(n), font=f_num,
                  fill=(255, 255, 255), anchor="mm")
        draw.text((ix + 16, iy), text, font=f_item, fill=INK)
    list_bottom = by0 + 22 + 15 * 11

    # ---- footer -------------------------------------------------------
    fy = max(by0 + 22 + map_h + 20, list_bottom + 8)
    assert fy + 16 <= H - M, "layout overflow: %d" % fy
    draw.rectangle([X0, fy, X1, fy + 2], fill=GOLD)
    f_foot = font(SANS, 11)
    draw.text((X0, fy + 7),
              "Every story here happened or was first reported on Tuesday "
              "17 November 2026. Sources: Reuters, AP, AFP, BBC, Al "
              "Jazeera, WHO, UN.",
              font=f_foot, fill=GREY)
    print("layout: hero_bottom=%d row_bottom=%d footer_y=%d"
          % (hero_bottom, row_bottom, fy))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    build()
