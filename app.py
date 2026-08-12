from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Page Configuration
st.set_page_config(
    page_title="Grow More Trading Institute - RRG Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Theme, Blinking Live Dot & Institute Branding)
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    
    /* Branding Banner Flex Container */
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
    
    /* Live Indicator & Clock Styling */
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

    /* Status Badges */
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

# Header Branding Banner with Blinking LIVE Badge & Realtime Clock
st.markdown(
    """
    <div class="brand-header">
        <div>
            <div class="brand-title">GROW MORE TRADING INSTITUTE</div>
            <div class="brand-subtitle">Real-time NSE 14 Sectors & Stock Rotation RRG Matrix</div>
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

# 14 Primary NSE Sectors & Benchmark Mapping (Verified Yahoo Finance Tickers)
SECTOR_MAP = {
    "Nifty Bank": {"index": "^NSEBANK", "stocks": {"HDFC Bank": "HDFCBANK.NS", "ICICI Bank": "ICICIBANK.NS", "SBI": "SBIN.NS", "Kotak Bank": "KOTAKBANK.NS", "Axis Bank": "AXISBANK.NS", "IndusInd Bank": "INDUSINDBK.NS"}},
    "Nifty IT": {"index": "^CNXIT", "stocks": {"TCS": "TCS.NS", "Infosys": "INFY.NS", "HCL Tech": "HCLTECH.NS", "Wipro": "WIPRO.NS", "Tech Mahindra": "TECHM.NS", "LTIMindtree": "LTIM.NS"}},
    "Nifty Auto": {"index": "^CNXAUTO", "stocks": {"Tata Motors": "TATAMOTORS.NS", "M&M": "M&M.NS", "Maruti": "MARUTI.NS", "Bajaj Auto": "BAJAJ-AUTO.NS", "Hero MotoCorp": "HEROMOTOCO.NS", "Eicher Motors": "EICHERMOT.NS"}},
    "Nifty Metal": {"index": "^CNXMETAL", "stocks": {"Tata Steel": "TATASTEEL.NS", "JSW Steel": "JSWSTEEL.NS", "Hindalco": "HINDALCO.NS", "Vedanta": "VEDL.NS", "Coal India": "COALINDIA.NS", "NMDC": "NMDC.NS"}},
    "Nifty Pharma": {"index": "^CNXPHARMA", "stocks": {"Sun Pharma": "SUNPHARMA.NS", "Cipla": "CIPLA.NS", "Dr. Reddy's": "DRREDDY.NS", "Divi's Lab": "DIVISLAB.NS", "Lupin": "LUPIN.NS", "Mankind": "MANKIND.NS"}},
    "Nifty FMCG": {"index": "^CNXFMCG", "stocks": {"ITC": "ITC.NS", "HUL": "HINDUNILVR.NS", "Britannia": "BRITANNIA.NS", "Tata Consumer": "TATACONSUM.NS", "Nestle": "NESTLEIND.NS", "VBL": "VBL.NS"}},
    "Nifty Realty": {"index": "^CNXREALTY", "stocks": {"DLF": "DLF.NS", "Lodha": "LODHA.NS", "Godrej Prop": "GODREJPROP.NS", "Oberoi Realty": "OBEROIRLTY.NS", "Phoenix Mills": "PHOENIXLTD.NS"}},
    "Nifty Energy": {"index": "^CNXENERGY", "stocks": {"Reliance": "RELIANCE.NS", "NTPC": "NTPC.NS", "ONGC": "ONGC.NS", "Power Grid": "POWERGRID.NS", "BPCL": "BPCL.NS", "IOC": "IOC.NS"}},
    "Nifty Infra": {"index": "^CNXINFRA", "stocks": {"L&T": "LT.NS", "Reliance": "RELIANCE.NS", "Bharti Airtel": "BHARTIARTL.NS", "NTPC": "NTPC.NS", "Power Grid": "POWERGRID.NS", "UltraTech": "ULTRACEMCO.NS"}},
    "Nifty Fin Service": {"index": "NIFTY_FIN_SERVICE.NS", "stocks": {"HDFC Bank": "HDFCBANK.NS", "ICICI Bank": "ICICIBANK.NS", "SBI": "SBIN.NS", "PFC": "PFC.NS", "REC": "REC.NS", "Chola Fin": "CHOLAFIN.NS"}},
    "Nifty PSU Bank": {"index": "^CNXPSUBANK", "stocks": {"SBI": "SBIN.NS", "Bank of Baroda": "BANKBARODA.NS", "PNB": "PNB.NS", "Canara Bank": "CANBK.NS", "Union Bank": "UNIONBANK.NS", "Indian Bank": "INDIANB.NS"}},
    "Nifty Media": {"index": "^CNXMEDIA", "stocks": {"ZEEL": "ZEEL.NS", "Sun TV": "SUNTV.NS", "PVR INOX": "PVRINOX.NS", "Nazara Tech": "NAZARA.NS", "TV18": "TV18BRDCST.NS"}},
    "Nifty Consumer Durables": {"index": "NIFTY_CONSR_DURBL.NS", "stocks": {"Dixon": "DIXON.NS", "Titan": "TITAN.NS", "Havells": "HAVELLS.NS", "Voltas": "VOLTAS.NS", "Crompton": "CROMPTON.NS", "Polycab": "POLYCAB.NS"}},
    "Nifty Healthcare": {"index": "NIFTY_HEALTHCARE.NS", "stocks": {"Sun Pharma": "SUNPHARMA.NS", "Cipla": "CIPLA.NS", "Apollo Hospitals": "APOLLOHOSP.NS", "Max Healthcare": "MAXHEALTH.NS", "Syngene": "SYNGENE.NS", "Dr Lal Path": "LALPATHLAB.NS"}}
}

BENCHMARK_SYMBOL = "^NSEI" # Nifty 50 Index

# Sidebar Controls
st.sidebar.header("⚙️ RRG Parameters")
timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    options=["1d", "1wk"],
    index=1,
    format_func=lambda x: "Daily Rotation" if x == "1d" else "Weekly Rotation",
)
tail_len = st.sidebar.slider("Tail Length (Periods)", min_value=2, max_value=15, value=5)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Stock Drill-Down")
selected_sector_for_stocks = st.sidebar.selectbox(
    "Select Sector to Analyze Stocks",
    options=list(SECTOR_MAP.keys()),
    index=0
)

# Helper Function for Calculation
def calculate_rrg_metrics(data_df, item_ticker, bench_ticker, period_len=14):
    if item_ticker not in data_df.columns or bench_ticker not in data_df.columns:
        return None
    
    # 1. Raw RS
    rs = (data_df[item_ticker] / data_df[bench_ticker]) * 100
    
    # 2. RS-Ratio
    rs_mean = rs.rolling(window=period_len).mean()
    rs_std = rs.rolling(window=period_len).std()
    rs_ratio = 100 + ((rs - rs_mean) / (rs_std + 1e-6)) * 10
    
    # 3. RS-Momentum
    ratio_mean = rs_ratio.rolling(window=period_len).mean()
    ratio_std = rs_ratio.rolling(window=period_len).std()
    rs_momentum = 100 + ((rs_ratio - ratio_mean) / (ratio_std + 1e-6)) * 10
    
    return pd.DataFrame({'ratio': rs_ratio, 'momentum': rs_momentum}).dropna()

@st.cache_data(ttl=300)
def fetch_and_build_rrg(items_dict, benchmark_ticker_sym, interval):
    all_tickers = list(items_dict.values()) + [benchmark_ticker_sym]
    df = yf.download(all_tickers, period="1y", interval=interval, progress=False)["Close"]
    
    if interval == "1wk":
        df = df.resample("W").last()
        
    rrg_results = {}
    for name, ticker in items_dict.items():
        metrics = calculate_rrg_metrics(df, ticker, benchmark_ticker_sym)
        if metrics is not None and not metrics.empty:
            rrg_results[name] = metrics
            
    return rrg_results

def get_quadrant(ratio, momentum):
    if ratio >= 100 and momentum >= 100:
        return "Leading", "🚀 Bullish Momentum & Strong RS", "bg-leading", "#10B981"
    if ratio >= 100 and momentum < 100:
        return "Weakening", "⚠️ RS High but Momentum Slowing", "bg-weakening", "#F59E0B"
    if ratio < 100 and momentum < 100:
        return "Lagging", "🔻 Bearish Momentum & Weak RS", "bg-lagging", "#EF4444"
    return "Improving", "⚡ RS Weak but Momentum Gaining", "bg-improving", "#3B82F6"

def render_rrg_chart(rrg_data_dict, title_text):
    fig = go.Figure()
    min_x, max_x, min_y, max_y = 98, 102, 98, 102
    summary_list = []
    
    colors = ["#10B981", "#3B82F6", "#EF4444", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6", "#F97316", "#6366F1", "#06B6D4", "#A855F7", "#EAB308", "#84CC16", "#F43F5E"]

    for idx, (name, df) in enumerate(rrg_data_dict.items()):
        history = df.tail(tail_len)
        if history.empty:
            continue
            
        x_vals = history['ratio'].values
        y_vals = history['momentum'].values
        head_x, head_y = x_vals[-1], y_vals[-1]
        
        min_x, max_x = min(min_x, min(x_vals)), max(max_x, max(x_vals))
        min_y, max_y = min(min_y, min(y_vals)), max(max_y, max(y_vals))
        
        quad_name, desc, badge_cls, quad_color = get_quadrant(head_x, head_y)
        color = colors[idx % len(colors)]
        
        mom_change = head_y - y_vals[-2] if len(y_vals) > 1 else 0
        trend_icon = "⬆️ Up" if mom_change > 0 else "⬇️ Down"
        
        summary_list.append({
            "Name": name,
            "RS-Ratio": round(head_x, 2),
            "RS-Momentum": round(head_y, 2),
            "Quadrant": quad_name,
            "Status": desc,
            "BadgeClass": badge_cls,
            "Trend": trend_icon
        })
        
        # Tail
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals,
            mode='lines',
            line=dict(color=color, width=2, dash='dot'),
            showlegend=False, hoverinfo='none'
        ))
        
        # Head Marker
        fig.add_trace(go.Scatter(
            x=[head_x], y=[head_y],
            mode='markers+text',
            name=name, text=[name],
            textposition="top center",
            textfont=dict(color="#F3F4F6", size=11),
            marker=dict(size=12, color=color),
            hovertemplate=f"<b>{name}</b><br>RS-Ratio: {head_x:.2f}<br>RS-Momentum: {head_y:.2f}<br>Quadrant: {quad_name}<extra></extra>"
        ))

    padding_x = max(abs(100 - min_x), abs(max_x - 100)) + 1.5
    padding_y = max(abs(100 - min_y), abs(max_y - 100)) + 1.5
    x_range = [100 - padding_x, 100 + padding_x]
    y_range = [100 - padding_y, 100 + padding_y]

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=16, color="#38BDF8")),
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        height=580, showlegend=False,
        xaxis=dict(title="RS-Ratio (Relative Strength)", range=x_range, gridcolor="#1F2937", color="#9CA3AF", zeroline=False),
        yaxis=dict(title="RS-Momentum (Rate of Change)", range=y_range, gridcolor="#1F2937", color="#9CA3AF", zeroline=False),
        shapes=[
            dict(type="rect", x0=100, x1=x_range[1], y0=100, y1=y_range[1], fillcolor="rgba(16, 185, 129, 0.08)", line_width=0, layer="below"),
            dict(type="rect", x0=100, x1=x_range[1], y0=y_range[0], y1=100, fillcolor="rgba(245, 158, 11, 0.08)", line_width=0, layer="below"),
            dict(type="rect", x0=x_range[0], x1=100, y0=y_range[0], y1=100, fillcolor="rgba(239, 68, 68, 0.08)", line_width=0, layer="below"),
            dict(type="rect", x0=x_range[0], x1=100, y0=100, y1=y_range[1], fillcolor="rgba(59, 130, 246, 0.08)", line_width=0, layer="below"),
            dict(type="line", x0=100, x1=100, y0=y_range[0], y1=y_range[1], line=dict(color="#4B5563", width=1.5, dash="dash")),
            dict(type="line", x0=x_range[0], x1=x_range[1], y0=100, y1=100, line=dict(color="#4B5563", width=1.5, dash="dash"))
        ],
        annotations=[
            dict(x=(100+x_range[1])/2, y=(100+y_range[1])/2, text="<b>LEADING</b>", showarrow=False, font=dict(color="rgba(16, 185, 129, 0.3)", size=24)),
            dict(x=(100+x_range[1])/2, y=(100+y_range[0])/2, text="<b>WEAKENING</b>", showarrow=False, font=dict(color="rgba(245, 158, 11, 0.3)", size=24)),
            dict(x=(100+x_range[0])/2, y=(100+y_range[0])/2, text="<b>LAGGING</b>", showarrow=False, font=dict(color="rgba(239, 68, 68, 0.3)", size=24)),
            dict(x=(100+x_range[0])/2, y=(100+y_range[1])/2, text="<b>IMPROVING</b>", showarrow=False, font=dict(color="rgba(59, 130, 246, 0.3)", size=24)),
        ]
    )
    
    # Safe DataFrame creation with default columns to prevent KeyError
    columns_list = ["Name", "RS-Ratio", "RS-Momentum", "Quadrant", "Status", "BadgeClass", "Trend"]
    summary_df = pd.DataFrame(summary_list, columns=columns_list)
    return fig, summary_df

def render_styled_table(data_frame, col_name="Sector / Stock Name"):
    if data_frame is None or data_frame.empty or "Quadrant" not in data_frame.columns:
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
<td style="padding:12px 16px; color:#9ca3af; font-size:0.85rem;">{row['Status']}</td>
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
<th style="padding:12px 16px;">Momentum Trend</th>
<th style="padding:12px 16px;">Technical Status</th>
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
# MAIN DASHBOARD TABS (1. SECTORS RRG | 2. STOCKS DRILL-DOWN)
# -------------------------------------------------------------------

main_tab1, main_tab2 = st.tabs(["🌐 14 Primary NSE Sectors RRG", "🎯 Sector Heavyweight Stocks Drill-Down"])

# Fetch All 14 Sectors Data
sector_ticker_dict = {sec: SECTOR_MAP[sec]["index"] for sec in SECTOR_MAP}

with st.spinner("Fetching Live Sector Market Data..."):
    sector_rrg_data = fetch_and_build_rrg(sector_ticker_dict, BENCHMARK_SYMBOL, timeframe)

# TAB 1: SECTORS RRG
with main_tab1:
    st.markdown("### 📊 14 NSE Sector Rotation vs Nifty 50")
    fig_sec, df_sec_summary = render_rrg_chart(sector_rrg_data, "14 NSE Sectors Relative Rotation Graph")
    st.plotly_chart(fig_sec, use_container_width=True)
    
    st.subheader("📋 Sector Rotation Matrix")
    t1, t2, t3, t4, t5 = st.tabs(["All Sectors", "🚀 Leading", "⚡ Improving", "⚠️ Weakening", "🔻 Lagging"])
    
    with t1: render_styled_table(df_sec_summary, "Sector Name")
    with t2: render_styled_table(df_sec_summary[df_sec_summary["Quadrant"]=="Leading"], "Sector Name")
    with t3: render_styled_table(df_sec_summary[df_sec_summary["Quadrant"]=="Improving"], "Sector Name")
    with t4: render_styled_table(df_sec_summary[df_sec_summary["Quadrant"]=="Weakening"], "Sector Name")
    with t5: render_styled_table(df_sec_summary[df_sec_summary["Quadrant"]=="Lagging"], "Sector Name")


# TAB 2: STOCK DRILL-DOWN RRG
with main_tab2:
    st.markdown(f"### 🎯 Stock Drill-Down Analysis: <span style='color:#38bdf8;'>{selected_sector_for_stocks}</span>", unsafe_allow_html=True)
    
    selected_sector_info = SECTOR_MAP[selected_sector_for_stocks]
    stock_dict = selected_sector_info["stocks"]
    sector_bench_symbol = selected_sector_info["index"]
    
    with st.spinner(f"Fetching Live Stock Data for {selected_sector_for_stocks}..."):
        # Benchmarking stocks against their parent Sector Index
        stock_rrg_data = fetch_and_build_rrg(stock_dict, sector_bench_symbol, timeframe)
        
    fig_stock, df_stock_summary = render_rrg_chart(stock_rrg_data, f"{selected_sector_for_stocks} Top Stocks vs Parent Sector Index")
    st.plotly_chart(fig_stock, use_container_width=True)
    
    st.subheader(f"📋 {selected_sector_for_stocks} Stock Matrix")
    st1, st2, st3, st4, st5 = st.tabs(["All Sector Stocks", "🚀 Leading", "⚡ Improving", "⚠️ Weakening", "🔻 Lagging"])
    
    with st1: render_styled_table(df_stock_summary, "Stock Name")
    with st2: render_styled_table(df_stock_summary[df_stock_summary["Quadrant"]=="Leading"], "Stock Name")
    with st3: render_styled_table(df_stock_summary[df_stock_summary["Quadrant"]=="Improving"], "Stock Name")
    with st4: render_styled_table(df_stock_summary[df_stock_summary["Quadrant"]=="Weakening"], "Stock Name")
    with st5: render_styled_table(df_stock_summary[df_stock_summary["Quadrant"]=="Lagging"], "Stock Name")

# Footer
st.markdown(
    """
    <div class="footer-text">
        © 2026 <b>Grow More Trading Institute</b> | Live Market Sector & Stock Rotation RRG Analytics Dashboard
    </div>
""",
    unsafe_allow_html=True,
)
