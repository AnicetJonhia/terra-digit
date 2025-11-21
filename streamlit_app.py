
# TerraDigit — Présentation interactive : Business Model / Financement / ROI
# Usage: streamlit run streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="TerraDigit — Business, Financement & ROI", layout="wide")

# ---------- Données (CSV-ready) ----------
BUSINESS_MODEL_CSV = """Bloc,Description
Clients cibles,"Coopératives agricoles, Collecteurs, PME agroalimentaires, Exportateurs, ONG / Projets de développement agricole"
Sources de revenus,"Projets sur mesure facturés à chaque client (sites vitrine, applications mobiles, intégration IA, services terrain)"
Proposition de valeur,"Digitalisation rapide et simple; IA pour optimisation production et traçabilité; Gain de visibilité et d’accès au marché; Réduction des pertes financières"
Canaux de distribution,"Vente directe, Partenariats ONG et projets agricoles, Démonstration via plateforme web ou application mobile"
Structure des coûts,"Développement logiciel et maintenance; Infrastructure cloud; Accompagnement terrain et support clients; Marketing et prospection"
"""

# Répartition par défaut du financement (doit totaliser 100 %)
DEFAULT_FINANCING_BREAKDOWN = {
    "Développement logiciel & IA": 40,
    "Infrastructure cloud": 20,
    "Accompagnement terrain (formation & support)": 20,
    "Marketing & prospection": 10,
    "Divers / imprévus": 10,
}

# ---------- Utilitaires ----------
def csv_bytes_from_string(s: str) -> bytes:
    return s.encode("utf-8")

def breakdown_table(total_amount: float, breakdown: dict) -> pd.DataFrame:
    rows = []
    for k, pct in breakdown.items():
        amount = total_amount * pct / 100.0
        rows.append({"Poste": k, "Pourcentage (%)": round(pct, 1), "Montant (MGA)": int(round(amount, 0))})
    return pd.DataFrame(rows)

def compute_roi_months(investment: float, revenue_per_project: float, projects_per_month: float, monthly_costs: float):
    revenue = revenue_per_project * projects_per_month
    net = revenue - monthly_costs
    if net <= 0:
        return np.inf, revenue, net
    months = investment / net
    return months, revenue, net

def cumulative_cashflow_series(investment, revenue_per_project, projects_per_month, monthly_costs, months=24):
    series = []
    cum = -investment
    for _ in range(months):
        rev = revenue_per_project * projects_per_month
        net = rev - monthly_costs
        cum += net
        series.append(cum)
    return series

def df_from_business_csv(csv_text: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(csv_text))

def fmt_mga(n):
    return f"{int(n):,} MGA"

# ---------- UI: Navigation ----------
st.sidebar.header("Navigation")
page = st.sidebar.radio("Sélectionner la page", ["Business Model", "Financement & utilisation", "ROI"])

# ---------- Page: Business Model ----------
if page == "Business Model":
    st.markdown("<h1 style='color:#0b6b2f'>Business Model — TerraDigit</h1>", unsafe_allow_html=True)
    st.markdown("Modèle économique synthétique — **projets sur-mesure facturés par client** (développement, IA légère, accompagnement terrain).")

    df_bm = df_from_business_csv(BUSINESS_MODEL_CSV)
    st.dataframe(df_bm, width="stretch")

    st.markdown("---")
    st.download_button(
        label="Télécharger Business Model (CSV)",
        data=csv_bytes_from_string(BUSINESS_MODEL_CSV),
        file_name="terradigit_business_model_MGA.csv",
        mime="text/csv",
    )

# ---------- Page: Financement & Utilisation ----------
elif page == "Financement & utilisation":
    st.markdown("<h1 style='color:#0b6b2f'>Demande de financement — Répartition</h1>", unsafe_allow_html=True)
    st.markdown("Devise : **MGA (Ariary)** ")

    col_left, col_right = st.columns([1, 1])
    with col_left:
        total_investment = st.number_input(
            "Montant total demandé (MGA)",
            min_value=0.0,
            value=20_000_000.0,
            step=50_000.0,
            format="%.0f"
        )
        st.markdown(f"<p style='font-size:20px; font-weight:bold;'>Montant total : <span style='color:#0b6b2f'>{int(total_investment):,} MGA</span></p>", unsafe_allow_html=True)

    with col_right:
        st.markdown("Ajuster la répartition (%) si besoin :")
        breakdown_inputs = {}
        for k, pct in DEFAULT_FINANCING_BREAKDOWN.items():
            breakdown_inputs[k] = st.number_input(f"{k} (%)", min_value=0.0, max_value=100.0, value=float(pct), step=1.0)

    total_pct = sum(breakdown_inputs.values())
    if total_pct <= 0:
        normalized = DEFAULT_FINANCING_BREAKDOWN
        st.warning("Les pourcentages doivent totaliser > 0. Utilisation des valeurs par défaut.")
    else:
        # Normaliser pour affichage afin d'obtenir exactement 100%
        normalized = {k: (v / total_pct * 100.0) for k, v in breakdown_inputs.items()}

    df_break = breakdown_table(total_investment, normalized)

    # Mises en valeur UX : trois métriques clés
    # Sécuriser extraction (col existe)
    def get_amount(df, key):
        row = df.loc[df["Poste"] == key, "Montant (MGA)"]
        return int(row.values[0]) if not row.empty else 0

    dev_amount = get_amount(df_break, "Développement logiciel & IA")
    infra_amount = get_amount(df_break, "Infrastructure cloud")
    terrain_amount = get_amount(df_break, "Accompagnement terrain (formation & support)")

    k1, k2, k3 = st.columns(3)
    k1.metric(label="Dev & IA", value=fmt_mga(dev_amount), delta=f"{normalized.get('Développement logiciel & IA',0):.1f}%")
    k2.metric(label="Infrastructure", value=fmt_mga(infra_amount), delta=f"{normalized.get('Infrastructure cloud',0):.1f}%")
    k3.metric(label="Accompagnement terrain", value=fmt_mga(terrain_amount), delta=f"{normalized.get('Accompagnement terrain (formation & support)',0):.1f}%")

    st.markdown("Répartition détaillée")
    # Styliser Montant en vert via pandas Styler
    styler = df_break.style.format({"Montant (MGA)": "{:,}"}).applymap(lambda v: "color: #0b6b2f; font-weight:600;", subset=["Montant (MGA)"])
    st.dataframe(styler, width="stretch")

    st.markdown("---")
    csv_buf = io.StringIO()
    df_break.to_csv(csv_buf, index=False)
    st.download_button(
        label="Télécharger la répartition (CSV)",
        data=csv_buf.getvalue().encode("utf-8"),
        file_name="terradigit_financement_repartition_MGA.csv",
        mime="text/csv",
    )

    st.markdown("**Résumé**")
    for _, row in df_break.iterrows():
        st.markdown(f"- **{row['Poste']}** : {row['Pourcentage (%)']}% → <span style='color:#0b6b2f'>{int(row['Montant (MGA)']):,} MGA</span>", unsafe_allow_html=True)

# ---------- Page: ROI ----------
elif page == "ROI":
    st.markdown("<h1 style='color:#0b6b2f'>Estimation du Retour sur Investissement (ROI)</h1>", unsafe_allow_html=True)
    st.markdown("Calculateur simplifié — hypothèses réalistes pour des projets sur-mesure à Madagascar. Ajustez les paramètres.")

    col1, col2 = st.columns(2)
    with col1:
        investment = st.number_input(
            "Investissement initial (MGA)",
            min_value=0.0,
            value=20_000_000.0,
            step=50_000.0,
            format="%.0f"
        )
        revenue_per_project = st.number_input(
            "Revenu moyen par projet (MGA)",
            min_value=0.0,
            value=4_000_000.0,
            step=10_000.0,
            format="%.0f"
        )
    with col2:
        projects_per_month = st.number_input(
            "Projets signés par mois (base)",
            min_value=0.0,
            value=1.0,
            step=0.5,
            format="%.1f"
        )
        monthly_costs = st.number_input(
            "Coûts opérationnels mensuels (MGA)",
            min_value=0.0,
            value=1_500_000.0,
            step=10_000.0,
            format="%.0f"
        )

    # Calculs scénarios
    base_months, base_revenue, base_net = compute_roi_months(investment, revenue_per_project, projects_per_month, monthly_costs)
    pessimistic_projects = max(0.0, projects_per_month * 0.5)
    optimistic_projects = projects_per_month * 1.5
    pess_months, pess_revenue, pess_net = compute_roi_months(investment, revenue_per_project, pessimistic_projects, monthly_costs)
    opt_months, opt_revenue, opt_net = compute_roi_months(investment, revenue_per_project, optimistic_projects, monthly_costs)

    def months_display(m):
        return ("Non atteint" if np.isinf(m) else f"{m:.1f} mois")

    result_df = pd.DataFrame([
        {
            "Scénario": "Pessimiste (50% rythme)",
            "Projets/mois": round(pessimistic_projects, 2),
            "Revenu brut/mois (MGA)": int(round(pess_revenue, 0)),
            "Revenu net/mois (MGA)": int(round(pess_net, 0)),
            "Payback": months_display(pess_months)
        },
        {
            "Scénario": "Base",
            "Projets/mois": round(projects_per_month, 2),
            "Revenu brut/mois (MGA)": int(round(base_revenue, 0)),
            "Revenu net/mois (MGA)": int(round(base_net, 0)),
            "Payback": months_display(base_months)
        },
        {
            "Scénario": "Optimiste (150% rythme)",
            "Projets/mois": round(optimistic_projects, 2),
            "Revenu brut/mois (MGA)": int(round(opt_revenue, 0)),
            "Revenu net/mois (MGA)": int(round(opt_net, 0)),
            "Payback": months_display(opt_months)
        },
    ])

    st.markdown("Résultats par scénario")
    st.table(result_df)

    # Métriques synthétiques
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Revenu brut/mois (base)", fmt_mga(base_revenue))
    col_b.metric("Revenu net/mois (base)", fmt_mga(base_net))
    col_c.metric("Payback (base)", months_display(base_months))

    st.markdown("Projection du cashflow cumulé (24 mois)")
    months = 24
    cum_base = cumulative_cashflow_series(investment, revenue_per_project, projects_per_month, monthly_costs, months=months)
    cum_pess = cumulative_cashflow_series(investment, revenue_per_project, pessimistic_projects, monthly_costs, months=months)
    cum_opt = cumulative_cashflow_series(investment, revenue_per_project, optimistic_projects, monthly_costs, months=months)

    df_plot = pd.DataFrame({
        "Mois": np.arange(1, months+1),
        "Pessimiste": cum_pess,
        "Base": cum_base,
        "Optimiste": cum_opt,
    }).set_index("Mois")

    # Plot — couleurs : rouge pess., vert base, bleu opt.
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(df_plot.index, df_plot["Pessimiste"], linestyle='--', label='Pessimiste', color="#b80000")
    ax.plot(df_plot.index, df_plot["Base"], linestyle='-', label='Base', color="#0b6b2f")
    ax.plot(df_plot.index, df_plot["Optimiste"], linestyle='-.', label='Optimiste', color="#1f77b4")
    ax.axhline(y=0, linewidth=0.9, linestyle=':', color="#444444")
    ax.set_xlabel("Mois")
    ax.set_ylabel("Flux de trésorerie cumulé (MGA)")
    ax.set_title("Projection du cashflow cumulé — Scénarios")
    ax.legend()
    ax.grid(alpha=0.2)
    st.pyplot(fig)

    # Téléchargements
    csv_buf = io.StringIO()
    df_plot.reset_index().to_csv(csv_buf, index=False)
    st.download_button(
        label="Télécharger cashflow (CSV)",
        data=csv_buf.getvalue().encode("utf-8"),
        file_name="terradigit_cashflow_projection_MGA.csv",
        mime="text/csv",
    )

    # Interprétation (sans unsafe HTML in st.success)
    st.markdown("Interprétation synthétique")
    if np.isinf(base_months):
        st.error("Le revenu net mensuel (scénario base) est inférieur ou égal à 0 — le remboursement n'est pas atteint. Recommandation : augmenter le nombre de projets signés ou réduire les coûts.")
    else:
        # Use st.markdown to color the key estimate
        st.markdown(f"**Estimation prudente :** récupération de l'investissement en environ **<span style='color:#0b6b2f'>{base_months:.1f} mois</span>** (scénario base).", unsafe_allow_html=True)

    st.info("Remarques : ces estimations sont simplifiées. À Madagascar, facteurs locaux (adoption, connectivité, saisonnalité) peuvent fortement impacter les résultats.")

# ---------- Footer ----------
st.sidebar.markdown("---")
st.sidebar.caption("TerraDigit — ESN Agri-Tech (MGA)")


