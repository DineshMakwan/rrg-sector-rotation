import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Page Configuration
st.set_page_config(
    page_title="Grow More Trading Institute - RRG",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Theme & Institute Branding)
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    
    /* Branding Banner */
    .brand-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0f172a 100%);
        padding: 16px 24px;
        border-radius: 12px;
        border-left: 6px solid #3b82f6;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .brand-title { font-size: 1.8rem; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: 0.5px; }
    .brand-subtitle { font-size: 0.95rem; color: #9ca3af; margin-top: 4px; }
    .brand-tag {
        background-color: #2563eb;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        vertical-align: middle;
    }

    /* Sector Summary Cards & Table */
    .table-container {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
        margin-top: 25px;
    }
    .status-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .bg-leading { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .bg-improving { background-color: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid #3b82f6; }
    .bg-weakening { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    .bg-lagging { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }

    /* Footer Branding */
    .footer-text {
        text-align: center;
        color: #6b7280;
        font-size: 0.85rem;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #1f2937;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Branding Banner
st.markdown(
    """
    <div class="brand-header">
        <div class="brand-title">
            GROW MORE TRADING INSTITUTE 
            <span class="brand-tag">LIVE RRG ANALYTICS</span>
        </div>
        <div class="brand-subtitle">Real-time NSE Sector Rotation & Relative Strength Matrix</div>
    </div>
""",
    unsafe_allow_html=True,
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
st.sidebar.header("⚙️ Controls & Parameters")
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


with st.spinner("Fetching live market data from Yahoo Finance..."):
    rrg_data = load_rrg_data(timeframe)


def get_quadrant(ratio, momentum):
    if ratio >= 100 and momentum >= 100:
        return (
            "Leading",
            "🚀 Bullish Momentum & Strong RS",
            "bg-leading",
            "#10B981",
        )
    if ratio >= 100 and momentum < 100:
        return (
            "Weakening",
            "⚠️ RS High but Momentum Slowing",
            "bg-weakening",
            "#F59E0B",
        )
    if ratio < 100 and momentum < 100:
        return (
            "Lagging",
            "🔻 Bearish Momentum & Weak RS",
            "bg-lagging",
            "#EF4444",
        )
    return (
        "Improving",
        "⚡ RS Weak but Momentum Gaining",
        "bg-improving",
        "#3B82F6",
    )


# Chart Logic
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

    quad_name, desc, badge_cls, quad_color = get_quadrant(head_x, head_y)
    color = SECTOR_COLORS.get(sector, "#3B82F6")

    # Momentum Direction Arrow
    mom_change = head_y - y_vals[-2] if len(y_vals) > 1 else 0
    trend_icon = "⬆️ Up" if mom_change > 0 else "⬇️ Down"

    sector_summary.append(
        {
            "Sector": sector,
            "RS-Ratio": round(head_x, 2),
            "RS-Momentum": round(head_y, 2),
            "Quadrant": quad_name,
            "Status": desc,
            "BadgeClass": badge_cls,
            "Trend": trend_icon,
        }
    )

    # Dotted Tail Line
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
            hovertemplate=f"<b>{sector}</b><br>RS-Ratio: {head_x:.2f}<br>RS-Momentum: {head_y:.2f}<br>Quadrant: {quad_name}<extra></extra>",
        )
    )

# Axis Bounds Calculations
padding_x = max(abs(100 - min_x), abs(max_x - 100)) + 1.5
padding_y = max(abs(100 - min_y), abs(max_y - 100)) + 1.5
x_range = [100 - padding_x, 100 + padding_x]
y_range = [100 - padding_y, 100 + padding_y]

# Quadrant Styling
fig.update_layout(
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    height=600,
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

# Render Chart
st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# ENHANCED SECTOR ROTATION SUMMARY TABLE (GROW MORE TRADING INSTITUTE)
# -------------------------------------------------------------------

st.subheader("📊 Grow More Institute — Live Sector Matrix")

df_summary = pd.DataFrame(sector_summary)

# Quick Metric Counters Banner
m1, m2, m3, m4 = st.columns(4)
leading_cnt = len(df_summary[df_summary["Quadrant"] == "Leading"])
improving_cnt = len(df_summary[df_summary["Quadrant"] == "Improving"])
weakening_cnt = len(df_summary[df_summary["Quadrant"] == "Weakening"])
lagging_cnt = len(df_summary[df_summary["Quadrant"] == "Lagging"])

m1.metric(label="🚀 Leading Sectors", value=leading_cnt)
m2.metric(label="⚡ Improving Sectors", value=improving_cnt)
m3.metric(label="⚠️ Weakening Sectors", value=weakening_cnt)
m4.metric(label="🔻 Lagging Sectors", value=lagging_cnt)

# Detailed Sector Table Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📋 All Sectors",
        "🚀 Leading",
        "⚡ Improving",
        "⚠️ Weakening",
        "🔻 Lagging",
    ]
)


def render_styled_table(data_frame):
    if data_frame.empty:
        st.info("No sectors currently in this quadrant.")
        return

    table_html = """
    <table style="width:100%; border-collapse:collapse; background-color:#111827; border-radius:8px; overflow:hidden;">
        <thead>
            <tr style="background-color:#1f2937; text-align:left; color:#9ca3af; font-size:0.9rem;">
                <th style="padding:12px 16px;">Sector Name</th>
                <th style="padding:12px 16px;">Quadrant</th>
                <th style="padding:12px 16px;">RS-Ratio</th>
                <th style="padding:12px 16px;">RS-Momentum</th>
                <th style="padding:12px 16px;">Momentum Trend</th>
                <th style="padding:12px 16px;">Technical Status</th>
            </tr>
        </thead>
        <tbody>
    """
    for _, row in data_frame.iterrows():
        table_html += f"""
            <tr style="border-bottom: 1px solid #1f2937; color:#f3f4f6; font-size:0.9rem;">
                <td style="padding:12px 16px; font-weight:600;">{row['Sector']}</td>
                <td style="padding:12px 16px;"><span class="status-badge {row['BadgeClass']}">{row['Quadrant']}</span></td>
                <td style="padding:12px 16px; font-weight:500;">{row['RS-Ratio']}</td>
                <td style="padding:12px 16px; font-weight:500;">{row['RS-Momentum']}</td>
                <td style="padding:12px 16px;">{row['Trend']}</td>
                <td style="padding:12px 16px; color:#9ca3af; font-size:0.85rem;">{row['Status']}</td>
            </tr>
        """
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)


with tab1:
    render_styled_table(df_summary)

with tab2:
    render_styled_table(df_summary[df_summary["Quadrant"] == "Leading"])

with tab3:
    render_styled_table(df_summary[df_summary["Quadrant"] == "Improving"])

with tab4:
    render_styled_table(df_summary[df_summary["Quadrant"] == "Weakening"])

with tab5:
    render_styled_table(df_summary[df_summary["Quadrant"] == "Lagging"])

# Footer
st.markdown(
    """
    <div class="footer-text">
        © 2026 <b>Grow More Trading Institute</b> | Live Market Sector Rotation Dashboard
    </div>
""",
    unsafe_allow_html=True,
)
