#!/usr/bin/env python3
"""THE WORLD IN ONE DAY -- Wednesday, 18 November 2026.

A one-page newspaper front page that sums up the day's world news in a
single 1024 x 1024 image. Everything is drawn by this program, pixel by
pixel, from rectangles, lines, circles, triangles and a hand-made 5x7
pixel font, then encoded as a PNG with zlib. Pure Python standard
library: no network, no clock, no randomness, no downloaded images, so
two runs write the same bytes.

Run:
    MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes:
    <MAKEFUN_OUTPUT_DIR>/entry.png   (or /output/entry.png)
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# --- palette ---------------------------------------------------------------
PAPER = (246, 242, 229)
INK = (26, 26, 26)
CRIMSON = (140, 17, 32)
GOLD = (198, 158, 38)
GOLD_LIGHT = (232, 196, 92)
SKY = (214, 226, 238)
DUSK_A = (243, 190, 128)
DUSK_B = (226, 148, 104)
SEA = (16, 66, 94)
SEA_LIGHT = (32, 96, 128)
NAVY = (24, 48, 84)
BLUE = (38, 84, 138)
TEAL = (18, 110, 110)
GREEN = (46, 120, 62)
PURPLE = (96, 62, 140)
YELLOW = (250, 204, 0)
ORANGE = (224, 110, 32)
WHITE = (250, 250, 248)
GREY = (120, 118, 110)
GREY_DARK = (74, 72, 66)
SMOKE = (150, 148, 142)
RED = (190, 30, 30)
BROWN = (120, 72, 20)
SKIN = (232, 190, 150)

# --- 5x7 pixel font --------------------------------------------------------
# One glyph per character: seven rows of five cells, "#" on, "." off.
FONT = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.#.#", "#....", ".###."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
}

# --- canvas ----------------------------------------------------------------
buf = bytearray(bytes(PAPER) * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        buf[o] = c[0]
        buf[o + 1] = c[1]
        buf[o + 2] = c[2]


def rect(x, y, w, h, c):
    if w <= 0 or h <= 0:
        return
    x0 = max(x, 0)
    y0 = max(y, 0)
    x1 = min(x + w, W)
    y1 = min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    span = (x1 - x0) * 3
    for yy in range(y0, y1):
        o = (yy * W + x0) * 3
        buf[o:o + span] = row


def hline(x0, x1, y, c):
    if x1 < x0:
        x0, x1 = x1, x0
    rect(x0, y, x1 - x0 + 1, 1, c)


def vline(x, y0, y1, c):
    if y1 < y0:
        y0, y1 = y1, y0
    rect(x, y0, 1, y1 - y0 + 1, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def thick_line(x0, y0, x1, y1, c, t):
    for k in range(-(t // 2), t // 2 + 1):
        line(x0 + k, y0, x1 + k, y1, c)


def disc(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = math.isqrt(max(r * r - dy * dy, 0))
        hline(cx - dx, cx + dx, cy + dy, c)


def ring(cx, cy, r, t, c, bg):
    disc(cx, cy, r, c)
    if r - t > 0:
        disc(cx, cy, r - t, bg)


def circle(cx, cy, r, c):
    x = r
    y = 0
    err = 0
    while x >= y:
        for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                       (x, -y), (y, -x), (-x, -y), (-y, -x)):
            px(cx + sx, cy + sy, c)
        y += 1
        err += 1 + 2 * y
        if 2 * (err - x) + 1 > 0:
            x -= 1
            err += 1 - 2 * x


def arc(cx, cy, r, a0, a1, c, step=4):
    a = a0
    while a <= a1:
        rad = math.radians(a)
        px(cx + int(r * math.cos(rad)), cy + int(r * math.sin(rad)), c)
        a += step


def tri(x0, y0, x1, y1, x2, y2, c):
    pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts

    def edge(xa, ya, xb, yb, y):
        if yb == ya:
            return xa
        return xa + (xb - xa) * (y - ya) / (yb - ya)

    for y in range(ay, cy + 1):
        if y < by:
            xa = edge(ax, ay, bx, by, y)
            xb = edge(ax, ay, cx, cy, y)
        else:
            xa = edge(bx, by, cx, cy, y)
            xb = edge(ax, ay, cx, cy, y)
        hline(int(min(xa, xb)), int(max(xa, xb)), y, c)


def burst(cx, cy, r):
    disc(cx, cy, r, ORANGE)
    disc(cx, cy, r * 2 // 3, YELLOW)
    disc(cx, cy, r // 3, WHITE)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x1 = cx + int((r + 2) * math.cos(rad))
        y1 = cy + int((r + 2) * math.sin(rad))
        x2 = cx + int((r + 10) * math.cos(rad))
        y2 = cy + int((r + 10) * math.sin(rad))
        line(x1, y1, x2, y2, ORANGE)


# --- text ------------------------------------------------------------------
def draw_text(s, x, y, scale, c):
    cx = x
    for ch in s.upper():
        rows = FONT.get(ch, FONT[" "])
        for r in range(7):
            bits = rows[r]
            for col in range(5):
                if bits[col] == "#":
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def text_w(s, scale):
    return max(len(s) * 6 * scale - scale, 0)


def draw_centred(s, cx, y, scale, c):
    draw_text(s, cx - text_w(s, scale) // 2, y, scale, c)


def wrap(s, max_w, scale):
    lines = []
    cur = ""
    for w in s.split(" "):
        trial = (cur + " " + w).strip()
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(s, x, y, max_w, scale, c, gap=4):
    for ln in wrap(s, max_w, scale):
        draw_text(ln, x, y, scale, c)
        y += 7 * scale + gap
    return y


# --- scenes ----------------------------------------------------------------
def scene_lead(sx, sy, sw, sh):
    # Dusk sky in two bands, then the sea.
    rect(sx, sy, sw, 50, DUSK_A)
    rect(sx, sy + 50, sw, 32, DUSK_B)
    rect(sx, sy + 82, sw, sh - 82, SEA)
    # Sun low over the Gulf.
    disc(sx + sw - 130, sy + 36, 22, GOLD_LIGHT)
    disc(sx + sw - 130, sy + 36, 15, YELLOW)
    # Waves.
    for wy, wx0, wx1 in ((sy + 96, sx + 20, sx + 200),
                         (sy + 108, sx + 300, sx + 520),
                         (sy + 122, sx + 60, sx + 320),
                         (sy + 136, sx + 420, sx + 700)):
        hline(wx0, wx1, wy, SEA_LIGHT)
        hline(wx0 + 30, wx1 + 40, wy + 4, SEA_LIGHT)
    # Bahrain shore, left, with a radar dome.
    rect(sx, sy + 128, 190, 22, (52, 52, 44))
    rect(sx + 40, sy + 112, 6, 16, GREY_DARK)
    disc(sx + 43, sy + 108, 9, WHITE)
    # Qeshm Island shore, right, with a missile-site tower.
    rect(sx + 620, sy + 132, sw - 620, 18, (52, 52, 44))
    rect(sx + 700, sy + 116, 8, 16, GREY_DARK)
    rect(sx + 696, sy + 110, 16, 6, GREY_DARK)
    # Warship mid-sea.
    ship_x = sx + 300
    ship_y = sy + 100
    rect(ship_x, ship_y, 150, 14, GREY_DARK)
    tri(ship_x + 150, ship_y, ship_x + 150, ship_y + 14,
        ship_x + 172, ship_y + 14, GREY_DARK)
    rect(ship_x + 30, ship_y - 16, 62, 16, (96, 96, 92))
    vline(ship_x + 60, ship_y - 30, ship_y - 16, GREY_DARK)
    rect(ship_x + 60, ship_y - 34, 16, 5, RED)
    # Jet high left with a contrail.
    jet_x, jet_y = sx + 150, sy + 26
    tri(jet_x, jet_y, jet_x + 34, jet_y + 5, jet_x, jet_y + 10, INK)
    line(jet_x + 8, jet_y + 5, jet_x + 26, jet_y - 6, INK)
    line(jet_x + 8, jet_y + 5, jet_x + 26, jet_y + 16, INK)
    for cx in range(jet_x - 90, jet_x - 6, 14):
        hline(cx, cx + 7, jet_y + 5, WHITE)
    # Drones, three small crosses with dotted trails.
    for dx, dy in ((sx + 430, sy + 34), (sx + 470, sy + 22), (sx + 512, sy + 44)):
        line(dx - 5, dy - 5, dx + 5, dy + 5, INK)
        line(dx - 5, dy + 5, dx + 5, dy - 5, INK)
        for tx in range(dx - 46, dx - 10, 10):
            px(tx, dy, INK)
    # Missile arcs rising from the ship, and their bursts over Qeshm.
    line(ship_x + 120, ship_y - 16, sx + 640, sy + 44, ORANGE)
    line(ship_x + 130, ship_y - 16, sx + 700, sy + 30, ORANGE)
    burst(sx + 640, sy + 44, 16)
    burst(sx + 700, sy + 30, 12)


def scene_bridge(sx, sy, sw, sh):
    rect(sx, sy, sw, sh, SKY)
    rect(sx, sy + 30, sw, sh - 30, SEA)
    # Far bridge on the Kyiv side, small and smoky.
    hline(sx + 8, sx + 90, sy + 20, GREY_DARK)
    vline(sx + 30, sy + 20, sy + 30, GREY_DARK)
    vline(sx + 68, sy + 20, sy + 30, GREY_DARK)
    disc(sx + 50, sy + 10, 6, SMOKE)
    disc(sx + 58, sy + 6, 4, SMOKE)
    # Kerch Bridge deck in two spans with the wrecked gap between them.
    rect(sx + 110, sy + 22, 190, 3, INK)
    rect(sx + 356, sy + 22, 68, 3, INK)
    for px0 in (140, 210, 400):
        vline(sx + px0, sy + 25, sy + 30, INK)
    # The arch span.
    line(sx + 180, sy + 22, sx + 222, sy + 4, BLUE)
    line(sx + 222, sy + 4, sx + 264, sy + 22, BLUE)
    line(sx + 186, sy + 22, sx + 222, sy + 8, BLUE)
    line(sx + 222, sy + 8, sx + 258, sy + 22, BLUE)
    # The wrecked span, tilted down into the strait.
    line(sx + 300, sy + 22, sx + 332, sy + 36, INK)
    line(sx + 332, sy + 36, sx + 356, sy + 40, INK)
    rect(sx + 336, sy + 38, 18, 4, INK)
    disc(sx + 330, sy + 34, 5, WHITE)
    disc(sx + 322, sy + 14, 7, SMOKE)
    disc(sx + 334, sy + 8, 5, SMOKE)
    burst(sx + 318, sy + 20, 7)


def draw_flag(x, y, kind):
    if kind == "us":
        rect(x, y, 18, 11, WHITE)
        for yy in (y, y + 3, y + 6, y + 9):
            rect(x, yy, 18, 2, RED)
        rect(x, y, 8, 6, BLUE)
    elif kind == "jp":
        rect(x, y, 18, 11, WHITE)
        disc(x + 9, y + 5, 3, RED)
    elif kind == "in":
        rect(x, y, 18, 4, (255, 153, 51))
        rect(x, y + 4, 18, 3, WHITE)
        rect(x, y + 7, 18, 4, (19, 136, 8))
        disc(x + 9, y + 5, 1, NAVY)
    elif kind == "au":
        rect(x, y, 18, 11, BLUE)
        for fx, fy in ((3, 2), (14, 3), (5, 8), (13, 8), (9, 5)):
            px(x + fx, y + fy, WHITE)


def scene_quad(sx, sy, sw, sh):
    rect(sx, sy, sw, sh, SKY)
    # Manila skyline.
    for bx, bw, bh in ((0, 40, 14), (48, 26, 22), (82, 34, 12),
                       (300, 30, 18), (338, 44, 26), (390, 26, 14)):
        rect(sx + bx, sy + sh - bh, bw, bh, GREY)
    # Four flags: US, Japan, India, Australia.
    for fx, kind in ((130, "us"), (180, "jp"), (230, "in"), (280, "au")):
        vline(sx + fx, sy + 2, sy + 34, GREY_DARK)
        draw_flag(sx + fx + 2, sy + 2, kind)
    # Four leaders behind the summit table.
    for hx in (140, 185, 230, 275):
        rect(sx + hx - 7, sy + 33, 14, 6, NAVY)
        disc(sx + hx, sy + 28, 5, SKIN)
    rect(sx + 118, sy + 37, 204, 5, BROWN)


def scene_bubble(sx, sy, sw, sh):
    rect(sx, sy, sw, sh, PAPER)
    # Rising bars of AI spending.
    base = sy + sh - 2
    for i, bh in enumerate((10, 18, 26, 34)):
        rect(sx + 20 + i * 30, base - bh, 22, bh, BLUE)
    # The bubble, with AI inside and a crack across it.
    bx, by, br = sx + 200, sy + 20, 16
    ring(bx, by, br, 3, (110, 175, 215), PAPER)
    draw_text("AI", bx - 11, by - 7, 2, BLUE)
    line(bx - 8, by - 12, bx + 2, by - 2, INK)
    line(bx + 2, by - 2, bx + 10, by + 6, INK)
    # A falling red arrow and two coins slipping away.
    line(sx + 300, sy + 8, sx + 300, sy + 30, RED)
    tri(sx + 294, sy + 28, sx + 306, sy + 28, sx + 300, sy + 38, RED)
    disc(sx + 340, sy + 14, 7, GOLD)
    disc(sx + 368, sy + 26, 7, GOLD)


def scene_cyclone(sx, sy, sw, sh):
    rect(sx, sy, sw, sh, (198, 208, 224))
    rect(sx, sy + 34, sw, 10, SEA)
    # Coastline with two houses.
    rect(sx + 300, sy + 28, 144, 6, (90, 140, 90))
    rect(sx + 320, sy + 20, 18, 8, (200, 120, 80))
    rect(sx + 360, sy + 22, 14, 6, (180, 100, 70))
    # The spiral, three arcs turning around a calm eye.
    cx, cy = sx + 130, sy + 20
    for r, a0 in ((6, 0), (11, 90), (16, 180)):
        arc(cx, cy, r, a0, a0 + 260, BLUE)
        arc(cx, cy, r + 1, a0, a0 + 260, BLUE)
    disc(cx, cy, 4, GOLD_LIGHT)
    circle(cx, cy, 5, BLUE)
    # Slanting rain.
    for rx in range(sx + 230, sx + 290, 12):
        line(rx, sy + 4, rx - 5, sy + 18, GREY)
    # Warning triangle.
    tri(sx + 420, sy + 26, sx + 436, sy + 26, sx + 428, sy + 10, YELLOW)
    draw_text("!", sx + 425, sy + 14, 1, INK)


def scene_sport(dx, dy):
    # Dhoni's number 7 badge.
    ring(dx + 22, dy + 44, 20, 3, WHITE, YELLOW)
    draw_text("7", dx + 16, dy + 37, 2, NAVY)
    # Stumps with bails.
    for sx in (dx + 90, dx + 98, dx + 106):
        rect(sx, dy + 26, 5, 40, BROWN)
    rect(dx + 90, dy + 22, 21, 4, BROWN)
    # Bat leaning on the stumps, and the ball.
    thick_line(dx + 130, dy + 66, dx + 158, dy + 18, BROWN, 5)
    disc(dx + 168, dy + 60, 8, RED)
    arc(dx + 168, dy + 60, 5, 20, 160, WHITE)


# --- layout ----------------------------------------------------------------
def masthead():
    rect(0, 0, W, 116, CRIMSON)
    rect(0, 116, W, 4, GOLD)
    draw_text("SIX STORIES", 24, 26, 2, GOLD_LIGHT)
    draw_text("ONE DAY", W - 24 - text_w("ONE DAY", 2), 26, 2, GOLD_LIGHT)
    draw_centred("THE WORLD IN ONE DAY", W // 2, 20, 5, WHITE)
    draw_centred("WEDNESDAY, 18 NOVEMBER 2026", W // 2, 70, 2, GOLD_LIGHT)
    hline(330, 694, 98, GOLD_LIGHT)
    rect(322, 95, 6, 6, GOLD_LIGHT)
    rect(696, 95, 6, 6, GOLD_LIGHT)


def lead_panel(x, y, w, h):
    rect(x, y, w, h, INK)
    rect(x + 2, y + 2, w - 4, h - 4, PAPER)
    rect(x + 2, y + 2, w - 4, 8, CRIMSON)
    draw_text("MIDDLE EAST - LEAD STORY", x + 16, y + 16, 2, CRIMSON)
    draw_text("US AND IRAN TRADE FIRE ACROSS THE GULF", x + 16, y + 38, 3, INK)
    scene_lead(x + 16, y + 66, w - 32, 156)
    para("IRAN FIRED DRONES AT THE US RADAR BASE AT SHEIKH ISA IN "
         "BAHRAIN, ITS THIRD STRIKE IN FIVE DAYS. BAHRAIN SAID ITS "
         "DEFENCES STOPPED THEM. HOURS LATER A US JET HIT A GUARD "
         "MISSILE SITE ON QESHM ISLAND IN THE STRAIT OF HORMUZ.",
         x + 16, y + 234, w - 32, 2, INK)


def story_panel(x, y, w, h, accent, kicker, heads, body, scene):
    rect(x, y, w, h, INK)
    rect(x + 2, y + 2, w - 4, h - 4, PAPER)
    rect(x + 2, y + 2, w - 4, 8, accent)
    draw_text(kicker, x + 16, y + 16, 2, accent)
    hy = y + 36
    for ln in heads:
        draw_text(ln, x + 16, hy, 2, INK)
        hy += 17
    scene(x + 16, y + 70, w - 32, 44)
    para(body, x + 16, y + 120, w - 32, 2, INK, gap=3)


def sport_strip(x, y, w, h):
    rect(x, y, w, h, INK)
    rect(x + 2, y + 2, w - 4, h - 4, YELLOW)
    draw_text("SPORT - DHONI BOWS OUT", x + 16, y + 14, 3, NAVY)
    para("MS DHONI HAS ENDED HIS IPL PLAYING CAREER. CHENNAI SUPER "
         "KINGS SAY HE WILL BE TEAM MENTOR FROM IPL 2027, AFTER "
         "MISSING 2026 WITH A CALF INJURY.",
         x + 16, y + 48, 740, 2, INK, gap=3)
    scene_sport(x + w - 200, y + 8)


# --- PNG -------------------------------------------------------------------
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)


def write_png(path):
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)
        raw += buf[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    masthead()
    lead_panel(24, 132, 976, 304)
    # Gold spine between the two columns, beaded in crimson.
    rect(508, 446, 8, 426, GOLD)
    rect(504, 446, 16, 16, CRIMSON)
    rect(504, 650, 16, 16, CRIMSON)
    rect(504, 856, 16, 16, CRIMSON)
    story_panel(24, 446, 476, 208, BLUE, "EUROPE - BRIDGE WAR",
                ["KERCH BRIDGE WRECKED", "KYIV BRIDGES HIT"],
                "UKRAINE BADLY DAMAGED THE KERCH BRIDGE OVERNIGHT, "
                "DROPPING A ROAD ARCH INTO THE STRAIT. RUSSIA HIT "
                "KYIV'S NORTH AND SOUTH BRIDGES, CUTTING WATER, HEAT "
                "AND METRO.",
                scene_bridge)
    story_panel(524, 446, 476, 208, GREEN, "ASIA - QUAD SUMMIT",
                ["TRUMP IN MANILA FOR QUAD TALKS"],
                "TRUMP ARRIVED IN MANILA FOR THE FIRST QUAD SUMMIT IN "
                "TWO YEARS. HE MEETS MARCOS ON WEDNESDAY, THEN HEADS "
                "TO THE APEC SUMMIT IN SHENZHEN FOR TALKS WITH XI AND "
                "PUTIN.",
                scene_quad)
    story_panel(24, 664, 476, 208, PURPLE, "TECH - AI BUBBLE WARNING",
                ["BAIDU CHIEF WARNS", "AI BUBBLE COULD TURN REAL"],
                "BAIDU CHIEF ROBIN LI WARNED AT THE APEC CEO SUMMIT "
                "THAT HEAVY AI SPENDING MUST TURN INTO PROFIT, OR "
                "FEARS OF AN AI BUBBLE COULD BECOME REAL.",
                scene_bubble)
    story_panel(524, 664, 476, 208, TEAL, "WEATHER - CYCLONE AKVAN",
                ["CYCLONE AKVAN BEARS DOWN", "ON THE BAY OF BENGAL"],
                "CYCLONE AKVAN OVER THE BAY OF BENGAL WAS SET TO "
                "STRENGTHEN INTO A SEVERE STORM BY 19 NOVEMBER, WITH "
                "INDIA'S WEATHER OFFICE WARNINGS IN FORCE.",
                scene_cyclone)
    sport_strip(24, 882, 976, 118)
    draw_centred("DRAWN FROM REPORTS OF 18 NOVEMBER 2026 - SIX STORIES, "
                 "ONE DAY", W // 2, 1006, 1, GREY_DARK)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out, exist_ok=True)
    write_png(os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
