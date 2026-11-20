"""Carte des forêts de Nouvelle-Aquitaine, classée par inflammabilité de la végétation, dans data/ign/.

Source : IGN, BD Forêt V2 (2006-2019), servie en image par la Géoplateforme (flux WMS LANDCOVER.FORESTINVENTORY.V2).
L'image IGN distingue 32 types de végétation. Chaque pixel est rattaché au type de sa légende officielle,
puis regroupé en 3 niveaux : résineux et landes (les plus inflammables), forêts mélangées, feuillus (les moins).
Image d'environ 300 m par pixel : assez pour voir les massifs à l'échelle de la région, pas une parcelle.
Usage : python sources/telecharger_foret.py
"""

import io
import json
import math

import numpy as np
from PIL import Image

from commun import DATA, telecharger

BORNES = [-1.9, 42.7, 2.7, 47.3]  # ouest, sud, est, nord : la région avec une marge
COUCHE = "LANDCOVER.FORESTINVENTORY.V2"
# Groupes, dans l'ordre des 32 cases de la légende IGN (de haut en bas), du plus au moins inflammable.
GROUPES = [
    ("Résineux et landes", "#006d2c", [0, *range(9, 23), 25, 27, 30, 31]),
    ("Forêts mélangées", "#31a354", [23, 24, 28]),
    ("Feuillus", "#74c476", [*range(1, 9), 26, 29]),
]


def mercator(lon, lat):
    rayon = 6378137
    return rayon * math.radians(lon), rayon * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


# Couleurs de la légende officielle : on lit le milieu de chaque case de couleur.
legende = np.asarray(
    Image.open(io.BytesIO(telecharger(f"https://data.geopf.fr/annexes/ressources/legendes/{COUCHE}-legend.png"))).convert("RGBA")
).astype(int)
colonne = legende[:, 27]
pleine = (colonne[:, 3] > 200) & (colonne[:, :3].min(axis=1) < 235)
bords = np.flatnonzero(np.diff(np.r_[0, pleine.astype(int), 0]))
cases = [colonne[(debut + fin) // 2, :3] for debut, fin in zip(bords[::2], bords[1::2])]
assert len(cases) == 32, f"{len(cases)} cases de couleur dans la légende IGN au lieu de 32 : la légende a changé"

# Image en Web Mercator, la projection de la carte de l'app : elle se superpose sans déformation.
x0, y0 = mercator(BORNES[0], BORNES[1])
x1, y1 = mercator(BORNES[2], BORNES[3])
largeur = 1200
hauteur = round(largeur * (y1 - y0) / (x1 - x0))
image = telecharger(
    "https://data.geopf.fr/wms-r?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap"
    f"&LAYERS={COUCHE}&STYLES=&CRS=EPSG:3857&BBOX={x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}"
    f"&WIDTH={largeur}&HEIGHT={hauteur}&FORMAT=image/png&TRANSPARENT=true"
)
pixels = np.asarray(Image.open(io.BytesIO(image)).convert("RGBA"))

# Chaque couleur distincte de l'image va au type de légende le plus proche, puis à son groupe.
couleurs, inverse = np.unique(pixels[..., :3].reshape(-1, 3), axis=0, return_inverse=True)
type_proche = np.argmin(((couleurs[:, None, :].astype(int) - np.array(cases)[None, :, :]) ** 2).sum(axis=2), axis=1)
groupe_du_type = np.empty(32, dtype=int)
for g, (_, _, types) in enumerate(GROUPES):
    groupe_du_type[types] = g
assert sorted(t for _, _, types in GROUPES for t in types) == list(range(32)), "chaque type doit avoir un seul groupe"
groupe = groupe_du_type[type_proche][inverse.ravel()].reshape(pixels.shape[:2])

teintes = np.array([[int(c[k : k + 2], 16) for k in (1, 3, 5)] for _, c, _ in GROUPES])
sortie = np.zeros_like(pixels)
sortie[..., :3] = teintes[groupe]
sortie[..., 3] = np.where(pixels[..., 3] >= 128, 255, 0)  # bords flous et zones sans forêt : transparents

(DATA / "ign").mkdir(parents=True, exist_ok=True)
Image.fromarray(sortie.astype(np.uint8)).save(DATA / "ign" / "foret_nouvelle_aquitaine.png", optimize=True)
(DATA / "ign" / "foret.json").write_text(
    json.dumps({"bornes": BORNES, "classes": [{"nom": n, "couleur": c} for n, c, _ in GROUPES]}, ensure_ascii=False),
    encoding="utf-8",
)
parts = np.bincount(groupe[sortie[..., 3] > 0], minlength=3) / max((sortie[..., 3] > 0).sum(), 1)
print("data/ign/foret_nouvelle_aquitaine.png :", {n: f"{p:.0%}" for (n, _, _), p in zip(GROUPES, parts)})
