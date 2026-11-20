"""Outils partagés par les scripts de téléchargement des sources."""

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data"  # ignoré par Git : chacun relance les scripts chez lui
DEPARTEMENTS_NA = ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"]


def telecharger(url, chemin=None, donnees=None):
    """Télécharge `url` (en POST si `donnees`) et l'écrit dans `chemin`, ou renvoie son contenu.

    Réessaie quand le serveur est surchargé (Overpass et Météo-France le sont souvent).
    """
    requete = urllib.request.Request(url, data=donnees, headers={"User-Agent": "allumez-le-feu (projet etudiant)"})
    for essai in range(4):
        try:
            with urllib.request.urlopen(requete, timeout=300) as reponse:
                contenu = reponse.read()
            break
        except urllib.error.HTTPError as erreur:
            if erreur.code not in (429, 502, 503, 504) or essai == 3:
                raise
            print(f"Serveur occupé ({erreur.code}), nouvel essai dans {30 * (essai + 1)} s…")
            time.sleep(30 * (essai + 1))
    if chemin is None:
        return contenu
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_bytes(contenu)
    print(f"{chemin.relative_to(RACINE)} ({len(contenu) // 1024} Ko)")
    return contenu


def ressources_data_gouv(jeu):
    """Liste des fichiers d'un jeu de données data.gouv.fr (titre, url…), d'après son identifiant."""
    return json.loads(telecharger(f"https://www.data.gouv.fr/api/1/datasets/{jeu}/"))["resources"]
