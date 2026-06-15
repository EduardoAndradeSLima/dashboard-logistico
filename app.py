import html
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_DIR = Path(__file__).parent
DATA_PATH = APP_DIR / "data" / "entregas.csv"
REQUIRED_COLUMNS = {
    "id_entrega",
    "transportadora",
    "regiao",
    "prazo_dias",
    "dias_reais",
}

COLORS = {
    "navy": "#172033",
    "purple": "#7C3AED",
    "violet": "#A78BFA",
    "coral": "#F97360",
    "amber": "#F59E0B",
    "green": "#10B981",
    "blue": "#3B82F6",
    "muted": "#687386",
    "grid": "#E8EAF1",
}


st.set_page_config(
    page_title="Radar Logístico",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        h1, h2, h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -0.03em; }
        .stApp { background: #F7F8FC; }
        [data-testid="stHeader"] { background: rgba(247, 248, 252, 0.92); }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #141A2B 0%, #202746 100%);
            border-right: 0;
        }
        [data-testid="stSidebar"] * { color: #F7F7FB; }
        [data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {
            background-color: #7C3AED;
        }
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background-color: #2B3354;
            border-color: #464F76;
        }
        [data-testid="stSidebar"] .stFileUploader section {
            background-color: #252D4B;
            border-color: #626B91;
        }
        .block-container { max-width: 1500px; padding-top: 2rem; padding-bottom: 3rem; }
        .hero {
            background: linear-gradient(120deg, #172033 0%, #262B55 58%, #5731A8 100%);
            padding: 2rem 2.2rem;
            border-radius: 22px;
            color: white;
            position: relative;
            overflow: hidden;
            box-shadow: 0 18px 45px rgba(23, 32, 51, 0.14);
            margin-bottom: 1.25rem;
        }
        .hero::after {
            content: '';
            position: absolute;
            width: 240px;
            height: 240px;
            border-radius: 50%;
            right: -80px;
            top: -110px;
            background: rgba(255,255,255,0.08);
        }
        .hero-kicker { color: #C4B5FD; font-size: .78rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
        .hero h1 { color: white; font-size: clamp(2rem, 4vw, 3.25rem); margin: .35rem 0 .25rem; }
        .hero p { color: #D8DCEC; max-width: 760px; font-size: 1.02rem; margin: 0; }
        .updated-pill {
            display: inline-block;
            margin-top: 1.1rem;
            padding: .45rem .75rem;
            border: 1px solid rgba(255,255,255,.18);
            background: rgba(255,255,255,.09);
            border-radius: 999px;
            color: #F3F0FF;
            font-size: .82rem;
        }
        .metric-card {
            background: white;
            border: 1px solid #ECEEF4;
            padding: 1.15rem 1.2rem;
            border-radius: 17px;
            min-height: 142px;
            box-shadow: 0 8px 24px rgba(23, 32, 51, .05);
        }
        .metric-label { color: #687386; font-size: .78rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; }
        .metric-value { color: #172033; font-family: 'Manrope', sans-serif; font-size: 2rem; font-weight: 800; line-height: 1.2; margin: .55rem 0 .2rem; }
        .metric-detail { color: #778095; font-size: .84rem; }
        .metric-accent { width: 38px; height: 4px; border-radius: 20px; margin-top: .8rem; }
        .section-title { color: #172033; font-family: 'Manrope', sans-serif; font-size: 1.22rem; font-weight: 800; margin: 1.5rem 0 .15rem; }
        .section-subtitle { color: #778095; font-size: .88rem; margin-bottom: .8rem; }
        .alert-box {
            padding: 1rem 1.15rem;
            border-radius: 14px;
            border-left: 5px solid #F97360;
            background: #FFF1EE;
            color: #7A2D25;
            margin: .25rem 0 1rem;
        }
        .good-box {
            padding: 1rem 1.15rem;
            border-radius: 14px;
            border-left: 5px solid #10B981;
            background: #ECFDF5;
            color: #075D44;
            margin: .25rem 0 1rem;
        }
        .sidebar-brand { padding: .6rem .15rem 1.1rem; }
        .sidebar-brand strong { font-family: 'Manrope', sans-serif; font-size: 1.35rem; }
        .sidebar-brand span { color: #AEB6D2 !important; font-size: .82rem; display: block; margin-top: .2rem; }
        .priority-chip { font-weight: 700; }
        div[data-testid="stDataFrame"] { border: 1px solid #E8EAF1; border-radius: 14px; overflow: hidden; }
        .stDownloadButton button {
            border-radius: 12px;
            border: 0;
            background: #172033;
            color: white;
            font-weight: 700;
        }
        .stDownloadButton button:hover { background: #7C3AED; color: white; }
        @media (max-width: 700px) {
            .block-container { padding-top: 1rem; }
            .hero { padding: 1.5rem; border-radius: 18px; }
            .metric-card { min-height: 125px; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def prepare_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate the input and create the operational metrics used by the app."""
    missing = REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError("Colunas ausentes: " + ", ".join(sorted(missing)))

    df = raw.copy()
    for column in ["id_entrega", "prazo_dias", "dias_reais"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df[["id_entrega", "prazo_dias", "dias_reais"]].isna().any().any():
        raise ValueError("ID, prazo e dias reais devem conter apenas números válidos.")
    if (df["prazo_dias"] <= 0).any():
        raise ValueError("O prazo deve ser maior que zero.")
    if (df["dias_reais"] < 0).any():
        raise ValueError("Os dias reais não podem ser negativos.")

    df["id_entrega"] = df["id_entrega"].astype(int)
    df["prazo_dias"] = df["prazo_dias"].astype(int)
    df["dias_reais"] = df["dias_reais"].astype(int)
    df["dias_atraso"] = (df["dias_reais"] - df["prazo_dias"]).clip(lower=0)
    df["variacao_dias"] = df["dias_reais"] - df["prazo_dias"]
    df["status"] = df["dias_atraso"].map(lambda value: "Atrasada" if value > 0 else "No prazo")
    df["prioridade"] = pd.cut(
        df["dias_atraso"],
        bins=[-1, 0, 2, 4, float("inf")],
        labels=["No prazo", "Moderada", "Alta", "Crítica"],
    ).astype(str)
    df["desvio_percentual"] = (df["variacao_dias"] / df["prazo_dias"] * 100).round(1)
    return df


@st.cache_data
def load_default_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def plot_layout(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=16, r=16, t=35, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=COLORS["navy"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", font_size=13),
    )
    fig.update_xaxes(showgrid=False, linecolor=COLORS["grid"])
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False)
    return fig


def metric_card(label: str, value: str, detail: str, accent: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-detail">{detail}</div>
            <div class="metric-accent" style="background:{accent}"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <strong>Radar Logístico</strong>
            <span>Central de monitoramento operacional</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Atualizar base (CSV)", type=["csv"])

try:
    source_df = pd.read_csv(uploaded_file) if uploaded_file else load_default_data()
    data = prepare_data(source_df)
except Exception as error:
    st.error(f"Nao foi possivel carregar a base: {error}")
    st.stop()

with st.sidebar:
    st.markdown("### Filtros")
    selected_carriers = st.multiselect(
        "Transportadora",
        sorted(data["transportadora"].unique()),
        default=sorted(data["transportadora"].unique()),
    )
    selected_regions = st.multiselect(
        "Região",
        sorted(data["regiao"].unique()),
        default=sorted(data["regiao"].unique()),
    )
    selected_status = st.multiselect(
        "Status",
        ["Atrasada", "No prazo"],
        default=["Atrasada", "No prazo"],
    )
    selected_priorities = st.multiselect(
        "Prioridade",
        ["Crítica", "Alta", "Moderada", "No prazo"],
        default=["Crítica", "Alta", "Moderada", "No prazo"],
    )
    min_delay, max_delay = int(data["dias_atraso"].min()), int(data["dias_atraso"].max())
    if min_delay == max_delay:
        delay_range = (min_delay, max_delay)
        st.caption(f"Faixa de atraso disponível: {min_delay} dia(s)")
    else:
        delay_range = st.slider(
            "Faixa de atraso (dias)",
            min_value=min_delay,
            max_value=max_delay,
            value=(min_delay, max_delay),
        )
    st.caption("Os indicadores respondem a todos os filtros selecionados.")

filtered = data[
    data["transportadora"].isin(selected_carriers)
    & data["regiao"].isin(selected_regions)
    & data["status"].isin(selected_status)
    & data["prioridade"].isin(selected_priorities)
    & data["dias_atraso"].between(delay_range[0], delay_range[1])
].copy()


st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">Inteligência operacional</div>
        <h1>Entregas sob controle.</h1>
        <p>Visão executiva para detectar gargalos, comparar parceiros e agir primeiro onde o atraso custa mais.</p>
        <span class="updated-pill">Base didática consolidada | Regra: dias reais &gt; prazo</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("Nenhuma entrega corresponde aos filtros atuais. Ajuste as selecoes na barra lateral.")
    st.stop()

total = len(filtered)
late = filtered[filtered["status"] == "Atrasada"]
late_count = len(late)
late_rate = late_count / total * 100
avg_delay = late["dias_atraso"].mean() if late_count else 0
on_time_rate = 100 - late_rate
critical_count = int((filtered["prioridade"] == "Crítica").sum())

metric_columns = st.columns(5)
with metric_columns[0]:
    metric_card("Entregas analisadas", f"{total}", "volume no recorte atual", COLORS["blue"])
with metric_columns[1]:
    metric_card("Taxa de atraso", f"{late_rate:.0f}%", f"{late_count} entrega(s) atrasada(s)", COLORS["coral"])
with metric_columns[2]:
    metric_card("Atraso médio", f"{avg_delay:.1f} d", "considerando apenas atrasadas", COLORS["amber"])
with metric_columns[3]:
    metric_card("No prazo", f"{on_time_rate:.0f}%", "cumprimento no recorte", COLORS["green"])
with metric_columns[4]:
    metric_card("Casos críticos", f"{critical_count}", "atrasos de 5 dias ou mais", COLORS["purple"])

if late_count:
    worst = late.sort_values(["dias_atraso", "desvio_percentual"], ascending=False).iloc[0]
    worst_carrier = html.escape(str(worst["transportadora"]))
    worst_region = html.escape(str(worst["regiao"]))
    st.markdown(
        f"""
        <div class="alert-box">
            <strong>Atenção imediata:</strong> entrega {int(worst['id_entrega'])} da {worst_carrier}
            acumula <strong>{int(worst['dias_atraso'])} dias de atraso</strong> na região {worst_region}.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="good-box"><strong>Operação regular:</strong> nenhuma entrega atrasada neste recorte.</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-title">Fila de ação prioritária</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Os maiores desvios aparecem primeiro para orientar a atuação da equipe.</div>',
    unsafe_allow_html=True,
)

priority_order = ["Crítica", "Alta", "Moderada", "No prazo"]
priority_rank = {name: index for index, name in enumerate(priority_order)}
priority_table = filtered.copy()
priority_table["ordem"] = priority_table["prioridade"].map(priority_rank)
priority_table = priority_table.sort_values(["ordem", "dias_atraso"], ascending=[True, False])
priority_table["prioridade_visual"] = priority_table["prioridade"].replace(
    {"Crítica": "CRÍTICA", "Alta": "ALTA", "Moderada": "MODERADA", "No prazo": "NO PRAZO"}
)

display_table = priority_table[
    [
        "prioridade_visual",
        "id_entrega",
        "transportadora",
        "regiao",
        "prazo_dias",
        "dias_reais",
        "dias_atraso",
        "status",
    ]
].rename(
    columns={
        "prioridade_visual": "Prioridade",
        "id_entrega": "Entrega",
        "transportadora": "Transportadora",
        "regiao": "Região",
        "prazo_dias": "Prazo",
        "dias_reais": "Realizado",
        "dias_atraso": "Atraso",
        "status": "Status",
    }
)

st.dataframe(
    display_table,
    use_container_width=True,
    hide_index=True,
    height=min(430, 42 + 35 * len(display_table)),
    column_config={
        "Atraso": st.column_config.ProgressColumn(
            "Atraso",
            help="Dias além do prazo contratado",
            format="%d dias",
            min_value=0,
            max_value=max(1, int(filtered["dias_atraso"].max())),
        ),
    },
)

tab_overview, tab_carriers, tab_regions, tab_detail = st.tabs(
    ["Visão operacional", "Transportadoras", "Regiões", "Base detalhada"]
)

with tab_overview:
    chart_col_1, chart_col_2 = st.columns([1.35, 1])
    with chart_col_1:
        sequence = filtered.sort_values("id_entrega")
        trend = go.Figure()
        trend.add_trace(
            go.Scatter(
                x=sequence["id_entrega"],
                y=sequence["prazo_dias"],
                name="Prazo",
                mode="lines+markers",
                line=dict(color=COLORS["violet"], width=3, dash="dot"),
                marker=dict(size=7),
            )
        )
        trend.add_trace(
            go.Scatter(
                x=sequence["id_entrega"],
                y=sequence["dias_reais"],
                name="Dias reais",
                mode="lines+markers",
                line=dict(color=COLORS["navy"], width=3),
                marker=dict(size=8, color=sequence["dias_atraso"], colorscale="OrRd", showscale=False),
            )
        )
        trend.update_layout(title="Prazo x tempo real por sequência de entrega")
        trend.update_xaxes(title="ID da entrega", dtick=1)
        trend.update_yaxes(title="Dias")
        st.plotly_chart(plot_layout(trend), use_container_width=True)

    with chart_col_2:
        status_counts = filtered["status"].value_counts().reindex(["Atrasada", "No prazo"], fill_value=0)
        donut = go.Figure(
            go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=.68,
                marker=dict(colors=[COLORS["coral"], COLORS["green"]]),
                textinfo="label+percent",
                hovertemplate="%{label}: %{value} entrega(s)<extra></extra>",
            )
        )
        donut.add_annotation(
            text=f"<b>{late_rate:.0f}%</b><br><span style='font-size:12px'>atrasadas</span>",
            x=.5,
            y=.5,
            showarrow=False,
            font=dict(size=21, color=COLORS["navy"]),
        )
        donut.update_layout(title="Saude do prazo", showlegend=False)
        st.plotly_chart(plot_layout(donut), use_container_width=True)

with tab_carriers:
    carrier_summary = (
        filtered.groupby("transportadora", as_index=False)
        .agg(
            entregas=("id_entrega", "count"),
            atrasadas=("dias_atraso", lambda values: int((values > 0).sum())),
            atraso_total=("dias_atraso", "sum"),
            pior_atraso=("dias_atraso", "max"),
        )
    )
    carrier_summary["taxa_atraso"] = carrier_summary["atrasadas"] / carrier_summary["entregas"] * 100
    carrier_summary["atraso_medio"] = carrier_summary.apply(
        lambda row: row["atraso_total"] / row["atrasadas"] if row["atrasadas"] else 0,
        axis=1,
    )
    carrier_summary = carrier_summary.sort_values(["taxa_atraso", "atraso_medio"], ascending=False)

    carrier_fig = px.bar(
        carrier_summary,
        x="transportadora",
        y="taxa_atraso",
        color="atraso_medio",
        text=carrier_summary["taxa_atraso"].map(lambda value: f"{value:.0f}%"),
        color_continuous_scale=["#C4B5FD", "#7C3AED", "#F97360"],
        labels={"transportadora": "Transportadora", "taxa_atraso": "Taxa de atraso (%)", "atraso_medio": "Atraso médio"},
        title="Indice de atraso por transportadora",
    )
    carrier_fig.update_traces(textposition="outside", cliponaxis=False)
    carrier_fig.update_layout(coloraxis_colorbar=dict(title="Media<br>(dias)"))
    st.plotly_chart(plot_layout(carrier_fig, 400), use_container_width=True)

    st.dataframe(
        carrier_summary.rename(
            columns={
                "transportadora": "Transportadora",
                "entregas": "Entregas",
                "atrasadas": "Atrasadas",
                "taxa_atraso": "Taxa de atraso (%)",
                "atraso_medio": "Atraso médio (dias)",
                "pior_atraso": "Pior atraso (dias)",
                "atraso_total": "Atraso acumulado",
            }
        ).style.format({"Taxa de atraso (%)": "{:.1f}", "Atraso médio (dias)": "{:.1f}"}),
        use_container_width=True,
        hide_index=True,
    )

with tab_regions:
    region_summary = (
        filtered.groupby("regiao", as_index=False)
        .agg(
            entregas=("id_entrega", "count"),
            atrasadas=("dias_atraso", lambda values: int((values > 0).sum())),
            dias_atraso=("dias_atraso", "sum"),
        )
    )
    region_summary["taxa_atraso"] = region_summary["atrasadas"] / region_summary["entregas"] * 100
    region_summary = region_summary.sort_values(["taxa_atraso", "dias_atraso"], ascending=True)

    region_fig = px.bar(
        region_summary,
        y="regiao",
        x="taxa_atraso",
        orientation="h",
        color="dias_atraso",
        text=region_summary["taxa_atraso"].map(lambda value: f"{value:.0f}%"),
        color_continuous_scale=["#BFDBFE", "#7C3AED", "#F97360"],
        labels={"regiao": "Região", "taxa_atraso": "Taxa de atraso (%)", "dias_atraso": "Dias acumulados"},
        title="Regiões críticas por incidência de atraso",
    )
    region_fig.update_traces(textposition="outside", cliponaxis=False)
    region_fig.update_xaxes(range=[0, 112])
    st.plotly_chart(plot_layout(region_fig, 400), use_container_width=True)

    critical_region = region_summary.sort_values(["taxa_atraso", "dias_atraso"], ascending=False).iloc[0]
    st.info(
        f"Região em destaque no recorte: {critical_region['regiao']} com "
        f"{critical_region['taxa_atraso']:.0f}% de entregas atrasadas e "
        f"{int(critical_region['dias_atraso'])} dias de atraso acumulado."
    )

with tab_detail:
    detail_columns = [
        "id_entrega",
        "transportadora",
        "regiao",
        "prazo_dias",
        "dias_reais",
        "dias_atraso",
        "desvio_percentual",
        "status",
        "prioridade",
    ]
    st.dataframe(filtered[detail_columns], use_container_width=True, hide_index=True)
    st.download_button(
        "Baixar recorte filtrado (CSV)",
        data=filtered[detail_columns].to_csv(index=False).encode("utf-8"),
        file_name="entregas_filtradas.csv",
        mime="text/csv",
    )

st.caption(
    "Dashboard acadêmico | A prioridade combina dias de atraso e permite que a gestão atue primeiro nos casos de maior impacto."
)
