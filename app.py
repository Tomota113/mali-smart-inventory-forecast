import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.forecasting_engine import InventoryForecastingEngine
from src.data_generator import generate_inventory_data

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Mali Smart Inventory Forecast",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #008751;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: #1e293b;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #008751;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .kpi-title {
        font-size: 0.95rem;
        color: #94a3b8;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">📦 Mali Smart Inventory Forecast</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Moteur IA de Prédiction des Ventes & Gestion Intelligente du Réapprovisionnement pour le Commerce & la Distribution</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ Configuration & Données")

data_source = st.sidebar.radio(
    "Source des Données :",
    ["Dataset Exemple (Commerce Mali)", "Téléverser mon fichier CSV"]
)

if data_source == "Téléverser mon fichier CSV":
    uploaded_file = st.sidebar.file_uploader("Fichier CSV (date, product_id, product_name, units_sold, stock_level...)", type=["csv"])
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
    else:
        st.info("📌 Fichier d'exemple chargé automatiquement.")
        df_raw = generate_inventory_data()
else:
    df_raw = generate_inventory_data()

forecast_horizon = st.sidebar.slider(
    "Horizon de Prédiction (Jours) :",
    min_value=7,
    max_value=60,
    value=30,
    step=7
)

# Exécution du moteur de prévision
engine = InventoryForecastingEngine(forecast_days=forecast_horizon)
df_health = engine.evaluate_inventory_health(df_raw)

# KPIs Principaux
col1, col2, col3, col4 = st.columns(4)

total_products = len(df_health)
critical_count = len(df_health[df_health['status'] == 'CRITIQUE'])
warning_count = len(df_health[df_health['status'] == 'ATTENTION'])
total_reorder_budget_xof = df_health['reorder_cost_xof'].sum()

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">PRODUITS SUIVIS</div>
            <div class="kpi-value">{total_products}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #ef4444;">
            <div class="kpi-title">ALERTES STOCK CRITIQUE</div>
            <div class="kpi-value" style="color: #ef4444;">{critical_count}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #f59e0b;">
            <div class="kpi-title">AVERTISSEMENTS STOCK</div>
            <div class="kpi-value" style="color: #f59e0b;">{warning_count}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #3b82f6;">
            <div class="kpi-title">BUDGET RÉAPPROVISONNEMENT</div>
            <div class="kpi-value" style="color: #3b82f6;">{total_reorder_budget_xof:,.0f} FCFA</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Bannières d'alertes en direct
critical_items = df_health[df_health['status'] == 'CRITIQUE']
if len(critical_items) > 0:
    for _, item in critical_items.iterrows():
        st.error(f"🚨 **ALERTE COMMANDE URGENTE** : Le produit **{item['product_name']}** (Stock actuel: {item['current_stock']} unités) risque la rupture dans **{item['days_of_stock_left']} jours**. Commande recommandée : **{item['recommended_reorder_qty']} unités** ({item['reorder_cost_xof']:,.0f} FCFA).")

# Sélection de produit pour visualisations détaillées
st.subheader("📈 Historique des Ventes & Prédiction IA sur 30 Jours")

product_names = df_health['product_name'].tolist()
selected_prod_name = st.selectbox("Sélectionner un produit pour analyser sa courbe :", product_names)

selected_prod_info = df_health[df_health['product_name'] == selected_prod_name].iloc[0]
prod_id = selected_prod_info['product_id']

# Extrait de l'historique du produit
df_raw['date'] = pd.to_datetime(df_raw['date'])
df_prod_hist = df_raw[df_raw['product_id'] == prod_id].sort_values('date').copy()

# Assemblage des prédictions
future_sales = selected_prod_info['future_sales_list']
last_hist_date = df_prod_hist['date'].max()
future_dates = [last_hist_date + timedelta(days=i) for i in range(1, len(future_sales) + 1)]

df_future = pd.DataFrame({
    'date': future_dates,
    'units_sold': future_sales,
    'type': 'Prédiction ML'
})

df_prod_hist['type'] = 'Historique Réel'

# Graphique Plotly
fig = go.Figure()

# Historique
fig.add_trace(go.Scatter(
    x=df_prod_hist['date'],
    y=df_prod_hist['units_sold'],
    mode='lines',
    name='Ventes Historiques',
    line=dict(color='#0284c7', width=2)
))

# Prédictions
fig.add_trace(go.Scatter(
    x=df_future['date'],
    y=df_future['units_sold'],
    mode='lines+markers',
    name='Prédiction IA (Machine Learning)',
    line=dict(color='#10b981', width=2.5, dash='dash'),
    marker=dict(size=5)
))

# Ligne de Seuil de réapprovisionnement
fig.add_hline(
    y=selected_prod_info['reorder_point'],
    line_dash="dot",
    line_color="#f59e0b",
    annotation_text=f"Seuil Alerte ({selected_prod_info['reorder_point']} u)",
    annotation_position="bottom right"
)

fig.update_layout(
    template="plotly_dark",
    height=420,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis_title="Date",
    yaxis_title="Ventes (Unités)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# Tableau Synthétique des Réapprovisionnements
st.subheader("📋 Tableau de Bord Santé des Stocks & Recommandations de Commande")

df_table_display = df_health[[
    'product_name', 'category', 'current_stock', 'reorder_point',
    'avg_daily_demand', 'forecasted_demand_30d', 'days_of_stock_left',
    'recommended_reorder_qty', 'reorder_cost_xof', 'status_msg'
]].rename(columns={
    'product_name': 'Produit',
    'category': 'Catégorie',
    'current_stock': 'Stock Actuel',
    'reorder_point': 'Seuil Alerte',
    'avg_daily_demand': 'Ventes/Jour Még',
    'forecasted_demand_30d': 'Demande Prévue (30j)',
    'days_of_stock_left': 'Autonomie (Jours)',
    'recommended_reorder_qty': 'Commande Recommandée',
    'reorder_cost_xof': 'Coût Estimé (FCFA)',
    'status_msg': 'Statut Stock'
})

st.dataframe(
    df_table_display,
    use_container_width=True,
    hide_index=True
)

# Exportation Bon de Commande CSV
csv_po = df_table_display.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Générer & Télécharger le Bon de Commande (CSV)",
    data=csv_po,
    file_name=f"bon_de_commande_reapprovisionnement_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv"
)
