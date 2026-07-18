#!/usr/bin/env python3
"""Generate inline SVG route map (countries + route + points) -> map_fragment.svg"""
import json, math, sys
sys.setrecursionlimit(50000)

# --- projection ---
LON0, LON1 = 17.15, 21.05
LAT0, LAT1 = 42.95, 45.15
W = 740
KX = math.cos(math.radians((LAT0 + LAT1) / 2))
H = round(W * (LAT1 - LAT0) / ((LON1 - LON0) * KX))

def P(lon, lat):
    x = (lon - LON0) / (LON1 - LON0) * W
    y = (LAT1 - lat) / (LAT1 - LAT0) * H
    return round(x, 1), round(y, 1)

# --- Douglas-Peucker simplify in px space ---
def dp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dmax, idx = 0, 0
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1e-9
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / L
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return dp(pts[:idx + 1], eps)[:-1] + dp(pts[idx:], eps)
    return [pts[0], pts[-1]]

def ring_to_path(ring, eps=1.2):
    pts = [P(lon, lat) for lon, lat in ring]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) >= 6:
        mid = len(pts) // 2
        pts = dp(pts[:mid + 1], eps)[:-1] + dp(pts[mid:] + [pts[0]], eps)[:-1]
    if len(pts) < 3:
        return ""
    d = f"M{pts[0][0]} {pts[0][1]}"
    for x, y in pts[1:]:
        d += f"L{x} {y}"
    return d + "Z"

def country_path(iso):
    gj = json.load(open(f"geo_{iso}_hi.json"))
    paths = []
    for f in gj["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            outer = poly[0]
            # skip rings entirely outside bbox
            if all(not (LON0 - .5 < lon < LON1 + .5 and LAT0 - .5 < lat < LAT1 + .5) for lon, lat in outer):
                continue
            p = ring_to_path(outer)
            if p:
                paths.append(p)
    return " ".join(paths)

# --- data: points (verified) ---
PTS = {}  # name -> (lon, lat)
for name, lat, lon in json.load(open("coords.json")):
    PTS[name] = (lon, lat)

def line(names, eps=0):
    pts = [P(*PTS[n]) for n in names]
    d = f"M{pts[0][0]} {pts[0][1]}"
    for x, y in pts[1:]:
        d += f"L{x} {y}"
    return d

# route legs
leg_south = line(["belgrade", "cacak", "pozega", "uzice", "mokra_gora", "visegrad", "rogatica", "sokolac", "sarajevo"])
leg_mount = line(["sarajevo", "hadzici", "babin_do", "umoljani", "lukomir"])
leg_konjic = line(["lukomir", "umoljani", "babin_do", "hadzici", "tarcin", "konjic", "boracko"])
leg_back1 = line(["boracko", "konjic", "tarcin", "hadzici", "sarajevo"])
leg_north = line(["sarajevo", "sokolac", "vlasenica", "zvornik", "loznica", "sabac", "belgrade"])
rail = line(["sarajevo", "hadzici", "tarcin", "ivan", "konjic", "jab_lake", "jablanica", "neretva_bend", "salakovac", "mostar"])
taxi = line(["mostar", "blagaj"])

# numbered stops: (key, label, dx, dy anchor tweaks)
STOPS = [
    ("belgrade", "Белград", "старт · финал Д9", -12, -4, "end"),
    ("mokra_gora", "Мокра Гора", "Д1", 8, -12, "start"),
    ("visegrad", "Вишеград", "Д1", -6, -14, "end"),
    ("sarajevo", "Сараево", "Д1-3 · Д7-9", 12, -10, "start"),
    ("umoljani", "Умоляни", "Д4", 13, -6, "start"),
    ("lukomir", "Лукомир", "Д4-6", -13, 16, "end"),
    ("konjic", "Коньиц", "Д6-7", -13, -16, "end"),
    ("boracko", "Борачко оз.", "Д6-7", 13, 12, "start"),
    ("mostar", "Мостар", "Д8, поезд", -13, -8, "end"),
    ("blagaj", "Благай", "Д8", 13, 6, "start"),
]

svg = []
svg.append(f'<svg width="100%" viewBox="0 0 {W} {H}" role="img" aria-label="Карта маршрута" xmlns="http://www.w3.org/2000/svg">')
svg.append('<title>Карта маршрута по Боснии</title>')
# countries
svg.append(f'<path d="{country_path("HRV")}" fill="none" stroke="var(--muted)" stroke-opacity="0.45" stroke-width="1.3"/>')
svg.append(f'<path d="{country_path("MNE")}" fill="none" stroke="var(--muted)" stroke-opacity="0.45" stroke-width="1.3"/>')
svg.append(f'<path d="{country_path("SRB")}" fill="none" stroke="var(--muted)" stroke-opacity="0.45" stroke-width="1.3"/>')
svg.append(f'<path d="{country_path("BIH")}" fill="var(--accent)" fill-opacity="0.07" stroke="var(--accent)" stroke-opacity="0.5" stroke-width="1.6"/>')
for nm, lon, lat in (("БОСНИЯ И ГЕРЦЕГОВИНА", 17.85, 44.55), ("СЕРБИЯ", 20.35, 44.35), ("ЧЕРНОГОРИЯ", 19.05, 43.05), ("ХОРВАТИЯ", 17.45, 45.02)):
    x, y = P(lon, lat)
    svg.append(f'<text x="{x}" y="{y}" font-size="11" letter-spacing="2" fill="var(--muted)" opacity="0.65" text-anchor="middle">{nm}</text>')
# route: car legs
for d in (leg_south, leg_mount, leg_konjic, leg_back1, leg_north):
    svg.append(f'<path d="{d}" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>')
# rail dashed copper
svg.append(f'<path d="{rail}" fill="none" stroke="var(--copper)" stroke-width="2.2" stroke-dasharray="7 5" stroke-linejoin="round" stroke-linecap="round"/>')
svg.append(f'<path d="{taxi}" fill="none" stroke="var(--copper)" stroke-width="1.6" stroke-dasharray="2 4" stroke-linecap="round"/>')
# direction labels on legs
def midlabel(names, text, dy=-6):
    a, b = PTS[names[0]], PTS[names[1]]
    x, y = P((a[0]+b[0])/2, (a[1]+b[1])/2)
    return f'<text x="{x}" y="{y+dy}" font-size="11" fill="var(--muted)" text-anchor="middle">{text}</text>'
svg.append(midlabel(["belgrade", "cacak"], "Д1 →", -8))
svg.append(midlabel(["vlasenica", "zvornik"], "← Д9"))
# stops
for i, (k, name, days, dx, dy, anchor) in enumerate(STOPS, 1):
    x, y = P(*PTS[k])
    svg.append(f'<circle cx="{x}" cy="{y}" r="9" fill="var(--accent)"/>')
    svg.append(f'<text x="{x}" y="{y}" font-size="10.5" font-weight="700" fill="var(--ground)" text-anchor="middle" dominant-baseline="central">{i}</text>')
    ly = y + dy
    svg.append(f'<text x="{x+dx}" y="{ly}" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="{anchor}">{name} <tspan fill="var(--muted)" font-weight="400" font-size="10">· {days}</tspan></text>')
# border crossings
for k, label in (("kotroman", "граница Котроман"), ("mali_zvornik", "граница М. Зворник")):
    if k in PTS:
        x, y = P(*PTS[k])
        svg.append(f'<rect x="{x-3.5}" y="{y-3.5}" width="7" height="7" fill="none" stroke="var(--muted)" stroke-width="1.4" transform="rotate(45 {x} {y})"/>')
        lx2, ly2, anch = (x - 8, y + 16, "end") if k == "kotroman" else (x + 9, y - 8, "start")
        svg.append(f'<text x="{lx2}" y="{ly2}" font-size="10" fill="var(--muted)" text-anchor="{anch}">{label}</text>')
# legend
lx, ly = 26, 36
svg.append(f'<rect x="{lx-10}" y="{ly-18}" width="196" height="74" rx="8" fill="var(--card)" stroke="var(--line)"/>')
svg.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+34}" y2="{ly}" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round"/>')
svg.append(f'<text x="{lx+42}" y="{ly+4}" font-size="11.5" fill="var(--ink)">машина</text>')
svg.append(f'<line x1="{lx}" y1="{ly+20}" x2="{lx+34}" y2="{ly+20}" stroke="var(--copper)" stroke-width="2.2" stroke-dasharray="7 5" stroke-linecap="round"/>')
svg.append(f'<text x="{lx+42}" y="{ly+24}" font-size="11.5" fill="var(--ink)">поезд (Д8, туда-обратно)</text>')
svg.append(f'<circle cx="{lx+6}" cy="{ly+40}" r="7" fill="var(--accent)"/>')
svg.append(f'<text x="{lx+42}" y="{ly+44}" font-size="11.5" fill="var(--ink)">точки маршрута</text>')
svg.append('</svg>')

open("map_fragment.svg", "w").write("\n".join(svg))
print(f"map_fragment.svg written, {W}x{H}, {len('.'.join(svg))//1024} KB")
