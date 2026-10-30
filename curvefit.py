"""Fit cubic Béziers to polygon outlines (Schneider's algorithm).

A contour is split into runs at corners and at long straight edges. Straight
runs become lines; curved runs are fitted with as few cubics as the tolerance
allows.
"""
import math

import numpy as np

CORNER_DEG = 24.0
LONG_EDGE = 40.0
FIT_ERR = 0.7


def _unit(v):
    n = np.hypot(*v)
    return v / n if n > 1e-12 else v


def _dedupe(pts):
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 0.05:
            out.append(p)
    if len(out) > 1 and math.dist(out[0], out[-1]) <= 0.05:
        out.pop()
    return out


def _bezier(c, t):
    mt = 1 - t
    return (mt ** 3)[:, None] * c[0] + (3 * mt ** 2 * t)[:, None] * c[1] \
        + (3 * mt * t ** 2)[:, None] * c[2] + (t ** 3)[:, None] * c[3]


def _bezier_d1(c, t):
    mt = 1 - t
    return (3 * mt ** 2)[:, None] * (c[1] - c[0]) + (6 * mt * t)[:, None] * (c[2] - c[1]) \
        + (3 * t ** 2)[:, None] * (c[3] - c[2])


def _bezier_d2(c, t):
    mt = 1 - t
    return (6 * mt)[:, None] * (c[2] - 2 * c[1] + c[0]) + (6 * t)[:, None] * (c[3] - 2 * c[2] + c[1])


def _chord_params(pts):
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
    return d / d[-1]


def _generate(pts, u, t1, t2):
    p0, p3 = pts[0], pts[-1]
    a1 = (3 * (1 - u) ** 2 * u)[:, None] * t1
    a2 = (3 * (1 - u) * u ** 2)[:, None] * t2
    c = np.array([[np.dot(a1[i], a1[i]) for i in range(len(u))],
                  [np.dot(a1[i], a2[i]) for i in range(len(u))],
                  [np.dot(a2[i], a2[i]) for i in range(len(u))]]).sum(axis=1)
    base = ((1 - u) ** 3 + 3 * (1 - u) ** 2 * u)[:, None] * p0 + ((1 - u) * u ** 2 * 3 + u ** 3)[:, None] * p3
    tmp = pts - base
    x = np.array([np.dot(a1[i], tmp[i]) for i in range(len(u))]).sum()
    y = np.array([np.dot(a2[i], tmp[i]) for i in range(len(u))]).sum()
    det = c[0] * c[2] - c[1] * c[1]
    seg = np.linalg.norm(p3 - p0)
    if abs(det) > 1e-12:
        al, ar = (x * c[2] - y * c[1]) / det, (c[0] * y - c[1] * x) / det
    else:
        al = ar = 0
    eps = 1e-6 * seg
    if al < eps or ar < eps:
        al = ar = seg / 3
    return np.array([p0, p0 + t1 * al, p3 + t2 * ar, p3])


def _reparam(c, pts, u):
    d = _bezier(c, u) - pts
    d1, d2 = _bezier_d1(c, u), _bezier_d2(c, u)
    num = (d * d1).sum(axis=1)
    den = (d1 * d1).sum(axis=1) + (d * d2).sum(axis=1)
    den[np.abs(den) < 1e-12] = 1e-12
    return np.clip(u - num / den, 0, 1)


def _max_err(c, pts, u):
    d = ((_bezier(c, u) - pts) ** 2).sum(axis=1)
    i = int(np.argmax(d))
    return d[i], i


def _fit(pts, t1, t2, err):
    if len(pts) == 2:
        dist = np.linalg.norm(pts[1] - pts[0]) / 3
        return [np.array([pts[0], pts[0] + t1 * dist, pts[1] + t2 * dist, pts[1]])]
    u = _chord_params(pts)
    c = _generate(pts, u, t1, t2)
    e, split = _max_err(c, pts, u)
    if e < err ** 2:
        return [c]
    if e < (err * 6) ** 2:
        for _ in range(12):
            u = _reparam(c, pts, u)
            c = _generate(pts, u, t1, t2)
            e, split = _max_err(c, pts, u)
            if e < err ** 2:
                return [c]
    split = min(max(split, 1), len(pts) - 2)
    tc = _unit(pts[split - 1] - pts[split + 1])
    return _fit(pts[:split + 1], t1, tc, err) + _fit(pts[split:], -tc, t2, err)


def _straight(run, tol=0.6):
    a, b = run[0], run[-1]
    d = _unit(b - a)
    n = np.array([-d[1], d[0]])
    return bool(np.all(np.abs((run - a) @ n) < tol))


def fit_contour(points):
    """Closed polygon -> list of ('L', p) / ('C', c1, c2, p) starting after points[0]."""
    pts = np.array(_dedupe([tuple(p) for p in points]), dtype=float)
    n = len(pts)
    if n < 3:
        return pts[0], []
    nxt = np.roll(pts, -1, axis=0)
    edge = nxt - pts
    elen = np.hypot(edge[:, 0], edge[:, 1])
    dirs = edge / np.maximum(elen, 1e-12)[:, None]
    breaks = []
    for i in range(n):
        d0, d1 = dirs[i - 1], dirs[i]
        turn = math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(d0, d1))))))
        if turn > CORNER_DEG or elen[i - 1] > LONG_EDGE or elen[i] > LONG_EDGE:
            breaks.append(i)
    if len(breaks) < 2:
        breaks = sorted({0, n // 2} | set(breaks))
    start = breaks[0]
    ops = []
    for bi, s in enumerate(breaks):
        e = breaks[(bi + 1) % len(breaks)]
        idx = [(s + k) % n for k in range(((e - s) % n or n) + 1)]
        run = pts[idx]
        if len(run) == 2 or _straight(run):
            ops.append(("L", tuple(run[-1])))
            continue
        t1, t2 = _unit(run[1] - run[0]), _unit(run[-2] - run[-1])
        for c in _fit(run, t1, t2, FIT_ERR):
            ops.append(("C", tuple(c[1]), tuple(c[2]), tuple(c[3])))
    return tuple(pts[start]), ops
