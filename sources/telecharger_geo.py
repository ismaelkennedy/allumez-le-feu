"""Contours de la Nouvelle-Aquitaine et centre de ses communes, dans main/geo/ (suivi par Git).

Sources : france-geojson (contours IGN simplifiés) et geo.api.gouv.fr (communes).
Usage : python sources/telecharger_geo.py
"""

import json

import pandas as pd

from commun import RACINE, telecharger

GEO = RACINE / "main" / "geo"
FRANCE_GEOJSON = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions/nouvelle-aquitaine/"

for nom in ("region-nouvelle-aquitaine", "departements-nouvelle-aquitaine"):
    telecharger(f"{FRANCE_GEOJSON}{nom}.geojson", GEO / f"{nom}.geojson")

communes = json.loads(telecharger("https://geo.api.gouv.fr/communes?codeRegion=75&fields=code,centre&format=json"))
pd.DataFrame(
    {
        "Code INSEE": [c["code"] for c in communes],
        "lon": [c["centre"]["coordinates"][0] for c in communes],
        "lat": [c["centre"]["coordinates"][1] for c in communes],
    }
).to_csv(GEO / "communes-nouvelle-aquitaine.csv", index=False)
print(f"main/geo/communes-nouvelle-aquitaine.csv ({len(communes)} communes)")
