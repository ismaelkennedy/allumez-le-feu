"""Chargement des données, partagé par la carte et le tableau de bord."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

ICI = Path(__file__).parent
DATA = ICI.parent / "data"  # rempli par les scripts du dossier sources/ (voir sources/README.md)
FEUX = DATA / "Incendies.csv"  # export BDIFF, téléchargé à la main


@st.cache_data
def charger_feux():
    """Feux BDIFF de Nouvelle-Aquitaine, placés au centre de leur commune."""
    # Export BDIFF : 2 lignes de métadonnées avant les en-têtes, séparateur « ; ».
    feux = pd.read_csv(
        FEUX, sep=";", skiprows=2, dtype={"Département": str, "Code INSEE": str}, parse_dates=["Date de première alerte"]
    )
    communes = pd.read_csv(ICI / "geo" / "communes-nouvelle-aquitaine.csv", dtype={"Code INSEE": str})
    # Jointure interne : ne garde que les communes de Nouvelle-Aquitaine (et écarte les codes INSEE inconnus).
    feux = feux.merge(communes, on="Code INSEE").reset_index(names="id")
    feux["ha"] = feux["Surface parcourue (m2)"] / 10_000
    return feux


@st.cache_data
def charger_trajets():
    """Temps de trajet par la route depuis la caserne la plus proche, par commune (sources/calculer_temps_trajet.py)."""
    chemin = DATA / "osrm" / "temps_trajet_communes.csv"
    return pd.read_csv(chemin, dtype={"Code INSEE": str}) if chemin.exists() else None


@st.cache_data
def charger_secours():
    """Casernes et points d'eau incendie d'après OpenStreetMap."""
    chemin = DATA / "osm" / "secours_nouvelle_aquitaine.csv"
    return pd.read_csv(chemin) if chemin.exists() else None


@st.cache_data
def charger_meteo_departements():
    """Température maximale et humidité minimale, moyennes des stations de chaque département, jour par jour."""

    def lire(groupe, colonne):
        fichiers = sorted((DATA / "meteo").glob(f"Q_*_{groupe}.csv.gz"))
        colonnes = ["NUM_POSTE", "AAAAMMJJ", colonne]
        if not fichiers:
            return pd.DataFrame(columns=colonnes)
        return pd.concat(pd.read_csv(f, sep=";", usecols=colonnes, dtype={"NUM_POSTE": str}) for f in fichiers)

    meteo = lire("RR-T-Vent", "TX").merge(lire("autres-parametres", "UN"), on=["NUM_POSTE", "AAAAMMJJ"], how="outer")
    meteo["Département"] = meteo["NUM_POSTE"].str[:2]  # les 2 premiers chiffres du numéro de station
    return meteo.groupby(["Département", "AAAAMMJJ"])[["TX", "UN"]].mean().reset_index()


def km_au_plus_proche(lat, lon, points):
    """Distance (km) de chaque position au plus proche des `points` (colonnes lat, lon). Approximation plane."""
    plat, plon = points["lat"].to_numpy(), points["lon"].to_numpy()
    distances = np.empty(len(lat))
    for debut in range(0, len(lat), 100):  # par paquets : 500 feux × 30 000 poteaux ne tiennent pas en mémoire d'un coup
        la, lo = lat[debut : debut + 100, None], lon[debut : debut + 100, None]
        dlon = (lo - plon[None, :]) * np.cos(np.radians(la))
        distances[debut : debut + 100] = 111 * np.sqrt((la - plat[None, :]) ** 2 + dlon**2).min(axis=1)
    return distances


# 1 degré de latitude ≈ 111 km.
assert abs(km_au_plus_proche(np.array([45.0]), np.array([0.0]), pd.DataFrame({"lat": [46.0, 50.0], "lon": [0.0, 0.0]}))[0] - 111) < 1e-9
