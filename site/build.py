#!/usr/bin/env python3
"""Assemble bosnia_trip.html: inject map SVG fragment, then inline photos as data URIs."""
import base64, os, re

tpl = open("template.html").read()

if os.path.exists("map_fragment.svg"):
    tpl = tpl.replace("MAPSVG_PLACEHOLDER", open("map_fragment.svg").read())
else:
    print("WARN: map_fragment.svg missing")

for k in set(re.findall(r"\{\{(\w+)\}\}", tpl)):
    b64 = base64.b64encode(open(f"web/{k}.jpg", "rb").read()).decode()
    tpl = tpl.replace("{{%s}}" % k, "data:image/jpeg;base64," + b64)

open("bosnia_trip.html", "w").write(tpl)
left = re.findall(r"\{\{(\w+)\}\}|MAPSVG_PLACEHOLDER", open("bosnia_trip.html").read())
print("size:", round(os.path.getsize("bosnia_trip.html") / 1024 / 1024, 2), "MB; leftovers:", [x for x in left if x] or "none")
