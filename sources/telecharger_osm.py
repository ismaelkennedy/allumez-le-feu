"""Casernes de pompiers et points d'eau incendie de Nouvelle-Aquitaine d'après OpenStreetMap, dans data/osm/.

Source : OpenStreetMap (licence ODbL) via l'API Overpass. Les données sont saisies par des bénévoles :
elles peuvent être incomplètes, à recouper avec les données officielles du SDIS et de la DFCI.
Points d'eau retenus, comme le proxy de la fiche KPI 3 : citernes, bassins, points d'aspiration et poteaux incendie.
Usage : python sources/telecharger_osm.py
"""

import json
import urllib.parse

import pandas as pd

from commun import DATA, telecharger

REQUETE = """
[out:json][timeout:300];
area["ref:INSEE"="75"]["admin_level"="4"]->.na;
(
  nwr["amenity"="fire_station"](area.na);
  nwr["emergency"~"^(water_tank|suction_point|fire_water_pond|fire_hydrant)$"](area.na);
);
out center tags;
"""

reponse = telecharger(
    "https://overpass-api.de/api/interpreter", donnees=urllib.parse.urlencode({"data": REQUETE}).encode()
)
lignes = []
for e in json.loads(reponse)["elements"]:
    position = e if "lat" in e else e["center"]  # un bâtiment ou un bassin a un centre, pas une position
    caserne = e["tags"].get("amenity") == "fire_station"
    lignes.append(
        {
            "categorie": "caserne" if caserne else "point d'eau",
            "type": "fire_station" if caserne else e["tags"]["emergency"],
            "nom": e["tags"].get("name", ""),
            "lat": position["lat"],
            "lon": position["lon"],
        }
    )

osm = pd.DataFrame(lignes)
(DATA / "osm").mkdir(parents=True, exist_ok=True)
osm.to_csv(DATA / "osm" / "secours_nouvelle_aquitaine.csv", index=False)
print("data/osm/secours_nouvelle_aquitaine.csv :", osm.groupby("type").size().to_dict())
