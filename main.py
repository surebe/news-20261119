"""main.py - "The Daily World": one page that sums up the world news of
Thursday 19 November 2026.

A pure-stdlib Python program. It draws a newspaper front page with its
own raster kit (drawkit), a hand-made bitmap font (font5x7), a
schematic world map (mapdata) and per-story vector illustrations
(scenes), then writes the page as a PNG to the output directory
(/output in the grader, $MAKEFUN_OUTPUT_DIR locally).

Deterministic by construction: no clock, no network, no randomness -
two runs write the same bytes.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import drawkit
import font5x7 as font
import mapdata
import scenes
from stories import STORIES

W = 1024
H = 1024
PAPER = (250, 248, 240)
INK = (24, 24, 28)
MUTE = (96, 96, 102)
ACCENT = (158, 42, 43)
RULE = (24, 24, 28)

REGION_COLORS = {
    "North America": (198, 52, 60),
    "Latin America": (228, 132, 36),
    "Europe": (52, 84, 168),
    "Africa": (206, 158, 32),
    "Middle East": (128, 78, 158),
    "Asia": (38, 142, 86),
    "Oceania": (36, 132, 176),
}

DATE_LINE = "Thursday 19 November 2026"


def _hline(cv, x, y, w, color=RULE, thick=1):
    cv.rect(x, y, w, thick, color)


def _tag(cv, x, y, text, color, scale=1):
    """Small filled label with white text; returns its width."""
    tw = font.text_width(text, scale) + 6
    th = 7 * scale + 4
    cv.rect(x, y, tw, th, color)
    font.draw_text(cv, x + 3, y + 2, text, scale=scale,
                   color=(255, 255, 255), bold=True)
    return tw


def draw_masthead(cv):
    # top meta line
    font.draw_text(cv, 20, 12, "Independent world digest - all times UTC",
                   scale=1, color=MUTE)
    right = "Vol. I - No. 19"
    font.draw_text(cv, W - 20 - font.text_width(right, 1), 12, right,
                   scale=1, color=MUTE)
    _hline(cv, 16, 26, W - 32, RULE, 1)
    # nameplate
    name = "THE DAILY WORLD"
    nw = font.text_width(name, 8)
    font.draw_text(cv, (W - nw) // 2, 34, name, scale=8, color=INK, bold=True)
    _hline(cv, 16, 96, W - 32, RULE, 3)
    # date line, big and unmissable
    dw = font.text_width(DATE_LINE, 4)
    font.draw_text(cv, (W - dw) // 2, 106, DATE_LINE, scale=4,
                   color=ACCENT, bold=True)
    strap = ("52 stories - 7 regions - 16 drawn - every story date-checked "
             "to this day")
    sw = font.text_width(strap, 2)
    font.draw_text(cv, (W - sw) // 2, 140, strap, scale=2, color=INK)
    _hline(cv, 16, 162, W - 32, RULE, 1)
    return 170


def draw_top_story(cv, story, y):
    x = 16
    img_w, img_h = 330, 188
    scenes.draw_scene(cv, story["scene"], x, y, img_w, img_h)
    tx = x + img_w + 16
    tw = 664 - tx
    color = REGION_COLORS[story["region"]]
    _tag(cv, tx, y + 2, story["region"].upper(), color, scale=1)
    font.draw_text(cv, tx + font.text_width(story["region"].upper(), 1) + 12,
                   y + 2, story["field"], scale=1, color=MUTE)
    lines = font.wrap(story["headline"], 3, tw)
    ly = y + 20
    for ln in lines[:3]:
        font.draw_text(cv, tx, ly, ln, scale=3, color=INK, bold=True)
        ly += 25
    sy = ly + 4
    for ln in font.wrap(story["summary"], 2, tw)[:5]:
        font.draw_text(cv, tx, sy, ln, scale=2, color=(52, 52, 58))
        sy += 16
    font.draw_text(cv, tx, min(sy + 4, y + img_h - 12),
                   story["location"] + " - " + story["source"],
                   scale=1, color=MUTE)
    return y + img_h


def draw_map_panel(cv, stories, x, y, w):
    font.draw_text(cv, x, y, "WHERE THURSDAY HAPPENED", scale=1,
                   color=INK, bold=True)
    my = y + 12
    mh = 138
    mapdata.draw_map(cv, x, my, w, mh, (198, 220, 238), (122, 172, 112),
                     (226, 236, 246))
    # pins: one per story, region colour, pushed apart deterministically
    # but never off land - a shifted pin must stay on a land pixel
    land_rgb = (122, 172, 112)

    def on_land(px, py):
        if not (x <= px < x + w and my <= py < my + mh):
            return False
        i = (py * cv.w + px) * 3
        return tuple(cv.px[i:i + 3]) == land_rgb

    pts = []
    for s in stories:
        px, py = mapdata.project(s["lon"], s["lat"], x, my, w, mh)
        pts.append([px, py, s])
    # coastal cities can fall a pixel off the schematic shoreline:
    # thicken the coast under any such pin so every pin stands on land
    for p in pts:
        if not on_land(p[0], p[1]):
            cv.circle(p[0], p[1], 3, land_rgb)
    pts.sort(key=lambda p: (p[1], p[0]))
    placed = []
    for p in pts:
        px, py = p[0], p[1]
        moved = False
        if any((px - qx) ** 2 + (py - qy) ** 2 < 36 for qx, qy in placed):
            for attempt in range(48):
                nx = p[0] + ((attempt % 6) - 2) * 4
                ny = p[1] + ((attempt // 6) - 2) * 4
                if any((nx - qx) ** 2 + (ny - qy) ** 2 < 36
                       for qx, qy in placed):
                    continue
                if not on_land(nx, ny):
                    continue
                px, py = nx, ny
                moved = True
                break
        if moved:
            cv.line(p[0], p[1], px, py, (90, 90, 96), 1)
        placed.append((px, py))
        col = REGION_COLORS[p[2]["region"]]
        cv.circle(px, py, 3, col)
        cv.circle(px, py, 3, (30, 30, 34), fill=False)
    cy = my + mh + 5
    font.draw_text(cv, x, cy, "One pin per story, every pin on land.",
                   scale=1, color=MUTE)
    return cy + 10


def draw_briefs(cv, briefs, y):
    font.draw_text(cv, 16, y, "AROUND THE WORLD IN BRIEF", scale=2,
                   color=INK, bold=True)
    right = "36 more stories from Thursday's wires"
    font.draw_text(cv, W - 16 - font.text_width(right, 1), y + 4, right,
                   scale=1, color=MUTE)
    _hline(cv, 16, y + 18, W - 32, RULE, 1)
    cols = 4
    gap = 10
    cw = (W - 32 - gap * (cols - 1)) // cols
    row_h = 25
    by = y + 24
    for i, s in enumerate(briefs):
        cx = 16 + (i % cols) * (cw + gap)
        cy = by + (i // cols) * row_h
        col = REGION_COLORS[s["region"]]
        cv.circle(cx + 3, cy + 3, 3, col)
        head = font.wrap(s["headline"], 1, cw - 12)
        font.draw_text(cv, cx + 10, cy, head[0] if head else "",
                       scale=1, color=INK, bold=True)
        ly = cy + 9
        for ln in font.wrap(s["summary"], 1, cw - 12)[:2]:
            font.draw_text(cv, cx + 10, ly, ln, scale=1,
                           color=(70, 70, 76))
            ly += 8
    rows = (len(briefs) + cols - 1) // cols
    return by + rows * row_h


def draw_footer(cv, y):
    _hline(cv, 16, y, W - 32, RULE, 2)
    line1 = ("Sources: Reuters - Associated Press - BBC - AFP - Al Jazeera - "
             "The Guardian and wires cited per story")
    font.draw_text(cv, 16, y + 4, line1, scale=1, color=(52, 52, 58))
    line2 = ("Date check: every story above happened or was first reported on "
             "Thursday 19 November 2026, in some time zone of that day.")
    font.draw_text(cv, 16, y + 12, line2, scale=1, color=(52, 52, 58))
    right = "Drawn and set by program - no photographs"
    font.draw_text(cv, W - 16 - font.text_width(right, 1), y + 12, right,
                   scale=1, color=MUTE)


def draw_lead_cell(cv, story, x, y, w):
    img_h = 72
    scenes.draw_scene(cv, story["scene"], x, y, w, img_h)
    color = REGION_COLORS[story["region"]]
    cv.circle(x + 6, y + img_h + 10, 3, color)
    ly = y + img_h + 4
    lines = font.wrap(story["headline"], 2, w - 12)
    for ln in lines[:2]:
        font.draw_text(cv, x + 12, ly, ln, scale=2, color=INK, bold=True)
        ly += 15
    font.draw_text(cv, x + 12, ly + 1, story["source"], scale=1, color=MUTE)


def draw_leads(cv, leads, y):
    cols = 5
    gap = 6
    cw = (W - 32 - gap * (cols - 1)) // cols
    cell_h = 116
    for i, story in enumerate(leads):
        cx = 16 + (i % cols) * (cw + gap)
        cy = y + (i // cols) * cell_h
        draw_lead_cell(cv, story, cx, cy, cw)
    rows = (len(leads) + cols - 1) // cols
    return y + rows * cell_h


def main():
    cv = drawkit.Canvas(W, H, PAPER)
    # page frame
    cv.polyline([(8, 8), (W - 9, 8), (W - 9, H - 9), (8, H - 9)], RULE, 2,
                close=True)
    y = draw_masthead(cv)
    leads = [s for s in STORIES if s.get("lead")]
    briefs = [s for s in STORIES if not s.get("lead")]
    top = leads[0]
    row_a = y + 8
    draw_map_panel(cv, STORIES, 680, row_a, W - 16 - 680)
    y = draw_top_story(cv, top, row_a) + 10
    _hline(cv, 16, y, W - 32, RULE, 1)
    y = draw_leads(cv, leads[1:], y + 8)
    _hline(cv, 16, y + 2, W - 32, RULE, 1)
    y = draw_briefs(cv, briefs, y + 8)
    draw_footer(cv, y + 6)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = drawkit.encode_png(cv.px, W, H)
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
