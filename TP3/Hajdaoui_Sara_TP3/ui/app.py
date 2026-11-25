"""Interface Streamlit de MaintAI : exploration des données et prédiction de panne."""

import httpx
import pandas as pd
import streamlit as st

from maintai.client import APIError, MaintaiClient
from maintai.config import FEATURES, get_settings


# --------------------------------------------------
# 1. Configuration de la page
# --------------------------------------------------

st.set_page_config(
    page_title="MaintAI",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 MaintAI · Prédiction de panne")
st.caption("Surveillance intelligente des équipements industriels")


# --------------------------------------------------
# 2. Chargement des données
# --------------------------------------------------

@st.cache_data
def charger(path) -> pd.DataFrame:
    """Charge le dataset CSV et le met en cache."""
    return pd.read_csv(path)


settings = get_settings()
df = charger(settings.data_path)


# --------------------------------------------------
# 3. Configuration de la connexion API
# --------------------------------------------------

with st.sidebar:
    st.header("⚙️ Configuration API")

    url = st.text_input(
        "URL de l'API",
        "http://localhost:8000"
    )

    cle = st.text_input(
        "Clé API",
        type="password"
    )


# --------------------------------------------------
# 4. Création des onglets
# --------------------------------------------------

onglet_donnees, onglet_prediction = st.tabs(
    ["📊 Données", "🤖 Prédiction"]
)


# ==================================================
# SPRINT 1 : EXPLORATION DES DONNÉES
# ==================================================

with onglet_donnees:

    st.header("Exploration du dataset")

    # Vérification des colonnes nécessaires
    colonnes_requises = FEATURES + ["failure"]

    if not all(col in df.columns for col in colonnes_requises):
        st.error("Le dataset ne contient pas toutes les colonnes nécessaires.")
        st.stop()

    # ----------------------------------------------
    # 4.1 Trois indicateurs statistiques
    # ----------------------------------------------

    nombre_releves = len(df)
    taux_panne = df["failure"].mean() * 100
    temperature_moyenne = df["temperature_c"].mean()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Nombre de relevés",
            f"{nombre_releves}"
        )

    with col2:
        st.metric(
            "Taux de panne",
            f"{taux_panne:.1f} %"
        )

    with col3:
        st.metric(
            "Température moyenne",
            f"{temperature_moyenne:.1f} °C"
        )

    st.divider()

    # ----------------------------------------------
    # 4.2 Choix de la variable à analyser
    # ----------------------------------------------

    st.subheader("Analyse du taux de panne")

    variable = st.selectbox(
        "Choisir une variable :",
        FEATURES
    )

    # ----------------------------------------------
    # 4.3 Découpage en tranches avec pd.cut
    # ----------------------------------------------

    donnees_tranches = df.copy()

    donnees_tranches["tranche"] = pd.cut(
        donnees_tranches[variable],
        bins=10
    )

    taux_par_tranche = (
        donnees_tranches
        .groupby("tranche", observed=True)["failure"]
        .mean()
        .mul(100)
        .to_frame()
    )

    # Étiquette = milieu de la tranche (un nombre, pas du texte)
    taux_par_tranche.index = [
        round(i.mid, 1) for i in taux_par_tranche.index
    ]

    # ----------------------------------------------
    # 4.4 Affichage du graphique en barres
    # ----------------------------------------------

    st.caption(
        f"Taux de panne selon les différentes tranches de {variable}"
    )

    st.bar_chart(
        taux_par_tranche,
        y="failure",
        y_label="Taux de panne (%)"
    )

    st.divider()

    # ----------------------------------------------
    # 4.5 Nuage de points température / vibration
    # ----------------------------------------------

    st.subheader("Relation température / vibration")

    donnees_scatter = df[
        ["temperature_c", "vibration_mm_s", "failure"]
    ].copy()

    donnees_scatter["État"] = donnees_scatter["failure"].map(
        {0: "Normal", 1: "Panne"}
    )

    st.scatter_chart(
        donnees_scatter,
        x="temperature_c",
        y="vibration_mm_s",
        color="État",
        x_label="Température (°C)",
        y_label="Vibration (mm/s)"
    )


# ==================================================
# SPRINT 2 : PRÉDICTION AVEC L'API
# ==================================================

with onglet_prediction:

    st.header("Prédiction du risque de panne")

    st.write(
        "Renseignez les caractéristiques de l'équipement "
        "pour estimer sa probabilité de défaillance."
    )

    # ----------------------------------------------
    # 5.1 Formulaire de saisie
    # ----------------------------------------------

    with st.form("releve"):
        releve = {
            "temperature_c": st.slider(
                "Température (°C)", min_value=-40.0, max_value=150.0, value=60.0, step=0.5
            ),
            "vibration_mm_s": st.slider(
                "Vibration (mm/s)", min_value=0.0, max_value=50.0, value=6.0, step=0.1
            ),
            "load_pct": st.slider(
                "Charge (%)", min_value=0.0, max_value=100.0, value=85.0, step=0.5
            ),
            "runtime_hours": st.number_input(
                "Heures de fonctionnement",
                min_value=0,
                max_value=100000,
                value=10000,
                step=100,
            ),
        }
        envoye = st.form_submit_button("Prédire")

    # ----------------------------------------------
    # 5.2 Appel de l'API et traitement de la réponse
    # ----------------------------------------------

    if envoye:

        try:

            # Création du client API
            api = MaintaiClient(
                url,
                api_key=cle
            )

            # Envoi des mesures et récupération du résultat
            resultat = api.predict(releve)

            # Extraction de la probabilité
            probabilite = float(
                resultat["failure_probability"]
            )

            pct = round(probabilite * 100)

            # Extraction de l'état d'alerte
            alerte = resultat["alert"]

            # --------------------------------------
            # 5.3 Affichage du résultat
            # --------------------------------------

            st.divider()

            st.metric(
                "Probabilité de panne",
                f"{pct} %"
            )

            if alerte:

                st.error(
                    f"🚨 ALERTE : risque élevé de panne ! "
                    f"La probabilité estimée est de {pct} %."
                )

            else:

                st.success(
                    f"✅ Situation normale. "
                    f"La probabilité estimée est de {pct} %."
                )

            st.caption(
                f"Seuil d'alerte : {resultat['threshold']} "
                f"| Version du modèle : {resultat['model_version']}"
            )

        # ------------------------------------------
        # 5.4 Gestion des erreurs
        # ------------------------------------------

        except APIError as e:

            st.warning(
                f"Erreur API {e.status_code} : {e.detail}"
            )

        except httpx.HTTPError as e:

            st.error(
                f"API injoignable : impossible de contacter le serveur. {e}"
            )

        except (KeyError, TypeError, ValueError) as e:

            st.error(
                f"Réponse API invalide : {e}"
            )
