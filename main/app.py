import json
from pathlib import Path

import pydeck as pdk
import streamlit as st

ICI = Path(__file__).parent

st.set_page_config(page_title="Allumez le feu", page_icon="🔥", layout="wide")
st.html(f"<style>{(ICI / 'style.css').read_text(encoding='utf-8')}</style>")


@st.cache_data
def charger_gironde():
    return json.loads((ICI / "geo" / "gironde.geojson").read_text(encoding="utf-8"))


def voile_hors_gironde(gironde):
    # Un grand rectangle percé à la forme de la Gironde : tout ce qui est hors du département est voilé.
    cadre = [[-30, 25], [30, 25], [30, 65], [-30, 65], [-30, 25]]
    trous = [polygone[0] for polygone in gironde["geometry"]["coordinates"]]
    return {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [cadre, *trous]}}


def a_rediger(texte):
    st.markdown(f'<p class="a-rediger">À rédiger : {texte}</p>', unsafe_allow_html=True)


st.title("Allumez le feu")
st.markdown(
    '<p class="chapeau">Où concentrer les moyens du SDIS 33, et à partir de quel niveau '
    "de la Météo des forêts déclencher le dispositif renforcé pour l'été 2027.</p>",
    unsafe_allow_html=True,
)

carte, presentation, tableau = st.tabs(["Carte", "Présentation", "Tableau de bord"])

with carte:
    gironde = charger_gironde()
    st.pydeck_chart(
        pdk.Deck(
            layers=[
                pdk.Layer("GeoJsonLayer", voile_hors_gironde(gironde), get_fill_color=[230, 232, 227, 215]),
                pdk.Layer(
                    "GeoJsonLayer",
                    gironde,
                    filled=False,
                    # Vert pin, pas rouge : le rouge est réservé aux données (feux, danger élevé).
                    get_line_color=[29, 51, 40],
                    line_width_min_pixels=2,
                ),
            ],
            initial_view_state=pdk.ViewState(latitude=44.88, longitude=-0.47, zoom=7.7, min_zoom=6),
            map_provider="carto",
            map_style=pdk.map_styles.CARTO_LIGHT,
        ),
        height=640,
    )
    st.caption("Contour du département : france-geojson.")

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
    a_rediger("les sources utilisées, leur période et leurs limites.")
    st.header("La méthode")
    a_rediger("comment on relie les départs de feu au niveau de l'indice.")
    st.header("L'équipe")
    st.markdown("Elias, Ismaël, Hoa, Melissa et Rim.")

with tableau:
    st.markdown(
        '<p class="a-rediger">Aucune donnée traitée pour l\'instant. Les indicateurs s\'afficheront ici '
        "dès que les données du SDIS et de la Météo des forêts seront prêtes.</p>",
        unsafe_allow_html=True,
    )
    # Valeurs à remplacer par les vrais chiffres une fois les données traitées.
    col1, col2, col3 = st.columns(3)
    col1.metric("Départs de feu par an", "—")
    col2.metric("Hectares brûlés par an", "—")
    col3.metric("Jours en dispositif renforcé", "—")
    with st.container(border=True, height=320, key="graphique"):
        # Avec les données, le titre doit porter le message (Minto), par exemple
        # « Les départs de feu augmentent nettement à partir du niveau élevé ».
        st.subheader("Départs de feu selon le niveau de l'indice")
        st.caption("Graphique à venir : une barre par niveau de l'indice, du plus faible au plus fort, axe à partir de zéro.")
