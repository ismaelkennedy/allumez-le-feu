"""Temps de trajet par la route entre chaque commune touchée par un feu et la caserne la plus proche, dans data/osrm/.

C'est une estimation du délai d'arrivée des pompiers, en attendant les vrais délais d'intervention du SDIS
(qui comptent aussi le traitement de l'alerte et le départ de la caserne). Itinéraire en voiture sur les routes
d'OpenStreetMap : un camion roule moins vite sur les pistes forestières.
Source : serveur de démonstration OSRM (router.project-osrm.org), à utiliser avec modération.
À lancer après telecharger_geo.py et telecharger_osm.py, avec l'export BDIFF dans data/Incendies.csv.
Usage : python sources/calculer_temps_trajet.py
"""

import json
import time

import numpy as np
import pandas as pd

from commun import DATA, RACINE, telecharger

CANDIDATES = 3  # les 3 casernes les plus proches à vol d'oiseau, départagées par la route
PAQUET = 20  # communes par requête : le serveur de démonstration limite le nombre de points

feux = pd.read_csv(DATA / "Incendies.csv", sep=";", skiprows=2, dtype={"Code INSEE": str})
communes = pd.read_csv(RACINE / "main" / "geo" / "communes-nouvelle-aquitaine.csv", dtype={"Code INSEE": str})
communes = communes[communes["Code INSEE"].isin(feux["Code INSEE"])].reset_index(drop=True)
osm = pd.read_csv(DATA / "osm" / "secours_nouvelle_aquitaine.csv")
casernes = osm[osm["categorie"] == "caserne"].reset_index(drop=True)

dlat = communes["lat"].to_numpy()[:, None] - casernes["lat"].to_numpy()[None, :]
dlon = (communes["lon"].to_numpy()[:, None] - casernes["lon"].to_numpy()[None, :]) * np.cos(
    np.radians(communes["lat"].to_numpy())
)[:, None]
candidates = np.argsort(dlat**2 + dlon**2, axis=1)[:, :CANDIDATES]

lignes = []
for debut in range(0, len(communes), PAQUET):
    lot = communes.iloc[debut : debut + PAQUET]
    stations = sorted(set(candidates[debut : debut + PAQUET].ravel()))
    points = [*zip(casernes.loc[stations, "lon"], casernes.loc[stations, "lat"]), *zip(lot["lon"], lot["lat"])]
    coordonnees = ";".join(f"{lon:.5f},{lat:.5f}" for lon, lat in points)
    sources = ";".join(map(str, range(len(stations))))
    destinations = ";".join(map(str, range(len(stations), len(points))))
    reponse = json.loads(
        telecharger(
            f"https://router.project-osrm.org/table/v1/driving/{coordonnees}"
            f"?sources={sources}&destinations={destinations}&annotations=duration,distance"
        )
    )
    # None (pas d'itinéraire) devient NaN, puis l'infini pour ne jamais être retenu.
    duree = np.nan_to_num(np.array(reponse["durations"], dtype=float), nan=np.inf)
    distance = np.array(reponse["distances"], dtype=float)
    for j, code in enumerate(lot["Code INSEE"]):
        lignes_candidates = [stations.index(c) for c in candidates[debut + j]]
        i = min(lignes_candidates, key=lambda k: duree[k, j])
        if np.isfinite(duree[i, j]):
            lignes.append(
                {
                    "Code INSEE": code,
                    "caserne": casernes.loc[stations[i], "nom"],
                    "km_route": round(distance[i, j] / 1000, 1),
                    "minutes": round(duree[i, j] / 60, 1),
                }
            )
    print(f"{min(debut + PAQUET, len(communes))}/{len(communes)} communes")
    time.sleep(1)  # serveur de démonstration : pas plus d'une requête par seconde

trajets = pd.DataFrame(lignes)
(DATA / "osrm").mkdir(parents=True, exist_ok=True)
trajets.to_csv(DATA / "osrm" / "temps_trajet_communes.csv", index=False)
print(
    f"data/osrm/temps_trajet_communes.csv : {len(trajets)} communes, "
    f"trajet médian {trajets['minutes'].median():.0f} min, le plus long {trajets['minutes'].max():.0f} min"
)
