import pandas as pd
import plotly_express as px
import streamlit as st

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="NFL Combine Dashboard", page_icon="🏈", layout="wide")

# ── Carregar dados ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("NFL_Combine_Since_2000.csv")

    # Converter colunas numéricas (algumas têm "DNP" = Did Not Participate)
    numeric_cols = ["40-yd Dash", "Vertical Jump", "Bench Press",
                    "Broad Jump", "3-Cone Drill", "20-yd Shuttle"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.header("🏈 NFL Scouting Combine — Dashboard (2000–presente)")
st.write(
    "Explore o desempenho de mais de 8.500 atletas que participaram do "
    "NFL Scouting Combine desde o ano 2000."
)

# ── Filtros na barra lateral ─────────────────────────────────────────────────
st.sidebar.header("Filtros")

all_positions = sorted(df["Position"].dropna().unique())
selected_positions = st.sidebar.multiselect(
    "Posição", all_positions, default=all_positions
)

year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
selected_years = st.sidebar.slider(
    "Intervalo de anos", year_min, year_max, (year_min, year_max)
)

drafted_filter = st.sidebar.radio(
    "Status no Draft", ["Todos", "Apenas draftados", "Apenas não draftados"]
)

# ── Aplicar filtros ──────────────────────────────────────────────────────────
filtered = df[
    df["Position"].isin(selected_positions) &
    df["Year"].between(*selected_years)
]

if drafted_filter == "Apenas draftados":
    filtered = filtered[filtered["Drafted"] == "Y"]
elif drafted_filter == "Apenas não draftados":
    filtered = filtered[filtered["Drafted"] == "N"]

# ── Métricas rápidas ─────────────────────────────────────────────────────────
st.subheader("Resumo")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de atletas", f"{len(filtered):,}")
col2.metric("Draftados", f"{(filtered['Drafted'] == 'Y').sum():,}")
col3.metric("Posições distintas", filtered["Position"].nunique())
col4.metric("Anos cobertos", filtered["Year"].nunique())

st.divider()

# ── Visualizações ────────────────────────────────────────────────────────────
st.subheader("Visualizações")

# Histograma
show_hist = st.checkbox("📊 Mostrar histograma")

if show_hist:
    st.write("### Distribuição do tempo no 40 jardas por posição")
    fig_hist = px.histogram(
        filtered.dropna(subset=["40-yd Dash"]),
        x="40-yd Dash",
        color="Position",
        nbins=50,
        title="Distribuição do tempo no 40 jardas (segundos)",
        labels={"40-yd Dash": "40 jardas (s)"},
        opacity=0.75,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# Gráfico de dispersão
show_scatter = st.checkbox("🔵 Mostrar gráfico de dispersão")

if show_scatter:
    st.write("### Peso × Tempo no 40 jardas")
    fig_scatter = px.scatter(
        filtered.dropna(subset=["40-yd Dash", "Weight"]),
        x="Weight",
        y="40-yd Dash",
        color="Position",
        hover_data=["First", "Last", "School", "Year"],
        title="Peso (lbs) vs. Tempo no 40 jardas (s)",
        labels={"Weight": "Peso (lbs)", "40-yd Dash": "40 jardas (s)"},
        opacity=0.6,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── Tabela de dados ──────────────────────────────────────────────────────────
with st.expander("🗂️ Ver tabela de dados filtrados"):
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
