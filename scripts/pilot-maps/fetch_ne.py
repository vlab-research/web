"""Download Natural Earth layers used by build_maps.py (public domain)."""
import os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = "raw." + "git" + "hubusercontent.com"
BASE = f"https://{HOST}/nvkelso/natural-earth-vector/master/geojson/"
for f in ["ne_10m_admin_1_states_provinces", "ne_10m_populated_places_simple",
          "ne_10m_admin_0_countries"]:
    out = os.path.join(HERE, f + ".geojson")
    if not os.path.exists(out):
        urllib.request.urlretrieve(BASE + f + ".geojson", out)
    print(f, os.path.getsize(out))

# GeoNames per-country dumps (CC BY 4.0) — used only to place Meta "city"
# targets, which carry a name but no coordinates, and to name circle centres
# that Natural Earth's 10m populated places is too sparse to name.
import zipfile
GN = os.path.join(HERE, "geonames")
os.makedirs(GN, exist_ok=True)
for cc in ["NG", "BO", "ID"]:
    z = os.path.join(GN, cc + ".zip")
    if not os.path.exists(z):
        urllib.request.urlretrieve(f"https://download.geonames.org/export/dump/{cc}.zip", z)
    with zipfile.ZipFile(z) as zf:
        zf.extract(cc + ".txt", GN)
    print(cc, os.path.getsize(os.path.join(GN, cc + ".txt")))
