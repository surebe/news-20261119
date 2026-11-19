"""scenes.py - small vector scene painters for the lead stories.

Each painter draws one recognisable scene inside a box: a background,
a setting and the story's object - a drawn picture, not an icon in a
coloured box. All shapes come from drawkit primitives and fixed
arithmetic, so every run paints the same pixels.
"""

INK = (28, 30, 38)
PAPER = (250, 248, 240)


def _sky(cv, x, y, w, h, top, bottom, ground, ground_h=None):
    gh = ground_h if ground_h is not None else max(6, h // 4)
    cv.vgrad(x, y, w, h - gh, top, bottom)
    cv.rect(x, y + h - gh, w, gh, ground)
    return y + h - gh


def _sun(cv, cx, cy, r, color=(246, 197, 66)):
    cv.circle(cx, cy, r, color)
    cv.circle(cx, cy, r + 3, color, fill=False)


def _cloud(cv, cx, cy, s, color=(255, 255, 255)):
    cv.ellipse(cx, cy, int(16 * s), int(7 * s), color)
    cv.ellipse(cx - int(10 * s), cy + int(2 * s), int(10 * s), int(5 * s), color)
    cv.ellipse(cx + int(11 * s), cy + int(2 * s), int(11 * s), int(6 * s), color)


def _building(cv, x, gy, w, h, body, roof, windows=(255, 226, 130)):
    cv.rect(x, gy - h, w, h, body)
    cv.poly([(x - 3, gy - h), (x + w // 2, gy - h - w // 4), (x + w + 3, gy - h)], roof)
    cols = max(1, w // 12)
    rows = max(1, h // 14)
    for i in range(cols):
        for j in range(rows):
            wx = x + 4 + i * (w - 8) // max(1, cols)
            wy = gy - h + 5 + j * (h - 10) // max(1, rows)
            cv.rect(wx, wy, 4, 6, windows)


def _leader_seated(cv, cx, table_y, r, suit, hair, tie):
    """One seated leader behind the table: head with a hair cap, a
    suited torso that the table edge cuts off, shirt and tie."""
    head_y = table_y - (r * 21) // 10
    # torso: a trapezoid widening from the neck to the table line
    cv.poly([(cx - r - 4, table_y), (cx - r + 1, head_y + r - 1),
             (cx + r - 1, head_y + r - 1), (cx + r + 4, table_y)], suit)
    # shirt V and tie
    cv.poly([(cx - r // 3 - 1, head_y + r - 1), (cx + r // 3 + 1, head_y + r - 1),
             (cx, table_y - 2)], (244, 244, 246))
    cv.line(cx, head_y + r, cx, table_y - 3, tie, max(2, r // 4))
    # head, then a slightly higher hair circle so a cap of hair shows
    cv.circle(cx, head_y, r, (238, 198, 160))
    cv.circle(cx, head_y - r // 3, r - max(1, r // 6), hair)
    cv.circle(cx, head_y + r // 5, r - max(2, r // 4), (238, 198, 160))
    # forearms resting on the table edge
    cv.line(cx - r - 3, table_y - 3, cx - r - 7, table_y, suit,
            max(2, r // 3))
    cv.line(cx + r + 3, table_y - 3, cx + r + 7, table_y, suit,
            max(2, r // 3))


def scene_summit(cv, x, y, w, h):
    """A summit room, drawn as a room: three national banners hang on
    the wall and three leaders sit at one long conference table."""
    floor_h = max(8, h // 5)
    cv.vgrad(x, y, w, h - floor_h, (196, 214, 233), (233, 239, 246))
    cv.rect(x, y + h - floor_h, w, floor_h, (128, 102, 76))
    cv.rect(x, y + h - floor_h - 3, w, 3, (168, 176, 190))
    table_y = y + (h * 68) // 100
    seats = (x + w // 4, x + w // 2, x + w * 3 // 4)
    # three hanging banners, one behind each seat
    flag_w = max(12, w // 11)
    flag_top = y + max(3, h // 16)
    flag_h = (h * 42) // 100
    for i, cx in enumerate(seats):
        fx = cx - flag_w // 2
        cv.rect(fx - 2, flag_top - 2, flag_w + 4, 3, (110, 84, 50))
        if i == 0:  # blue field, white stars as a dot grid
            cv.rect(fx, flag_top, flag_w, flag_h, (52, 74, 160))
            for gx in range(3):
                for gy2 in range(4):
                    cv.rect(fx + 3 + gx * (flag_w - 6) // 2,
                            flag_top + 4 + gy2 * (flag_h - 8) // 3,
                            2, 2, (255, 255, 255))
        elif i == 1:  # red field, one big and four small gold stars
            cv.rect(fx, flag_top, flag_w, flag_h, (198, 44, 48))
            cv.circle(fx + flag_w // 3, flag_top + flag_h // 4,
                      max(2, flag_w // 6), (246, 205, 66))
            for k in range(3):
                cv.rect(fx + flag_w * 2 // 3,
                        flag_top + 3 + k * (flag_h // 4), 2, 2,
                        (246, 205, 66))
        else:  # white-blue-red horizontal bands
            band = flag_h // 3
            cv.rect(fx, flag_top, flag_w, band, (244, 244, 246))
            cv.rect(fx, flag_top + band, flag_w, band, (52, 84, 168))
            cv.rect(fx, flag_top + 2 * band, flag_w, flag_h - 2 * band,
                    (198, 52, 60))
    # the three leaders: fair hair / dark hair / grey hair, three suits
    r = max(5, h // 9)
    leaders = (
        ((36, 48, 88), (228, 198, 122), (178, 40, 48)),
        ((28, 28, 34), (22, 22, 26), (52, 74, 160)),
        ((54, 54, 62), (198, 198, 204), (150, 36, 44)),
    )
    for cx, (suit, hair, tie) in zip(seats, leaders):
        _leader_seated(cv, cx, table_y, r, suit, hair, tie)
    # the long table over their laps, with a name plate at each seat
    tx0 = x + (w * 6) // 100
    tx1 = x + (w * 94) // 100
    cv.rect(tx0 - 4, table_y - 3, tx1 - tx0 + 8, 5, (146, 102, 62))
    cv.rect(tx0, table_y + 2, tx1 - tx0, y + h - floor_h + 3 - table_y,
            (104, 70, 42))
    for cx in seats:
        pw = max(10, r * 2)
        cv.rect(cx - pw // 2, table_y + 5, pw, max(4, h // 22),
                (246, 244, 238))
        # a slim microphone rising from the table toward each leader
        cv.line(cx + r + 6, table_y - 2, cx + r // 2, table_y - r - 2,
                INK, 1)
        cv.circle(cx + r // 2, table_y - r - 3, 2, INK)


def scene_court(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (196, 205, 222), (235, 238, 244), (150, 144, 130))
    bw = w * 3 // 4
    bx = x + (w - bw) // 2
    # pediment + columns
    cv.poly([(bx - 4, gy - h * 2 // 3), (bx + bw // 2, gy - h * 5 // 6),
             (bx + bw + 4, gy - h * 2 // 3)], (120, 124, 140))
    cv.rect(bx - 4, gy - h * 2 // 3, bw + 8, 5, (120, 124, 140))
    for i in range(4):
        cx = bx + 8 + i * (bw - 16) // 3
        cv.rect(cx - 3, gy - h * 2 // 3 + 6, 6, h * 2 // 3 - 12, (232, 230, 222))
    cv.rect(bx - 4, gy - 6, bw + 8, 6, (120, 124, 140))
    # scales of justice in front
    cx = x + w // 2
    top = gy - h // 2
    cv.line(cx, top, cx, gy - h // 6, INK, 2)
    cv.line(cx - w // 7, top + 4, cx + w // 7, top + 4, INK, 2)
    for sx in (cx - w // 7, cx + w // 7):
        cv.line(sx, top + 4, sx - 5, top + h // 7, INK, 1)
        cv.line(sx, top + 4, sx + 5, top + h // 7, INK, 1)
        cv.ellipse(sx, top + h // 7 + 2, 8, 3, (198, 160, 60))


def scene_rocket(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (24, 34, 74), (86, 110, 168), (70, 74, 84))
    # stars, fixed pattern
    for i in range(14):
        sx = x + (i * 53) % max(1, w - 8) + 3
        sy = y + (i * 29) % max(1, h // 2)
        cv.set(sx, sy, (255, 255, 255))
        cv.set(sx + 1, sy, (210, 220, 255))
    cx = x + w // 2
    # rocket body
    cv.rect(cx - 7, gy - h * 3 // 5, 14, h * 2 // 5, (238, 238, 242))
    cv.poly([(cx - 7, gy - h * 3 // 5), (cx, gy - h * 4 // 5), (cx + 7, gy - h * 3 // 5)], (198, 52, 60))
    cv.circle(cx, gy - h // 2, 3, (90, 150, 210))
    cv.poly([(cx - 7, gy - h // 4), (cx - 16, gy - h // 8), (cx - 7, gy - h // 8)], (198, 52, 60))
    cv.poly([(cx + 7, gy - h // 4), (cx + 16, gy - h // 8), (cx + 7, gy - h // 8)], (198, 52, 60))
    # flame and smoke
    cv.poly([(cx - 5, gy - h // 8), (cx, gy + 2), (cx + 5, gy - h // 8)], (246, 150, 50))
    _cloud(cv, cx - w // 5, gy - 4, w / 120, (200, 204, 214))
    _cloud(cv, cx + w // 5, gy - 4, w / 110, (200, 204, 214))
    cv.rect(x + w // 8, gy - h // 6, 6, h // 6, (110, 114, 124))


def scene_cyclone(cv, x, y, w, h):
    cv.vgrad(x, y, w, h * 2 // 3, (86, 104, 128), (150, 168, 188))
    # spiral storm
    cx, cy = x + w // 2, y + h // 3
    import math
    for t_i in range(160):
        t = t_i / 10.0
        r = 2 + t * min(w, h) / 42.0
        px = int(cx + r * math.cos(t))
        py = int(cy + r * math.sin(t) * 0.55)
        cv.circle(px, py, 2, (236, 240, 246))
    cv.circle(cx, cy, 4, (60, 74, 96))
    # sea with waves and a palm bending
    cv.rect(x, y + h * 2 // 3, w, h // 3, (52, 96, 140))
    for i in range(5):
        wx = x + 6 + i * (w // 5)
        wy = y + h * 2 // 3 + 6 + (i % 2) * 5
        cv.polyline([(wx, wy), (wx + 8, wy - 4), (wx + 16, wy)], (210, 232, 248), 2)
    gx = x + w * 4 // 5
    gy = y + h * 2 // 3 + 4
    cv.line(gx, gy, gx + 3, gy - h // 4, (96, 74, 50), 3)
    for a in range(5):
        ex = gx + 3 + int(14 * ((a - 1) / 2.2))
        ey = gy - h // 4 - 4 + abs(a - 2) * 2
        cv.line(gx + 3, gy - h // 4, ex, ey, (52, 130, 66), 2)


def scene_flood(cv, x, y, w, h):
    cv.vgrad(x, y, w, h // 2, (170, 190, 214), (214, 226, 238))
    wy = y + h // 2
    cv.rect(x, wy, w, h // 2, (74, 116, 156))
    for i in range(6):
        wx = x + 4 + i * (w // 6)
        cv.polyline([(wx, wy + 8 + (i % 3) * 6), (wx + 9, wy + 4 + (i % 3) * 6),
                     (wx + 18, wy + 8 + (i % 3) * 6)], (196, 224, 244), 2)
    # two houses half sunk
    for hx, col in ((x + w // 7, (188, 120, 84)), (x + w * 3 // 5, (150, 96, 120))):
        hw = w // 4
        cv.rect(hx, wy - h // 6, hw, h // 6 + 4, col)
        cv.poly([(hx - 3, wy - h // 6), (hx + hw // 2, wy - h // 3),
                 (hx + hw + 3, wy - h // 6)], (110, 66, 52))
        cv.rect(hx + hw // 2 - 3, wy - h // 8, 6, h // 8, (70, 52, 44))
    # rescue boat
    bx = x + w * 2 // 5
    cv.poly([(bx, wy + h // 5), (bx + w // 4, wy + h // 5), (bx + w // 5, wy + h // 3),
             (bx + w // 20, wy + h // 3)], (220, 120, 40))
    cv.circle(bx + w // 8, wy + h // 6, 3, (238, 198, 160))
    cv.line(bx + w // 8, wy + h // 6 + 3, bx + w // 8, wy + h // 5, (40, 60, 120), 2)


def scene_chart(cv, x, y, w, h):
    cv.rect(x, y, w, h, (18, 26, 44))
    # grid
    for i in range(1, 5):
        gy = y + i * h // 5
        cv.line(x + 4, gy, x + w - 4, gy, (44, 58, 88), 1)
    pts = [(x + 8, y + h * 4 // 5), (x + w // 4, y + h * 3 // 5),
           (x + w * 2 // 5, y + h * 2 // 3), (x + w * 3 // 5, y + h * 2 // 5),
           (x + w * 4 // 5, y + h // 3), (x + w - 12, y + h // 6)]
    cv.polyline(pts, (84, 220, 130), 3)
    ax, ay = pts[-1]
    cv.poly([(ax, ay), (ax - 12, ay + 2), (ax - 3, ay + 10)], (84, 220, 130))
    # candle bars
    for i, (bx, bh) in enumerate(((x + w // 6, 14), (x + w * 2 // 6, 20), (x + w * 3 // 6, 12))):
        cv.rect(bx, y + h - 12 - bh, 7, bh, (220, 90, 80) if i == 1 else (84, 200, 120))


def scene_fire(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (74, 62, 66), (140, 96, 84), (52, 46, 44))
    # tree line burnt
    for i in range(6):
        tx = x + 6 + i * (w // 6)
        cv.line(tx, gy, tx, gy - h // 5, (30, 26, 26), 3)
        cv.line(tx, gy - h // 5, tx - 6, gy - h // 3, (30, 26, 26), 2)
        cv.line(tx, gy - h // 5, tx + 6, gy - h * 2 // 7, (30, 26, 26), 2)
    # flames
    for i, fx in enumerate((x + w // 4, x + w // 2, x + w * 3 // 4)):
        fh = h // 2 - (i % 2) * h // 9
        cv.poly([(fx - 12, gy), (fx, gy - fh), (fx + 12, gy)], (232, 96, 30))
        cv.poly([(fx - 7, gy), (fx, gy - fh * 2 // 3), (fx + 7, gy)], (246, 168, 50))
        cv.poly([(fx - 3, gy), (fx, gy - fh // 3), (fx + 3, gy)], (252, 226, 120))
    _cloud(cv, x + w // 3, y + h // 8, w / 110, (120, 112, 112))
    _cloud(cv, x + w * 2 // 3, y + h // 6, w / 120, (104, 98, 98))


def scene_vote(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (172, 208, 240), (228, 242, 252), (120, 150, 105))
    _sun(cv, x + w - w // 6, y + h // 6, max(5, w // 14))
    # ballot box
    bx, bw = x + w // 4, w // 2
    by = gy - h // 3
    cv.rect(bx, by, bw, h // 3, (52, 84, 168))
    cv.rect(bx - 3, by - 5, bw + 6, 6, (36, 58, 120))
    cv.rect(bx + bw // 3, by - 3, bw // 3, 3, (16, 22, 40))
    # ballot paper going in, with a big tick
    px = bx + bw // 4
    cv.rect(px, by - h // 3, bw // 2, h // 3 - 4, (252, 252, 250))
    cv.polyline([(px + 6, by - h // 6), (px + bw // 5, by - h // 9),
                 (px + bw // 2 - 5, by - h // 4)], (198, 52, 60), 3)
    # queue of voters
    for i, col in enumerate(((198, 120, 60), (90, 150, 90), (150, 90, 140))):
        fx = x + w // 10 + i * (w // 9)
        cv.circle(fx, gy - h // 5, 4, (238, 198, 160))
        cv.line(fx, gy - h // 5 + 4, fx, gy - 2, col, 3)


def scene_parliament(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (160, 190, 226), (224, 238, 250), (110, 128, 104))
    cx = x + w // 2
    bw = w * 2 // 3
    bx = x + (w - bw) // 2
    base = gy
    # main block with columns
    cv.rect(bx, base - h // 3, bw, h // 3, (216, 208, 192))
    for i in range(5):
        cxx = bx + 8 + i * (bw - 16) // 4
        cv.rect(cxx - 2, base - h // 3 + 4, 4, h // 3 - 8, (244, 240, 230))
    cv.rect(bx - 3, base - h // 3 - 4, bw + 6, 4, (150, 144, 134))
    # drum and a shallow dome on top
    cv.rect(cx - bw // 6, base - h // 3 - h // 7, bw // 3, h // 7, (204, 198, 186))
    cv.ellipse(cx, base - h // 3 - h // 7, bw // 6, h // 8, (96, 130, 170))
    cv.rect(cx - 1, base - h // 3 - h // 7 - h // 8 - 5, 2, 6, INK)
    cv.circle(cx, base - h // 3 - h // 7 - h // 8 - 7, 2, (198, 52, 60))


def scene_oil(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (226, 190, 140), (244, 224, 190), (168, 138, 96))
    _sun(cv, x + w // 6, y + h // 6, max(5, w // 13), (240, 160, 60))
    # pumpjack
    px = x + w // 5
    cv.line(px, gy, px + w // 3, gy - h // 2, INK, 3)
    cv.line(px + w // 3, gy - h // 2, px + w // 2, gy - h // 3, INK, 3)
    cv.poly([(px + w // 2, gy - h // 3), (px + w * 3 // 5, gy - h // 4),
             (px + w // 2, gy - h // 4)], INK)
    cv.line(px + w // 6, gy, px + w // 4, gy - h // 3, INK, 2)
    cv.rect(px + w // 6 - 4, gy - 6, w // 8, 6, INK)
    # barrels
    for i, col in enumerate(((52, 84, 168), (198, 120, 40))):
        bx = x + w * 3 // 5 + i * (w // 5)
        cv.rect(bx, gy - h // 4, w // 6, h // 4, col)
        cv.rect(bx, gy - h // 4 + 4, w // 6, 2, INK)
        cv.rect(bx, gy - 8, w // 6, 2, INK)


def scene_stadium(cv, x, y, w, h):
    cv.vgrad(x, y, w, h * 3 // 5, (20, 28, 54), (52, 68, 110))
    gy = y + h * 3 // 5
    cv.rect(x, gy, w, h * 2 // 5, (52, 140, 70))
    # floodlights
    for fx in (x + w // 7, x + w * 6 // 7):
        cv.line(fx, gy, fx, y + h // 6, (200, 204, 214), 2)
        cv.rect(fx - 9, y + h // 6 - 8, 18, 9, (240, 240, 220))
    # stand arc
    cv.ellipse(x + w // 2, gy + 4, w // 2, h // 5, (90, 96, 130))
    cv.ellipse(x + w // 2, gy + 4, w // 2, h // 5 - 6, (52, 140, 70))
    # ball and two players
    cv.circle(x + w // 2, gy + h // 5, 5, (250, 250, 250))
    cv.circle(x + w // 2, gy + h // 5, 5, INK, fill=False)
    for fx, col in ((x + w // 3, (198, 52, 60)), (x + w * 2 // 3, (250, 250, 250))):
        cv.circle(fx, gy + h // 7, 4, (238, 198, 160))
        cv.line(fx, gy + h // 7 + 4, fx, gy + h // 4, col, 3)


def scene_plane(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (120, 178, 232), (214, 236, 252))
    _cloud(cv, x + w // 4, y + h * 3 // 5, w / 120)
    _cloud(cv, x + w * 3 // 4, y + h * 4 // 5, w / 100)
    cx, cy = x + w // 2, y + h * 2 // 5
    # fuselage
    cv.ellipse(cx, cy, w // 3, h // 11, (240, 242, 246))
    cv.poly([(cx - w // 3, cy - 2), (cx - w * 2 // 5, cy - h // 5),
             (cx - w // 4, cy - h // 12)], (198, 52, 60))
    cv.poly([(cx - 4, cy + 2), (cx - w // 6, cy + h // 4), (cx + w // 12, cy + 3)], (160, 168, 182))
    cv.poly([(cx + 2, cy - 2), (cx + w // 8, cy - h // 5), (cx + w // 5, cy - 2)], (198, 205, 218))
    for i in range(6):
        cv.rect(cx - w // 5 + i * (w // 11), cy - 3, 4, 4, (90, 150, 210))


def scene_ship(cv, x, y, w, h):
    cv.vgrad(x, y, w, h * 3 // 5, (170, 205, 235), (226, 242, 250))
    wy = y + h * 3 // 5
    cv.rect(x, wy, w, h * 2 // 5, (52, 100, 148))
    for i in range(5):
        wx = x + 5 + i * (w // 5)
        cv.polyline([(wx, wy + 9 + (i % 2) * 6), (wx + 9, wy + 5 + (i % 2) * 6),
                     (wx + 18, wy + 9 + (i % 2) * 6)], (190, 224, 246), 2)
    # container ship
    sx, sw = x + w // 8, w * 3 // 4
    cv.poly([(sx, wy + 2), (sx + sw, wy + 2), (sx + sw - 14, wy + h // 6),
             (sx + 10, wy + h // 6)], (40, 48, 64))
    for i, col in enumerate(((198, 90, 60), (70, 130, 190), (90, 170, 100), (220, 160, 60))):
        cv.rect(sx + 12 + i * (sw // 5), wy - h // 7, sw // 5 - 4, h // 7, col)
    cv.rect(sx + sw - 26, wy - h // 4, 16, h // 4, (232, 232, 228))


def scene_volcano(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (150, 140, 150), (214, 200, 196), (104, 92, 84))
    cx = x + w // 2
    cv.poly([(cx - w // 3, gy), (cx - w // 14, gy - h * 3 // 5),
             (cx + w // 14, gy - h * 3 // 5), (cx + w // 3, gy)], (96, 84, 80))
    cv.poly([(cx - w // 14, gy - h * 3 // 5), (cx, gy - h * 2 // 3),
             (cx + w // 14, gy - h * 3 // 5)], (70, 60, 58))
    # lava
    cv.poly([(cx - 4, gy - h * 3 // 5 + 2), (cx, gy - h // 3), (cx + 4, gy - h * 3 // 5 + 2)], (240, 110, 30))
    cv.polyline([(cx, gy - h // 3), (cx - 6, gy - h // 5), (cx - 3, gy - h // 9)], (240, 110, 30), 2)
    # ash plume
    _cloud(cv, cx, y + h // 7, w / 90, (110, 104, 108))
    _cloud(cv, cx + w // 8, y + h // 5, w / 110, (128, 122, 124))


def scene_snow(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (168, 188, 214), (228, 238, 248), (240, 244, 250))
    # pines with snow
    for i, tx in enumerate((x + w // 6, x + w // 2, x + w * 5 // 6)):
        th = h // 2 - (i % 2) * h // 10
        cv.line(tx, gy, tx, gy - th // 4, (96, 74, 50), 3)
        for j in range(3):
            tw = (th // 3) - j * 3
            ty = gy - th // 4 - j * (th // 5)
            cv.poly([(tx - tw, ty), (tx, ty - th // 4), (tx + tw, ty)], (44, 104, 74))
            cv.poly([(tx - tw // 2, ty - th // 6), (tx, ty - th // 4), (tx + tw // 2, ty - th // 6)], (250, 252, 255))
    # snowflakes fixed pattern
    for i in range(16):
        sx = x + (i * 37) % max(1, w - 6) + 2
        sy = y + (i * 23) % max(1, h // 2)
        cv.set(sx, sy, (255, 255, 255))
        cv.set(sx + 1, sy + 1, (255, 255, 255))


def scene_heat(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (244, 178, 92), (250, 216, 140), (206, 158, 96))
    _sun(cv, x + w // 2, y + h // 3, w // 7, (246, 120, 40))
    # cracked dry earth
    for i in range(4):
        sx = x + 8 + i * (w // 4)
        cv.polyline([(sx, gy + 3), (sx + 8, gy + h // 9), (sx + 3, gy + h // 5)], (120, 84, 50), 2)
    # wilting plant
    px = x + w * 4 // 5
    cv.line(px, gy + h // 6, px, gy - h // 8, (110, 96, 60), 2)
    cv.ellipse(px - 6, gy - h // 8, 7, 3, (140, 130, 84))
    cv.ellipse(px + 6, gy - h // 9, 7, 3, (140, 130, 84))


def scene_train(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (158, 196, 232), (226, 240, 250), (104, 118, 96))
    # hills
    cv.ellipse(x + w // 5, gy + 6, w // 3, h // 5, (96, 140, 92))
    cv.ellipse(x + w * 4 // 5, gy + 6, w // 3, h // 4, (86, 128, 84))
    # track
    cv.line(x, gy + h // 8, x + w, gy + h // 8, INK, 2)
    for i in range(7):
        tx = x + 4 + i * (w // 7)
        cv.line(tx, gy + h // 8 - 2, tx + 4, gy + h // 8 + 3, (110, 84, 60), 2)
    # train
    tx, tw = x + w // 7, w * 4 // 7
    ty = gy - h // 4
    cv.rect(tx, ty, tw, h // 4, (198, 60, 60))
    cv.poly([(tx + tw, ty), (tx + tw + w // 9, ty + h // 9), (tx + tw + w // 9, ty + h // 4), (tx + tw, ty + h // 4)], (168, 48, 52))
    for i in range(4):
        cv.rect(tx + 6 + i * (tw // 4), ty + 5, tw // 5, h // 9, (210, 232, 248))
    cv.circle(tx + tw // 4, gy + h // 8 - 2, 5, INK)
    cv.circle(tx + tw * 3 // 4, gy + h // 8 - 2, 5, INK)


def scene_chip(cv, x, y, w, h):
    cv.rect(x, y, w, h, (16, 34, 40))
    # circuit traces
    for i in range(4):
        ly = y + (i + 1) * h // 5
        cv.line(x + 4, ly, x + w // 3, ly, (40, 120, 110), 2)
        cv.circle(x + w // 3, ly, 2, (80, 200, 180))
        cv.line(x + w * 2 // 3, ly, x + w - 4, ly, (40, 120, 110), 2)
        cv.circle(x + w * 2 // 3, ly, 2, (80, 200, 180))
    # the chip
    cw = w // 3
    cx, cy = x + (w - cw) // 2, y + (h - cw) // 2
    cv.rect(cx, cy, cw, cw, (28, 90, 96))
    cv.rect(cx + 5, cy + 5, cw - 10, cw - 10, (44, 140, 150))
    for i in range(4):
        pin = cy + 6 + i * (cw - 12) // 3
        cv.rect(cx - 6, pin, 6, 3, (180, 190, 200))
        cv.rect(cx + cw, pin, 6, 3, (180, 190, 200))


def scene_protest(cv, x, y, w, h):
    gy = _sky(cv, x, y, w, h, (176, 200, 228), (230, 240, 250), (128, 128, 124))
    _building(cv, x + w * 3 // 5, gy, w // 3, h * 3 // 5, (168, 162, 152), (120, 116, 110))
    # crowd with big placards
    for i in range(7):
        fx = x + 8 + i * (w // 7)
        fy = gy - (i % 2) * 4
        col = ((198, 90, 60), (70, 120, 190), (90, 160, 90), (200, 160, 60))[i % 4]
        cv.circle(fx, fy - h // 5, 4, (238, 198, 160))
        cv.line(fx, fy - h // 5 + 4, fx, fy, col, 3)
        if i % 2 == 0:
            cv.line(fx + 4, fy - h // 5, fx + 4, fy - h * 2 // 5, INK, 2)
            cv.rect(fx - 5, fy - h * 2 // 5 - 12, 19, 12, (252, 252, 250))
            cv.polyline([(fx - 5, fy - h * 2 // 5 - 12), (fx + 14, fy - h * 2 // 5 - 12),
                         (fx + 14, fy - h * 2 // 5), (fx - 5, fy - h * 2 // 5)],
                        INK, 1, close=True)
            cv.rect(fx - 2, fy - h * 2 // 5 - 9, 13, 2, col)
            cv.rect(fx - 2, fy - h * 2 // 5 - 5, 10, 2, col)


def scene_health(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (196, 224, 238), (236, 246, 250))
    # hospital building with a strong outline
    bw = w * 3 // 5
    bx = x + (w - bw) // 2
    top = y + h // 5
    cv.rect(bx, top, bw, h - h // 5, (248, 250, 252))
    cv.polyline([(bx, y + h - 1), (bx, top), (bx + bw, top), (bx + bw, y + h - 1)],
                (90, 110, 140), 2)
    cv.rect(bx - 3, top - 6, bw + 6, 7, (90, 130, 175))
    for i in range(3):
        for j in range(2):
            cv.rect(bx + 8 + i * (bw - 16) // 2, top + 12 + j * (h // 4), 8, 9,
                    (140, 185, 220))
    # big red cross on the facade
    cx, cy = x + w // 2, y + h * 3 // 5
    cv.circle(cx, cy, w // 8, (255, 255, 255))
    cv.circle(cx, cy, w // 8, (205, 45, 55), fill=False)
    cv.rect(cx - 3, cy - 10, 6, 20, (205, 45, 55))
    cv.rect(cx - 10, cy - 3, 20, 6, (205, 45, 55))


def scene_bridge(cv, x, y, w, h):
    """A long suspension bridge over water, hit amidships: the deck is
    broken at the centre, smoke and flame rise from the gap, and the
    train that should cross it stands stopped on the near span."""
    cv.vgrad(x, y, w, h * 2 // 3, (150, 190, 228), (222, 240, 250))
    wy = y + h * 2 // 3
    cv.rect(x, wy, w, h // 3, (66, 110, 156))
    for i in range(4):
        wx = x + 6 + i * (w // 4)
        cv.polyline([(wx, wy + h // 7), (wx + 9, wy + h // 7 - 4),
                     (wx + 18, wy + h // 7)], (190, 224, 246), 2)
    deck_y = wy - h // 8
    gap0 = x + (w * 44) // 100
    gap1 = x + (w * 57) // 100
    # towers
    for tx in (x + w // 4, x + w * 3 // 4):
        cv.rect(tx - 3, y + h // 6, 6, deck_y + 6 - y - h // 6,
                (150, 96, 70))
    # suspension cables: two catenary runs per tower (kept from the
    # intact bridge - the smoke below hides where the blast cut them)
    for side in range(2):
        tx = x + w // 4 if side == 0 else x + w * 3 // 4
        other = x if side == 0 else x + w
        mid = x + w // 2
        for t_i in range(25):
            t = t_i / 24.0
            px = int(tx + (mid - tx) * t)
            py = int((y + h // 6) + (deck_y - (y + h // 6)) * (t * t))
            cv.set(px, py, (90, 60, 44))
            cv.set(px, py + 1, (90, 60, 44))
            qx = int(tx + (other - tx) * t)
            qy = int((y + h // 6) + (deck_y - (y + h // 6))
                     * (1 - (1 - t) * (1 - t)))
            cv.set(qx, qy, (90, 60, 44))
            cv.set(qx, qy + 1, (90, 60, 44))
    # the deck, in two pieces with jagged broken ends at the gap
    cv.rect(x, deck_y, gap0 - x, 5, (120, 76, 56))
    cv.rect(gap1, deck_y, x + w - gap1, 5, (120, 76, 56))
    cv.poly([(gap0 - 5, deck_y), (gap0 + 2, deck_y + 2), (gap0 - 3, deck_y + 5)],
            (90, 56, 40))
    cv.poly([(gap1 + 5, deck_y), (gap1 - 2, deck_y + 2), (gap1 + 3, deck_y + 5)],
            (90, 56, 40))
    # a train stopped on the left span, short of the break
    train_w = max(20, w // 5)
    train_x = gap0 - train_w - max(4, w // 20)
    train_y = deck_y - max(8, h // 9)
    train_h = max(8, h // 9)
    cv.rect(train_x, train_y, train_w, train_h, (178, 52, 52))
    cv.rect(train_x, train_y, train_w // 4, train_h, (120, 36, 40))
    for i in range(3):
        cv.rect(train_x + train_w // 3 + i * (train_w // 5),
                train_y + 2, max(3, train_w // 8), train_h // 2,
                (214, 234, 248))
    # flames licking from the broken centre
    mid = (gap0 + gap1) // 2
    fh = max(12, h // 4)
    cv.poly([(gap0 + 1, deck_y + 2), (mid, deck_y - fh), (gap1 - 1, deck_y + 2)],
            (232, 96, 30))
    cv.poly([(gap0 + 4, deck_y + 2), (mid, deck_y - fh * 2 // 3),
             (gap1 - 4, deck_y + 2)], (246, 178, 60))
    # a smoke plume rising over the gap - kept small and to the
    # right of the flames, so the broken deck stays visible
    _cloud(cv, mid + w // 9, deck_y - fh - max(4, h // 12), w / 230,
           (104, 100, 104))
    _cloud(cv, mid + w // 5, deck_y - fh - max(7, h // 7), w / 280,
           (80, 76, 82))
    # falling debris and the splash where it lands
    for i, dx in enumerate((-6, 0, 7)):
        dy0 = deck_y + 6 + i * 3
        cv.line(mid + dx, dy0, mid + dx - 2, dy0 + max(5, h // 10),
                (70, 52, 40), 2)
    cv.polyline([(mid - 12, wy + 5), (mid - 5, wy + 1), (mid, wy + 5),
                 (mid + 5, wy + 1), (mid + 12, wy + 5)],
                (235, 246, 252), 2)


def scene_storm(cv, x, y, w, h):
    cv.vgrad(x, y, w, h * 3 // 4, (58, 66, 88), (110, 120, 140))
    gy = y + h * 3 // 4
    cv.rect(x, gy, w, h // 4, (70, 76, 84))
    # dark storm clouds
    _cloud(cv, x + w // 3, y + h // 6, w / 90, (52, 58, 74))
    _cloud(cv, x + w * 2 // 3, y + h // 5, w / 100, (44, 50, 66))
    # lightning bolt
    cx = x + w // 2
    cv.poly([(cx, y + h // 4), (cx - 7, y + h // 2), (cx - 1, y + h // 2),
             (cx - 6, y + h * 2 // 3), (cx + 8, y + h * 9 // 20),
             (cx + 1, y + h * 9 // 20)], (250, 214, 64))
    # rain streaks
    for i in range(12):
        rx = x + 4 + (i * 53) % max(1, w - 8)
        ry = y + h // 3 + (i * 31) % max(1, h // 3)
        cv.line(rx, ry, rx - 3, ry + 7, (170, 196, 226), 1)
    # transmission tower leaning, wires down
    tx = x + w * 4 // 5
    cv.line(tx, gy, tx - 8, gy - h // 3, INK, 2)
    cv.line(tx - 8, gy - h // 3, tx - 18, gy - h // 3 + 3, INK, 2)
    cv.line(tx - 8, gy - h // 3, tx + 2, gy - h // 3 + 3, INK, 2)
    cv.polyline([(tx - 18, gy - h // 3 + 3), (tx - 10, gy - h // 6),
                 (tx - 14, gy - 2)], (40, 42, 50), 1)


def scene_missile(cv, x, y, w, h):
    """Riyadh at dusk: a tower skyline, one tower with an arched top,
    and the bright streak of falling missile debris over the city."""
    gy = _sky(cv, x, y, w, h, (52, 62, 108), (196, 116, 84),
              (38, 36, 48), ground_h=max(5, h // 9))
    # the debris streak, high right falling toward the towers, with a
    # pale smoke trail curling behind its glowing head
    hx, hy = x + (w * 56) // 100, y + (h * 40) // 100
    tx, ty = x + (w * 94) // 100, y + (h * 6) // 100
    cv.line(tx, ty, hx + 6, hy - 4, (196, 188, 190), 3)
    cv.line(tx - 8, ty + 5, hx + 2, hy - 7, (150, 142, 148), 2)
    cv.line(tx, ty, hx, hy, (250, 224, 150), 3)
    cv.circle(hx, hy, max(3, h // 16), (252, 190, 90))
    # smaller fragments tumbling below the head, with spark dots
    for i, (dx, dy) in enumerate(((-14, 12), (-4, 18), (7, 13))):
        px, py = hx + dx * w // 160, hy + dy * h // 64
        cv.rect(px, py, 4, 3, (60, 48, 44))
        cv.set(px - 3, py - 3, (250, 190, 90))
        cv.set(px + 6, py + 4, (250, 190, 90))
    # skyline silhouette: plain blocks plus one arched tower
    base = gy + max(5, h // 9)
    blocks = ((2, 34), (22, 48), (70, 40), (88, 30))
    for bx_pc, bh_pc in blocks:
        bw2 = max(10, w // 7)
        bx = x + (w * bx_pc) // 100
        bh = (h * bh_pc) // 100
        cv.rect(bx, base - bh, bw2, bh, (30, 30, 44))
        for wy2 in range(base - bh + 4, base - 5, 8):
            cv.rect(bx + 3, wy2, 3, 4, (255, 216, 120))
    # the arched tower, centre: two legs and a beam, sky in the arch
    tw = max(14, w // 6)
    tx0 = x + (w * 42) // 100
    th = (h * 62) // 100
    cv.rect(tx0, base - th, tw // 3, th, (30, 30, 44))
    cv.rect(tx0 + tw * 2 // 3, base - th, tw // 3, th, (30, 30, 44))
    cv.rect(tx0, base - th, tw, th // 4, (30, 30, 44))
    # smoke puff where an earlier fragment struck a rooftop, far right
    _cloud(cv, x + (w * 88) // 100, base - (h * 36) // 100, w / 210,
           (120, 112, 116))


def scene_envoy(cv, x, y, w, h):
    """An embassy send-off: a flat-roofed mission building, its flag
    flying lowered on the pole, and the envoy walking away with a
    suitcase toward the gate."""
    gy = _sky(cv, x, y, w, h, (168, 204, 236), (230, 240, 250),
              (178, 158, 120))
    # mission building, left half: flat roof, door, shaded windows
    bw = (w * 48) // 100
    bh = (h * 58) // 100
    bx = x + (w * 4) // 100
    cv.rect(bx, gy - bh, bw, bh, (238, 232, 216))
    cv.rect(bx - 3, gy - bh - 4, bw + 6, 5, (150, 96, 70))
    cv.rect(bx + bw // 2 - 4, gy - 12, 8, 12, (110, 74, 50))
    for i in range(3):
        cv.rect(bx + 5 + i * (bw - 10) // 2, gy - bh + 7, 7, 8,
                (96, 130, 160))
    cv.rect(bx + 5, gy - bh + bh // 2, bw - 10, 3, (198, 178, 140))
    # a low fence running from the building to the right edge
    for fx in range(x + (w * 56) // 100, x + w - 4, 10):
        cv.rect(fx, gy - 9, 2, 9, (90, 84, 78))
    cv.rect(x + (w * 56) // 100, gy - 8, w - (w * 56) // 100 - 4, 2,
            (90, 84, 78))
    # flagpole with the flag lowered to half mast: green, white and
    # black bands with the red band at the hoist
    px = x + (w * 64) // 100
    pole_top = y + (h * 8) // 100
    cv.line(px, gy, px, pole_top, INK, 2)
    cv.circle(px, pole_top - 1, 2, (198, 160, 60))
    fw, fh = max(16, w // 6), max(9, h // 5)
    fy = gy - (h * 46) // 100
    cv.rect(px + 1, fy, fw, fh // 3, (44, 140, 84))
    cv.rect(px + 1, fy + fh // 3, fw, fh // 3, (244, 244, 246))
    cv.rect(px + 1, fy + 2 * (fh // 3), fw, fh - 2 * (fh // 3),
            (36, 36, 40))
    cv.rect(px + 1, fy, fw // 4, fh, (198, 52, 60))
    # the envoy himself, right of the pole: dark suit, one suitcase
    ex = x + (w * 84) // 100
    cv.circle(ex, gy - (h * 34) // 100, max(3, h // 14), (238, 198, 160))
    cv.line(ex, gy - (h * 34) // 100 + 4, ex, gy - 3, (34, 34, 40),
            max(3, w // 48))
    cv.line(ex, gy - 3, ex - 4, gy, (34, 34, 40), 2)
    cv.line(ex, gy - 3, ex + 5, gy, (34, 34, 40), 2)
    case_x, case_y = ex + max(6, w // 22), gy - (h * 20) // 100
    cv.rect(case_x, case_y, max(9, w // 13), max(7, h // 7),
            (150, 96, 52))
    cv.rect(case_x + 2, case_y - 3, max(5, w // 26), 3, (110, 70, 38))
    cv.line(ex + 3, gy - (h * 26) // 100, case_x + 3, case_y - 2,
            (34, 34, 40), 2)


def scene_law(cv, x, y, w, h):
    """A parliament that has just passed a law: a pillared block with
    a steep green cone-roofed tower, a gavel and the signed document
    laid over the foreground."""
    gy = _sky(cv, x, y, w, h, (164, 196, 230), (228, 240, 250),
              (116, 132, 104))
    # pillared main block
    bw = (w * 72) // 100
    bx = x + (w * 6) // 100
    bh = (h * 36) // 100
    cv.rect(bx, gy - bh, bw, bh, (224, 216, 198))
    cv.rect(bx - 3, gy - bh - 3, bw + 6, 4, (148, 140, 128))
    for i in range(5):
        cxx = bx + 7 + i * (bw - 14) // 4
        cv.rect(cxx - 2, gy - bh + 4, 4, bh - 7, (246, 242, 232))
    # central tower with the steep dark-green cone roof
    tw = max(14, w // 7)
    tcx = x + w // 2
    cv.rect(tcx - tw // 2, gy - bh - (h * 22) // 100, tw, (h * 22) // 100,
            (214, 206, 188))
    cv.poly([(tcx - tw // 2 - 4, gy - bh - (h * 22) // 100),
             (tcx, gy - bh - (h * 52) // 100),
             (tcx + tw // 2 + 4, gy - bh - (h * 22) // 100)],
            (44, 106, 70))
    cv.rect(tcx - 1, gy - bh - (h * 52) // 100 - 4, 2, 5, INK)
    # the signed document, bottom right: white sheet, text lines, seal
    dw, dh = (w * 30) // 100, (h * 40) // 100
    dx, dy = x + (w * 64) // 100, y + (h * 56) // 100
    cv.rect(dx, dy, dw, dh, (252, 252, 250))
    cv.polyline([(dx, dy), (dx + dw - 1, dy), (dx + dw - 1, dy + dh - 1),
                 (dx, dy + dh - 1)], INK, 1, close=True)
    for i in range(3):
        cv.rect(dx + 4, dy + 4 + i * 5, dw - 10 - (i % 2) * 5, 2,
                (140, 140, 148))
    cv.circle(dx + dw - 8, dy + dh - 7, 4, (198, 52, 60))
    cv.circle(dx + dw - 8, dy + dh - 7, 2, (246, 205, 66))
    # the gavel, bottom left: a banded head on a short handle, held
    # over its sounding block
    hx0, hy0 = x + (w * 22) // 100, y + (h * 54) // 100
    hx1, hy1 = x + (w * 42) // 100, y + (h * 72) // 100
    cv.rect(x + (w * 24) // 100, y + (h * 82) // 100, (w * 20) // 100,
            4, (110, 74, 44))
    cv.line(x + (w * 10) // 100, y + (h * 92) // 100,
            (hx0 + hx1) // 2, (hy0 + hy1) // 2, (150, 100, 56),
            max(3, h // 13))
    cv.line(hx0, hy0, hx1, hy1, (104, 66, 36), max(6, h // 7))
    cv.line(hx0 + 3, hy0 + 1, hx1 - 3, hy1 - 1, (170, 124, 74),
            max(2, h // 18))
    cv.circle(hx0, hy0, max(3, h // 16), (104, 66, 36))
    cv.circle(hx1, hy1, max(3, h // 16), (104, 66, 36))


def scene_generic(cv, x, y, w, h):
    """Fallback: a dawn skyline - still a drawn scene, never a bare box."""
    gy = _sky(cv, x, y, w, h, (140, 170, 210), (235, 220, 180), (90, 96, 108))
    _sun(cv, x + w * 3 // 4, y + h // 4, max(5, w // 12), (248, 176, 70))
    for i, (bx, bh) in enumerate(((x + 4, h // 2), (x + w // 4, h * 3 // 5),
                                  (x + w // 2, h * 2 // 5), (x + w * 3 // 4, h // 2))):
        _building(cv, bx, gy + h // 4, w // 5, bh, (88, 96, 118), (60, 66, 84))


SCENES = {
    "summit": scene_summit,
    "court": scene_court,
    "rocket": scene_rocket,
    "cyclone": scene_cyclone,
    "flood": scene_flood,
    "chart": scene_chart,
    "fire": scene_fire,
    "vote": scene_vote,
    "parliament": scene_parliament,
    "oil": scene_oil,
    "stadium": scene_stadium,
    "plane": scene_plane,
    "ship": scene_ship,
    "volcano": scene_volcano,
    "snow": scene_snow,
    "heat": scene_heat,
    "train": scene_train,
    "chip": scene_chip,
    "protest": scene_protest,
    "health": scene_health,
    "bridge": scene_bridge,
    "storm": scene_storm,
    "missile": scene_missile,
    "envoy": scene_envoy,
    "law": scene_law,
    "generic": scene_generic,
}


def draw_scene(cv, name, x, y, w, h):
    SCENES.get(name, scene_generic)(cv, x, y, w, h)
    # thin frame so the picture reads as a picture on the page
    cv.polyline([(x, y), (x + w - 1, y), (x + w - 1, y + h - 1), (x, y + h - 1)],
                (90, 90, 96), 1, close=True)
