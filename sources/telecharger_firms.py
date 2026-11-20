"""Points chauds détectés par satellite en France (NASA FIRMS, satellite VIIRS S-NPP), dans data/firms/.

Chaque ligne est une détection de feu actif : position, date et heure (UTC) du passage du satellite.
Plusieurs passages par jour : c'est la seule source gratuite qui montre comment un grand feu avance.
Limite : les petits feux (la plupart de ceux de la BDIFF) ne sont pas détectés.
Usage : python sources/telecharger_firms.py [année, 2025 par défaut]
"""

import sys

from commun import DATA, telecharger

ANNEE = int(sys.argv[1]) if len(sys.argv) > 1 else 2025

telecharger(
    f"https://firms.modaps.eosdis.nasa.gov/data/country/viirs-snpp/{ANNEE}/viirs-snpp_{ANNEE}_France.csv",
    DATA / "firms" / f"viirs-snpp_{ANNEE}_France.csv",
)
