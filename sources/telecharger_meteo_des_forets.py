"""Archives de la Météo des forêts (niveau de danger par département et par jour, en été), dans data/meteo_des_forets/.

Source : jeu « Archives de la Météo des forêts » sur data.gouv.fr (Météo-France), depuis 2024.
Usage : python sources/telecharger_meteo_des_forets.py [année, 2025 par défaut]
"""

import sys

from commun import DATA, ressources_data_gouv, telecharger

ANNEE = int(sys.argv[1]) if len(sys.argv) > 1 else 2025

fichiers = [r for r in ressources_data_gouv("archives-de-la-meteo-des-forets") if r["title"] == f"mdf.{ANNEE}"]
if not fichiers:
    sys.exit(f"Pas d'archive Météo des forêts pour {ANNEE} (elles commencent en 2024).")
telecharger(fichiers[0]["url"], DATA / "meteo_des_forets" / f"mdf_{ANNEE}.csv.gz")
