from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Page Configuration
st.set_page_config(
    page_title="Grow More Trading Institute - Advanced RRG Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Dark Theme Styling & Institute Branding
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    
    .brand-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0f172a 100%);
        padding: 18px 24px;
        border-radius: 12px;
        border-left: 6px solid #3b82f6;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
    }
    .brand-title { font-size: 1.8rem; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: 0.5px; }
    .brand-subtitle { font-size: 0.95rem; color: #9ca3af; margin-top: 4px; }
    
    .live-container {
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(15, 23, 42, 0.6);
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid #1e293b;
    }
    .live-badge {
        background-color: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        letter-spacing: 1px;
    }
    .live-dot {
        height: 9px;
        width: 9px;
        background-color: #ef4444;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        box-shadow: 0 0 8px #ef4444;
        animation: pulse 1.2s infinite ease-in-out;
    }
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.3; transform: scale(0.85); }
        100% { opacity: 1; transform: scale(1); }
    }
    .clock-text {
        font-size: 0.9rem;
        color: #38bdf8;
        font-weight: 600;
        font-family: monospace;
    }

    /* Badges & Setup Cards */
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
    .bg-near-high { background-color: rgba(236, 72, 153, 0.2); color: #ec4899; border: 1px solid #ec4899; }
    .bg-normal-high { background-color: rgba(107, 114, 128, 0.2); color: #9ca3af; border: 1px solid #4b5563; }

    .setup-card-long {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid #10b981;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .setup-card-short {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

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
        <div>
            <div class="brand-title">GROW MORE TRADING INSTITUTE</div>
            <div class="brand-subtitle">Real-Time Sector RRG, Animated Rotations & AI Trade Intelligence</div>
        </div>
        <div class="live-container">
            <div class="live-badge">
                <span class="live-dot"></span>LIVE
            </div>
            <div id="live-clock" class="clock-text">⏰ Loading Clock...</div>
        </div>
    </div>

    <script>
    function updateClock() {
        const now = new Date();
        const options = { 
            timeZone: 'Asia/Kolkata', 
            hour12: true, 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            day: '2-digit',
            month: 'short'
        };
        const timeString = now.toLocaleString('en-IN', options);
        const clockElem = document.getElementById('live-clock');
        if(clockElem) {
            clockElem.innerText = '⏰ ' + timeString + ' IST';
        }
    }
    setInterval(updateClock, 1000);
    updateClock();
    </script>
""",
    unsafe_allow_html=True,
)

# 14 Primary NSE Sectors Mapping
SECTOR_MAP = {
    "Nifty Bank": {
        "index": "^NSEBANK",
        "stocks": {
            "HDFC Bank": "HDFCBANK.NS",
            "ICICI Bank": "ICICIBANK.NS",
            "SBI": "SBIN.NS",
            "Kotak Bank": "KOTAKBANK.NS",
            "Axis Bank": "AXISBANK.NS",
            "IndusInd Bank": "INDUSINDBK.NS",
        },
    },
    "Nifty IT": {
        "index": "^CNXIT",
        "stocks": {
            "TCS": "TCS.NS",
            "Infosys": "INFY.NS",
            "HCL Tech": "HCLTECH.NS",
            "Wipro": "WIPRO.NS",
            "Tech Mahindra": "TECHM.NS",
            "LTIMindtree": "LTIM.NS",
        },
    },
    "Nifty Auto": {
        "index": "^CNXAUTO",
        "stocks": {
            "Tata Motors": "TATAMOTORS.NS",
            "M&M": "M&M.NS",
            "Maruti": "MARUTI.NS",
            "Bajaj Auto": "BAJAJ-AUTO.NS",
            "Hero MotoCorp": "HEROMOTOCO.NS",
            "Eicher Motors": "EICHERMOT.NS",
        },
    },
    "Nifty Metal": {
        "index": "^CNXMETAL",
        "stocks": {
            "Tata Steel": "TATASTEEL.NS",
            "JSW Steel": "JSWSTEEL.NS",
            "Hindalco": "HINDALCO.NS",
            "Vedanta": "VEDL.NS",
            "Coal India": "COALINDIA.NS",
            "NMDC": "NMDC.NS",
        },
    },
    "Nifty Pharma": {
        "index": "^CNXPHARMA",
        "stocks": {
            "Sun Pharma": "SUNPHARMA.NS",
            "Cipla": "CIPLA.NS",
            "Dr. Reddy's": "DRREDDY.NS",
            "Divi's Lab": "DIVISLAB.NS",
            "Lupin": "LUPIN.NS",
            "Mankind": "MANKIND.NS",
        },
    },
    "Nifty FMCG": {
        "index": "^CNXFMCG",
        "stocks": {
            "ITC": "ITC.NS",
            "HUL": "HINDUNILVR.NS",
            "Britannia": "BRITANNIA.NS",
            "Tata Consumer": "TATACONSUM.NS",
            "Nestle": "NESTLEIND.NS",
            "VBL": "VBL.NS",
        },
    },
    "Nifty Realty": {
        "index": "^CNXREALTY",
        "stocks": {
            "DLF": "DLF.NS",
            "Lodha": "LODHA.NS",
            "Godrej Prop": "GODREJPROP.NS",
            "Oberoi Realty": "OBEROIRLTY.NS",
            "Phoenix Mills": "PHOENIXLTD.NS",
        },
    },
    "Nifty Energy": {
        "index": "^CNXENERGY",
        "stocks": {
            "Reliance": "RELIANCE.NS",
            "NTPC": "NTPC.NS",
            "ONGC": "ONGC.NS",
            "Power Grid": "POWERGRID.NS",
            "BPCL": "BPCL.NS",
            "IOC": "IOC.NS",
        },
    },
    "Nifty Infra": {
        "index": "^CNXINFRA",
        "stocks": {
            "L&T": "LT.NS",
            "Reliance": "RELIANCE.NS",
            "Bharti Airtel": "BHARTIARTL.NS",
            "NTPC": "NTPC.NS",
            "Power Grid": "POWERGRID.NS",
            "UltraTech": "ULTRACEMCO.NS",
        },
    },
    "Nifty Fin Service": {
        "index": "NIFTY_FIN_SERVICE.NS",
        "stocks": {
            "HDFC Bank": "HDFCBANK.NS",
            "ICICI Bank": "ICICIBANK.NS",
            "SBI": "SBIN.NS",
            "PFC": "PFC.NS",
            "REC": "REC.NS",
            "Chola Fin": "CHOLAFIN.NS",
        },
    },
    "Nifty PSU Bank": {
        "index": "^CNXPSUBANK",
        "stocks": {
            "SBI": "SBIN.NS",
            "Bank of Baroda": "BANKBARODA.NS",
            "PNB": "PNB.NS",
            "Canara Bank": "CANBK.NS",
            "Union Bank": "UNIONBANK.NS",
            "Indian Bank": "INDIANB.NS",
        },
    },
    "Nifty Media": {
        "index": "^CNXMEDIA",
        "stocks": {
            "ZEEL": "ZEEL.NS",
            "Sun TV": "SUNTV.NS",
            "PVR INOX": "PVRINOX.NS",
            "Nazara Tech": "NAZARA.NS",
            "TV18": "TV18BRDCST.NS",
        },
    },
    "Nifty Consumer Durables": {
        "index": "NIFTY_CONSR_DURBL.NS",
        "stocks": {
            "Dixon": "DIXON.NS",
            "Titan": "TITAN.NS",
            "Havells": "HAVELLS.NS",
            "Voltas": "VOLTAS.NS",
            "Crompton": "CROMPTON.NS",
            "Polycab": "POLYCAB.NS",
        },
    },
    "Nifty Healthcare": {
        "index": "NIFTY_HEALTHCARE.NS",
        "stocks": {
            "Sun Pharma": "SUNPHARMA.NS",
            "Cipla": "CIPLA.NS",
            "Apollo Hospitals": "APOLLOHOSP.NS",
            "Max Healthcare": "MAXHEALTH.NS",
            "Syngene": "SYNGENE.NS",
            "Dr Lal Path": "LALPATHLAB.NS",
        },
    },
}

BENCHMARK_SYMBOL = "^NSEI"  # Nifty 50 Benchmark

# Sidebar Controls
st.sidebar.header("⚙️ RRG Controls")
timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    options=["1d", "1wk"],
    index=1,
    format_func=lambda x: "Daily Rotation" if x == "1d" else "Weekly Rotation",
)
tail_len = st.sidebar.slider(
    "Tail Length (Periods)", min_value=2, max_value=15, value=5
)

st.sidebar.markdown("---")
st.sidebar.header("🔥 52-Week High Filters")
high_threshold = st.sidebar.slider(
    "Near 52W High Threshold (%)",
    min_value=1.0,
    max_value=15.0,
    value=5.0,
    step=0.5,
)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Stock Drill-Down")
selected_sector_for_stocks = st.sidebar.selectbox(
    "Select Sector to Analyze Stocks", options=list(SECTOR_MAP.keys()), index=0
)


# RRG Metric Calculation Engine
def calculate_rrg_metrics(data_df, item_ticker, bench_ticker, period_len=14):
    if item_ticker not in data_df.columns or bench_ticker not in data_df.columns:
        return None

    rs = (data_df[item_ticker] / data_df[bench_ticker]) * 100
    rs_mean = rs.rolling(window=period_len).mean()
    rs_std = rs.rolling(window=period_len).std()
    rs_ratio = 100 + ((rs - rs_mean) / (rs_std + 1e-6)) * 10

    ratio_mean = rs_ratio.rolling(window=period_len).mean()
    ratio_std = rs_ratio.rolling(window=period_len).std()
    rs_momentum = 100 + ((rs_ratio - ratio_mean) / (ratio_std + 1e-6)) * 10

    return pd.DataFrame({"ratio": rs_ratio, "momentum": rs_momentum}).dropna()


@st.cache_data(ttl=300)
def fetch_and_build_rrg(items_dict, benchmark_ticker_sym, interval):
    all_tickers = list(items_dict.values()) + [benchmark_ticker_sym]
    raw_data = yf.download(
        all_tickers, period="2y", interval=interval, progress=False
    )

    if isinstance(raw_data.columns, pd.MultiIndex):
        df_close = raw_data["Close"]
        df_high = raw_data["High"]
    else:
        df_close = raw_data[["Close"]]
        df_high = raw_data[["High"]]

    if interval == "1wk":
        df_close = df_close.resample("W").last()
        df_high = df_high.resample("W").max()

    rrg_results = {}
    for name, ticker in items_dict.items():
        metrics = calculate_rrg_metrics(df_close, ticker, benchmark_ticker_sym)
        if metrics is not None and not metrics.empty:
            if ticker in df_close.columns and ticker in df_high.columns:
                cmp = df_close[ticker].dropna().iloc[-1]
                high_52w = df_high[ticker].dropna().max()
                dist_52w = ((high_52w - cmp) / high_52w) * 100
            else:
                cmp, high_52w, dist_52w = 0, 0, 0

            rrg_results[name] = {
                "metrics": metrics,
                "prices": df_close[ticker].dropna(),
                "cmp": round(cmp, 2),
                "high_52w": round(high_52w, 2),
                "dist_52w": round(dist_52w, 2),
                "ticker": ticker,
            }

    return rrg_results


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


def render_rrg_chart(rrg_data_dict, title_text):
    fig = go.Figure()
    min_x, max_x, min_y, max_y = 98, 102, 98, 102
    summary_list = []

    colors = [
        "#10B981",
        "#3B82F6",
        "#EF4444",
        "#F59E0B",
        "#8B5CF6",
        "#EC4899",
        "#14B8A6",
        "#F97316",
        "#6366F1",
        "#06B6D4",
        "#A855F7",
        "#EAB308",
        "#84CC16",
        "#F43F5E",
    ]

    for idx, (name, item_data) in enumerate(rrg_data_dict.items()):
        df = item_data["metrics"]
        cmp = item_data["cmp"]
        high_52w = item_data["high_52w"]
        dist_52w = item_data["dist_52w"]

        history = df.tail(tail_len)
        if history.empty:
            continue

        x_vals = history["ratio"].values
        y_vals = history["momentum"].values
        head_x, head_y = x_vals[-1], y_vals[-1]

        min_x, max_x = min(min_x, min(x_vals)), max(max_x, max(x_vals))
        min_y, max_y = min(min_y, min(y_vals)), max(max_y, max(y_vals))

        quad_name, desc, badge_cls, quad_color = get_quadrant(head_x, head_y)
        color = colors[idx % len(colors)]

        mom_change = head_y - y_vals[-2] if len(y_vals) > 1 else 0
        trend_icon = "⬆️ Up" if mom_change > 0 else "⬇️ Down"

        is_near = dist_52w <= high_threshold
        near_high_status = (
            f"🔥 YES ({dist_52w}%)" if is_near else f"NO ({dist_52w}%)"
        )
        near_badge_cls = "bg-near-high" if is_near else "bg-normal-high"

        summary_list.append({
            "Name": name,
            "RS-Ratio": round(head_x, 2),
            "RS-Momentum": round(head_y, 2),
            "Quadrant": quad_name,
            "Status": desc,
            "BadgeClass": badge_cls,
            "Trend": trend_icon,
            "CMP": cmp,
            "52W High": high_52w,
            "Dist 52W High (%)": dist_52w,
            "Near 52W High": near_high_status,
            "NearBadgeClass": near_badge_cls,
        })

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

        fig.add_trace(
            go.Scatter(
                x=[head_x],
                y=[head_y],
                mode="markers+text",
                name=name,
                text=[name],
                textposition="top center",
                textfont=dict(color="#F3F4F6", size=11),
                marker=dict(size=12, color=color),
                hovertemplate=f"<b>{name}</b><br>CMP: ₹{cmp}<br>52W High: ₹{high_52w}<br>Dist High: {dist_52w}%<br>RS-Ratio: {head_x:.2f}<br>RS-Momentum: {head_y:.2f}<br>Quadrant: {quad_name}<extra></extra>",
            )
        )

    padding_x = max(abs(100 - min_x), abs(max_x - 100)) + 1.5
    padding_y = max(abs(100 - min_y), abs(max_y - 100)) + 1.5
    x_range = [100 - padding_x, 100 + padding_x]
    y_range = [100 - padding_y, 100 + padding_y]

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=16, color="#38BDF8")),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        height=580,
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

    columns_list = [
        "Name",
        "RS-Ratio",
        "RS-Momentum",
        "Quadrant",
        "Status",
        "BadgeClass",
        "Trend",
        "CMP",
        "52W High",
        "Dist 52W High (%)",
        "Near 52W High",
        "NearBadgeClass",
    ]
    summary_df = pd.DataFrame(summary_list, columns=columns_list)
    return fig, summary_df


def render_styled_table(data_frame, col_name="Sector / Stock Name"):
    if (
        data_frame is None
        or data_frame.empty
        or "Quadrant" not in data_frame.columns
    ):
        st.info("No items currently in this quadrant.")
        return

    rows = ""
    for _, row in data_frame.iterrows():
        rows += f"""
<tr style="border-bottom: 1px solid #1f2937; color:#f3f4f6; font-size:0.9rem;">
<td style="padding:12px 16px; font-weight:600;">{row['Name']}</td>
<td style="padding:12px 16px;"><span class="status-badge {row['BadgeClass']}">{row['Quadrant']}</span></td>
<td style="padding:12px 16px; font-weight:500;">{row['RS-Ratio']}</td>
<td style="padding:12px 16px; font-weight:500;">{row['RS-Momentum']}</td>
<td style="padding:12px 16px;">{row['Trend']}</td>
<td style="padding:12px 16px; font-weight:600; color:#38bdf8;">₹{row['CMP']}</td>
<td style="padding:12px 16px; font-weight:600; color:#f3f4f6;">₹{row['52W High']}</td>
<td style="padding:12px 16px; font-weight:600;">{row['Dist 52W High (%)']}%</td>
<td style="padding:12px 16px;"><span class="status-badge {row['NearBadgeClass']}">{row['Near 52W High']}</span></td>
</tr>
"""

    table_html = f"""
<table style="width:100%; border-collapse:collapse; background-color:#111827; border-radius:8px; overflow:hidden; margin-top:10px;">
<thead>
<tr style="background-color:#1f2937; text-align:left; color:#9ca3af; font-size:0.9rem;">
<th style="padding:12px 16px;">{col_name}</th>
<th style="padding:12px 16px;">Quadrant</th>
<th style="padding:12px 16px;">RS-Ratio</th>
<th style="padding:12px 16px;">RS-Momentum</th>
<th style="padding:12px 16px;">Trend</th>
<th style="padding:12px 16px;">CMP (₹)</th>
<th style="padding:12px 16px;">52W High (₹)</th>
<th style="padding:12px 16px;">Dist High (%)</th>
<th style="padding:12px 16px;">Near 52W High (&le;{high_threshold}%)</th>
</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
"""
    clean_html = "\n".join([line.strip() for line in table_html.split("\n")])
    st.markdown(clean_html, unsafe_allow_html=True)


# -------------------------------------------------------------------
# FEATURE 1: ANIMATED RRG ROTATION GENERATOR
# -------------------------------------------------------------------
def render_animated_rrg(sector_rrg_dict, lookback_periods=12):
    # Find common date index across all sectors
    all_dates = None
    for item in sector_rrg_dict.values():
        df_m = item["metrics"]
        if all_dates is None:
            all_dates = set(df_m.index)
        else:
            all_dates = all_dates.intersection(set(df_m.index))

    if not all_dates:
        st.warning("Not enough overlapping historical data for animation.")
        return

    sorted_dates = sorted(list(all_dates))[-lookback_periods:]
    if len(sorted_dates) < 3:
        st.warning("Insufficient dates for animation window.")
        return

    colors = [
        "#10B981",
        "#3B82F6",
        "#EF4444",
        "#F59E0B",
        "#8B5CF6",
        "#EC4899",
        "#14B8A6",
        "#F97316",
        "#6366F1",
        "#06B6D4",
        "#A855F7",
        "#EAB308",
        "#84CC16",
        "#F43F5E",
    ]

    # Initial frame data setup
    init_date = sorted_dates[0]
    fig = go.Figure()

    for idx, (name, item) in enumerate(sector_rrg_dict.items()):
        df = item["metrics"]
        color = colors[idx % len(colors)]
        if init_date in df.index:
            rx = df.loc[init_date, "ratio"]
            ry = df.loc[init_date, "momentum"]
            fig.add_trace(
                go.Scatter(
                    x=[rx],
                    y=[ry],
                    mode="markers+text",
                    name=name,
                    text=[name],
                    textposition="top center",
                    marker=dict(size=12, color=color),
                )
            )

    # Build Animation Frames
    frames = []
    for dt in sorted_dates:
        frame_data = []
        date_str = pd.to_datetime(dt).strftime("%d %b %Y")
        for idx, (name, item) in enumerate(sector_rrg_dict.items()):
            df = item["metrics"]
            color = colors[idx % len(colors)]
            if dt in df.index:
                # Get historical tail up to dt
                sub_df = df.loc[:dt].tail(4)
                x_tail = sub_df["ratio"].values
                y_tail = sub_df["momentum"].values
                frame_data.append(
                    go.Scatter(
                        x=x_tail,
                        y=y_tail,
                        mode="lines+markers+text",
                        name=name,
                        text=[""] * (len(x_tail) - 1) + [name],
                        textposition="top center",
                        marker=dict(
                            size=[6] * (len(x_tail) - 1) + [12], color=color
                        ),
                        line=dict(color=color, width=2),
                    )
                )
        frames.append(
            go.Frame(data=frame_data, name=date_str, layout=dict(title=f"🎬 RRG Sector Rotation Date: {date_str}"))
        )

    fig.frames = frames

    fig.update_layout(
        title="🎬 Interactive Sector Rotation Animation (Click Play below)",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        height=620,
        xaxis=dict(
            title="RS-Ratio",
            range=[94, 106],
            gridcolor="#1F2937",
            zeroline=False,
        ),
        yaxis=dict(
            title="RS-Momentum",
            range=[94, 106],
            gridcolor="#1F2937",
            zeroline=False,
        ),
        shapes=[
            dict(
                type="line",
                x0=100,
                x1=100,
                y0=90,
                y1=110,
                line=dict(color="#4B5563", width=1.5, dash="dash"),
            ),
            dict(
                type="line",
                x0=90,
                x1=110,
                y0=100,
                y1=100,
                line=dict(color="#4B5563", width=1.5, dash="dash"),
            ),
        ],
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                y=0.0,
                x=0.0,
                xanchor="left",
                yanchor="top",
                pad=dict(t=10, r=10),
                buttons=[
                    dict(
                        label="▶️ Play Rotation",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=600, redraw=True),
                                fromcurrent=True,
                                mode="immediate",
                            ),
                        ],
                    ),
                    dict(
                        label="⏸️ Pause",
                        method="animate",
                        args=[
                            [None],
                            dict(
                                frame=dict(duration=0, redraw=False),
                                mode="immediate",
                            ),
                        ],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [f.name],
                            dict(
                                mode="immediate",
                                frame=dict(duration=300, redraw=True),
                            ),
                        ],
                        label=f.name,
                    )
                    for f in frames
                ],
                transition=dict(duration=0),
                x=0.1,
                y=0,
                currentvalue=dict(
                    font=dict(size=12, color="#38bdf8"),
                    prefix="Date: ",
                    visible=True,
                ),
            )
        ],
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------------------------
# FEATURE 2: SECTOR VS SECTOR PAIR MATRIX
# -------------------------------------------------------------------
def render_pair_comparison(sec1_name, sec2_name, interval):
    t1 = SECTOR_MAP[sec1_name]["index"]
    t2 = SECTOR_MAP[sec2_name]["index"]

    data = yf.download(
        [t1, t2, BENCHMARK_SYMBOL],
        period="1y",
        interval=interval,
        progress=False,
    )
    if isinstance(data.columns, pd.MultiIndex):
        df_close = data["Close"]
    else:
        df_close = data[["Close"]]

    if t1 not in df_close.columns or t2 not in df_close.columns:
        st.error("Pair comparison data unavailable.")
        return

    # Relative Pair Ratio = Sector 1 / Sector 2
    pair_ratio = (df_close[t1] / df_close[t2]) * 100
    metrics = calculate_rrg_metrics(
        pd.DataFrame({t1: df_close[t1]}), t1, BENCHMARK_SYMBOL
    )

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Current Price ({sec1_name})", f"₹{df_close[t1].iloc[-1]:.2f}")
    c2.metric(f"Current Price ({sec2_name})", f"₹{df_close[t2].iloc[-1]:.2f}")

    curr_pair_ratio = pair_ratio.iloc[-1]
    prev_pair_ratio = pair_ratio.iloc[-5] if len(pair_ratio) > 5 else curr_pair_ratio
    pair_chg = ((curr_pair_ratio - prev_pair_ratio) / prev_pair_ratio) * 100
    c3.metric(
        f"Pair Strength ({sec1_name} / {sec2_name})",
        f"{curr_pair_ratio:.2f}",
        delta=f"{pair_chg:.2f}% (5 Periods)",
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=pair_ratio.index,
            y=pair_ratio.values,
            mode="lines",
            line=dict(color="#38bdf8", width=2),
            name=f"{sec1_name} / {sec2_name} Ratio",
        )
    )

    # 20-period Moving Average on Pair Ratio
    ma_pair = pair_ratio.rolling(20).mean()
    fig.add_trace(
        go.Scatter(
            x=ma_pair.index,
            y=ma_pair.values,
            mode="lines",
            line=dict(color="#f59e0b", width=1.5, dash="dash"),
            name="20-Period MA Ratio",
        )
    )

    fig.update_layout(
        title=f"⚖️ Pair Strength Ratio Chart: {sec1_name} vs {sec2_name}",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        height=400,
        xaxis=dict(gridcolor="#1F2937", color="#9CA3AF"),
        yaxis=dict(
            title="Relative Ratio", gridcolor="#1F2937", color="#9CA3AF"
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------------------------
# FEATURE 3 & 4: AUTOMATED TRADE SETUPS & BACKTESTING
# -------------------------------------------------------------------
def generate_trade_setups(sector_rrg_data):
    long_setups = []
    short_setups = []

    for sec_name, data in sector_rrg_data.items():
        metrics = data["metrics"]
        cmp = data["cmp"]
        high_52w = data["high_52w"]
        dist_52w = data["dist_52w"]

        if metrics.empty:
            continue

        curr_ratio = metrics["ratio"].iloc[-1]
        curr_mom = metrics["momentum"].iloc[-1]
        quad_name, _, _, _ = get_quadrant(curr_ratio, curr_mom)

        # LONG SETUP CONDITION:
        # In Leading or Early Improving + Distance from 52W High <= 6% + Momentum > 99.5
        if (
            quad_name in ["Leading", "Improving"]
            and dist_52w <= 6.0
            and curr_mom >= 99.5
        ):
            stop_loss = round(cmp * 0.96, 2)  # 4% trailing SL
            target_1 = round(cmp * 1.08, 2)  # 8% T1
            target_2 = round(cmp * 1.15, 2)  # 15% T2
            long_setups.append({
                "Sector": sec_name,
                "Quadrant": quad_name,
                "CMP": cmp,
                "52W High": high_52w,
                "Dist High": f"{dist_52w}%",
                "Stop Loss": f"₹{stop_loss}",
                "Target 1": f"₹{target_1}",
                "Target 2": f"₹{target_2}",
                "Risk Reward": "1 : 2.0",
            })

        # SHORT / EXIT SETUP CONDITION:
        # In Lagging Quadrant + Distance from High > 15% + Momentum < 99.5
        if quad_name == "Lagging" and dist_52w >= 12.0 and curr_mom < 99.5:
            stop_loss = round(cmp * 1.04, 2)
            target_1 = round(cmp * 0.92, 2)
            short_setups.append({
                "Sector": sec_name,
                "Quadrant": quad_name,
                "CMP": cmp,
                "52W High": high_52w,
                "Dist High": f"{dist_52w}%",
                "Stop Loss": f"₹{stop_loss}",
                "Target Downside": f"₹{target_1}",
                "Alert": "⚠️ Avoid Long / Consider Hedging",
            })

    return long_setups, short_setups


def run_quadrant_backtest(sector_rrg_data):
    results = []

    for sec_name, data in sector_rrg_data.items():
        metrics = data["metrics"]
        prices = data["prices"]

        if metrics.empty or len(prices) < 50:
            continue

        quadrants = []
        for r, m in zip(metrics["ratio"], metrics["momentum"]):
            q, _, _, _ = get_quadrant(r, m)
            quadrants.append(q)

        metrics["quadrant"] = quadrants
        metrics["price"] = prices.reindex(metrics.index)

        # Detect transition into LEADING quadrant
        metrics["prev_quadrant"] = metrics["quadrant"].shift(1)
        transitions = metrics[
            (metrics["prev_quadrant"] == "Improving")
            & (metrics["quadrant"] == "Leading")
        ]

        total_trades = 0
        returns_5d = []
        returns_10d = []

        for idx_date in transitions.index:
            try:
                p_entry = metrics.loc[idx_date, "price"]
                future_prices = metrics.loc[idx_date:, "price"]

                if len(future_prices) > 5:
                    p_5d = future_prices.iloc[5]
                    ret_5d = ((p_5d - p_entry) / p_entry) * 100
                    returns_5d.append(ret_5d)

                if len(future_prices) > 10:
                    p_10d = future_prices.iloc[10]
                    ret_10d = ((p_10d - p_entry) / p_entry) * 100
                    returns_10d.append(ret_10d)

                total_trades += 1
            except Exception:
                continue

        if total_trades > 0:
            avg_5d = np.mean(returns_5d) if returns_5d else 0
            avg_10d = np.mean(returns_10d) if returns_10d else 0
            win_rate = (
                (len([r for r in returns_10d if r > 0]) / len(returns_10d))
                * 100
                if returns_10d
                else 0
            )

            results.append({
                "Sector": sec_name,
                "Signals Count": total_trades,
                "Avg 5-Period Return (%)": round(avg_5d, 2),
                "Avg 10-Period Return (%)": round(avg_10d, 2),
                "Win Rate (10P) (%)": f"{round(win_rate, 1)}%",
            })

    return pd.DataFrame(results)


# -------------------------------------------------------------------
# MAIN DASHBOARD NAVIGATION (4 INTEGRATED TABS)
# -------------------------------------------------------------------

main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
    "🌐 14 Primary NSE Sectors",
    "🎯 Heavyweight Stock Drill-Down",
    "🎬 Animated RRG & Pair Matrix",
    "🤖 AI Trade Setups & Backtesting",
])

# Fetch Sector Data
sector_ticker_dict = {sec: SECTOR_MAP[sec]["index"] for sec in SECTOR_MAP}

with st.spinner("Fetching Live Sector Market Data..."):
    sector_rrg_data = fetch_and_build_rrg(
        sector_ticker_dict, BENCHMARK_SYMBOL, timeframe
    )

# TAB 1: SECTORS RRG
with main_tab1:
    st.markdown("### 📊 14 NSE Sector Rotation vs Nifty 50")
    fig_sec, df_sec_summary = render_rrg_chart(
        sector_rrg_data, "14 NSE Sectors Relative Rotation Graph"
    )
    st.plotly_chart(fig_sec, use_container_width=True)

    st.subheader("📋 Sector Rotation Matrix")
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "All Sectors",
        "🔥 Near 52W High",
        "🚀 Leading",
        "⚡ Improving",
        "⚠️ Weakening",
        "🔻 Lagging",
    ])

    with t1:
        render_styled_table(df_sec_summary, "Sector Name")
    with t2:
        render_styled_table(
            df_sec_summary[
                df_sec_summary["Dist 52W High (%)"] <= high_threshold
            ],
            "Sector Name",
        )
    with t3:
        render_styled_table(
            df_sec_summary[df_sec_summary["Quadrant"] == "Leading"],
            "Sector Name",
        )
    with t4:
        render_styled_table(
            df_sec_summary[df_sec_summary["Quadrant"] == "Improving"],
            "Sector Name",
        )
    with t5:
        render_styled_table(
            df_sec_summary[df_sec_summary["Quadrant"] == "Weakening"],
            "Sector Name",
        )
    with t6:
        render_styled_table(
            df_sec_summary[df_sec_summary["Quadrant"] == "Lagging"],
            "Sector Name",
        )


# TAB 2: STOCK DRILL-DOWN RRG
with main_tab2:
    st.markdown(
        f"### 🎯 Stock Drill-Down Analysis: <span style='color:#38bdf8;'>{selected_sector_for_stocks}</span>",
        unsafe_allow_html=True,
    )

    selected_sector_info = SECTOR_MAP[selected_sector_for_stocks]
    stock_dict = selected_sector_info["stocks"]
    sector_bench_symbol = selected_sector_info["index"]

    with st.spinner(
        f"Fetching Live Stock Data for {selected_sector_for_stocks}..."
    ):
        stock_rrg_data = fetch_and_build_rrg(
            stock_dict, sector_bench_symbol, timeframe
        )

    fig_stock, df_stock_summary = render_rrg_chart(
        stock_rrg_data,
        f"{selected_sector_for_stocks} Top Stocks vs Parent Sector Index",
    )
    st.plotly_chart(fig_stock, use_container_width=True)

    st.subheader(f"📋 {selected_sector_for_stocks} Stock Matrix")
    st1, st2, st3, st4, st5, st6 = st.tabs([
        "All Sector Stocks",
        "🔥 Near 52W High",
        "🚀 Leading",
        "⚡ Improving",
        "⚠️ Weakening",
        "🔻 Lagging",
    ])

    with st1:
        render_styled_table(df_stock_summary, "Stock Name")
    with st2:
        render_styled_table(
            df_stock_summary[
                df_stock_summary["Dist 52W High (%)"] <= high_threshold
            ],
            "Stock Name",
        )
    with st3:
        render_styled_table(
            df_stock_summary[df_stock_summary["Quadrant"] == "Leading"],
            "Stock Name",
        )
    with st4:
        render_styled_table(
            df_stock_summary[df_stock_summary["Quadrant"] == "Improving"],
            "Stock Name",
        )
    with st5:
        render_styled_table(
            df_stock_summary[df_stock_summary["Quadrant"] == "Weakening"],
            "Stock Name",
        )
    with st6:
        render_styled_table(
            df_stock_summary[df_stock_summary["Quadrant"] == "Lagging"],
            "Stock Name",
        )


# TAB 3: ANIMATED RRG & SECTOR PAIR MATRIX
with main_tab3:
    st.markdown("### 🎬 Historical RRG Rotation Player")
    st.caption(
        "Niche **Play** button par click karke dekhein ki pichle 12 periods mein sectors ne quadrants kaise rotate kiye."
    )
    render_animated_rrg(sector_rrg_data, lookback_periods=12)

    st.markdown("---")
    st.markdown("### ⚔️ Sector vs Sector Pair Strength Ratio")
    st.caption(
        "Select any 2 sectors to compare their relative strength ratio directly (Pair Trading Analysis)."
    )

    col1, col2 = st.columns(2)
    s1 = col1.selectbox("Base Sector (Numerator)", options=list(SECTOR_MAP.keys()), index=0)
    s2 = col2.selectbox("Benchmark Sector (Denominator)", options=list(SECTOR_MAP.keys()), index=1)

    if s1 == s2:
        st.warning("Please select two different sectors to compare.")
    else:
        render_pair_comparison(s1, s2, timeframe)


# TAB 4: AI TRADE SETUPS & BACKTESTING
with main_tab4:
    st.markdown("### 🤖 Automated AI Trade Setups")
    st.caption(
        "High-conviction setups generated automatically based on RRG Quadrants & 52-Week High Proximity."
    )

    long_ideas, short_ideas = generate_trade_setups(sector_rrg_data)

    c_long, c_short = st.columns(2)

    with c_long:
        st.markdown(
            "#### 🚀 Bullish High-Conviction Setups (Leading / Early Improving)"
        )
        if not long_ideas:
            st.info("No high-conviction bullish setups at this moment.")
        else:
            for item in long_ideas:
                st.markdown(
                    f"""
                <div class="setup-card-long">
                    <h4 style="color:#10b981; margin:0;">{item['Sector']} <span style="font-size:0.8rem; color:#9ca3af;">({item['Quadrant']})</span></h4>
                    <p style="margin:5px 0; color:#f3f4f6;"><b>CMP:</b> ₹{item['CMP']} | <b>52W High:</b> ₹{item['52W High']} (Dist: {item['Dist High']})</p>
                    <p style="margin:5px 0; color:#38bdf8;">🎯 <b>Target 1:</b> {item['Target 1']} | 🎯 <b>Target 2:</b> {item['Target 2']}</p>
                    <p style="margin:5px 0; color:#ef4444;">🛑 <b>Stop Loss:</b> {item['Stop Loss']} (RR {item['Risk Reward']})</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    with c_short:
        st.markdown(
            "#### 🔻 Bearish / Exit Warning Setups (Lagging Quadrant)"
        )
        if not short_ideas:
            st.info("No high-risk short/exit setups detected.")
        else:
            for item in short_ideas:
                st.markdown(
                    f"""
                <div class="setup-card-short">
                    <h4 style="color:#ef4444; margin:0;">{item['Sector']} <span style="font-size:0.8rem; color:#9ca3af;">({item['Quadrant']})</span></h4>
                    <p style="margin:5px 0; color:#f3f4f6;"><b>CMP:</b> ₹{item['CMP']} | <b>52W High:</b> ₹{item['52W High']} (Dist: {item['Dist High']})</p>
                    <p style="margin:5px 0; color:#f59e0b;"><b>Downside Target:</b> {item['Target Downside']}</p>
                    <p style="margin:5px 0; color:#ef4444;">⚠️ <b>{item['Alert']}</b></p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.markdown("### 📈 Historical Quadrant Shift Backtest Engine")
    st.caption(
        "Proof of Performance: Jab koi sector **Improving se Leading Quadrant** mein enter hota hai, uske baad ke historical returns:"
    )

    backtest_df = run_quadrant_backtest(sector_rrg_data)
    if backtest_df.empty:
        st.info("Calculating backtest metrics...")
    else:
        st.dataframe(backtest_df, use_container_width=True, hide_index=True)


# Footer Branding
st.markdown(
    """
    <div class="footer-text">
        © 2026 <b>Grow More Trading Institute</b> | Institutional RRG & AI Trade Intelligence Dashboard
    </div>
""",
    unsafe_allow_html=True,
)
