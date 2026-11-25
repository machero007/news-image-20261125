#!/usr/bin/env python3
"""Build entry.png for make.fun news-image-20261125.

Draws a dense 1024x1024 newspaper-style image summing up the world news
of Wednesday 25 November 2026. Everything is drawn with PIL; no external
images, no network, deterministic output (fixed seed, no timestamps).

Layout:
  header band          y   0..118
  4 panels (2 x 2)     y 126..322 and 330..526
  "More from 25 Nov"   y 534..896  (title bar + 2 columns x 10/9 items)
  UTC wire strip       y 902..960
  footer               y 966..1024
"""

import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

random.seed(20261125)

# ---------------------------------------------------------------- palette
NAVY = (20, 36, 62)
NAVY2 = (28, 52, 88)
CREAM = (247, 243, 232)
PAPER = (255, 253, 246)
INK = (24, 24, 22)
MUTED = (90, 86, 76)
GOLD = (212, 160, 32)
GOLD_LT = (255, 214, 90)
RED = (178, 34, 34)
TEAL = (14, 116, 110)
BLUE = (30, 90, 160)
ORANGE = (214, 110, 20)
GREEN = (34, 120, 60)
PURPLE = (110, 70, 160)
RULE = (200, 192, 172)
PANEL_BG = (255, 255, 255)
SKY = (214, 232, 244)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


F_TITLE = font(FONTB, 46)
F_SUB = font(FONTB, 20)
F_DATE = font(FONTB, 17)
F_KICK = font(FONTB, 13)
F_HEAD = font(FONTB, 20)
F_SUBCAP = font(FONT, 15)
F_MORE_TITLE = font(FONTB, 17)
F_MORE_B = font(FONTB, 13)
F_MORE = font(FONT, 13)
F_WIRE = font(FONT, 13)
F_WIRE_B = font(FONTB, 13)
F_FOOT = font(FONT, 12)
F_FOOT_B = font(FONTB, 12)


# ---------------------------------------------------------------- wrapping
def wrap(text, fnt, max_w):
    """Greedy word wrap; returns list of lines, each fitting max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    for line in lines:
        assert fnt.getlength(line) <= max_w, "overflow: %r" % line
    return lines


def wrap_mixed(segments, max_w):
    """Wrap [(word, font), ...] lines; a line may mix bold lead + regular.

    segments: list of (word, font) tuples in reading order.
    Returns list of lines, each a list of (word, font) tuples.
    """
    lines, cur, cur_w = [], [], 0.0
    for word, fnt in segments:
        w = fnt.getlength(word)
        space = fnt.getlength(" ") if cur else 0.0
        if cur and cur_w + space + w > max_w:
            lines.append(cur)
            cur, cur_w = [(word, fnt)], w
        else:
            if cur:
                cur_w += space
            cur.append((word, fnt))
            cur_w += w
    if cur:
        lines.append(cur)
    for line in lines:
        total = sum(f.getlength(w) for w, f in line)
        total += sum(f.getlength(" ") for (_, f) in line[1:])
        assert total <= max_w + 0.5, "mixed overflow: %r" % (line,)
    return lines


def draw_mixed(draw, x, y, line):
    cx = x
    for i, (word, fnt) in enumerate(line):
        if i:
            cx += fnt.getlength(" ")
        draw.text((cx, y), word, font=fnt, fill=INK)
        cx += fnt.getlength(word)
    return cx


def text_w(fnt, s):
    return fnt.getlength(s)


# ---------------------------------------------------------------- content
PANELS = [
    {
        "kicker": "MIDDLE EAST",
        "color": RED,
        "headline": "HOUTHIS STRIKE SAUDI OIL REFINERY",
        "sub": (
            "Houthis say they hit the Ras Tanura refinery and Riyadh's "
            "financial district. The coalition says it downed four drones; "
            "11 were hurt in a tower strike on Tuesday."
        ),
        "icon": "refinery",
    },
    {
        "kicker": "SPACE",
        "color": BLUE,
        "headline": "CHINA FLIES FIRST FOREIGN ASTRONAUT",
        "sub": (
            "Shenzhou-24 lifts off for the Tiangong station carrying "
            "Pakistan's Muhammad Zeeshan Ali - the first foreign astronaut "
            "aboard China's space station."
        ),
        "icon": "rocket",
    },
    {
        "kicker": "TECH / LAW",
        "color": PURPLE,
        "headline": "US JURY CONVICTS HUAWEI",
        "sub": (
            "Guilty on 10 of 12 counts - trade-secret theft, bank fraud and "
            "Iran sanctions breaches. Acquitted of racketeering; sentencing "
            "set for September 2027."
        ),
        "icon": "chip",
    },
    {
        "kicker": "LABOUR",
        "color": GREEN,
        "headline": "BANGLADESH RAISES GARMENT PAY 36%",
        "sub": (
            "Minimum wage rises to 17,000 taka ($139) after weeks of "
            "protests shut factories. Workers still demand 30,000 taka "
            "and kept protesting."
        ),
        "icon": "factory",
    },
]

# (bold lead, rest of line) -- each must wrap to <= 2 lines at 13px.
MORE = [
    ("COLOMBIA -", "All hostages freed as forces storm a Cartagena supermarket; one captor killed after a day-long siege."),
    ("PACIFIC -", "Solomon Islands signs an Australia treaty as top security partner, ending its 2022 China pact."),
    ("CHINA -", "Politburo member Chen Jining, Shanghai party chief, probed for graft; fourth purge since 2025."),
    ("N. KOREA -", "Pyongyang orders the Swiss office shut and expels its diplomat within 48 hours."),
    ("BRITAIN -", "UK warns firms backing Ukraine to brace for Russian sabotage, MI5 says."),
    ("INDONESIA -", "Flooded Bogor gold mine: 3 bodies found, 23 miners still trapped 100m down."),
    ("AUSTRALIA -", "Digital Duty of Care passes; Big Tech faces fines up to 5% of global revenue."),
    ("TARIFFS -", "Trump administration set to unveil new duties on China, the EU and others over excess capacity."),
    ("MARKETS -", "Asian stocks slide as the AI rally stumbles; Nvidia falls 5.9% and Seoul drops 5.3%."),
    ("UKRAINE -", "Leaked Russian data put war dead near 500,000, BBC Russian reports."),
    ("UKRAINE -", "Kyiv says it needs \u20ac115bn in outside financing for 2027, Zelensky says."),
    ("SPAIN -", "Record 2,100+ migrants reach the Canary Islands in a single day, rescue data show."),
    ("SPAIN -", "Catalan leader Puigdemont to return on Dec 12, ending nine years in exile."),
    ("EUROPE -", "EU postpones talks on approving Tesla self-driving tech to Dec 15."),
    ("USA -", "Six dead, incl. two boys, as a Cessna crashes into the Gulf off the Mississippi coast."),
    ("USA -", "Abrego Garcia leaves the US for Spain, ending his deportation fight."),
    ("FRANCE -", "Ex-president Sarkozy and wife Carla Bruni to face trial, court rules."),
    ("S. AFRICA -", "Ramaphosa wins a court battle over an impeachment threat."),
    ("USA -", "East Coast storm looms for Thanksgiving; Macy's parade marks a milestone."),
]

WIRE = [
    ("01:31", "China opens a graft probe into Politburo member Chen Jining, Shanghai party chief."),
    ("04:50", "North Korea orders Switzerland's Pyongyang office shut; diplomat given 48 hours."),
    ("06:01", "Bangladesh raises the garment minimum wage 36% to 17,000 taka after weeks of protests."),
    ("07:02", "Colombia frees all hostages in the Cartagena supermarket siege; one captor killed."),
]

FOOTER = (
    "Sources: Reuters, AP, BBC, AFP, CNN, The Hindu Business Line, TBS News. "
    "Every story first reported or confirmed on 25 November 2026 (UTC)."
)
CREDIT = "make.fun news-image-20261125  |  Built with Python + PIL  |  No external images  |  Entry: machero007"


# ---------------------------------------------------------------- pictograms
def draw_icon(draw, kind, x0, y0, s):
    """Draw a simple pictogram inside the s x s box at (x0, y0)."""
    if kind == "refinery":
        draw.rectangle([x0, y0, x0 + s, y0 + s], fill=SKY, outline=RULE)
        # ground
        draw.rectangle([x0, y0 + s * 0.72, x0 + s, y0 + s], fill=(120, 118, 110))
        # towers
        draw.rectangle([x0 + s * 0.14, y0 + s * 0.30, x0 + s * 0.30, y0 + s * 0.72],
                       fill=INK)
        draw.rectangle([x0 + s * 0.38, y0 + s * 0.45, x0 + s * 0.58, y0 + s * 0.72],
                       fill=INK)
        draw.rectangle([x0 + s * 0.64, y0 + s * 0.22, x0 + s * 0.80, y0 + s * 0.72],
                       fill=INK)
        # flame on tallest tower
        fx, fy = x0 + s * 0.72, y0 + s * 0.20
        draw.polygon([(fx - 9, fy + 8), (fx, fy - 12), (fx + 9, fy + 8)],
                     fill=ORANGE)
        draw.ellipse([fx - 5, fy - 2, fx + 5, fy + 8], fill=GOLD)
        # sun
        draw.ellipse([x0 + s * 0.06, y0 + s * 0.06, x0 + s * 0.20, y0 + s * 0.20],
                     fill=GOLD)
    elif kind == "rocket":
        draw.rectangle([x0, y0, x0 + s, y0 + s], fill=NAVY, outline=RULE)
        # stars
        for sx, sy in [(0.12, 0.18), (0.85, 0.14), (0.80, 0.55), (0.16, 0.62),
                       (0.55, 0.10)]:
            draw.ellipse([x0 + s * sx - 2, y0 + s * sy - 2,
                          x0 + s * sx + 2, y0 + s * sy + 2], fill="white")
        cx = x0 + s * 0.5
        # flame
        draw.polygon([(cx - 10, y0 + s * 0.72), (cx, y0 + s * 0.92),
                      (cx + 10, y0 + s * 0.72)], fill=ORANGE)
        # body
        draw.rectangle([cx - 14, y0 + s * 0.28, cx + 14, y0 + s * 0.74],
                       fill="white", outline=INK)
        draw.polygon([(cx - 14, y0 + s * 0.28), (cx, y0 + s * 0.10),
                      (cx + 14, y0 + s * 0.28)], fill=RED)
        draw.ellipse([cx - 6, y0 + s * 0.42, cx + 6, y0 + s * 0.54],
                     fill=SKY, outline=INK)
        draw.polygon([(cx - 14, y0 + s * 0.60), (cx - 26, y0 + s * 0.76),
                      (cx - 14, y0 + s * 0.74)], fill=RED)
        draw.polygon([(cx + 14, y0 + s * 0.60), (cx + 26, y0 + s * 0.76),
                      (cx + 14, y0 + s * 0.74)], fill=RED)
    elif kind == "chip":
        draw.rectangle([x0, y0, x0 + s, y0 + s], fill=SKY, outline=RULE)
        # pins
        for i in range(4):
            yy = y0 + s * (0.24 + i * 0.17)
            draw.rectangle([x0 + s * 0.06, yy, x0 + s * 0.20, yy + 5], fill=INK)
            draw.rectangle([x0 + s * 0.80, yy, x0 + s * 0.94, yy + 5], fill=INK)
        # chip body
        draw.rectangle([x0 + s * 0.22, y0 + s * 0.22, x0 + s * 0.78, y0 + s * 0.78],
                       fill=INK)
        draw.rectangle([x0 + s * 0.36, y0 + s * 0.36, x0 + s * 0.64, y0 + s * 0.64],
                       fill=GOLD_LT, outline=GOLD)
        draw.text((x0 + s * 0.50, y0 + s * 0.50), "10/12",
                  font=font(FONTB, 10), fill=INK, anchor="mm")
    elif kind == "factory":
        draw.rectangle([x0, y0, x0 + s, y0 + s], fill=SKY, outline=RULE)
        # sun
        draw.ellipse([x0 + s * 0.68, y0 + s * 0.08, x0 + s * 0.84, y0 + s * 0.24],
                     fill=GOLD)
        # chimney
        draw.rectangle([x0 + s * 0.14, y0 + s * 0.22, x0 + s * 0.26, y0 + s * 0.72],
                       fill=INK)
        draw.ellipse([x0 + s * 0.16, y0 + s * 0.12, x0 + s * 0.24, y0 + s * 0.20],
                     fill=MUTED)
        # factory body with sawtooth roof
        draw.polygon([(x0 + s * 0.30, y0 + s * 0.72), (x0 + s * 0.30, y0 + s * 0.52),
                      (x0 + s * 0.48, y0 + s * 0.40), (x0 + s * 0.48, y0 + s * 0.52),
                      (x0 + s * 0.66, y0 + s * 0.40), (x0 + s * 0.66, y0 + s * 0.52),
                      (x0 + s * 0.88, y0 + s * 0.40), (x0 + s * 0.88, y0 + s * 0.72)],
                     fill=INK)
        # windows
        for wx in (0.36, 0.54, 0.72):
            draw.rectangle([x0 + s * wx, y0 + s * 0.58, x0 + s * (wx + 0.08),
                            y0 + s * 0.68], fill=GOLD_LT)
        # ground
        draw.rectangle([x0, y0 + s * 0.72, x0 + s, y0 + s], fill=(120, 118, 110))


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- header band
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.rectangle([0, 118, W, 122], fill=GOLD)
    title = "25 NOVEMBER 2026"
    assert text_w(F_TITLE, title) <= 992
    d.text((16, 8), title, font=F_TITLE, fill="white")
    d.text((16, 62), "THE WORLD IN ONE IMAGE", font=F_SUB, fill=GOLD_LT)
    date_line = "DATE CHECK: Wednesday, 25 November 2026  |  23 stories  |  All times UTC"
    assert text_w(F_DATE, date_line) <= 992
    d.text((16, 92), date_line, font=F_DATE, fill="white")

    # ---- 4 panels, 2 x 2
    pw, ph, gap = 488, 196, 8
    xs = [16, 16 + pw + gap]
    ys = [126, 126 + ph + gap]
    for idx, panel in enumerate(PANELS):
        x = xs[idx % 2]
        y = ys[idx // 2]
        d.rectangle([x, y, x + pw, y + ph], fill=PANEL_BG, outline=RULE, width=2)
        d.rectangle([x, y, x + pw, y + 4], fill=panel["color"])
        # kicker
        d.text((x + 12, y + 12), panel["kicker"], font=F_KICK,
               fill=panel["color"])
        # headline, max 2 lines across full panel width
        head_lines = wrap(panel["headline"], F_HEAD, pw - 24)
        assert len(head_lines) <= 2, panel["headline"]
        hy = y + 32
        for line in head_lines:
            d.text((x + 12, hy), line, font=F_HEAD, fill=INK)
            hy += 24
        # pictogram left, sub-caption right
        icon_s = 92
        iy = y + 88
        draw_icon(d, panel["icon"], x + 12, iy, icon_s)
        sub_w = pw - 12 - icon_s - 12 - 12
        sub_lines = wrap(panel["sub"], F_SUBCAP, sub_w)
        assert len(sub_lines) <= 4, panel["sub"]
        sy = iy + 2
        for line in sub_lines:
            d.text((x + 12 + icon_s + 12, sy), line, font=F_SUBCAP, fill=INK)
            sy += 19

    # ---- "More from 25 Nov" section
    my = 534
    d.rectangle([16, my, W - 16, my + 26], fill=NAVY2)
    d.text((28, my + 4), "MORE FROM 25 NOVEMBER", font=F_MORE_TITLE, fill="white")
    d.text((W - 16 - text_w(F_MORE_TITLE, "19 MORE STORIES") - 12, my + 4),
           "19 MORE STORIES", font=F_MORE_TITLE, fill=GOLD_LT)

    col_w = 488
    col_xs = [16, 16 + col_w + 8]
    # split 19 items: 10 left, 9 right
    cols = [MORE[:10], MORE[10:]]
    row_h = 33
    iy0 = my + 32
    for ci, col in enumerate(cols):
        cx = col_xs[ci]
        for ri, (lead, rest) in enumerate(col):
            yy = iy0 + ri * row_h
            segs = [(w, F_MORE_B) for w in lead.split(" ")]
            segs += [(w, F_MORE) for w in rest.split(" ")]
            lines = wrap_mixed(segs, col_w - 12)
            assert len(lines) <= 2, (lead, rest)
            ly = yy
            for line in lines:
                draw_mixed(d, cx + 6, ly, line)
                ly += 16
            if ri < len(col) - 1:
                d.line([cx + 6, yy + 30, cx + col_w - 6, yy + 30], fill=RULE)

    # ---- UTC wire strip
    wy = 902
    d.rectangle([16, wy, W - 16, wy + 58], fill=NAVY)
    wx = 28
    for t, text in WIRE:
        line = t + " UTC  -  " + text
        assert text_w(F_WIRE, line) <= W - 16 - wx - 12, line
        d.text((wx, wy + 2 + WIRE.index((t, text)) * 14), line,
               font=F_WIRE, fill="white")

    # ---- footer
    fy = 968
    foot_lines = wrap(FOOTER, F_FOOT, W - 32)
    assert len(foot_lines) <= 2, FOOTER
    for line in foot_lines:
        d.text((16, fy), line, font=F_FOOT, fill=MUTED)
        fy += 15
    assert text_w(F_FOOT_B, CREDIT) <= W - 32
    d.text((16, fy + 2), CREDIT, font=F_FOOT_B, fill=INK)

    img.save(OUT, format="PNG", optimize=True)
    return OUT


if __name__ == "__main__":
    path = build()
    print("wrote", path)
