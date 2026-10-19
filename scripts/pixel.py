#!/usr/bin/env python3
"""Generates the pixel-art SVGs used in README.md.

    python3 scripts/pixel.py

Everything is drawn on a grid of art pixels; each art pixel is PX screen pixels.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
PX = 4
W = 240

INK = "#e6edf3"
MUTED = "#6e76b8"
LINE = "#2e3466"
CARD = "#0f1229"
GREEN = "#3fb950"
YELLOW = "#e3b341"
RUST = "#f74c00"
TS = "#4d94e8"

FONT = {k: v.split() for k, v in {
    "A": ".###. #...# #...# ##### #...# #...# #...#",
    "B": "####. #...# #...# ####. #...# #...# ####.",
    "C": ".###. #...# #.... #.... #.... #...# .###.",
    "D": "####. #...# #...# #...# #...# #...# ####.",
    "E": "##### #.... #.... ####. #.... #.... #####",
    "F": "##### #.... #.... ####. #.... #.... #....",
    "G": ".###. #...# #.... #.### #...# #...# .####",
    "H": "#...# #...# #...# ##### #...# #...# #...#",
    "I": "### .#. .#. .#. .#. .#. ###",
    "J": "..### ...#. ...#. ...#. ...#. #..#. .##..",
    "K": "#...# #..#. #.#.. ##... #.#.. #..#. #...#",
    "L": "#.... #.... #.... #.... #.... #.... #####",
    "M": "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    "N": "#...# #...# ##..# #.#.# #..## #...# #...#",
    "O": ".###. #...# #...# #...# #...# #...# .###.",
    "P": "####. #...# #...# ####. #.... #.... #....",
    "Q": ".###. #...# #...# #...# #.#.# #..#. .##.#",
    "R": "####. #...# #...# ####. #.#.. #..#. #...#",
    "S": ".#### #.... #.... .###. ....# ....# ####.",
    "T": "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..",
    "U": "#...# #...# #...# #...# #...# #...# .###.",
    "V": "#...# #...# #...# #...# #...# .#.#. ..#..",
    "W": "#...# #...# #...# #.#.# #.#.# #.#.# .#.#.",
    "X": "#...# #...# .#.#. ..#.. .#.#. #...# #...#",
    "Y": "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..",
    "Z": "##### ....# ...#. ..#.. .#... #.... #####",
    "1": ".#. ##. .#. .#. .#. .#. ###",
    "0": ".###. #...# #..## #.#.# ##..# #...# .###.",
    "2": ".###. #...# ....# ...#. ..#.. .#... #####",
    "3": "####. ....# ....# .###. ....# ....# ####.",
    "4": "...#. ..##. .#.#. #..#. ##### ...#. ...#.",
    "5": "##### #.... ####. ....# ....# #...# .###.",
    "6": "..##. .#... #.... ####. #...# #...# .###.",
    "7": "##### ....# ...#. ..#.. .#... .#... .#...",
    "8": ".###. #...# #...# .###. #...# #...# .###.",
    "9": ".###. #...# #...# .#### ....# ...#. .##..",
    "=": "..... ..... ##### ..... ##### ..... .....",
    "²": "##. ..# .#. #.. ### ... ...",
    "∑": "##### #.... .#... ..#.. .#... #.... #####",
    "π": "..... ##### .#.#. .#.#. .#.#. .#.#. .#.#.",
    "(": ".# #. #. #. #. #. .#",
    ")": "#. .# .# .# .# .# #.",
    "{": ".## .#. .#. #.. .#. .#. .##",
    "}": "##. .#. .#. ..# .#. .#. ##.",
    ";": ".. .. ## .. ## .# #.",
    ".": ".. .. .. .. .. ## ##",
    "?": ".###. #...# ....# ...#. ..#.. ..... ..#..",
    "$": "..#.. .#### #.#.. .###. ..#.# ####. ..#..",
    "+": "..... ..#.. ..#.. ##### ..#.. ..#.. .....",
    "-": "... ... ... ### ... ... ...",
    "/": "....# ....# ...#. ..#.. .#... #.... #....",
    "&": ".##.. #..#. #.#.. .#... #.#.# #..#. .##.#",
    "!": "# # # # # . #",
    "·": ".. .. .. ## ## .. ..",
    " ": "... ... ... ... ... ... ...",
}.items()}


def rect(x, y, w=1, h=1, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{extra}/>'


def pix(rows, colors, x=0, y=0, s=1):
    """Draws a bitmap: rows of chars, `colors` maps char -> fill ('.' etc. stay empty)."""
    runs = {}
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            c = row[i]
            k = i
            while k < len(row) and row[k] == c:
                k += 1
            if c in colors:
                runs.setdefault(colors[c], []).append(rect(x + i * s, y + j * s, (k - i) * s, s))
            i = k
    return "".join(f'<g fill="{f}">{"".join(r)}</g>' for f, r in runs.items())


def text_width(s, scale=1):
    return (sum(len(FONT[c][0]) for c in s) + len(s) - 1) * scale


def text(s, x, y, fill, scale=1):
    rows = [""] * 7
    for n, c in enumerate(s):
        rows = [r + ("." if n else "") + g for r, g in zip(rows, FONT[c])]
    return pix(rows, {"#": fill}, x, y, scale)


def spans(parts, x, y):
    """Draws [(text, color), ...] on one line, returns (svg, end_x)."""
    out = []
    for s, color in parts:
        out.append(text(s, x, y, color))
        x += text_width(s) + 1
    return "".join(out), x


def card(w, h):
    """Background with notched pixel corners and a 1px border."""
    bg = rect(2, 0, w - 4, h) + rect(0, 2, w, h - 4) + rect(1, 1, w - 2, h - 2)
    border = (rect(2, 0, w - 4) + rect(2, h - 1, w - 4) + rect(0, 2, 1, h - 4) + rect(w - 1, 2, 1, h - 4)
              + rect(1, 1) + rect(w - 2, 1) + rect(1, h - 2) + rect(w - 2, h - 2))
    return f'<g fill="{CARD}">{bg}</g><g fill="{LINE}">{border}</g>'


def frame(x, y, w, h):
    return rect(x + 1, y, w - 2) + rect(x + 1, y + h - 1, w - 2) + rect(x, y + 1, 1, h - 2) + rect(x + w - 1, y + 1, 1, h - 2)


def svg(name, w, h, label, body, style=""):
    label = label.replace("&", "&amp;")
    reduced = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * PX}" height="{h * PX}" viewBox="0 0 {w} {h}" '
           f'shape-rendering="crispEdges" role="img" aria-label="{label}"><title>{label}</title>'
           f"<style>{style}{reduced}</style>{body}</svg>\n")
    (OUT / name).write_text(doc)


# Ferris the crab, 19x16.
FERRIS = [
    "oo.o...........o.oo",
    "oo.o...........o.oo",
    "oooo...........oooo",
    ".oo.............oo.",
    "..o....ooooo....o..",
    "..o..ohhoooooo..o..",
    "..ooooooooooooooo..",
    ".ooooowkooowkooooo.",
    ".oooookkoookkooooo.",
    ".ooooooooooooooooo.",
    ".oooooomooomoooooo.",
    "..oooooommmoooooo..",
    "...ooooooooooooo...",
    "....ddddddddddd....",
]
LEGS = [["..d.d.d.....d.d.d..", ".d.d.d.......d.d.d."]]
FERRIS_COLORS = {"o": RUST, "h": "#ff8a4d", "d": "#a52b00", "m": "#6e1d00", "k": "#0d0d0d", "w": "#ffffff"}


def ferris(x, y, s=1):
    return pix(FERRIS + LEGS[0], FERRIS_COLORS, x, y, s)


FLICKER = ("@keyframes frame{0%{opacity:1}50%{opacity:0}}"
           ".f0{animation:frame .4s steps(1) infinite}.f1{animation:frame .4s steps(1) infinite reverse}")


def disc(r, inside):
    """Bitmap of a disc of radius r, cells marked by inside(dx, dy, dist)."""
    n = 2 * r + 1
    return ["".join(inside(i - r, j - r, math.hypot(i - r, j - r)) for i in range(n)) for j in range(n)]


def anim(rng, durations, spread):
    return f' style="animation-duration:{rng.choice(durations)}s;animation-delay:-{rng.random() * spread:.1f}s"'


def pattern(pid, w, h, cells, color):
    return (f'<pattern id="{pid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">'
            + "".join(rect(x, y, cw, ch, f' fill="{color}"') for x, y, cw, ch in cells) + "</pattern>")


def falling(pid, h, dur, steps):
    vals = ";".join(f"0 {h * k // steps}" for k in range(steps + 1))
    return (f'<animateTransform attributeName="patternTransform" type="translate" values="{vals}" '
            f'dur="{dur}s" calcMode="discrete" repeatCount="indefinite"/>')


CLOUDS = [
    ["......######........", "...############.....", ".#################..", "####################"],
    ["....#####.....", ".##########...", "##############"],
    [".....#####..........", "..###########.####..", "####################.", "#####################"],
]

FLAME = [
    ["..#..", ".#y#.", ".yYy.", "#yYy#", ".rrr."],
    [".#...", "..#y.", ".yYy#", "#yYy.", ".rrr."],
]


def hero():
    h, top = 130, 86
    rng = random.Random(11)
    body, defs = [], []

    # sky: banded night gradient with dithered seams, glowing towards the horizon
    bands = [(0, "#0a0b20"), (24, "#0e0f2a"), (48, "#131436"), (72, "#1a1944"), (96, "#231f52")]
    for i, (y0, color) in enumerate(bands):
        y1 = bands[i + 1][0] if i + 1 < len(bands) else h
        body.append(rect(0, y0, W, y1 - y0, f' fill="{color}"'))
        if i:
            defs.append(pattern(f"q{i}", 2, 2, [(0, 0, 1, 1)], color) + pattern(f"h{i}", 2, 2, [(0, 0, 1, 1), (1, 1, 1, 1)], color))
            body.append(rect(0, y0 - 4, W, 2, f' fill="url(#q{i})"') + rect(0, y0 - 2, W, 2, f' fill="url(#h{i})"'))

    # stars
    name = "SERHII KALIUZHNYI"
    nx = (W - text_width(name, 2)) // 2
    keep_out = [(nx - 3, 5, nx + text_width(name, 2) + 3, 26), (30, 27, 210, 52), (204, 20, 234, 46)]
    stars = []
    while len(stars) < 45:
        x, y = rng.randrange(2, W - 2), rng.randrange(2, 92)
        if any(a <= x <= c and b <= y <= d for a, b, c, d in keep_out) or (40 <= x <= 200 and y > 52):
            continue
        if any(abs(x - sx) < 5 and abs(y - sy) < 5 for sx, sy, _ in stars):
            continue
        stars.append((x, y, rng.random()))
    for x, y, r in stars:
        a = anim(rng, [2.4, 3.1, 4.3, 5.2], 5)
        if r > 0.9:
            body.append(f'<g class="tw" fill="#ffffff"{a}>{rect(x, y)}</g>'
                        f'<g class="tw" fill="#7d84c8"{a}>{rect(x - 1, y)}{rect(x + 1, y)}{rect(x, y - 1)}{rect(x, y + 1)}</g>')
        else:
            body.append(rect(x, y, 1, 1, f' class="tw" fill="{"#8b93d6" if r > 0.6 else "#424887"}"{a}'))

    # moon with a halo and craters
    defs.append(pattern("halo", 2, 2, [(0, 0, 1, 1)], "#3a3870"))
    body.append(pix(disc(11, lambda dx, dy, d: "h" if d <= 11.3 else "."), {"h": "url(#halo)"}, 207, 22))
    body.append(pix(disc(7, lambda dx, dy, d: "." if d > 7.2 else ("c" if (dx, dy) in {(-2, -2), (-3, -2), (2, 1), (3, 1), (2, 2), (-1, 3)} else "m")),
                    {"m": "#ece6c8", "c": "#c9c2a2"}, 211, 26))

    # distant hills
    for color, base, amp, seed in (("#16163c", 104, 7, 3), ("#101130", 112, 6, 5)):
        r2 = random.Random(seed)
        y, cols = base, []
        for x in range(W):
            y = max(base - amp, min(base + amp, y + r2.choice([-1, 0, 0, 0, 1])))
            cols.append(rect(x, y, 1, h - y))
        body.append(f'<g fill="{color}">{"".join(cols)}</g>')

    # drifting clouds (behind the moon's right half, the text and the island)
    cloud_svg = []
    for k, (cy, ci, dur) in enumerate([(14, 0, 140), (30, 1, 110), (58, 2, 170), (40, 0, 125)]):
        shape = CLOUDS[ci]
        rows = [row.replace("#", "t") if j == 0 else (row.replace("#", "s") if j == len(shape) - 1 else row) for j, row in enumerate(shape)]
        cloud_svg.append(f'<g class="cloud" style="animation-duration:{dur}s;animation-delay:-{dur * (k * 0.29 + 0.1):.0f}s">'
                         + pix(rows, {"#": "#22234f", "t": "#2e2f66", "s": "#1b1b44"}, -24, cy) + "</g>")
    body.append("".join(cloud_svg))

    # the floating island: grass top, layered soil, rocks, crystals, glowing roots
    left, right = 50, 190
    edges, lx, rx = [], left, right
    depth = 34
    for j in range(depth):
        t = j / depth
        hw = (right - left) / 2 * (1 - t ** 1.25)
        cx = 120 + 3 * math.sin(j / 5)
        lx = round(cx - hw + rng.choice([-1, 0, 0, 1]))
        rx = round(cx + hw + rng.choice([-1, 0, 0, 1]))
        if rx - lx < 2:
            break
        edges.append((lx, rx))
    soil = []
    for j, (a, b) in enumerate(edges):
        color = "#4a3248" if j < 3 else ("#3a273f" if j < 12 else ("#2d1f35" if j < 22 else "#22182b"))
        soil.append(rect(a, top + j, b - a, 1, f' fill="{color}"'))
        soil.append(rect(a, top + j, 1, 1, ' fill="#1a1222"') + rect(b - 1, top + j, 1, 1, ' fill="#1a1222"'))
    body.append("".join(soil))
    stones = []
    for _ in range(40):
        j = rng.randrange(3, len(edges) - 3)
        a, b = edges[j]
        if b - a < 10:
            continue
        x = rng.randrange(a + 2, b - 4)
        w = rng.choice([1, 2, 3])
        stones.append(rect(x, top + j, w, 1, ' fill="#5a4560"') + rect(x, top + j + 1, w, 1, ' fill="#1c1424"'))
    body.append("".join(stones))
    # roots dangling from the underside with glowing tips
    roots = []
    for x in range(edges[-1][0] - 30, edges[-1][1] + 30, 7):
        j = next((j for j in range(len(edges) - 1, -1, -1) if edges[j][0] <= x < edges[j][1]), None)
        if j is None:
            continue
        ln = rng.randrange(2, 7)
        roots.append(rect(x, top + j + 1, 1, ln, ' fill="#2a1d30"')
                     + rect(x, top + j + 1 + ln, 1, 1, f' class="glow" fill="#59f0ff"{anim(rng, [1.8, 2.6, 3.4], 3)}'))
    body.append("".join(roots))
    crystal = ["..c..", ".cCc.", "cCCCc", ".cCc."]
    for x, j in ((84, 9), (139, 15), (110, 22), (156, 6)):
        body.append(f'<g class="glow"{anim(rng, [2.2, 3.0], 3)}>' + pix(crystal, {"c": "#2bb5c9", "C": "#9ff8ff"}, x, top + j) + "</g>")

    # grass
    grass = rect(left + 1, top - 1, right - left - 2, 1, ' fill="#2f6b45"') + rect(left, top, right - left, 1, ' fill="#24503a"')
    for x in range(left + 2, right - 2):
        if rng.random() < 0.35:
            grass += rect(x, top - 2, 1, 1, f' fill="{rng.choice(["#4caf6a", "#3d8f57"])}"')
    body.append(grass)

    # pond + waterfall over the left edge
    px0, px1 = left + 1, 82
    body.append(rect(px0, top - 1, px1 - px0, 5, ' fill="#174458"') + rect(px0, top + 4, px1 - px0 - 4, 1, ' fill="#123446"')
                + rect(px0, top - 1, px1 - px0, 1, ' fill="#2c7f96"'))
    body.append("".join(rect(x, top + rng.randrange(0, 4), 2, 1, f' class="glint" fill="#7fd8e6"{anim(rng, [1.6, 2.4, 3.2], 3)}')
                        for x in range(px0 + 3, px1 - 3, 6)))
    defs.append(f'<pattern id="fall" width="2" height="6" patternUnits="userSpaceOnUse">{rect(0, 0, 1, 3, " fill=" + chr(34) + "#7fd8e6" + chr(34))}'
                f'{rect(1, 2, 1, 3, " fill=" + chr(34) + "#3a9fb5" + chr(34))}{falling("fall", 6, 0.5, 6)}</pattern>')
    body.append(rect(left - 2, top - 1, 2, h - top + 1, ' fill="#1f6378"') + rect(left - 2, top - 1, 2, h - top + 1, ' fill="url(#fall)"'))
    body.append(rect(left - 4, h - 3, 6, 1, ' fill="#3a9fb5"') + rect(left - 5, h - 2, 8, 2, ' fill="#2c7f96"'))

    # lamp post with a dithered pool of light
    defs.append(pattern("light", 2, 2, [(0, 0, 1, 1)], "#4a3f6a"))
    body.append(pix(disc(9, lambda dx, dy, d: "l" if d <= 9.3 and dy > -4 else "."), {"l": "url(#light)"}, 81, 63))
    body.append(rect(90, 67, 1, top - 67, ' fill="#2a2838"') + rect(89, 65, 3, 2, ' fill="#ffd27a"') + rect(88, 64, 5, 1, ' fill="#2a2838"'))

    # cabin: roof, chimney, timber walls, warm windows
    hx0, hx1, wall = 96, 134, 68
    body.append(rect(hx0, wall, hx1 - hx0, top - 1 - wall, ' fill="#4a4562"'))
    beams = rect(hx0, wall, hx1 - hx0, 1) + rect(hx0, 75, hx1 - hx0, 1) + rect(hx0, wall, 1, top - 1 - wall) + rect(hx1 - 1, wall, 1, top - 1 - wall)
    beams += rect(115, wall, 1, 7)
    for k in range(6):
        beams += rect(98 + k, wall + 1 + k, 1, 1) + rect(132 - k, wall + 1 + k, 1, 1)
    body.append(f'<g fill="#2b2740">{beams}</g>')
    chimney = rect(125, 50, 5, 10, ' fill="#7a3428"') + rect(124, 49, 7, 2, ' fill="#4a2420"')
    chimney += "".join(rect(126 + (k % 2) * 2, 52 + k * 2, 1, 1, ' fill="#4a2420"') for k in range(4))
    body.append(chimney)
    roof = []
    for r in range(13):
        span = 4 + r * 2
        color = "#4a7a8a" if r == 0 else ("#2a4d5c" if r % 2 else "#24434f")
        roof.append(rect(115 - span, 56 + r, span * 2 + 1, 1, f' fill="{color}"'))
        roof.append(rect(115 - span, 56 + r, 1, 1, ' fill="#4a7a8a"') + rect(115 + span, 56 + r, 1, 1, ' fill="#4a7a8a"'))
    body.append("".join(roof) + rect(113, 60, 5, 3, ' fill="#1a2f38"') + rect(114, 61, 3, 1, ' fill="#ffb347"'))
    win = ["wwwww", "wWwWw", "fffff", "wWwWw", "wwwww"]
    wc = {"w": "#ffb347", "W": "#ffd98a", "f": "#9a4a1a"}
    for x in (101, 125):
        body.append(f'<g class="flick"{anim(rng, [3.7, 5.3], 4)}>{pix(win, wc, x, 69)}</g>')
    body.append(pix(["wwwwwwwwwww", "wWWwwwwwWWw", "wWWwbbbwWWw", "wwwwbgbwwww", "fffffffffff"], {**wc, "b": "#2b2740", "g": GREEN}, 112, 77))
    body.append(rect(100, 77, 5, top - 78, ' fill="#231c2c"') + rect(103, 81, 1, 1, ' fill="#ffb347"') + rect(99, 76, 7, 1, ' fill="#2b2740"'))
    body.append(rect(112, top - 1, 11, 1, ' fill="#6b5a3a"'))
    for k, d in enumerate((0, 1.3, 2.6)):
        body.append(rect(127, 46, 2, 2, f' class="smoke" fill="#6a6a8e" style="animation-delay:-{d}s"'))

    # a small rack next to the cabin
    rx0, rtop = 139, 70
    body.append(rect(rx0, rtop, 9, top - 1 - rtop, ' fill="#171a3d"') + rect(rx0, rtop, 9, 1, ' fill="#3d4483"')
                + rect(rx0, rtop + 1, 1, top - 2 - rtop, ' fill="#2a2f5e"') + rect(rx0 + 8, rtop + 1, 1, top - 2 - rtop, ' fill="#2a2f5e"'))
    for u in range(rtop + 2, top - 2, 3):
        body.append(rect(rx0 + 1, u, 7, 2, ' fill="#22264f"') + rect(rx0 + 4, u, 3, 1, ' fill="#30376b"'))
        for lx in (rx0 + 2, rx0 + 3):
            c = rng.choices([GREEN, "#58a6ff", "#d29922"], [6, 2, 1])[0]
            body.append(rect(lx, u, 1, 1, f' class="led" fill="{c}"{anim(rng, [0.7, 1.1, 1.7, 2.3], 3)}'))
    body.append(rect(rx0 + 4, rtop - 3, 1, 3, ' fill="#3d4483"') + rect(rx0 + 4, rtop - 4, 1, 1, ' class="beacon" fill="#ff5555"'))

    # campfire, sparks, and Ferris under an umbrella
    fx = 154
    body.append(pix(disc(7, lambda dx, dy, d: "l" if d <= 7.3 and dy > -3 else "."), {"l": "url(#light)"}, fx - 5, top - 10))
    fc = {"#": "#ff8c1a", "y": "#ffd23f", "Y": "#fff3b0", "r": "#c43c1a"}
    for i, f in enumerate(FLAME):
        body.append(f'<g class="f{i}">{pix(f, fc, fx, top - 6)}</g>')
    body.append(rect(fx - 1, top - 1, 7, 1, ' fill="#6b3b1e"') + rect(fx, top - 2, 1, 1, ' fill="#8a5028"') + rect(fx + 4, top - 2, 1, 1, ' fill="#8a5028"'))
    for k in range(4):
        body.append(rect(fx + 1 + k % 3, top - 8, 1, 1, f' class="spark" fill="#ffb347" style="animation-delay:-{k * 0.55:.2f}s"'))
    ux = 170
    canopy = ["......rrrrrr......", "...rrrRRRRRRrrr...", ".rrRRRRRRRRRRRRrr.", "rrrrrrrrrrrrrrrrrr", "d..d..d..d..d..d.."]
    body.append(rect(ux + 8, 63, 1, top - 1 - 63, ' fill="#3a3040"') + pix(canopy, {"r": "#b8323c", "R": "#e0525a", "d": "#7a1f28"}, ux, 58))
    body.append(f'<g class="bob">{ferris(ux, top - 1 - len(FERRIS) - len(LEGS[0]))}</g>')

    # fireflies
    for x, y in ((62, 72), (74, 64), (56, 58), (186, 66), (196, 76), (48, 78)):
        body.append(f'<g class="fly"{anim(rng, [4.5, 6.0, 7.5], 6)}>{rect(x - 1, y - 1, 3, 3, " fill=" + chr(34) + "#2bb5c9" + chr(34) + " opacity=" + chr(34) + ".35" + chr(34))}'
                    f'{rect(x, y, 1, 1, " fill=" + chr(34) + "#9ff8ff" + chr(34))}</g>')

    # rain, two layers for depth
    for pid, tw, th, n, dur, color in (("rf", 37, 41, 5, 0.9, "#3d4483"), ("rn", 53, 47, 5, 0.55, "#7f88d6")):
        cells = [(rng.randrange(tw), rng.randrange(th), 1, 3 if pid == "rf" else 4) for _ in range(n)]
        defs.append(pattern(pid, tw, th, cells, color).replace("</pattern>", falling(pid, th, dur, 8) + "</pattern>"))
        body.append(rect(0, 0, W, h, f' fill="url(#{pid})" opacity="{".5" if pid == "rf" else ".45"}"'))

    # title
    role = "DEVOPS & SOFTWARE ENGINEER"
    line3 = [("7+ YEARS", YELLOW), (" · ", MUTED), ("RUST", RUST), (" · ", MUTED), ("TYPESCRIPT", TS)]
    l3w = sum(text_width(s) for s, _ in line3) + len(line3) - 1
    body.append(text(name, nx + 1, 9, "#2a1f5e", 2) + text(name, nx, 8, INK, 2))
    body.append(text(role, (W - text_width(role)) // 2, 30, "#9aa5ce"))
    line, end = spans(line3, (W - l3w) // 2, 41)
    body.append(line + rect(end + 1, 41, 4, 7, f' class="blink" fill="{INK}"'))

    style = ("@keyframes tw{0%,100%{opacity:1}50%{opacity:.2}}.tw{animation:tw 3s steps(3) infinite}"
             "@keyframes led{0%,100%{opacity:1}50%{opacity:.15}}.led{animation:led 1s steps(1) infinite}"
             "@keyframes blink{0%{opacity:1}50%{opacity:0}}.blink{animation:blink 1.1s steps(1) infinite}"
             ".beacon{animation:blink 2s steps(1) infinite}"
             "@keyframes glow{0%,100%{opacity:1}50%{opacity:.35}}.glow{animation:glow 2.6s steps(4) infinite}"
             ".glint{animation:blink 2s steps(1) infinite}"
             "@keyframes flick{0%,92%,100%{opacity:1}94%{opacity:.75}96%{opacity:.9}}.flick{animation:flick 4s steps(1) infinite}"
             "@keyframes smoke{0%{transform:translate(0,0);opacity:.9}100%{transform:translate(-6px,-22px);opacity:0}}"
             ".smoke{animation:smoke 3.9s steps(11) infinite}"
             "@keyframes spark{0%{transform:translate(0,0);opacity:1}100%{transform:translate(2px,-12px);opacity:0}}"
             ".spark{animation:spark 2.2s steps(6) infinite}"
             "@keyframes cloud{from{transform:translateX(0)}to{transform:translateX(290px)}}.cloud{animation:cloud 120s steps(290) infinite}"
             "@keyframes fly{0%,100%{transform:translate(0,0)}25%{transform:translate(3px,-2px)}50%{transform:translate(5px,1px)}"
             "75%{transform:translate(2px,3px)}}.fly{animation:fly 6s steps(10) infinite}"
             "@keyframes bob{0%{transform:translateY(0)}50%{transform:translateY(-1px)}}.bob{animation:bob 1.6s steps(1) infinite}"
             + FLICKER)
    svg("hero.svg", W, h, "Serhii Kaliuzhnyi — DevOps & Software Engineer, 7+ years, Rust and TypeScript",
        f"<defs>{''.join(defs)}</defs>{''.join(body)}", style)


def blend(fg, bg, a):
    f = [int(fg[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(b[i] + (f[i] - b[i]) * a):02x}" for i in range(3))


def chip(label, x, y, color):
    w = text_width(label) + 6
    return (rect(x + 1, y + 1, w - 2, 9, f' fill="{blend(color, CARD, 0.14)}"')
            + f'<g fill="{color}">{frame(x, y, w, 11)}</g>' + text(label, x + 3, y + 2, color)), w


HEART = [".#.#.", "#####", "#####", ".###.", "..#.."]

SKILLS = [
    ("LANG", None, [("RUST", RUST), ("TYPESCRIPT", TS)]),
    ("ORCH", "#6d9bff", ["KUBERNETES", "HELM", "ARGOCD", "ISTIO"]),
    ("INFRA", "#a77bea", ["TERRAFORM", "ANSIBLE", "AWS"]),
    ("SHIP", "#39c5cf", ["DOCKER", "GH ACTIONS", "GITLAB CI"]),
    ("OBSERVE", "#f0a04b", ["PROMETHEUS", "GRAFANA", "JAEGER"]),
]


def stats():
    top, pitch = 60, 15
    h = top + pitch * len(SKILLS) + 22
    body = [card(W, h)]

    # portrait
    body.append(rect(8, 8, 44, 40, ' fill="#14173b"') + f'<g fill="{LINE}">{frame(8, 8, 44, 40)}</g>')
    body.append(f'<g class="bob">{ferris(11, 12, 2)}</g>')

    # header: player tag + hearts
    line, _ = spans([("P1", YELLOW), (" GROK-RS", INK)], 58, 9)
    body.append(line)
    for i in range(3):
        cls = ' class="blink"' if i == 2 else ""
        body.append(f"<g{cls}>{pix(HEART, {'#': '#ff5577'}, W - 26 + i * 6, 10)}</g>")

    # class + level
    body.append(text("CLASS", 58, 21, MUTED) + text("DEVOPS ENGINEER", 94, 21, INK) + text("SOFTWARE ENGINEER", 94, 30, INK))
    body.append(text("LVL", 58, 39, MUTED) + text("7+", 94, 39, YELLOW))

    # XP bar: segments revealed by a sliding cover, last one blinks (almost level 8)
    bx, by, seg = 112, 39, 4
    n = (W - 10 - bx - 2) // seg
    bw = n * seg + 3
    body.append(f'<g fill="{LINE}">{frame(bx, by, bw, 7)}</g>')
    body.append(f'<g fill="{GREEN}">' + "".join(rect(bx + 2 + k * seg, by + 2, seg - 1, 3) for k in range(n - 1)) + "</g>")
    defs = f'<clipPath id="xp">{rect(bx + 1, by + 1, bw - 2, 5)}</clipPath>'
    body.append(f'<g clip-path="url(#xp)"><rect class="xp" x="{bx + 1}" y="{by + 1}" width="{bw - 2}" height="5" fill="{CARD}"/></g>')
    body.append(rect(bx + 2 + (n - 1) * seg, by + 2, seg - 1, 3, f' class="blink" fill="{YELLOW}"'))
    fill = (n - 1) * seg

    # skills
    body.append(f'<g fill="{LINE}">' + "".join(rect(x, 52) for x in range(8, W - 8, 2)) + "</g>")
    cx = 8 + max(text_width(label) for label, _, _ in SKILLS) + 6
    for r, (label, color, items) in enumerate(SKILLS):
        y = top + r * pitch
        body.append(text(label, 8, y + 2, MUTED))
        x = cx
        for item in items:
            name, c = item if isinstance(item, tuple) else (item, color)
            svg_chip, w = chip(name, x, y, c)
            body.append(svg_chip)
            x += w + 3
        assert x - 3 <= W - 8, f"{label} row overflows by {x - 3 - (W - 8)}"

    # current quest
    qy = top + pitch * len(SKILLS) + 3
    body.append(f'<g fill="{LINE}">' + "".join(rect(x, qy - 5) for x in range(8, W - 8, 2)) + "</g>")
    body.append(text("QUEST", 8, qy + 2, MUTED) + text("!", cx, qy + 2, YELLOW).replace("<g ", '<g class="blink" ', 1)
                + text("EMBEDDED DEVELOPMENT", cx + 5, qy + 2, INK))

    style = ("@keyframes blink{0%{opacity:1}50%{opacity:0}}.blink{animation:blink 1.1s steps(1) infinite}"
             "@keyframes bob{0%{transform:translateY(0)}50%{transform:translateY(-1px)}}.bob{animation:bob 1s steps(1) infinite}"
             f"@keyframes xp{{0%{{transform:translateX(0)}}40%,100%{{transform:translateX({fill}px)}}}}"
             f".xp{{animation:xp 7s steps({fill // seg}) infinite}}")
    svg("stats.svg", W, h, "Character sheet: DevOps & Software Engineer, level 7+. Rust, TypeScript, Kubernetes, Helm, "
        "Argo CD, Istio, Terraform, Ansible, AWS, Docker, GitHub Actions, GitLab CI, Prometheus, Grafana, Jaeger",
        f"<defs>{defs}</defs>{''.join(body)}", style)


def pipeline():
    h, stages = 29, ["PUSH", "BUILD", "TEST", "SHIP", "RUN"]
    nh, ny = 13, 8
    widths = [text_width(s) + 10 for s in stages]
    gap = (W - 16 - sum(widths)) / (len(stages) - 1)
    xs, x = [], 8.0
    for w in widths:
        xs.append(round(x))
        x += w + gap
    body = [card(W, h)]
    mid = ny + nh // 2

    # track between nodes
    body.append(f'<g fill="{LINE}">' + "".join(
        rect(x, mid) for i in range(len(stages) - 1) for x in range(xs[i] + widths[i] + 1, xs[i + 1] - 1, 2)) + "</g>")

    # the packet: a little container, drawn under the nodes so it disappears into each stage
    start = xs[0] + widths[0] // 2 - 2
    end = xs[-1] + widths[-1] // 2 - 2
    dist, move = end - start, 0.8
    body.append(f'<g class="pkt">{pix(["#####", "#.#.#", "#.#.#", "#####"], {"#": "#39c5cf", ".": "#1b6f75"}, start, mid - 1)}</g>')

    style = [f"@keyframes pkt{{0%{{transform:translateX(0)}}{move * 100:.0f}%,100%{{transform:translateX({dist}px)}}}}"
             f".pkt{{animation:pkt 7s steps({dist}) infinite}}"]
    for i, (s, x, w) in enumerate(zip(stages, xs, widths)):
        at = max(0.0, (x - start) / dist * move) * 100
        style.append(f"@keyframes n{i}{{0%{{fill:{LINE}}}{at:.1f}%,100%{{fill:{GREEN}}}}}"
                     f"@keyframes t{i}{{0%{{fill:{MUTED}}}{at:.1f}%,100%{{fill:{INK}}}}}"
                     f".n{i}{{animation:n{i} 7s steps(1) infinite}}.t{i}{{animation:t{i} 7s steps(1) infinite}}")
        body.append(rect(x + 1, ny + 1, w - 2, nh - 2, f' fill="{CARD}"') + rect(x, ny + 1, w, nh - 2, f' fill="{CARD}"')
                    + f'<g class="n{i}" fill="{LINE}">{frame(x, ny, w, nh)}</g>'
                    + f'<g class="t{i}" fill="{MUTED}">{text(s, x + 5, ny + 3, "inherit")}</g>')
    svg("pipeline.svg", W, h, "Pipeline: push, build, test, ship, run", "".join(body), "".join(style))


class Timeline:
    """Keyframes placed on one shared loop, so every scene of the story stays in sync."""

    def __init__(self, total):
        self.total, self.css = total, []

    def __call__(self, frames, before=None, timing="steps(1)"):
        name = f"k{len(self.css)}"
        pts = [f"0%{{{before if before is not None else frames[0][1]}}}"]
        pts += [f"{t / self.total * 100:.3f}%{{{decl}}}" for t, decl in frames]
        pts.append(f"100%{{{frames[-1][1]}}}")
        self.css.append(f"@keyframes {name}{{{''.join(pts)}}}.{name}{{animation:{name} {self.total}s {timing} infinite}}")
        return name

    def show(self, t0, t1=None):
        return self([(t0, "opacity:1")] + ([(t1, "opacity:0")] if t1 is not None else []), before="opacity:0")

    def move(self, t0, t1, dx, dy, before=None, steps=None):
        steps = steps or max(abs(dx), abs(dy), 1)
        return self([(t0, f"transform:translate({before or '0px,0px'})"), (t1, f"transform:translate({dx}px,{dy}px)")],
                    timing=f"steps({steps})")


def lightbulb(x, y):
    bulb = ["..yyy..", ".yYYYy.", "yYYYYYy", "yYYYYYy", ".yYYYy.", "..yyy..", "..ggg..", "..ggg..", "...g..."]
    rays = rect(x - 3, y + 3, 2, 1) + rect(x + 8, y + 3, 2, 1) + rect(x + 3, y - 3, 1, 2) + rect(x - 1, y - 1) + rect(x + 7, y - 1)
    return pix(bulb, {"y": "#e3b341", "Y": "#fff3b0", "g": "#9aa5ce"}, x, y) + f'<g fill="#fff3b0">{rays}</g>'


def bresenham(x0, y0, x1, y1):
    pts, dx, dy = [], abs(x1 - x0), -abs(y1 - y0)
    sx, sy, err = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1), abs(x1 - x0) - abs(y1 - y0)
    while True:
        pts.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return pts
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def story():
    h, S = 96, 5
    T = 5 * S + 3
    X0, Y0, X1, Y1, FL = 6, 6, 234, 80, 70
    tl = Timeline(T)
    rng = random.Random(3)
    defs, clips = [], []

    def typed(parts, x, y, t0, t1, bg):
        line, end = spans(parts, x, y)
        w = end - x
        cid = f"c{len(clips)}"
        clips.append(f'<clipPath id="{cid}">{rect(x, y, w, 7)}</clipPath>')
        k = tl.move(t0, t1, w, 0)
        return line + f'<g clip-path="url(#{cid})"><rect class="cover {k}" x="{x}" y="{y}" width="{w}" height="7" fill="{bg}"/></g>'

    defs.append(pattern("wp", 8, 8, [(0, 0, 1, 1), (4, 4, 1, 1)], "#20234a"))

    def indoor():
        return (rect(X0, Y0, X1 - X0, FL - Y0, ' fill="#181a38"') + rect(X0, Y0, X1 - X0, FL - Y0, ' fill="url(#wp)"')
                + rect(X0, FL - 6, X1 - X0, 1, ' fill="#23264f"')
                + rect(X0, FL, X1 - X0, Y1 - FL, ' fill="#2e2235"') + rect(X0, FL, X1 - X0, 1, ' fill="#3d2e44"')
                + "".join(rect(x, FL + 1, 1, Y1 - FL - 1, ' fill="#251b2c"') for x in range(X0 + 14, X1, 22)))

    def sky(colors, ground):
        out, step = "", (ground - Y0) // len(colors) + 1
        for i, c in enumerate(colors):
            out += rect(X0, Y0 + i * step, X1 - X0, min(step, ground - Y0 - i * step), f' fill="{c}"')
        for _ in range(14):
            x, y = rng.randrange(X0 + 2, X1 - 2), rng.randrange(Y0 + 2, ground - 20)
            out += rect(x, y, 1, 1, f' class="tw" fill="{rng.choice(["#8b93d6", "#454c8a"])}"{anim(rng, [2.4, 3.6], 4)}')
        return out

    def desk():
        return (rect(28, 62, 184, 2, ' fill="#6b4a2b"') + rect(28, 64, 184, 1, ' fill="#4a321e"')
                + rect(34, 65, 3, FL - 65, ' fill="#4a321e"') + rect(203, 65, 3, FL - 65, ' fill="#4a321e"'))

    def ferris_at(x, y, cls="bob"):
        return f'<g class="{cls}">{ferris(x, y)}</g>'

    scenes = []

    # 1 · MATH: chalkboard proofs, then a lightbulb
    t = 0
    s = indoor()
    s += rect(22, 12, 130, 46, ' fill="#6b4a2b"') + rect(24, 14, 126, 42, ' fill="#1d3a2e"')
    s += "".join(rect(rng.randrange(26, 146), rng.randrange(16, 54), 2, 1, ' fill="#24473a"') for _ in range(12))
    s += rect(26, 58, 122, 2, ' fill="#8a6a45"') + rect(40, 57, 4, 1, ' fill="#e8efe6"') + rect(110, 57, 3, 1, f' fill="{YELLOW}"')
    chalk = "#e8efe6"
    s += typed([("A²+B²=C²", chalk)], 30, 19, t + 0.5, t + 1.5, "#1d3a2e")
    s += typed([("∑ 1/N² = π²/6", chalk)], 30, 31, t + 1.8, t + 3.2, "#1d3a2e")
    s += typed([("DY/DX = 2X", YELLOW)], 30, 43, t + 3.4, t + 4.2, "#1d3a2e")
    s += ferris_at(166, FL - 16) + rect(163, FL - 15, 2, 1, f' fill="{chalk}"')
    s += f'<g class="{tl.show(t + 4.3)}">{lightbulb(172, 30)}</g>'
    scenes.append(("CH.1  MATH", s))

    # 2 · PHYSICS: an apple, a bonk, and an atom
    t = S
    s = sky(["#120f2e", "#1a1440", "#241a52", "#2e1f5e"], FL)
    s += rect(X0, FL, X1 - X0, Y1 - FL, ' fill="#24503a"') + rect(X0, FL, X1 - X0, 1, ' fill="#2f6b45"')
    s += rect(46, 34, 6, FL - 34, ' fill="#5a3a28"') + rect(46, 34, 2, FL - 34, ' fill="#43291c"')
    s += pix(disc(15, lambda dx, dy, d: "." if d > 15.3 else ("h" if dx + dy < -9 else ("s" if dx + dy > 9 else "g"))),
             {"g": "#2f6b45", "h": "#3d8f57", "s": "#24503a"}, 34, 11)
    s += "".join(rect(x, y, 2, 2, ' fill="#d13b3b"') for x, y in ((40, 20), (52, 15), (36, 30)))
    s += ferris_at(54, FL - 16)
    apple = pix([".g.", "rrr", "rrr"], {"g": "#3d8f57", "r": "#d13b3b"}, 62, 30)
    fall = tl([(t + 1.0, "transform:translate(0px,0px)"), (t + 1.5, "transform:translate(0px,21px)"),
               (t + 1.7, "transform:translate(6px,15px)"), (t + 2.1, "transform:translate(16px,37px)")], timing="steps(6)")
    s += f'<g class="{fall}">{apple}</g>'
    s += f'<g class="{tl.show(t + 1.5, t + 2.4)}">{text("!", 76, 42, YELLOW)}</g>'
    for k, (x, y) in enumerate(((80, 46), (85, 41), (90, 36))):
        s += rect(x, y, 2, 2, f' class="{tl.show(t + 2.4 + k * 0.15)}" fill="{INK}"')
    s += f'<g class="{tl.show(t + 2.9)}">{text("F = MA", 96, 22, YELLOW)}</g>'
    s += f'<g class="{tl.show(t + 3.6)}">{text("E = MC²", 96, 34, INK)}</g>'
    ax, ay = 190, 36
    orbit_px, electrons = set(), []
    for j, phi in enumerate((0, math.pi / 3, 2 * math.pi / 3)):
        pts = []
        for k in range(120):
            th = 2 * math.pi * k / 120
            ex, ey = 24 * math.cos(th), 8 * math.sin(th)
            p = (round(ax + ex * math.cos(phi) - ey * math.sin(phi)), round(ay + ex * math.sin(phi) + ey * math.cos(phi)))
            orbit_px.add(p)
            if k % 6 == 0:
                pts.append(p)
        kf = "".join(f"{i / len(pts) * 100:.2f}%{{transform:translate({px - pts[0][0]}px,{py - pts[0][1]}px)}}" for i, (px, py) in enumerate(pts))
        tl.css.append(f"@keyframes e{j}{{{kf}}}.e{j}{{animation:e{j} 1.8s steps(1) infinite;animation-delay:-{j * 0.6}s}}")
        electrons.append(rect(pts[0][0], pts[0][1], 2, 2, f' class="e{j}" fill="#59f0ff"'))
    s += f'<g fill="#2e3466">{"".join(rect(x, y) for x, y in sorted(orbit_px))}</g>'
    s += pix(["rb", "br"], {"r": "#d13b3b", "b": "#4d94e8"}, ax - 1, ay - 1, 2) + "".join(electrons)
    scenes.append(("CH.2  PHYSICS", s))

    # 3 · RUST: Ferris writes and runs a program
    t = 2 * S
    s = indoor() + desk()
    s += rect(44, 8, 96, 50, ' fill="#2b2f45"') + rect(44, 8, 96, 1, ' fill="#3d4483"') + rect(47, 11, 90, 44, ' fill="#0a0d1c"')
    s += rect(88, 58, 8, 4, ' fill="#2b2f45"') + rect(82, 61, 20, 1, ' fill="#3d4483"')
    scr = "#0a0d1c"
    s += typed([("FN", RUST), (" MAIN", INK), ("()", MUTED), (" {", INK)], 50, 13, t + 0.3, t + 1.1, scr)
    s += typed([("  DEPLOY", "#39c5cf"), ("();", MUTED)], 50, 21, t + 1.3, t + 2.1, scr)
    s += typed([("}", INK)], 50, 29, t + 2.2, t + 2.4, scr)
    s += typed([("$", GREEN), (" CARGO RUN", INK)], 50, 37, t + 2.8, t + 3.6, scr)
    s += f'<g class="{tl.show(t + 4.0)}">{text("OK", 50, 45, GREEN)}</g>'
    s += rect(140, 60, 18, 2, ' fill="#3a3f5c"') + "".join(rect(x, 60, 1, 1, ' fill="#6e76b8"') for x in range(141, 157, 2))
    s += ferris_at(160, 46, "type")
    s += pix(["mmmm.", "mmmmh", "mmmmh", "mmmm.", "mmmm."], {"m": "#8a3b2e", "h": "#8a3b2e"}, 190, 57)
    s += "".join(rect(191 + k, 54, 1, 2, f' class="smoke" fill="#6a6a8e" style="animation-delay:-{k * 0.8}s"') for k in range(2))
    scenes.append(("CH.3  RUST", s))

    # 4 · DEVOPS: containers fall from the cloud onto a ship, and it sails to prod
    t = 3 * S
    s = sky(["#0c0f24", "#10132f", "#14173b", "#1a1b48"], 60)
    s += pix(disc(4, lambda dx, dy, d: "m" if d <= 4.2 else "."), {"m": "#ece6c8"}, 206, 9)
    defs.append('<pattern id="wave" width="12" height="2" patternUnits="userSpaceOnUse">'
                + rect(0, 0, 3, 1, ' fill="#3d7fa6"') + rect(6, 1, 3, 1, ' fill="#2a5f80"')
                + '<animateTransform attributeName="patternTransform" type="translate" values="0 0;3 0;6 0;9 0;12 0" '
                  'dur=".8s" calcMode="discrete" repeatCount="indefinite"/></pattern>')
    s += rect(X0, 60, X1 - X0, Y1 - 60, ' fill="#123048"')
    s += rect(X0, 50, 40, 3, ' fill="#6b4a2b"') + rect(12, 53, 2, 9, ' fill="#4a321e"') + rect(36, 53, 2, 9, ' fill="#4a321e"')
    ship = ""
    for r in range(10):
        color = "#d9dde8" if r == 2 else ("#4a1c1c" if r >= 7 else "#7a2e2e")
        ship += rect(50 + r // 2, 52 + r, 85 - r // 2 - r * 2, 1, f' fill="{color}"')
    ship += rect(54, 40, 15, 12, ' fill="#c9cfe0"') + rect(53, 39, 17, 1, ' fill="#7a2e2e"')
    ship += "".join(rect(x, 43, 2, 2, ' fill="#ffd27a"') for x in (56, 59, 62, 65))
    ship += rect(58, 31, 5, 8, ' fill="#326ce5"') + rect(58, 31, 5, 2, ' fill="#15151f"')
    ship += "".join(rect(60, 29, 2, 2, f' class="smoke" fill="#6a6a8e" style="animation-delay:-{k * 1.1}s"') for k in range(3))
    for k, ((bx, by), c) in enumerate(zip(((72, 45), (85, 45), (98, 45), (78, 38), (91, 38)),
                                          ("#39c5cf", "#a77bea", "#f0a04b", "#3fb950", "#4d94e8"))):
        box = ["".join("d" if j in (0, 6) or i in (0, 11) else ("l" if i % 2 == 0 else "c") for i in range(12)) for j in range(7)]
        drop = tl.move(t + 0.4 + k * 0.45, t + 0.8 + k * 0.45, 0, 0, before=f"0px,{Y0 - 8 - by}px", steps=10)
        ship += f'<g class="{drop}">{pix(box, {"c": c, "l": blend("#ffffff", c, 0.75), "d": blend("#000000", c, 0.6)}, bx, by)}</g>'
    ship += ferris(113, 36)
    s += f'<g class="{tl.move(t + 3.0, t + 5.0, 130, 0)}">{ship}</g>'
    s += rect(X0, 60, X1 - X0, Y1 - 60, ' fill="#123048" opacity=".85"') + rect(X0, 60, X1 - X0, 2, ' fill="url(#wave)"')
    cloud = ["......########..........", "...##############.####..", ".#######################.", "#########################",
             "#########################", ".#######################.", "...####################..."]
    s += pix(cloud, {"#": "#2e2f66"}, 66, 6) + pix(cloud, {"#": "#2e2f66"}, 84, 7)
    scenes.append(("CH.4  DEVOPS", s))

    # 5 · EMBEDDED: solder a board, print hello world, blink an LED
    t = 4 * S
    s = indoor() + desk()
    s += rect(52, 12, 84, 24, ' fill="#1f6b3a"') + rect(55, 15, 78, 18, ' fill="#20251a"') + rect(56, 16, 76, 16, ' fill="#8fbf3f"')
    s += "".join(rect(x, y, 2, 2, ' fill="#9aa5ce"') for x in (53, 133) for y in (13, 33))
    s += typed([("HELLO WORLD", "#2b3a12")], 60, 20, t + 2.4, t + 3.6, "#8fbf3f")
    s += rect(127, 20, 4, 7, f' class="{tl.show(t + 3.6)}" fill="#2b3a12"')
    s += rect(70, 36, 1, 10, ' fill="#d13b3b"') + rect(74, 36, 1, 10, ' fill="#2b2f45"') + rect(78, 36, 1, 10, f' fill="{YELLOW}"')
    s += rect(56, 46, 84, 14, ' fill="#1f6b3a"') + rect(56, 60, 84, 2, ' fill="#164d2a"')
    s += rect(60, 50, 22, 1, ' fill="#2f8f52"') + rect(104, 55, 30, 1, ' fill="#2f8f52"') + rect(82, 50, 1, 6, ' fill="#2f8f52"')
    s += rect(86, 49, 18, 8, ' fill="#15151f"') + "".join(rect(x, y, 1, 1, ' fill="#9aa5ce"') for x in range(87, 104, 2) for y in (48, 57))
    s += "".join(rect(x, 47, 1, 1, f' fill="{YELLOW}"') for x in range(60, 80, 2)) + rect(56, 51, 3, 4, ' fill="#9aa5ce"')
    s += rect(124, 49, 3, 3, ' fill="#3a1414"')
    led = tl([(t + 3.8 + k * 0.3, f"opacity:{k % 2 ^ 1}") for k in range(5)], before="opacity:0")
    s += rect(124, 49, 3, 3, f' class="{led}" fill="#ff4040"')
    iron = bresenham(158, 42, 141, 53)
    s += "".join(rect(x, y, 1, 2, f' fill="{"#c43c1a" if i < 8 else ("#9aa5ce" if i < len(iron) - 2 else "#ffb347")}"') for i, (x, y) in enumerate(iron))
    sparks = tl([(t + 0.3, "opacity:1"), (t + 2.2, "opacity:0")], before="opacity:0")
    s += f'<g class="{sparks}"><g class="spark" fill="#fff3b0">{rect(139, 52)}{rect(138, 55)}{rect(142, 56)}</g></g>'
    s += ferris_at(160, 46)
    s += f'<g class="{tl.show(t + 4.2)}">{lightbulb(166, 26)}</g>'
    scenes.append(("CH.5  EMBEDDED", s))

    # epilogue
    t = 5 * S
    s = rect(X0, Y0, X1 - X0, Y1 - Y0, ' fill="#06070f"')
    s += "".join(rect(rng.randrange(X0 + 2, X1 - 2), rng.randrange(Y0 + 2, Y1 - 2), 1, 1, ' class="tw" fill="#454c8a"') for _ in range(20))
    msg = "TO BE CONTINUED"
    mx = (W - text_width(msg)) // 2
    s += typed([(msg, INK)], mx, 24, t + 0.3, t + 1.5, "#06070f")
    s += rect(mx + text_width(msg) + 2, 24, 4, 7, f' class="blink" fill="{INK}"')
    s += ferris_at((W - 19) // 2, 44)
    scenes.append(("CH.6  ???", s))

    # assemble: stage + caption bar + progress pips
    body = [card(W, h), f'<g fill="{LINE}">{frame(X0 - 1, Y0 - 1, X1 - X0 + 2, Y1 - Y0 + 2)}</g>']
    clips.append(f'<clipPath id="stage">{rect(X0, Y0, X1 - X0, Y1 - Y0)}</clipPath>')
    still = 4  # the scene shown when motion is reduced
    stage, captions = [], []
    for i, (caption, scene) in enumerate(scenes):
        cls = tl.show(i * S, (i + 1) * S if i < len(scenes) - 1 else None)
        hidden = "" if i == still else ' opacity="0"'
        stage.append(f'<g class="{cls}"{hidden}>{scene}</g>')
        captions.append(f'<g class="{cls}"{hidden}>{text(caption, 8, 85, INK)}</g>')
        px = W - 8 - (len(scenes) - i) * 6 + 1
        captions.append(rect(px, 87, 4, 3, f' fill="{LINE}"') + rect(px, 87, 4, 3, f' class="{cls}"{hidden} fill="{YELLOW}"'))
    body.append(f'<g clip-path="url(#stage)">{"".join(stage)}</g>' + "".join(captions))

    style = ("@keyframes tw{0%,100%{opacity:1}50%{opacity:.2}}.tw{animation:tw 3s steps(3) infinite}"
             "@keyframes blink{0%{opacity:1}50%{opacity:0}}.blink{animation:blink 1.1s steps(1) infinite}"
             "@keyframes bob{0%{transform:translateY(0)}50%{transform:translateY(-1px)}}.bob{animation:bob 1.6s steps(1) infinite}"
             ".type{animation:bob .3s steps(1) infinite}.spark{animation:blink .2s steps(1) infinite}"
             "@keyframes smoke{0%{transform:translate(0,0);opacity:.9}100%{transform:translate(-3px,-14px);opacity:0}}"
             ".smoke{animation:smoke 2.4s steps(7) infinite}"
             + "".join(tl.css) + "@media (prefers-reduced-motion:reduce){.cover{display:none}}")
    svg("story.svg", W, h, "Animated story: Ferris the crab studies math and physics, writes Rust, ships containers to production, "
        "and is now learning embedded development. To be continued.",
        f"<defs>{''.join(defs)}{''.join(clips)}</defs>{''.join(body)}", style)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    hero()
    stats()
    pipeline()
    story()
