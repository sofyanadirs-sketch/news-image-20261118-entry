#!/usr/bin/env python3
"""make.fun news-image-20261118 entry: draws one newspaper front page that
sums up Wednesday 18 November 2026 in a single image.

Six stories, chosen for breadth across regions and fields, each with a
hand-drawn icon, a headline and a short summary:

  1. MIDDLE EAST (lead) - US and Iran trade fire: Iranian drones target a
     US radar in Bahrain; US jets answer by striking a missile site on
     Qeshm Island in the Strait of Hormuz.
  2. EUROPE - Ukraine wrecks the Kerch (Crimean) Bridge; Russia hits
     Kyiv's bridges and infrastructure in reply.
  3. ASIA - Trump in Manila for the first Quad summit in two years,
     ahead of APEC in Shenzhen and talks with Xi and Putin.
  4. TECH - Baidu's chief warns the AI bubble could become real if heavy
     AI spending never turns into profit.
  5. WEATHER - Cyclone Akvan bears down on the Bay of Bengal and may
     turn severe by Thursday.
  6. SPORT - MS Dhoni ends his IPL playing career and becomes Chennai
     Super Kings' mentor for 2027.

Layout (new for this day, unlike the 13 Nov entry's plain 2x3 grid): a
crimson masthead, one full-width lead story with a wide drawn scene, two
rows of two panels with a coloured spine, and a full-width sport strip.

Every pixel is drawn by this program at run time: no photos, no downloaded
images, no network, no clock, no randomness. Pure standard library, so it
runs exactly the same in the grader's Python 3.13 sandbox. It writes one
1024x1024 PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
Deterministic: two runs write byte-identical files.
"""

import math
import os
import struct
import zlib
from pathlib import Path

# Logical canvas, upscaled 4x with nearest neighbour (chunky pixel look that
# stays legible when the image is shown small).
W = 256
H = 256
SCALE = 4
OUT_W = W * SCALE
OUT_H = H * SCALE

# --- palette ---------------------------------------------------------------
PAPER = (247, 243, 234)
CRIMSON = (150, 30, 40)
CREAM = (250, 240, 210)
GOLD = (255, 209, 102)
RED = (192, 57, 43)
INK = (30, 30, 34)
BODY = (70, 70, 78)
BORDER = (120, 120, 125)
WHITE = (255, 255, 255)
PANEL_BG = (255, 255, 255)

CAT_MIDEAST = (150, 30, 40)
CAT_EUROPE = (43, 76, 155)
CAT_ASIA = (15, 118, 110)
CAT_TECH = (90, 60, 140)
CAT_WEATHER = (30, 90, 160)
CAT_SPORT = (180, 140, 0)

SKY = (150, 200, 235)
SKY_LIGHT = (190, 220, 240)
SEA_DARK = (40, 90, 140)
SEA_LIGHT = (168, 208, 235)
UKR_BLUE = (0, 87, 183)
UKR_YELLOW = (255, 213, 0)
DARK_GRAY = (70, 72, 78)
BAR_GRAY = (140, 140, 145)
ORANGE = (235, 120, 30)
FLAME = (255, 176, 32)
GREEN = (60, 140, 60)
CSK_YELLOW = (255, 215, 0)
BROWN = (120, 80, 40)

# --- 5x7 pixel font (uppercase, digits, a little punctuation) --------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines = []
    for word in text.split(" "):
        if not lines or len(lines[-1]) + 1 + len(word) > max_chars:
            lines.append(word)
        else:
            lines[-1] += " " + word
    return lines


# --- canvas ----------------------------------------------------------------
class Canvas:
    def __init__(self):
        self.px = bytearray(W * H * 3)

    def set(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(H, y1 + 1)):
            for x in range(max(0, x0), min(W, x1 + 1)):
                self.set(x, y, color)

    def rect_outline(self, x0, y0, x1, y1, color):
        self.fill_rect(x0, y0, x1, y0, color)
        self.fill_rect(x0, y1, x1, y1, color)
        self.fill_rect(x0, y0, x0, y1, color)
        self.fill_rect(x1, y0, x1, y1, color)

    def circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    self.set(x, y, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / steps
            x = round(x0 + (x1 - x0) * t)
            y = round(y0 + (y1 - y0) * t)
            self.circle(x, y, max(0, width // 2), color)

    def arc(self, cx, cy, r, a0, a1, color, thick=2):
        """Arc of a circle; angles in degrees, y-down screen coords."""
        for y in range(cy - r - thick, cy + r + thick + 1):
            for x in range(cx - r - thick, cx + r + thick + 1):
                dx, dy = x - cx, y - cy
                d = math.hypot(dx, dy)
                if abs(d - r) > thick / 2 + 0.6:
                    continue
                ang = math.degrees(math.atan2(dy, dx))
                if a0 <= ang <= a1:
                    self.set(x, y, color)

    def triangle(self, p0, p1, p2, color):
        xs = [p0[0], p1[0], p2[0]]
        ys = [p0[1], p1[1], p2[1]]

        def sign(ax, ay, bx, by, cx, cy):
            return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)

        for y in range(min(ys), max(ys) + 1):
            for x in range(min(xs), max(xs) + 1):
                d0 = sign(x, y, p0[0], p0[1], p1[0], p1[1])
                d1 = sign(x, y, p1[0], p1[1], p2[0], p2[1])
                d2 = sign(x, y, p2[0], p2[1], p0[0], p0[1])
                if (d0 >= 0 and d1 >= 0 and d2 >= 0) or (
                    d0 <= 0 and d1 <= 0 and d2 <= 0
                ):
                    self.set(x, y, color)

    def rounded_rect(self, x0, y0, x1, y1, r, color):
        self.fill_rect(x0 + r, y0, x1 - r, y1, color)
        self.fill_rect(x0, y0 + r, x1, y1 - r, color)
        self.circle(x0 + r, y0 + r, r, color)
        self.circle(x1 - r, y0 + r, r, color)
        self.circle(x0 + r, y1 - r, r, color)
        self.circle(x1 - r, y1 - r, r, color)

    def text(self, text, x, y, scale, color):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "1":
                        self.fill_rect(
                            cx + col * scale,
                            y + row * scale,
                            cx + col * scale + scale - 1,
                            y + row * scale + scale - 1,
                            color,
                        )
            cx += 6 * scale

    def text_bold(self, text, x, y, scale, color):
        self.text(text, x, y, scale, color)
        self.text(text, x + 1, y, scale, color)


# --- PNG encoding (stdlib only) --------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    # Upscale 4x nearest neighbour, filter byte 0 per row.
    raw = bytearray()
    for ly in range(H):
        row = bytearray()
        for lx in range(W):
            i = (ly * W + lx) * 3
            px = canvas.px[i : i + 3]
            row += px * SCALE
        raw.append(0)
        raw += row
        for _ in range(SCALE - 1):
            raw.append(0)
            raw += row
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", OUT_W, OUT_H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png

# --- story icons -------------------------------------------------------------
def icon_lead(c, ix, iy):
    """Wide scene (94x50): a radar dish in Bahrain, a drone overhead, and a
    blast over Qeshm Island across the strait. US and Iran trade fire."""
    c.fill_rect(ix, iy, ix + 93, iy + 29, SKY)
    c.fill_rect(ix, iy + 30, ix + 93, iy + 49, SEA_DARK)
    c.line(ix, iy + 35, ix + 93, iy + 35, WHITE, width=1)
    c.line(ix, iy + 42, ix + 93, iy + 42, WHITE, width=1)
    # Radar dish on a mast, left (Bahrain): a small wedge dish.
    c.fill_rect(ix + 9, iy + 24, ix + 11, iy + 30, DARK_GRAY)
    c.triangle((ix + 10, iy + 24), (ix + 4, iy + 15), (ix + 16, iy + 15),
               DARK_GRAY)
    c.line(ix + 10, iy + 24, ix + 10, iy + 14, (200, 200, 200), width=1)
    # Drone in the sky, centre.
    c.fill_rect(ix + 44, iy + 9, ix + 52, iy + 11, DARK_GRAY)
    c.fill_rect(ix + 40, iy + 8, ix + 44, iy + 9, DARK_GRAY)
    c.fill_rect(ix + 52, iy + 8, ix + 56, iy + 9, DARK_GRAY)
    c.fill_rect(ix + 47, iy + 12, ix + 49, iy + 14, DARK_GRAY)
    # Blast starburst over the island, right (Qeshm).
    c.ellipse(ix + 76, iy + 40, 12, 5, (60, 140, 60))
    c.circle(ix + 76, iy + 22, 5, FLAME)
    for k in range(8):
        ang = math.radians(k * 45)
        c.line(
            round(ix + 76 + math.cos(ang) * 6),
            round(iy + 22 + math.sin(ang) * 6),
            round(ix + 76 + math.cos(ang) * 11),
            round(iy + 22 + math.sin(ang) * 11),
            ORANGE,
            width=1,
        )
    # Smoke puffs.
    c.circle(ix + 70, iy + 14, 2, (200, 200, 200))
    c.circle(ix + 82, iy + 12, 2, (200, 200, 200))


def icon_bridge(c, ix, iy):
    """Broken bridge (22x22): two deck ends, a gap, a span falling into
    the strait. Ukraine wrecks the Kerch Bridge."""
    c.fill_rect(ix, iy, ix + 21, iy + 12, SKY_LIGHT)
    c.fill_rect(ix, iy + 13, ix + 21, iy + 21, SEA_LIGHT)
    # Left and right deck ends with pylons.
    c.fill_rect(ix + 1, iy + 9, ix + 7, iy + 11, BAR_GRAY)
    c.fill_rect(ix + 14, iy + 9, ix + 20, iy + 11, BAR_GRAY)
    c.fill_rect(ix + 3, iy + 3, ix + 4, iy + 9, DARK_GRAY)
    c.fill_rect(ix + 17, iy + 3, ix + 18, iy + 9, DARK_GRAY)
    # Falling span, tilted, mid-air over the gap.
    c.line(ix + 8, iy + 10, ix + 13, iy + 15, BAR_GRAY, width=2)
    # Splash where the span will land.
    c.line(ix + 9, iy + 18, ix + 13, iy + 18, WHITE, width=1)
    c.line(ix + 10, iy + 20, ix + 12, iy + 20, WHITE, width=1)
    # Blue over yellow hint (Ukraine).
    c.fill_rect(ix, iy + 21, ix + 21, iy + 21, UKR_YELLOW)


def icon_quad(c, ix, iy):
    """Four flags in a 2x2 grid (22x22): US, Japan, India, Australia.
    The Quad meets in Manila for the first time in two years."""
    # US: red-white stripes, blue corner.
    for s in range(4):
        c.fill_rect(ix + 1, iy + 1 + s * 2, ix + 9, iy + 1 + s * 2,
                    RED if s % 2 == 0 else WHITE)
    c.fill_rect(ix + 1, iy + 1, ix + 4, iy + 4, (40, 60, 140))
    # Japan: white field, red disc.
    c.fill_rect(ix + 12, iy + 1, ix + 20, iy + 9, WHITE)
    c.circle(ix + 16, iy + 5, 2, RED)
    # India: saffron, white, green bands.
    c.fill_rect(ix + 1, iy + 12, ix + 9, iy + 14, (255, 153, 51))
    c.fill_rect(ix + 1, iy + 15, ix + 9, iy + 17, WHITE)
    c.fill_rect(ix + 1, iy + 18, ix + 9, iy + 20, (19, 136, 8))
    # Australia: blue field, stars.
    c.fill_rect(ix + 12, iy + 12, ix + 20, iy + 20, (0, 40, 120))
    c.set(ix + 13, iy + 13, WHITE)
    c.set(ix + 19, iy + 13, WHITE)
    c.set(ix + 16, iy + 17, WHITE)
    c.set(ix + 14, iy + 19, WHITE)
    c.set(ix + 18, iy + 19, WHITE)


def icon_bubble(c, ix, iy):
    """An AI bubble about to burst (22x22): a big circle with AI inside,
    a pin from the top right, a falling arrow."""
    c.fill_rect(ix, iy, ix + 21, iy + 21, (238, 238, 232))
    # Bubble.
    c.arc(ix + 10, iy + 11, 8, 0, 359, (90, 60, 140), thick=2)
    c.text("AI", ix + 6, iy + 8, 1, (90, 60, 140))
    # Pin needle from top right.
    c.line(ix + 21, iy, ix + 16, iy + 5, DARK_GRAY, width=1)
    c.triangle((ix + 15, iy + 4), (ix + 18, iy + 7), (ix + 16, iy + 7),
               DARK_GRAY)
    # Falling arrow, bottom right.
    c.line(ix + 17, iy + 15, ix + 17, iy + 19, RED, width=2)
    c.triangle((ix + 15, iy + 18), (ix + 19, iy + 18), (ix + 17, iy + 21),
               RED)


def icon_cyclone(c, ix, iy):
    """Cyclone spiral (22x22): concentric arcs over a coastline, rain."""
    c.fill_rect(ix, iy, ix + 21, iy + 21, SKY_LIGHT)
    # Spiral: three arcs of growing radius, staggered so they read as a
    # rotating storm (arc angles are atan2 degrees, -180..180).
    c.arc(ix + 11, iy + 10, 3, -90, 150, SEA_DARK, thick=2)
    c.arc(ix + 11, iy + 10, 6, -180, 60, (90, 140, 190), thick=2)
    c.arc(ix + 11, iy + 10, 9, -60, 180, (140, 180, 220), thick=2)
    c.circle(ix + 11, iy + 10, 1, SEA_DARK)
    # Coastline at the bottom.
    c.fill_rect(ix, iy + 18, ix + 21, iy + 21, (220, 200, 150))
    # Rain drops.
    c.line(ix + 3, iy + 15, ix + 3, iy + 17, SEA_DARK, width=1)
    c.line(ix + 19, iy + 14, ix + 19, iy + 16, SEA_DARK, width=1)


def icon_cricket(c, ix, iy):
    """Cricket (22x22): a bat, a red ball and three stumps on CSK yellow.
    Dhoni ends his IPL playing career."""
    c.fill_rect(ix, iy, ix + 21, iy + 21, CSK_YELLOW)
    # Bat, angled.
    c.line(ix + 5, iy + 4, ix + 12, iy + 16, BROWN, width=3)
    c.line(ix + 3, iy + 2, ix + 5, iy + 5, BROWN, width=2)
    # Ball.
    c.circle(ix + 17, iy + 6, 3, RED)
    # Three stumps.
    c.fill_rect(ix + 15, iy + 13, ix + 15, iy + 20, WHITE)
    c.fill_rect(ix + 18, iy + 13, ix + 18, iy + 20, WHITE)
    c.fill_rect(ix + 21, iy + 13, ix + 21, iy + 20, WHITE)
    c.fill_rect(ix + 15, iy + 12, ix + 21, iy + 12, WHITE)


ICONS = {
    "bridge": icon_bridge,
    "quad": icon_quad,
    "bubble": icon_bubble,
    "cyclone": icon_cyclone,
    "cricket": icon_cricket,
}

# --- stories ----------------------------------------------------------------
# (category tag, tag colour, headline, body, icon key)
STORIES = [
    (
        "EUROPE",
        CAT_EUROPE,
        "BRIDGE WAR",
        "UKRAINE WRECKS KERCH BRIDGE. RUSSIA HITS KYIV.",
        "bridge",
    ),
    (
        "ASIA",
        CAT_ASIA,
        "QUAD MEETS",
        "TRUMP IN MANILA FOR FIRST QUAD SUMMIT IN TWO YEARS.",
        "quad",
    ),
    (
        "TECH",
        CAT_TECH,
        "AI BUBBLE?",
        "BAIDU CHIEF: AI MUST PAY OFF OR THE BUBBLE BURSTS.",
        "bubble",
    ),
    (
        "WEATHER",
        CAT_WEATHER,
        "CYCLONE AKVAN",
        "STORM IN BAY OF BENGAL MAY TURN SEVERE BY THURSDAY.",
        "cyclone",
    ),
]

LEAD_BODY = "IRAN DRONES A US RADAR IN BAHRAIN. US JETS HIT QESHM MISSILE SITE."

PANEL_W = 124
PANEL_H = 55
GRID_X = (2, 130)
GRID_Y = (98, 157)


def draw_panel(c, px, py, story):
    tag, color, headline, body, icon_key = story
    c.fill_rect(px, py, px + PANEL_W - 1, py + PANEL_H - 1, PANEL_BG)
    c.rect_outline(px, py, px + PANEL_W - 1, py + PANEL_H - 1, BORDER)
    # Coloured spine on the left edge.
    c.fill_rect(px, py, px + 3, py + PANEL_H - 1, color)
    # Category tag.
    c.text(tag, px + 7, py + 2, 1, color)
    # Icon (22x22) at left, headline beside it.
    ICONS[icon_key](c, px + 7, py + 11)
    c.text_bold(headline, px + 33, py + 18, 1, INK)
    # Body: up to 3 wrapped lines across the full panel width.
    lines = wrap_text(body, 19)
    assert len(lines) <= 3, (headline, lines)
    for i, line in enumerate(lines):
        c.text(line, px + 7, py + 33 + i * 7, 1, BODY)


def draw_lead(c):
    px, py = 2, 36
    pw, ph = 252, 58
    c.fill_rect(px, py, px + pw - 1, py + ph - 1, PANEL_BG)
    c.rect_outline(px, py, px + pw - 1, py + ph - 1, BORDER)
    # Red top rule marks the lead story.
    c.fill_rect(px, py, px + pw - 1, py + 2, CAT_MIDEAST)
    # Wide drawn scene, left.
    icon_lead(c, px + 4, py + 5)
    # Tag, headline, body on the right.
    c.text("MIDDLE EAST - TOP STORY", px + 106, py + 6, 1, CAT_MIDEAST)
    c.text_bold("US AND IRAN TRADE FIRE", px + 106, py + 15, 1, INK)
    lines = wrap_text(LEAD_BODY, 23)
    assert len(lines) <= 3, lines
    for i, line in enumerate(lines):
        c.text(line, px + 106, py + 25 + i * 8, 1, BODY)


def draw_sport_strip(c):
    px, py = 2, 216
    pw, ph = 252, 29
    c.fill_rect(px, py, px + pw - 1, py + ph - 1, PANEL_BG)
    c.rect_outline(px, py, px + pw - 1, py + ph - 1, BORDER)
    c.fill_rect(px, py, px + 3, py + ph - 1, CAT_SPORT)
    icon_cricket(c, px + 7, py + 4)
    c.text_bold("DHONI BOWS OUT", px + 33, py + 3, 1, INK)
    c.text("MS DHONI ENDS IPL CAREER, BECOMES", px + 33, py + 12, 1, BODY)
    c.text("CSK MENTOR FOR 2027.", px + 33, py + 21, 1, BODY)
    c.text("SPORT", px + 216, py + 3, 1, CAT_SPORT)


def draw_masthead(c):
    c.fill_rect(0, 0, W - 1, 31, CRIMSON)
    title = "THE WORLD IN ONE DAY"
    c.text_bold(title, (W - text_width(title, 2)) // 2, 4, 2, CREAM)
    date = "WEDNESDAY, 18 NOVEMBER 2026"
    c.text(date, (W - text_width(date, 1)) // 2, 21, 1, GOLD)
    c.fill_rect(0, 32, W - 1, 33, GOLD)


def build_canvas():
    c = Canvas()
    c.fill_rect(0, 0, W - 1, H - 1, PAPER)
    draw_masthead(c)
    draw_lead(c)
    for i, story in enumerate(STORIES):
        px = GRID_X[i % 2]
        py = GRID_Y[i // 2]
        draw_panel(c, px, py, story)
    draw_sport_strip(c)
    footer = "SOURCES: REUTERS, AP, AFP, IMD, CSK"
    c.text(footer, (W - text_width(footer, 1)) // 2, 249, 1, BODY)
    return c


def main():
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "entry.png").write_bytes(encode_png(build_canvas()))


if __name__ == "__main__":
    main()
