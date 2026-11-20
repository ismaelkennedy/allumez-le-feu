"""Données climatologiques quotidiennes Météo-France des 12 départements, dans data/meteo/.

Source : jeu « Données climatologiques de base - quotidiennes » sur data.gouv.fr. Deux fichiers par département :
RR-T-Vent (pluie, température, vent) et autres-parametres (humidité, ensoleillement, orages).
Usage : python sources/telecharger_meteo.py [année des feux, 2025 par défaut]
"""

import re
import sys

from commun import DATA, DEPARTEMENTS_NA, ressources_data_gouv, telecharger

ANNEE = int(sys.argv[1]) if len(sys.argv) > 1 else 2025

for ressource in ressources_data_gouv("donnees-climatologiques-de-base-quotidiennes"):
    # Titre du type « QUOT_departement_33_periode_2025-2026_RR-T-Vent »
    titre = re.fullmatch(
        r"QUOT_departement_(\w+)_periode_(\d{4})-(\d{4})_(RR-T-Vent|autres-parametres)", ressource["title"]
    )
    if titre and titre[1] in DEPARTEMENTS_NA and int(titre[2]) <= ANNEE <= int(titre[3]):
        telecharger(ressource["url"], DATA / "meteo" / ressource["url"].rsplit("/", 1)[1])
