import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Page Configuration
st.set_page_config(
    page_title="Grow More RRG Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark Theme Custom Styling
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    div[data-testid="metric-container"] { 
        background-color: #111827; 
        border: 1px solid #1f2937; 
        border-radius: 8px; 
        padding: 10px; 
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header
st.title("📈 Live Sector Relative Rotation Graph (RRG)")
st.caption(
    "NSE Sector Rotation & Relative Strength Dashboard — Powered by Yahoo Finance API"
)

# Sector & Ticker Configuration
SECTORS = {
    "Nifty Bank": "^CNXBANK",
    "Nifty IT": "^CNXIT",
    "Nifty Auto": "^CNXAUTO",
    "Nifty Metal": "^CNXMETAL",
    "Nifty Pharma": "^CNXPHARMA",
    "Nifty FMCG": "^CNXFMCG",
    "Nifty Energy": "^CNXENERGY",
    "Nifty Realty": "^CNXREALTY",
    "Nifty Infra": "^CNXINFRA",
}

SECTOR_COLORS = {
    "Nifty Bank": "#10B981",
    "Nifty IT": "#EF4444",
    "Nifty Auto": "#3B82F6",
    "Nifty Metal": "#F59E0B",
    "Nifty Pharma": "#8B5CF6",
    "Nifty FMCG": "#EC4899",
    "Nifty Energy": "#14B8A6",
    "Nifty Realty": "#F97316",
    "Nifty Infra": "#6366F1",
}

# Sidebar Controls
st.sidebar.header("⚙️ Dashboard Controls")
timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    options=["1d", "1wk"],
    index=1,
    format_func=lambda x: "Daily Rotation" if x == "1d" else "Weekly Rotation",
)
tail_len = st.sidebar.slider(
    "Tail Length (Periods)", min_value=2, max_value=15, value=5
)
benchmark_ticker = "^NSEI"


# Fetch & Calculate RRG Metrics
@st.cache_data(ttl=300)
def load_rrg_data(interval, period_len=14):
    tickers = list(SECTORS.values()) + [benchmark_ticker]
    df = yf.download(tickers, period="1y", interval=interval, progress=False)[
        "Close"
    ]

    if interval == "1wk":
        df = df.resample("W").last()

    rrg_dict = {}
    for name, ticker in SECTORS.items():
        if ticker in df.columns and benchmark_ticker in df.columns:
            # 1. Raw RS
            rs = (df[ticker] / df[benchmark_ticker]) * 100

            # 2. RS-Ratio
            rs_mean = rs.rolling(window=period_len).mean()
            rs_std = rs.rolling(window=period_len).std()
            rs_ratio = 100 + ((rs - rs_mean) / (rs_std + 1e-6)) * 10

            # 3. RS-Momentum
            ratio_mean = rs_ratio.rolling(window=period_len).mean()
            ratio_std = rs_ratio.rolling(window=period_len).std()
            rs_momentum = 100 + (
                (rs_ratio - ratio_mean) / (ratio_std + 1e-6)
            ) * 10

            data = (
                pd.DataFrame({"ratio": rs_ratio, "momentum": rs_momentum})
                .dropna()
            )
            rrg_dict[name] = data

    return rrg_dict


with st.spinner("Fetching live market data..."):
    rrg_data = load_rrg_data(timeframe)


def get_quadrant(ratio, momentum):
    if ratio >= 100 and momentum >= 100:
        return "Leading", "#10B981"
    if ratio >= 100 and momentum < 100:
        return "Weakening", "#F59E0B"
    if ratio < 100 and momentum < 100:
        return "Lagging", "#EF4444"
    return "Improving", "#3B82F6"


# Layout Construction
col_chart, col_sidebar = st.columns([3, 1])

fig = go.Figure()
min_x, max_x, min_y, max_y = 98, 102, 98, 102
sector_summary = []

for sector, df in rrg_data.items():
    history = df.tail(tail_len)
    if history.empty:
        continue

    x_vals = history["ratio"].values
    y_vals = history["momentum"].values
    head_x, head_y = x_vals[-1], y_vals[-1]

    min_x, max_x = min(min_x, min(x_vals)), max(max_x, max(x_vals))
    min_y, max_y = min(min_y, min(y_vals)), max(max_y, max(y_vals))

    quad, quad_color = get_quadrant(head_x, head_y)
    color = SECTOR_COLORS.get(sector, "#3B82F6")

    sector_summary.append(
        {
            "Sector": sector,
            "RS-Ratio": round(head_x, 2),
            "RS-Momentum": round(head_y, 2),
            "Quadrant": quad,
        }
    )

    # Dotted Tail
    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            line=dict(color=color, width=2, dash="dot"),
            showlegend=False,
            hoverinfo="none",
        )
    )

    # Head Marker
    fig.add_trace(
        go.Scatter(
            x=[head_x],
            y=[head_y],
            mode="markers+text",
            name=sector,
            text=[sector],
            textposition="top center",
            textfont=dict(color="#F3F4F6", size=11),
            marker=dict(size=12, color=color),
            hovertemplate=f"<b>{sector}</b><br>RS-Ratio: {head_x:.2f}<br>RS-Momentum: {head_y:.2f}<br>Quadrant: {quad}<extra></extra>",
        )
    )

# Dynamic Bounds Calculation
padding_x = max(abs(100 - min_x), abs(max_x - 100)) + 1.5
padding_y = max(abs(100 - min_y), abs(max_y - 100)) + 1.5
x_range = [100 - padding_x, 100 + padding_x]
y_range = [100 - padding_y, 100 + padding_y]

# Chart Layout & Background Quadrants
fig.update_layout(
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    height=650,
    showlegend=False,
    xaxis=dict(
        title="RS-Ratio (Relative Strength)",
        range=x_range,
        gridcolor="#1F2937",
        color="#9CA3AF",
        zeroline=False,
    ),
    yaxis=dict(
        title="RS-Momentum (Rate of Change)",
        range=y_range,
        gridcolor="#1F2937",
        color="#9CA3AF",
        zeroline=False,
    ),
    shapes=[
        dict(
            type="rect",
            x0=100,
            x1=x_range[1],
            y0=100,
            y1=y_range[1],
            fillcolor="rgba(16, 185, 129, 0.08)",
            line_width=0,
            layer="below",
        ),
        dict(
            type="rect",
            x0=100,
            x1=x_range[1],
            y0=y_range[0],
            y1=100,
            fillcolor="rgba(245, 158, 11, 0.08)",
            line_width=0,
            layer="below",
        ),
        dict(
            type="rect",
            x0=x_range[0],
            x1=100,
            y0=y_range[0],
            y1=100,
            fillcolor="rgba(239, 68, 68, 0.08)",
            line_width=0,
            layer="below",
        ),
        dict(
            type="rect",
            x0=x_range[0],
            x1=100,
            y0=100,
            y1=y_range[1],
            fillcolor="rgba(59, 130, 246, 0.08)",
            line_width=0,
            layer="below",
        ),
        dict(
            type="line",
            x0=100,
            x1=100,
            y0=y_range[0],
            y1=y_range[1],
            line=dict(color="#4B5563", width=1.5, dash="dash"),
        ),
        dict(
            type="line",
            x0=x_range[0],
            x1=x_range[1],
            y0=100,
            y1=100,
            line=dict(color="#4B5563", width=1.5, dash="dash"),
        ),
    ],
    annotations=[
        dict(
            x=(100 + x_range[1]) / 2,
            y=(100 + y_range[1]) / 2,
            text="<b>LEADING</b>",
            showarrow=False,
            font=dict(color="rgba(16, 185, 129, 0.3)", size=24),
        ),
        dict(
            x=(100 + x_range[1]) / 2,
            y=(100 + y_range[0]) / 2,
            text="<b>WEAKENING</b>",
            showarrow=False,
            font=dict(color="rgba(245, 158, 11, 0.3)", size=24),
        ),
        dict(
            x=(100 + x_range[0]) / 2,
            y=(100 + y_range[0]) / 2,
            text="<b>LAGGING</b>",
            showarrow=False,
            font=dict(color="rgba(239, 68, 68, 0.3)", size=24),
        ),
        dict(
            x=(100 + x_range[0]) / 2,
            y=(100 + y_range[1]) / 2,
            text="<b>IMPROVING</b>",
            showarrow=False,
            font=dict(color="rgba(59, 130, 246, 0.3)", size=24),
        ),
    ],
)

with col_chart:
    st.plotly_chart(fig, use_container_width=True)

# Sidebar Sector Metrics
with col_sidebar:
    st.subheader("📌 Sector Status")
    for item in sector_summary:
        st.metric(
            label=item["Sector"],
            value=item["Quadrant"],
            delta=f"Ratio: {item['RS-Ratio']} | Mom: {item['RS-Momentum']}",
        )