import calendar
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

import tableau_de_bord
from donnees import DATA, FEUX, charger_feux, charger_meteo_departements, charger_secours, charger_trajets

ICI = Path(__file__).parent
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
# Une seule teinte, du clair au foncé, pour les zones : le rouge reste réservé aux feux.
BLEUS = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
# Couche de zones : colonne, bornes des classes, unité de l'étiquette.
COUCHES = {
    "Température max": ("TX", [20, 25, 30, 35], "°"),
    "Humidité min": ("UN", [30, 40, 50, 60], " %"),
}
EAU = [0, 145, 199]  # points d'eau
VUE = {"latitude": 44.98, "longitude": 0.41, "zoom": 6.1}  # vue de départ de la carte
# Mètres par pixel à la vue de départ (Web Mercator, tuiles de 512 px comme deck.gl).
METRES_PAR_PIXEL = 78271.517 * np.cos(np.radians(VUE["latitude"])) / 2 ** VUE["zoom"]
TYPES_EAU = {"water_tank": "citerne", "suction_point": "point d'aspiration", "fire_water_pond": "réserve d'eau"}

st.set_page_config(page_title="Saison feux 2027, SDIS 33", page_icon=":material/local_fire_department:", layout="wide")
st.html(f"<style>{(ICI / 'style.css').read_text(encoding='utf-8')}</style>")


@st.cache_data
def charger_geo(nom):
    return json.loads((ICI / "geo" / f"{nom}.geojson").read_text(encoding="utf-8"))


def voile_hors(zone):
    # Un grand rectangle percé à la forme de la zone (MultiPolygon) : tout ce qui est autour est voilé.
    cadre = [[-30, 25], [30, 25], [30, 65], [-30, 65], [-30, 25]]
    trous = [polygone[0] for polygone in zone["geometry"]["coordinates"]]
    return {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [cadre, *trous]}}


@st.cache_data
def charger_feux_carte():
    feux = charger_feux()
    feux["mois"] = feux["Date de première alerte"].dt.month
    feux["j"] = feux["Date de première alerte"].dt.day
    feux["commune"] = feux["Nom de la commune"]
    feux["date"] = feux["Date de première alerte"].dt.strftime("%d/%m/%Y à %Hh%M")
    feux["ha"] = feux["ha"].round(2)
    # Aire du cercle proportionnelle à la surface brûlée. Rayon en mètres, pour que le rond garde son emprise sur la
    # carte quand on zoome : à la vue de départ, il fait 2,5 pixels par racine d'hectare.
    feux["rayon"] = 2.5 * np.sqrt(feux.ha) * METRES_PAR_PIXEL
    # Orange clair en début de mois, rouge sombre en fin de mois : on suit l'évolution des feux jour après jour.
    avancement = (feux.j - 1) / 30
    feux["couleur"] = [[int(229 - 107 * a), int(140 - 124 * a), int(69 - 53 * a), 220] for a in avancement]
    trajets = charger_trajets()
    if trajets is not None:
        feux = feux.merge(trajets, on="Code INSEE", how="left")
    feux["info"] = [
        f"{f['commune']}\n{f['date']}\n{str(f['ha']).replace('.', ',')} ha brûlés"
        + (
            f"\nCaserne la plus proche : {f['minutes']:.0f} min par la route"
            if trajets is not None and pd.notna(f["minutes"])
            else ""
        )
        for _, f in feux.iterrows()
    ]
    return feux[["Année", "Département", "mois", "j", "lon", "lat", "ha", "rayon", "couleur", "info"]]


@st.cache_data
def charger_secours_carte():
    """Casernes, et points d'eau des massifs : les 30 000 poteaux incendie des bourgs seraient illisibles à cette échelle."""
    secours = charger_secours()
    if secours is None:
        return None, None
    secours = secours.fillna({"nom": ""})
    casernes = secours[secours["categorie"] == "caserne"]
    eau = secours[secours["type"].isin(TYPES_EAU)]
    casernes = casernes.assign(info=[f"Caserne de pompiers\n{n}".strip() for n in casernes["nom"]])
    eau = eau.assign(info=[f"Point d'eau : {TYPES_EAU[t]}\n{n}".strip() for t, n in zip(eau["type"], eau["nom"])])
    return casernes[["lon", "lat", "info"]], eau[["lon", "lat", "info"]]


def charger_vegetation():
    """Image de la végétation classée par inflammabilité et sa légende (sources/telecharger_foret.py)."""
    image, legende_vegetation = DATA / "ign" / "foret_nouvelle_aquitaine.png", DATA / "ign" / "foret.json"
    if not (image.exists() and legende_vegetation.exists()):
        return None
    return image, json.loads(legende_vegetation.read_text(encoding="utf-8"))


def classes(couche):
    """Teintes et libellés des classes d'une couche de zones."""
    _, bornes, unite = COUCHES[couche]
    libelles = [f"moins de {bornes[0]}{unite}", *[f"{a} à {b}{unite}" for a, b in zip(bornes, bornes[1:])]]
    return BLEUS, [*libelles, f"{bornes[-1]}{unite} ou plus"]


def zones(departements, valeurs, couche):
    """Départements colorés selon `valeurs` (indexées par code), et l'étiquette de la valeur au centre de chacun."""
    _, bornes, unite = COUCHES[couche]
    teintes, _ = classes(couche)
    entites, etiquettes = [], []
    for d in departements["features"]:
        valeur = valeurs.get(d["properties"]["code"])
        if valeur is None or pd.isna(valeur):
            continue  # pas de mesure ce jour-là : la zone reste vide
        teinte = teintes[int(np.digitize(valeur, bornes))]
        rvb = [int(teinte[k : k + 2], 16) for k in (1, 3, 5)]
        entites.append({**d, "properties": {**d["properties"], "couleur": [*rvb, 190]}})
        coordonnees = d["geometry"]["coordinates"]
        polygones = coordonnees if d["geometry"]["type"] == "MultiPolygon" else [coordonnees]
        contour = max((p[0] for p in polygones), key=len)
        etiquettes.append(
            {
                "position": np.mean(contour, axis=0).tolist(),
                "texte": f"{valeur:.0f}{unite}",
                # Texte blanc sur les bleus foncés, vert pin sur les clairs.
                "couleur": [255, 255, 255] if BLEUS.index(teinte) >= 2 else [29, 51, 40],
            }
        )
    return {"type": "FeatureCollection", "features": entites}, etiquettes


def legende(titre, teintes, libelles):
    cases = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:.35rem;margin-right:1rem">'
        f'<span style="width:14px;height:14px;border-radius:3px;background:{t}"></span>{l}</span>'
        for t, l in zip(teintes, libelles)
    )
    st.markdown(f'<p style="font-size:.875rem;margin-bottom:.25rem">{titre} : {cases}</p>', unsafe_allow_html=True)


def a_rediger(texte):
    st.markdown(f'<p class="a-rediger">À rédiger : {texte}</p>', unsafe_allow_html=True)


titre, cartouche = st.columns([2, 1], vertical_alignment="bottom")
titre.title("Saison feux 2027", anchor=False)
titre.markdown(
    '<p class="chapeau">Aide à la décision pour le SDIS de la Gironde : où concentrer les moyens, et à partir de '
    "quel niveau de la Météo des forêts déclencher le dispositif renforcé.</p>",
    unsafe_allow_html=True,
)
cartouche.markdown(
    '<dl class="cartouche">'
    "<dt>Commanditaire</dt><dd>SDIS de la Gironde (SDIS 33)</dd>"
    "<dt>Rendu</dt><dd>11 décembre 2026</dd>"
    "<dt>Données</dt><dd>BDIFF 2025, Météo-France, OpenStreetMap</dd>"
    "<dt>Statut</dt><dd>Prototype, chiffres à valider</dd>"
    "</dl>",
    unsafe_allow_html=True,
)

# La synthèse d'abord : c'est ce que lit la direction. Le code remplit les onglets dans un autre ordre (la carte
# charge les contours dont le tableau de bord a besoin), ce qui ne change pas leur ordre à l'écran.
tableau, carte, presentation = st.tabs(["Tableau de bord", "Carte", "Méthode et données"])

with carte:
    departements = charger_geo("departements-nouvelle-aquitaine")
    foret, zones_fond, zones_texte, secours, points_feux = [], [], [], [], []
    if FEUX.exists():
        feux = charger_feux_carte()
        annee = int(feux["Année"].max())
        mois = st.select_slider(
            "Mois", options=list(range(1, 13)), value=int(feux.mois.mode()[0]), format_func=lambda m: MOIS[m - 1]
        )
        du_mois = feux[(feux.mois == mois) & (feux["Année"] == annee)]
        if du_mois.empty:
            st.markdown(f"Aucun départ de feu en Nouvelle-Aquitaine en {MOIS[mois - 1]} {annee}.")
        else:
            st.markdown(
                f"**{len(du_mois)} départs de feu** en Nouvelle-Aquitaine en {MOIS[mois - 1]} {annee}, "
                f"dont {(du_mois['Département'] == '33').sum()} en Gironde."
            )
        # Jour après jour : les feux s'accumulent depuis le 1er, ceux du jour choisi ressortent.
        gauche, droite = st.columns([3, 2])
        jour = gauche.slider(
            "Jour",
            1,
            calendar.monthrange(annee, mois)[1],
            int(du_mois.j.mode()[0]) if not du_mois.empty else 15,
            help="Déplace le curseur pour faire défiler le mois : les feux s'ajoutent jour après jour.",
        )
        couche = droite.segmented_control("Zones", [*COUCHES, "Aucune"], default="Aucune")
        afficher = droite.pills(
            "Afficher", ["Végétation", "Casernes", "Points d'eau"], selection_mode="multi",
            default=["Végétation", "Casernes", "Points d'eau"],
        )
        visibles = du_mois[du_mois.j <= jour].copy()
        visibles["couleur"] = [c[:3] + [255 if j == jour else 80] for c, j in zip(visibles.couleur, visibles.j)]
        n = (visibles.j == jour).sum()
        st.markdown(
            f"Le {jour}{'er' if jour == 1 else ''} {MOIS[mois - 1]} : **{n} départ{'s' if n > 1 else ''} de feu**, "
            f"{len(visibles)} depuis le 1er."
        )

        vegetation = charger_vegetation()
        if "Végétation" in afficher and vegetation is not None:
            image, legende_vegetation = vegetation
            foret.append(pdk.Layer("BitmapLayer", image=str(image), bounds=legende_vegetation["bornes"], opacity=0.55))
            legende(
                "Végétation, du plus au moins inflammable",
                [c["couleur"] for c in legende_vegetation["classes"]],
                [c["nom"] for c in legende_vegetation["classes"]],
            )
        elif "Végétation" in afficher:
            st.caption("Lance `python sources/telecharger_foret.py` pour afficher la végétation.")

        if couche in COUCHES:
            meteo = charger_meteo_departements()
            jour_aaaammjj = annee * 10000 + mois * 100 + jour
            valeurs = meteo[meteo["AAAAMMJJ"] == jour_aaaammjj].set_index("Département")[COUCHES[couche][0]]
            if valeurs.dropna().empty:
                st.caption(f"Pas de donnée « {couche.lower()} » ce jour-là : lance `python sources/telecharger_meteo.py`.")
            else:
                entites, etiquettes = zones(departements, valeurs, couche)
                zones_fond.append(pdk.Layer("GeoJsonLayer", entites, get_fill_color="properties.couleur", stroked=False))
                zones_texte.append(
                    pdk.Layer(
                        "TextLayer",
                        etiquettes,
                        get_position="position",
                        get_text="texte",
                        get_color="couleur",
                        get_size=14,
                        font_family="'Archivo, sans-serif'",  # guillemets : sinon pydeck le lit comme une expression
                        font_weight=600,
                        character_set="'auto'",  # accents et « ° »
                    )
                )
                legende(couche, *classes(couche))

        casernes, points_eau = charger_secours_carte()
        if "Points d'eau" in afficher and points_eau is not None:
            secours.append(
                pdk.Layer(
                    "ScatterplotLayer", points_eau, get_position=["lon", "lat"], get_radius=1.8,
                    radius_units="'pixels'", get_fill_color=EAU, pickable=True,
                )
            )
        if "Casernes" in afficher and casernes is not None:
            secours.append(
                pdk.Layer(
                    "ScatterplotLayer", casernes, get_position=["lon", "lat"], get_radius=2.5,
                    radius_units="'pixels'", get_fill_color=[255, 255, 255], stroked=True,
                    get_line_color=[29, 51, 40], line_width_min_pixels=1, pickable=True,
                )
            )
        # Feux de 1 ha ou plus à l'échelle de la carte, sans plafond : ils grossissent quand on zoome et gardent leur
        # emprise sur le terrain. Les plus petits (et ceux sans surface) restent un point fixe de 3 pixels, par-dessus.
        grands = visibles["ha"] >= 1
        style_feu = dict(
            get_position=["lon", "lat"], get_fill_color="couleur", stroked=True, get_line_color=[255, 255, 255],
            line_width_min_pixels=0.5, pickable=True,
        )
        points_feux += [
            pdk.Layer(
                "ScatterplotLayer", visibles[grands], get_radius="rayon",
                radius_units="'meters'",  # guillemets internes : sinon pydeck lit « meters » comme une expression
                radius_min_pixels=3,  # dézoomé au-delà de la vue de départ, ils restent visibles
                **style_feu,
            ),
            pdk.Layer("ScatterplotLayer", visibles[~grands], get_radius=3, radius_units="'pixels'", **style_feu),
        ]
    else:
        st.info("Pour afficher les départs de feu, ajoute l'export BDIFF dans data/Incendies.csv (voir sources/README.md).")

    region = charger_geo("region-nouvelle-aquitaine")
    # Fond, voile et contours suivent le thème. shortcut: Streamlit ne relance pas le script quand on change
    # de thème (issue #11920), la carte suit à la prochaine interaction ; à retirer si Streamlit corrige.
    sombre = st.context.theme.type == "dark"
    fond, trait = ([17, 25, 21], [228, 233, 230]) if sombre else ([242, 244, 243], [28, 42, 36])  # couleurs du thème
    # Contours en vert pin (cendre en sombre), pas en rouge : le rouge est réservé aux données (feux, danger élevé).
    st.pydeck_chart(
        pdk.Deck(
            layers=[  # de bas en haut
                *foret,
                pdk.Layer("GeoJsonLayer", voile_hors(region), get_fill_color=[*fond, 215]),
                *zones_fond,
                *secours,
                *zones_texte,
                pdk.Layer("GeoJsonLayer", departements, filled=False, get_line_color=[*trait, 140], line_width_min_pixels=1),
                pdk.Layer("GeoJsonLayer", region, filled=False, get_line_color=trait, line_width_min_pixels=2),
                *points_feux,
            ],
            initial_view_state=pdk.ViewState(**VUE, min_zoom=5),
            map_provider="carto",
            map_style=pdk.map_styles.CARTO_DARK if sombre else pdk.map_styles.CARTO_LIGHT,
            # Infobulle en texte simple : les retours à la ligne passent, et aucun nom venu d'un fichier n'est lu comme du HTML.
            tooltip={
                "text": "{info}",
                "style": {"backgroundColor": "#1d3328", "color": "#f3f4f0", "fontFamily": "Archivo, sans-serif"},
            },
        ),
        height=640,
    )
    st.caption(
        "Points orange à rouges : départs de feu, placés au centre de leur commune (la BDIFF ne donne pas l'emplacement "
        "exact). Les feux de 1 ha ou plus sont à l'échelle de la carte : leur aire est proportionnelle à la surface brûlée. "
        "Leur couleur va de "
        "l'orange clair (début du mois) au "
        "rouge sombre (fin du mois). Les feux du jour choisi sont pleins, ceux des jours précédents estompés."
    )
    st.caption(
        "Ronds blancs cerclés de vert : casernes de pompiers. Points bleus : points d'eau des massifs (citernes, réserves, "
        "points d'aspiration), sans les poteaux incendie des bourgs. Végétation : BD Forêt V2 de l'IGN, regroupée en trois "
        "niveaux, les résineux et les landes brûlant plus facilement que les feuillus. Le temps de trajet affiché au survol "
        "d'un feu est calculé en voiture depuis la caserne la plus proche : ce n'est pas le délai d'intervention réel, "
        "qui compte aussi l'alerte et le départ. Sources : BDIFF, IGN, Météo-France, OpenStreetMap, OSRM, "
        "geo.api.gouv.fr, france-geojson."
    )

with presentation:
    st.header("La commande")
    st.markdown(
        "Le SDIS 33 ne peut pas couvrir tout le département tout l'été. Il doit choisir où concentrer "
        "ses moyens et à partir de quel niveau de la Météo des forêts déclencher le dispositif renforcé. "
        "Rendu à la direction le 11 décembre."
    )
    st.header("Contexte")
    a_rediger("les feux de l'été 2026, les moyens actuels du SDIS 33, ce que mesure la Météo des forêts.")
    st.header("Les données")
    st.markdown(
        "- **Départs de feu** : BDIFF, année 2025, 12 départements de Nouvelle-Aquitaine. Commune, date de l'alerte, "
        "surface brûlée par type de végétation, bâtiments détruits.\n"
        "- **Seuil actuel** : archives de la Météo des forêts (Météo-France), niveau de danger prévu la veille pour "
        "chaque département, de juin à septembre, depuis 2024.\n"
        "- **Météo** : température maximale et humidité minimale du jour, stations Météo-France, moyennées par département.\n"
        "- **Moyens** : casernes et points d'eau d'OpenStreetMap ; temps de trajet par la route calculé avec OSRM.\n"
        "- **Végétation** : BD Forêt V2 de l'IGN, en trois niveaux d'inflammabilité.\n\n"
        "**Limites** : une seule année de feux ; chaque feu est placé au centre de sa commune ; les surfaces sont "
        "surtout estimées ; OpenStreetMap est incomplet en forêt ; le temps de trajet n'est pas le délai "
        "d'intervention réel. Détail des sources et licences dans `SOURCES.md`."
    )
    st.header("La méthode")
    st.markdown(
        "1. Chaque départ de feu est rattaché à **un département et un jour**.\n"
        "2. Pour chaque jour et chaque département, on compte les **départs de feu** et les **hectares brûlés**.\n"
        "3. On compare ces jours selon le **niveau de la Météo des forêts** prévu la veille (le seuil actuel), puis "
        "selon la **température** et l'**humidité** du jour (la matière du nouveau seuil).\n"
        "4. On divise par le **nombre de jours** de chaque catégorie : sans cela, les catégories fréquentes "
        "paraîtraient plus dangereuses.\n\n"
        f"**Garde-fous** : une catégorie vue moins de {tableau_de_bord.JOURS_MINI} jours n'est pas affichée ; un écart "
        f"calculé sur moins de {tableau_de_bord.FEUX_MINI} feux est signalé « à confirmer ». Un lien entre deux "
        "mesures ne prouve pas que l'une cause l'autre."
    )
    st.header("L'équipe")
    st.markdown("Projet « Allumez le feu » : Elias, Ismaël, Hoa, Melissa et Rim.")

with tableau:
    tableau_de_bord.afficher({d["properties"]["code"]: d["properties"]["nom"] for d in departements["features"]})
