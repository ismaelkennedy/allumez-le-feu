"""Tableau de bord décisionnel, construit d'après les fiches KPI du projet (KPI_fiches.docx).

La section « Redéfinir le seuil » montre d'abord ce que vaut le seuil actuel (départs de feu et surfaces brûlées
par niveau de la Météo des forêts), puis dans quelles conditions de chaleur et d'humidité les feux partent.
"""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from donnees import (
    FEUX,
    charger_feux,
    charger_meteo_departements,
    charger_meteo_des_forets,
    charger_secours,
    charger_trajets,
    km_au_plus_proche,
)

ROUGE, GRIS = "#b71c1c", "#b9c0b7"  # rouge réservé à ce qu'on veut faire ressortir, le reste en gris
NIVEAUX = {1: "1 faible", 2: "2 modéré", 3: "3 élevé", 4: "4 très élevé"}  # échelle de la Météo des forêts
DISTANCES = ([0, 2, 5, np.inf], ["moins de 2 km", "2 à 5 km", "5 km ou plus"])
TRAJETS = ([0, 10, 20, np.inf], ["moins de 10 min", "10 à 20 min", "20 min ou plus"])
TEMPERATURES = ([-np.inf, 20, 25, 30, 35, np.inf], ["moins de 20°", "20 à 25°", "25 à 30°", "30 à 35°", "35° ou plus"])
HUMIDITES = ([0, 30, 40, 50, 60, np.inf], ["moins de 30 %", "30 à 40 %", "40 à 50 %", "50 à 60 %", "60 % ou plus"])
JOURS_MINI = 10  # en dessous, une case de la grille météo (ou un niveau) n'a pas assez de jours pour un taux fiable
FEUX_MINI = 30  # en dessous, un pourcentage calculé sur ces feux est fragile


def fr(x, decimales=0):
    return f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")


def pc(part, decimales=0):
    return f"{fr(100 * part, decimales)} %"


@st.cache_data
def preparer(feux, secours, trajets):
    feux = feux.assign(AAAAMMJJ=feux["Date de première alerte"].dt.strftime("%Y%m%d").astype(int))
    if secours is not None:
        eau = secours[secours["categorie"] == "point d'eau"]
        lat, lon = feux["lat"].to_numpy(), feux["lon"].to_numpy()
        feux["km_eau"] = km_au_plus_proche(lat, lon, eau)
        feux["km_eau_massif"] = km_au_plus_proche(lat, lon, eau[eau["type"] != "fire_hydrant"])
    if trajets is not None:
        feux = feux.merge(trajets[["Code INSEE", "minutes"]], on="Code INSEE", how="left")
    return feux


def barres(valeurs, titre, *, rouges=(), horizontal=False, ordonne=False, format_valeur=",.0f", nom_valeur=""):
    """Barres grises, en rouge les catégories `rouges` ; axe des valeurs à partir de zéro.

    `valeurs` est une Series : l'index donne les catégories, dans l'ordre si `ordonne`, sinon triées par valeur.
    """
    st.markdown(f"**{titre}**")
    df = valeurs.rename_axis("categorie").reset_index(name="valeur")
    df["couleur"] = np.where(df["categorie"].isin(rouges), ROUGE, GRIS)
    axe_cat, axe_val = (alt.Y, alt.X) if horizontal else (alt.X, alt.Y)
    tri = list(df["categorie"]) if ordonne else ("-x" if horizontal else "-y")
    graphe = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            # En vertical, Vega masque les étiquettes qui se chevauchent ; en horizontal, toutes restent lisibles.
            axe_cat("categorie:N", sort=tri, title=None, axis=alt.Axis(labelAngle=0, labelLimit=220, labelOverlap=not horizontal)),
            axe_val("valeur:Q", title=nom_valeur, axis=alt.Axis(format=format_valeur, tickCount=6)),
            color=alt.Color("couleur:N", scale=None),
            tooltip=[
                alt.Tooltip("categorie:N", title=" "),
                alt.Tooltip("valeur:Q", title=nom_valeur, format=format_valeur),
            ],
        )
        .properties(height=max(220, 32 * len(df)) if horizontal else 240)
    )
    st.altair_chart(graphe, width="stretch", alt=f"Graphique en barres : {titre}")


def part_au_dessus(feux, colonne, tranches, quoi):
    """Part des feux de plus de 1 ha par tranche (distance ou temps), le message qui compare les tranches extrêmes,
    et la barre à mettre en rouge : aucune si une tranche comparée a moins de FEUX_MINI feux."""
    bornes, libelles = tranches
    groupes = (feux["ha"] > 1).groupby(pd.cut(feux[colonne], bornes, right=False, labels=libelles), observed=False)
    parts, effectifs = groupes.mean().dropna(), groupes.size()
    message, fiable = f"Part des feux de plus de 1 ha selon l'éloignement {quoi}", False
    if len(parts) >= 2 and parts.index[0] == libelles[0] and parts.index[-1] == libelles[-1]:
        message = (
            f"À {libelles[-1]} {quoi}, {pc(parts.iloc[-1])} des feux dépassent 1 ha, "
            f"contre {pc(parts.iloc[0])} à {libelles[0]}"
        )
        petite = min(libelles[0], libelles[-1], key=lambda t: effectifs[t])
        fiable = effectifs[petite] >= FEUX_MINI
        if not fiable:
            message += f" (seulement {effectifs[petite]} feux à {petite} : à confirmer)"
    parts.index = [f"{t} ({effectifs[t]} feux)" for t in parts.index]
    return parts, message, [parts.index[-1]] if fiable else []


def jours_avec_feux(jours, feux, codes):
    """Jours-départements de `jours` pris sur le territoire et l'année des feux, avec leurs départs et hectares brûlés."""
    jours = jours[jours["Département"].isin(codes) & (jours["AAAAMMJJ"] // 10000 == feux["Année"].iloc[0])]
    par_jour = feux.groupby(["Département", "AAAAMMJJ"]).agg(n=("id", "size"), ha=("ha", "sum")).reset_index()
    return jours.merge(par_jour, on=["Département", "AAAAMMJJ"], how="left").fillna({"n": 0, "ha": 0})


def par_niveau(feux, mdf, codes):
    """Départs de feu et hectares brûlés par jour, selon le niveau de la Météo des forêts prévu la veille.

    Les niveaux vus moins de JOURS_MINI jours sont écartés ; l'index donne le niveau et son nombre de jours.
    """
    jours = jours_avec_feux(mdf, feux, codes)
    niveaux = jours.groupby("niveau").agg(jours=("n", "size"), departs=("n", "mean"), surface=("ha", "mean")).reset_index()
    niveaux = niveaux[niveaux["jours"] >= JOURS_MINI]
    return niveaux.set_index(pd.Index([f"{NIVEAUX.get(n, n)} ({j} jours)" for n, j in zip(niveaux["niveau"], niveaux["jours"])]))


# 10 jours au niveau 1 sans feu, puis 10 jours au niveau 2 avec un feu de 2 ha par jour.
assert par_niveau(
    pd.DataFrame({"id": range(10), "Département": "33", "Année": 2025, "AAAAMMJJ": range(20250611, 20250621), "ha": 2.0}),
    pd.DataFrame({"Département": "33", "AAAAMMJJ": range(20250601, 20250621), "niveau": [1] * 10 + [2] * 10}),
    ["33"],
)[["departs", "surface"]].values.tolist() == [[0, 0], [1, 2]]


def grille_meteo(feux, meteo, codes):
    """Départs de feu et surface brûlée par jour, selon la température et l'humidité du jour dans le département."""
    jours = jours_avec_feux(meteo.dropna(subset=["TX", "UN"]), feux, codes)
    jours["temperature"] = pd.cut(jours["TX"], TEMPERATURES[0], right=False, labels=TEMPERATURES[1])
    jours["humidite"] = pd.cut(jours["UN"], HUMIDITES[0], right=False, labels=HUMIDITES[1])
    grille = jours.groupby(["temperature", "humidite"], observed=False).agg(jours=("n", "size"), n=("n", "sum"), ha=("ha", "sum"))
    grille = grille.reset_index()
    fiable = grille["jours"] >= JOURS_MINI
    grille["departs"] = np.where(fiable, grille["n"] / grille["jours"].clip(lower=1), np.nan)
    grille["surface"] = np.where(fiable, grille["ha"] / grille["jours"].clip(lower=1), np.nan)
    return grille, jours["n"].sum() / max(len(jours), 1), jours["ha"].sum() / max(len(jours), 1)


def carte_chaleur(grille, colonne, titre, nom_valeur, format_valeur):
    st.markdown(f"**{titre}**")
    # Domaines fixés : la grille garde toutes ses lignes et colonnes, même quand des cases sont vides.
    # Espace entre les cases plutôt qu'un contour blanc : le fond du thème (clair ou sombre) passe entre elles.
    base = alt.Chart(grille).transform_filter(f"isValid(datum.{colonne})").encode(
        alt.X("humidite:O", scale=alt.Scale(domain=HUMIDITES[1], paddingInner=0.04), title="Humidité min",
              axis=alt.Axis(labelAngle=0, labelOverlap=False, labelExpr="replace(datum.label, 'moins de ', '< ')")),
        alt.Y("temperature:O", scale=alt.Scale(domain=TEMPERATURES[1][::-1], paddingInner=0.06), title="Température max",
              axis=alt.Axis(labelOverlap=False)),
    )
    cases = base.mark_rect(cornerRadius=3).encode(
        alt.Color(f"{colonne}:Q", scale=alt.Scale(scheme="reds", zero=True), title=nom_valeur, legend=None),
        tooltip=[
            alt.Tooltip("temperature:O", title="Température"),
            alt.Tooltip("humidite:O", title="Humidité"),
            alt.Tooltip(f"{colonne}:Q", title=nom_valeur, format=format_valeur),
            alt.Tooltip("jours:Q", title="Jours-départements"),
        ],
    )
    # La valeur est écrite dans chaque case : la lecture ne dépend pas que de la couleur.
    textes = base.mark_text(fontSize=12).encode(
        alt.Text(f"{colonne}:Q", format=format_valeur),
        color=alt.condition(f"datum.{colonne} > {grille[colonne].max() / 2}", alt.value("white"), alt.value("#1d3328")),
    )
    st.altair_chart((cases + textes).properties(height=300), width="stretch", alt=f"Grille : {titre}")


def afficher(noms_departements):
    st.markdown(
        "Comment mobiliser les pompiers pendant la saison des feux 2027 pour réduire les surfaces brûlées ? "
        "Trois leviers sont étudiés : mieux prévoir les jours à risque (redéfinir le seuil de renforcement), "
        "créer des points d'eau et débroussailler."
    )
    if not FEUX.exists():
        st.info("Ajoute l'export BDIFF dans data/Incendies.csv (voir sources/README.md).")
        return
    secours, trajets = charger_secours(), charger_trajets()
    feux = preparer(charger_feux(), secours, trajets)

    gauche, droite = st.columns([2, 1])
    territoires = ["NA", *noms_departements]
    territoire = gauche.selectbox(
        "Territoire",
        territoires,
        index=territoires.index("33") if "33" in territoires else 0,
        format_func=lambda c: noms_departements.get(c, "Nouvelle-Aquitaine"),
        help="La Gironde par défaut : la commande vient du SDIS 33. La région sert à comparer.",
    )
    annee = droite.selectbox("Année", sorted(feux["Année"].unique(), reverse=True), help="Années de l'export BDIFF.")
    codes = list(noms_departements) if territoire == "NA" else [territoire]
    feux = feux[feux["Département"].isin(codes) & (feux["Année"] == annee)]
    sans_surface = feux["ha"].isna().sum()
    feux = feux.dropna(subset=["ha"])  # fiches 1 et 2 : feux sans surface exclus, comptés à part
    if feux.empty:
        st.info("Aucun départ de feu sur ce territoire cette année-là dans l'export BDIFF.")
        return
    if len(feux) < FEUX_MINI:
        st.warning(f"Seulement {len(feux)} départs de feu : les pourcentages sont fragiles.")
    estimees = (feux["Précision des surfaces"] == "Estimées").mean()

    # ---- KPI de décision (fiche 1) -------------------------------------------------------------
    with st.container(border=True):
        st.subheader("KPI de décision : surface brûlée")
        st.caption("Q3. Les dégâts diminuent-ils réellement ?")
        colonnes = st.columns(3)
        colonnes[0].metric("Surface brûlée", f"{fr(feux['ha'].sum())} ha")
        colonnes[1].metric(
            "Part due aux feux de plus de 10 ha",
            pc(feux.loc[feux["ha"] > 10, "ha"].sum() / feux["ha"].sum()) if feux["ha"].sum() else "—",
        )
        colonnes[2].metric("Plus grand feu", f"{fr(feux['ha'].max())} ha")
        par = "Département" if territoire == "NA" else "Nom de la commune"
        surface = feux.groupby(par)["ha"].sum().nlargest(10)
        if territoire == "NA":
            surface = surface.rename(index=noms_departements)
        barres(
            surface,
            f"{surface.index[0]} : {pc(surface.iloc[0] / feux['ha'].sum())} de la surface brûlée",
            rouges=[surface.index[0]],
            horizontal=True,
            nom_valeur="Hectares brûlés",
        )
        st.caption(
            "La fiche 1 rapporte la surface brûlée aux jours de danger élevé. Le seuil actuel étant à redéfinir, "
            "la surface est donnée brute ; la section « Redéfinir le seuil » la donne par niveau de la Météo des forêts "
            f"et selon la météo du jour. {pc(estimees)} des surfaces sont estimées, pas mesurées. "
            f"{fr(sans_surface)} feux sans surface, exclus."
        )

    # ---- KPI de pilotage (fiches 2 et 3) -------------------------------------------------------
    st.subheader("KPI de pilotage")
    gauche, droite = st.columns(2)
    with gauche, st.container(border=True):
        st.markdown("**Q1. Les feux sont-ils attaqués assez vite pour rester petits ?**")
        echappes = (feux["ha"] > 10).sum()
        colonnes = st.columns(3)
        colonnes[0].metric(
            "Taux d'échappement",
            pc(echappes / len(feux), 1),
            help="Part des départs de feu qui finissent par brûler plus de 10 ha (fiche 2).",
        )
        colonnes[1].metric("Feux éteints à moins de 1 ha", pc((feux["ha"] < 1).mean()))
        colonnes[2].metric(
            "Trajet depuis la caserne",
            f"{fr(feux['minutes'].median())} min" if "minutes" in feux else "—",
            help="Médiane du temps de trajet en voiture par la route, depuis la caserne la plus proche du centre de la "
            "commune (OSRM). Ce n'est pas le délai d'intervention réel, qui compte aussi l'alerte et le départ.",
        )
        st.caption(f"{fr(echappes)} feux de plus de 10 ha sur {fr(len(feux))} départs.")
        if "minutes" in feux:
            parts, message, rouges = part_au_dessus(feux, "minutes", TRAJETS, "de la caserne")
            barres(parts, message, rouges=rouges, ordonne=True, format_valeur=".0%", nom_valeur="Feux de plus de 1 ha")
            st.caption("Temps de trajet estimé : le vrai délai d'intervention est dans les données du SDIS.")
        else:
            st.info("Lance `python sources/calculer_temps_trajet.py` pour estimer les temps de trajet depuis les casernes.")

    with droite, st.container(border=True):
        st.markdown("**Q2. Les pompiers ont-ils de l'eau là où les feux se déclarent ?**")
        if secours is None:
            st.info("Lance `python sources/telecharger_osm.py` pour situer les points d'eau.")
        else:
            colonnes = st.columns(2)
            colonnes[0].metric(
                "Feux à moins de 2 km d'un point d'eau",
                pc((feux["km_eau"] < 2).mean()),
                help="Proxy de la fiche 3 : citernes, bassins, points d'aspiration et poteaux incendie d'OpenStreetMap.",
            )
            colonnes[1].metric(
                "Sans les poteaux incendie",
                pc((feux["km_eau_massif"] < 2).mean()),
                help="Seulement citernes, bassins et points d'aspiration : les points d'eau des massifs.",
            )
            parts, message, rouges = part_au_dessus(feux, "km_eau_massif", DISTANCES, "d'un point d'eau de massif")
            barres(parts, message, rouges=rouges, ordonne=True, format_valeur=".0%", nom_valeur="Feux de plus de 1 ha")
            st.caption(
                "La fiche 3 mesure la part de la forêt à moins de 2 km d'un point d'eau DFCI. Sans la BD Forêt "
                "ni les points d'eau DFCI (PIGMA), on mesure ici la part des départs de feu couverts. "
                "OpenStreetMap est incomplet en forêt, et les poteaux des bourgs font paraître les lisières bien couvertes."
            )

    if secours is not None:
        colonnes_table = {"departs": ("id", "size"), "plus_1ha": ("ha", lambda s: (s >= 1).sum()), "ha": ("ha", "sum"),
                          "km_eau": ("km_eau_massif", "min")}
        if "minutes" in feux:
            colonnes_table["minutes"] = ("minutes", "min")
        loin = (
            feux[feux["km_eau_massif"] >= 2]
            .groupby(["Nom de la commune", "Département"])
            .agg(**colonnes_table)
            .reset_index()
            .sort_values(["plus_1ha", "departs", "ha"], ascending=False)
        )
        st.markdown(
            f"**Où créer des points d'eau en priorité ? {fr(len(loin))} communes ont eu un départ de feu à 2 km ou plus "
            "d'un point d'eau de massif, celles aux feux les plus étendus d'abord**"
        )
        st.dataframe(
            loin.head(15).assign(Département=lambda d: d["Département"].map(noms_departements)),
            hide_index=True,
            width="stretch",
            column_config={
                "Nom de la commune": "Commune",
                "departs": st.column_config.NumberColumn("Départs de feu"),
                "plus_1ha": st.column_config.NumberColumn("Feux de plus de 1 ha"),
                "ha": st.column_config.NumberColumn("Surface brûlée (ha)", format="%.1f"),
                "km_eau": st.column_config.NumberColumn("Point d'eau de massif le plus proche (km)", format="%.1f"),
                "minutes": st.column_config.NumberColumn("Trajet depuis la caserne (min)", format="%.0f"),
            },
        )

    # ---- Dégâts aux habitations (Q3) -----------------------------------------------------------
    st.subheader("Dégâts aux habitations")
    touches = feux[feux["Décès ou bâtiments touchés"] == "Oui"]
    renseignes = feux["Nombre de bâtiments totalement détruits"].notna().sum()
    colonnes = st.columns(4)
    colonnes[0].metric("Feux ayant touché des bâtiments", f"{fr(len(touches))} ({pc(len(touches) / len(feux), 1)})")
    colonnes[1].metric("Bâtiments totalement détruits", fr(feux["Nombre de bâtiments totalement détruits"].sum()))
    colonnes[2].metric("Bâtiments partiellement détruits", fr(feux["Nombre de bâtiments partiellement détruits"].sum()))
    colonnes[3].metric("Décès", fr(feux["Nombre de décès"].sum()))
    if not touches.empty:
        st.dataframe(
            touches.assign(date=touches["Date de première alerte"].dt.strftime("%d/%m/%Y"))[
                ["Nom de la commune", "date", "ha", "Nombre de bâtiments totalement détruits",
                 "Nombre de bâtiments partiellement détruits", "Nombre de décès"]
            ],
            hide_index=True,
            width="stretch",
            column_config={
                "Nom de la commune": "Commune",
                "date": "Date",
                "ha": st.column_config.NumberColumn("Surface brûlée (ha)", format="%.1f"),
                "Nombre de bâtiments totalement détruits": st.column_config.NumberColumn("Bâtiments détruits"),
                "Nombre de bâtiments partiellement détruits": st.column_config.NumberColumn("Bâtiments endommagés"),
                "Nombre de décès": st.column_config.NumberColumn("Décès"),
            },
        )
    st.caption(
        f"Source : BDIFF. Le nombre de bâtiments n'est renseigné que pour {fr(renseignes)} feux sur {fr(len(feux))}. "
        "La fiche KPI vise les feux passés à moins de 200 m d'une maison : il faudrait les contours des feux."
    )

    # ---- Végétation touchée ---------------------------------------------------------------------
    st.subheader("Végétation : qu'est-ce qui brûle ?")
    types = {
        "Surface forêt (m2)": "Forêt",
        "Surface maquis garrigues (m2)": "Maquis et garrigues",
        "Autres surfaces naturelles hors forêt (m2)": "Espaces naturels hors forêt",
        "Surfaces agricoles (m2)": "Surfaces agricoles",
        "Autres surfaces (m2)": "Autres surfaces",
    }
    brule = (feux[[c for c in types if c in feux]].sum() / 10_000).rename(index=types)
    brule = brule[brule > 0].sort_values(ascending=False)
    if not brule.empty:
        barres(brule, f"{brule.index[0]} : {pc(brule.iloc[0] / brule.sum())} de la surface brûlée",
               rouges=[brule.index[0]], horizontal=True, nom_valeur="Hectares brûlés")
    st.caption(
        "Répartition déclarée dans la BDIFF. Le type d'arbres touchés (pins, feuillus) n'y est pas renseigné : "
        "la carte montre où sont les résineux et les landes, qui brûlent plus facilement que les feuillus."
    )

    # ---- Redéfinir le seuil (prévisions) -------------------------------------------------------
    st.subheader("Redéfinir le seuil : dans quelles conditions les feux partent-ils ?")
    unite = "par jour et par département" if territoire == "NA" else "par jour"

    # Le seuil actuel d'abord : la commande demande à partir de quel niveau de la Météo des forêts déclencher.
    mdf = charger_meteo_des_forets()
    niveaux = par_niveau(feux, mdf, codes) if mdf is not None else pd.DataFrame()
    if niveaux.empty:
        st.info(
            f"Lance `python sources/telecharger_meteo_des_forets.py {annee}` pour comparer avec le seuil actuel "
            "de la Météo des forêts (archives depuis 2024)."
        )
    else:
        haut, bas = niveaux.iloc[-1], niveaux.iloc[0]
        nom_haut, nom_bas = NIVEAUX.get(int(haut["niveau"])), NIVEAUX.get(int(bas["niveau"]))
        graphes = [("departs", "départ de feu", "Départs de feu", 2), ("surface", "ha brûlés", "Hectares brûlés", 1)]
        for colonne, (col, quoi, nom_valeur, decimales) in zip(st.columns(2), graphes):
            with colonne:
                titre = (
                    f"Niveau {nom_haut} : {fr(haut[col], decimales)} {quoi} {unite}, "
                    f"contre {fr(bas[col], decimales)} au niveau {nom_bas}"
                    if len(niveaux) > 1
                    else f"{nom_valeur} {unite} selon le niveau de la Météo des forêts"
                )
                barres(
                    niveaux[col], titre, rouges=list(niveaux.index[-1:]) if len(niveaux) > 1 else [], ordonne=True,
                    format_valeur=f".{decimales}f", nom_valeur=nom_valeur,
                )
        st.caption(
            "Le seuil actuel : niveau de la Météo des forêts prévu la veille par Météo-France (1 faible à 4 très élevé), "
            "un seul niveau par département. Publié de juin à septembre : les feux hors saison ne sont pas comptés. "
            f"Niveaux vus moins de {JOURS_MINI} jours dans l'année : non affichés."
        )

    meteo = charger_meteo_departements()
    grille, moyenne_departs, moyenne_surface = grille_meteo(feux, meteo, codes)
    if grille["departs"].notna().sum() == 0:
        st.info("Lance `python sources/telecharger_meteo.py` pour croiser les feux avec la température et l'humidité.")
    else:
        pire = grille.loc[grille["departs"].idxmax()]
        st.markdown(
            f"Quand il fait **{pire['temperature']}** et que l'humidité est à **{pire['humidite']}**, "
            f"on compte **{fr(pire['departs'], 2)} départ de feu {unite}**, "
            f"contre {fr(moyenne_departs, 2)} en moyenne sur l'année."
        )
        gauche, droite = st.columns(2)
        with gauche:
            carte_chaleur(grille, "departs", f"Départs de feu {unite}", "Départs par jour", ".2f")
        with droite:
            carte_chaleur(grille, "surface", f"Hectares brûlés {unite}", "Hectares par jour", ".1f")
        st.caption(
            f"Chaque case regroupe les jours-départements de {annee} qui ont eu cette température maximale et cette "
            "humidité minimale (moyennes des stations Météo-France du département). Cases vides : moins de "
            f"{JOURS_MINI} jours, taux trop instable. Le nouveau seuil peut se placer là où les départs et les surfaces "
            "décollent ; à confirmer sur plusieurs années."
        )

    st.subheader("Contexte")
    colonnes = st.columns(2)
    colonnes[0].metric("Départs de feu", fr(len(feux)))
    colonnes[1].metric("Grands feux de plus de 100 ha", fr((feux["ha"] > 100).sum()), help="À suivre en moyenne sur 5 ans.")

    with st.expander("Options de la décision et indicateurs à suivre"):
        st.markdown(
            "| Option | Indicateurs à suivre | Pourquoi |\n|---|---|---|\n"
            "| Prévisions | Nouveau seuil (température, humidité), temps de trajet, taux d'échappement | "
            "Savoir où et quand le risque est fort permet de placer les pompiers à l'avance et d'arriver plus vite. |\n"
            "| Création de points d'eau | Couverture en eau, taux d'échappement | "
            "De l'eau à proximité permet d'éteindre le feu avant qu'il dépasse 10 ha. |\n"
            "| Débroussaillement | Grands feux de plus de 100 ha, dégâts aux habitations | "
            "Moins de végétation : le feu se propage moins vite et atteint moins les maisons. |"
        )
    with st.expander("Limites"):
        st.markdown(
            f"- **Une seule année** ({annee}) : il faut exporter les autres années de la BDIFF pour comparer.\n"
            f"- **Surfaces estimées** : {pc(estimees)} des surfaces sont estimées. Un feu de 9 ou 11 ha peut changer "
            "de côté du seuil de 10 ha selon l'estimation.\n"
            "- **Petits effectifs** : peu de feux de plus de 10 ha ; lisser sur 3 à 5 ans.\n"
            "- **Lieu du feu** : la BDIFF ne donne que la commune ; distances et trajets partent du centre de la commune.\n"
            "- **Temps de trajet** : itinéraire en voiture (OSRM), sans le temps d'alerte ni de départ ; un camion roule "
            "moins vite sur les pistes forestières.\n"
            "- **Points d'eau et casernes** : OpenStreetMap, incomplet en forêt. À remplacer par les données DFCI et SDIS.\n"
            "- **Météo** : moyenne des stations du département, pas la météo exacte au lieu du feu.\n"
            "- **Corrélation** : un lien entre distance et taille du feu ne prouve pas que l'un cause l'autre."
        )
    st.caption(
        "Sources : BDIFF (feux, dégâts), Météo-France (température, humidité), OpenStreetMap (casernes, points d'eau), "
        "OSRM (temps de trajet), geo.api.gouv.fr (communes). Indicateurs définis dans KPI_fiches.docx."
    )
