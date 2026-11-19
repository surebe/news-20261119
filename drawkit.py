"""drawkit.py - a tiny deterministic raster drawing kit (pure stdlib).

Written for the news-image entry: no PIL, no network, no randomness.
Everything renders into an RGB framebuffer and is encoded as PNG with
zlib/struct only. All iteration orders are fixed, so two runs of the
same program produce byte-identical files.
"""

import struct
import zlib

# ---------------------------------------------------------------- PNG


def _chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png(pixels, width, height):
    """pixels: bytearray of width*height*3 RGB bytes. Returns PNG bytes.

    Each scanline picks, deterministically, the filter (None/Sub/Up)
    with the smallest sum of absolute signed byte values, which keeps
    flat illustration areas small.
    """
    stride = width * 3
    raw = bytearray()
    prev = bytes(stride)
    for y in range(height):
        row = bytes(pixels[y * stride:(y + 1) * stride])
        best = b"\x00" + row
        best_score = sum(b if b < 128 else 256 - b for b in row)
        sub = bytearray(stride)
        for i in range(stride):
            left = row[i - 3] if i >= 3 else 0
            sub[i] = (row[i] - left) & 0xFF
        score = sum(b if b < 128 else 256 - b for b in sub)
        if score < best_score:
            best = b"\x01" + bytes(sub)
            best_score = score
        up = bytearray(stride)
        for i in range(stride):
            up[i] = (row[i] - prev[i]) & 0xFF
        score = sum(b if b < 128 else 256 - b for b in up)
        if score < best_score:
            best = b"\x02" + bytes(up)
        raw += best
        prev = row
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------- canvas


class Canvas:
    def __init__(self, width, height, bg=(255, 255, 255)):
        self.w = width
        self.h = height
        self.px = bytearray(bytes(bg) * (width * height))

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def blend(self, x, y, color, alpha):
        """alpha 0..255: color over current pixel."""
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            a = alpha
            ia = 255 - a
            self.px[i] = (self.px[i] * ia + color[0] * a) // 255
            self.px[i + 1] = (self.px[i + 1] * ia + color[1] * a) // 255
            self.px[i + 2] = (self.px[i + 2] * ia + color[2] * a) // 255

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        stride = self.w * 3
        start = (y0 * self.w + x0) * 3
        for yy in range(y0, y1):
            off = start + (yy - y0) * stride
            self.px[off:off + len(row)] = row

    def vgrad(self, x, y, w, h, top, bottom):
        """Vertical linear gradient inside a rect."""
        if h <= 0:
            return
        for i in range(h):
            t = i / max(1, h - 1)
            c = (
                int(top[0] + (bottom[0] - top[0]) * t),
                int(top[1] + (bottom[1] - top[1]) * t),
                int(top[2] + (bottom[2] - top[2]) * t),
            )
            self.rect(x, y + i, w, 1, c)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = thick // 2
        while True:
            if thick == 1:
                self.set(x0, y0, color)
            else:
                self.rect(x0 - r, y0 - r, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=True):
        if r <= 0:
            return
        if fill:
            for yy in range(cy - r, cy + r + 1):
                dy = yy - cy
                span = int((r * r - dy * dy) ** 0.5)
                self.rect(cx - span, yy, span * 2 + 1, 1, color)
        else:
            # midpoint circle
            x = r
            y = 0
            err = 0
            while x >= y:
                for px, py in (
                    (cx + x, cy + y), (cx + y, cy + x), (cx - y, cy + x),
                    (cx - x, cy + y), (cx - x, cy - y), (cx - y, cy - x),
                    (cx + y, cy - x), (cx + x, cy - y),
                ):
                    self.set(px, py, color)
                y += 1
                err += 1 + 2 * y
                if 2 * (err - x) + 1 > 0:
                    x -= 1
                    err += 1 - 2 * x

    def ellipse(self, cx, cy, rx, ry, color):
        if rx <= 0 or ry <= 0:
            return
        for yy in range(cy - ry, cy + ry + 1):
            dy = (yy - cy) / ry
            if abs(dy) > 1:
                continue
            span = int(rx * (1 - dy * dy) ** 0.5)
            self.rect(cx - span, yy, span * 2 + 1, 1, color)

    def poly(self, pts, color):
        """Filled polygon via scanline over its bounding box."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0 = max(0, min(ys))
        y1 = min(self.h - 1, max(ys))
        n = len(pts)
        for yy in range(y0, y1 + 1):
            nodes = []
            for i in range(n):
                xa, ya = pts[i]
                xb, yb = pts[(i + 1) % n]
                if ya == yb:
                    continue
                if (yy >= min(ya, yb)) and (yy < max(ya, yb)):
                    nodes.append(xa + (yy - ya) * (xb - xa) / (yb - ya))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                xa = int(nodes[i])
                xb = int(nodes[i + 1])
                if xb >= xa:
                    self.rect(xa, yy, xb - xa + 1, 1, color)

    def polyline(self, pts, color, thick=1, close=False):
        seq = list(pts)
        if close and seq:
            seq.append(seq[0])
        for i in range(len(seq) - 1):
            self.line(seq[i][0], seq[i][1], seq[i + 1][0], seq[i + 1][1],
                      color, thick)

    def triangle(self, a, b, c, color):
        self.poly([a, b, c], color)
