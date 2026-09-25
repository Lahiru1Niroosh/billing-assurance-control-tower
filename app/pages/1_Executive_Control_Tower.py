import pandas as pd
import plotly.express as px
import streamlit as st
from utils.database import get_control_performance, get_executive_kpis, get_sla_kpis

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Executive Control Tower",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# NEXT-LEVEL CSS & ANIMATIONS
# ============================================================
st.markdown("""
<style>
    /* -------------------------------------------------------
       GLOBAL & BACKGROUND
    ------------------------------------------------------- */
    .stApp {
        background: 
            radial-gradient(circle at 10% 10%, rgba(37, 99, 235, 0.15), transparent 35%),
            radial-gradient(circle at 90% 15%, rgba(139, 92, 246, 0.12), transparent 35%),
            radial-gradient(circle at 50% 90%, rgba(6, 182, 212, 0.1), transparent 40%),
            linear-gradient(135deg, #07111f 0%, #0b1628 50%, #111827 100%);
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.25); }

    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* -------------------------------------------------------
       ANIMATIONS
    ------------------------------------------------------- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    @keyframes floatOrb {
        0% { transform: translate(0, 0); }
        50% { transform: translate(-20px, 15px); }
        100% { transform: translate(10px, -10px); }
    }

    /* -------------------------------------------------------
       HERO SECTION
    ------------------------------------------------------- */
    .hero {
        position: relative;
        overflow: hidden;
        padding: 40px 45px;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.45), rgba(88, 28, 135, 0.35), rgba(8, 145, 178, 0.25));
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
        animation: fadeInUp 0.8s ease-out;
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 300px; height: 300px;
        right: -80px; top: -120px;
        border-radius: 50%;
        background: rgba(59, 130, 246, 0.25);
        filter: blur(50px);
        animation: floatOrb 8s ease-in-out infinite;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 250px; height: 250px;
        left: -100px; bottom: -130px;
        border-radius: 50%;
        background: rgba(168, 85, 247, 0.2);
        filter: blur(50px);
        animation: floatOrb 10s ease-in-out infinite reverse;
    }

    .hero-content { position: relative; z-index: 2; }

    .hero h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #ffffff, #93c5fd, #c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero p {
        color: #cbd5e1;
        font-size: 1.1rem;
        margin: 10px 0 18px 0;
        font-weight: 400;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 999px;
        color: #bbf7d0;
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(74, 222, 128, 0.35);
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        animation: pulseGlow 3s infinite;
    }

    /* -------------------------------------------------------
       KPI CARDS
    ------------------------------------------------------- */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 18px;
        margin-bottom: 25px;
    }

    .card {
        position: relative;
        padding: 22px;
        border-radius: 20px;
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out backwards;
    }

    /* Staggered animation delays */
    .card:nth-child(1) { animation-delay: 0.1s; }
    .card:nth-child(2) { animation-delay: 0.15s; }
    .card:nth-child(3) { animation-delay: 0.2s; }
    .card:nth-child(4) { animation-delay: 0.25s; }
    .card:nth-child(5) { animation-delay: 0.1s; }
    .card:nth-child(6) { animation-delay: 0.15s; }
    .card:nth-child(7) { animation-delay: 0.2s; }
    .card:nth-child(8) { animation-delay: 0.25s; }

    .card:hover {
        transform: translateY(-6px) scale(1.01);
        border-color: rgba(147, 197, 253, 0.4);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 0 0 20px rgba(59, 130, 246, 0.1);
    }

    .card::after {
        content: "";
        position: absolute;
        width: 120px; height: 120px;
        right: -40px; bottom: -50px;
        border-radius: 50%;
        opacity: 0.15;
        filter: blur(15px);
        transition: opacity 0.3s ease;
    }

    .card:hover::after { opacity: 0.3; }

    .card .icon {
        font-size: 1.5rem;
        margin-bottom: 10px;
        display: block;
    }

    .card .label {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }

    .card .value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.5px;
    }

    /* Accent Colors */
    .card.blue::after { background: #3b82f6; }
    .card.purple::after { background: #a855f7; }
    .card.cyan::after { background: #06b6d4; }
    .card.orange::after { background: #f97316; }
    .card.red::after { background: #ef4444; }
    .card.yellow::after { background: #eab308; }
    .card.green::after { background: #22c55e; }
    .card.pink::after { background: #ec4899; }

    /* -------------------------------------------------------
       SECTION HEADERS
    ------------------------------------------------------- */
    .section-header {
        margin: 35px 0 20px 0;
        font-size: 1.4rem;
        font-weight: 750;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .section-header::after {
        content: "";
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.15), transparent);
    }

    /* -------------------------------------------------------
       TABS (Standardized & Clean)
    ------------------------------------------------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255, 255, 255, 0.03);
        padding: 6px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 10px 22px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        border: none;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #e2e8f0;
        background: rgba(255, 255, 255, 0.05);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.15));
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(147, 197, 253, 0.2);
    }

    /* -------------------------------------------------------
       INFO / MANAGEMENT CARDS
    ------------------------------------------------------- */
    .info-card {
        padding: 26px;
        border-radius: 20px;
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        height: 100%;
        transition: transform 0.25s ease, border-color 0.25s ease;
        animation: fadeInUp 0.6s ease-out backwards;
    }

    .info-card:hover {
        transform: translateY(-4px);
        border-color: rgba(147, 197, 253, 0.3);
    }

    .info-card h4 {
        margin: 0 0 14px 0;
        color: #93c5fd;
        font-size: 1.1rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .info-card p {
        color: #cbd5e1;
        line-height: 1.7;
        font-size: 0.95rem;
        margin: 0;
    }

    .info-card strong {
        color: #f8fafc;
        font-weight: 700;
    }

    /* -------------------------------------------------------
       PLOTLY CHART CONTAINERS
    ------------------------------------------------------- */
    .stPlotlyChart {
        border-radius: 18px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 10px;
        transition: border-color 0.3s ease;
    }

    .stPlotlyChart:hover {
        border-color: rgba(255, 255, 255, 0.15);
    }

    /* -------------------------------------------------------
       EXPANDER
    ------------------------------------------------------- */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        color: #cbd5e1;
        font-weight: 600;
    }

    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 0 0 12px 12px;
        color: #94a3b8;
    }

    /* -------------------------------------------------------
       DATAFRAME
    ------------------------------------------------------- */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .signal-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        padding: 12px 14px;
        margin: 0 0 24px 0;
        border-radius: 14px;
        background: rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(148, 163, 184, 0.14);
    }

    .signal-strip span {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #cbd5e1;
    }

    .signal-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #4ade80;
        box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7);
        animation: pulseGlow 3s infinite;
    }

    @media (max-width: 1100px) {
        .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (prefers-reduced-motion: reduce) {
        * { animation: none !important; transition: none !important; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def card(icon, label, value, accent="blue"): 
    return f'''
    <div class="card {accent}">
        <div class="icon">{icon}</div>
        <div class="label">{label}</div>
        <div class="value">{value}</div>
    </div>
    '''

def money(v): 
    return f"${float(v):,.2f}"

def style(fig, h=360): 
    fig.update_layout(
        height=h,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb",
        margin=dict(l=15, r=15, t=55, b=15),
        hovermode="x unified"
    )
    return fig

# ============================================================
# DATA LOADING
# ============================================================
try: 
    kpi_df = get_executive_kpis()
    control_df = get_control_performance()
    sla_df = get_sla_kpis()
except Exception as error: 
    st.error(f"Unable to load executive data: {error}")
    st.stop()

if kpi_df.empty: 
    st.error("Executive KPI data is unavailable.")
    st.stop()

# Extract Data
k = kpi_df.iloc[0]
control_hits = int(k.control_hits)
customers = int(k.unique_customers)
impact = float(k.financial_impact)
open_count = int(k.open_exceptions)
high = int(k.high_severity_exceptions)
medium = int(k.medium_severity_exceptions)
low = int(k.low_severity_exceptions)
compliance = float(sla_df.iloc[0].sla_compliance_pct) if not sla_df.empty else 0

# ============================================================
# HERO SECTION
# ============================================================
st.markdown('''
<div class="hero">
    <div class="hero-content">
        <h1>Billing Assurance Control Tower</h1>
        <p>Revenue protection • Billing integrity • Discount governance • SLA operations</p>
        <span class="badge">● CONTROL ENVIRONMENT ACTIVE</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="signal-strip">
    <span><span class="signal-dot"></span> Control engine ready</span>
    <span>Data source • DuckDB</span>
    <span>Control hits • live</span>
    <span>Operational status • monitoring</span>
</div>
''', unsafe_allow_html=True)

# ============================================================
# KPI GRID
# ============================================================
st.markdown(f'''
<div class="kpi-grid">
    <div class="card blue">
        <div class="icon">🛡️</div>
        <div class="label">Control Hits</div>
        <div class="value">{control_hits:,}</div>
    </div>
    <div class="card purple">
        <div class="icon">👥</div>
        <div class="label">Unique Customers</div>
        <div class="value">{customers:,}</div>
    </div>
    <div class="card cyan">
        <div class="icon">💰</div>
        <div class="label">Financial Impact</div>
        <div class="value">{money(impact)}</div>
    </div>
    <div class="card orange">
        <div class="icon">🚨</div>
        <div class="label">Open Exceptions</div>
        <div class="value">{open_count:,}</div>
    </div>
    <div class="card red">
        <div class="icon">🔴</div>
        <div class="label">High Severity</div>
        <div class="value">{high:,}</div>
    </div>
    <div class="card yellow">
        <div class="icon">🟡</div>
        <div class="label">Medium Severity</div>
        <div class="value">{medium:,}</div>
    </div>
    <div class="card green">
        <div class="icon">🟢</div>
        <div class="label">Low Severity</div>
        <div class="value">{low:,}</div>
    </div>
    <div class="card pink">
        <div class="icon">⏱️</div>
        <div class="label">SLA Compliance</div>
        <div class="value">{compliance:.1f}%</div>
    </div>
</div>
''', unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
overview, performance, financial, management = st.tabs([
    "📊 Executive View", 
    "📈 Control Performance", 
    "💰 Financial Exposure", 
    "🧠 Management View"
])

# ------------------------------------------------------------
# TAB 1: EXECUTIVE VIEW
# ------------------------------------------------------------
with overview:
    st.markdown('<div class="section-header">Control Intelligence</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    
    with a: 
        st.plotly_chart(
            style(px.bar(
                control_df, x="control_id", y="control_hits", 
                text="control_hits", template="plotly_dark", 
                title="Control Activity"
            )), 
            use_container_width=True
        )
    
    with b: 
        st.plotly_chart(
            style(px.pie(
                pd.DataFrame({"severity":["High","Medium","Low"], "exceptions":[high,medium,low]}),
                names="severity", values="exceptions", hole=.58, 
                template="plotly_dark", title="Exception Severity"
            )), 
            use_container_width=True
        )
    
    st.markdown('''
    <div class="info-card">
        <h4>📝 Executive Interpretation</h4>
        <p>Control activity shows where exceptions are generated. Severity distribution shows the current exception profile, while SLA compliance provides operational monitoring visibility.</p>
    </div>
    ''', unsafe_allow_html=True)

# ------------------------------------------------------------
# TAB 2: CONTROL PERFORMANCE
# ------------------------------------------------------------
with performance:
    st.markdown('<div class="section-header">Control Performance Detail</div>', unsafe_allow_html=True)
    
    detail = control_df.copy()
    detail["financial_impact"] = detail.financial_impact.map(money)
    st.dataframe(detail, use_container_width=True, hide_index=True)
    
    st.plotly_chart(
        style(px.bar(
            control_df, x="control_id", y="control_hits", 
            color="control_name", template="plotly_dark", 
            title="Control Hits by Control"
        )), 
        use_container_width=True
    )

# ------------------------------------------------------------
# TAB 3: FINANCIAL EXPOSURE
# ------------------------------------------------------------
with financial:
    st.markdown('<div class="section-header">Financial Impact by Control</div>', unsafe_allow_html=True)
    
    fig = px.bar(
        control_df, x="control_id", y="financial_impact", 
        text="financial_impact", template="plotly_dark", 
        title="Identified Financial Impact"
    )
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(yaxis_tickprefix="$")
    st.plotly_chart(style(fig, 420), use_container_width=True)
    
    st.markdown(f'''
    <div class="info-card">
        <h4>💡 Financial Exposure</h4>
        <p>Total identified impact: <strong>{money(impact)}</strong><br>
        Financial impact represents control-identified impact requiring investigation and is not confirmed revenue loss.</p>
    </div>
    ''', unsafe_allow_html=True)

# ------------------------------------------------------------
# TAB 4: MANAGEMENT VIEW
# ------------------------------------------------------------
with management:
    a, b, c = st.columns(3)
    
    with a: 
        st.markdown(f'''
        <div class="info-card">
            <h4>🚨 Exception Position</h4>
            <p><strong>{open_count:,}</strong> exceptions are currently open.<br>
            High severity: <strong>{high:,}</strong></p>
        </div>
        ''', unsafe_allow_html=True)
    
    with b: 
        st.markdown(f'''
        <div class="info-card">
            <h4>💰 Financial Position</h4>
            <p>Controls identify <strong>{money(impact)}</strong> requiring investigation or operational decision-making.</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with c: 
        st.markdown(f'''
        <div class="info-card">
            <h4>⏱️ Operational Position</h4>
            <p>Current SLA compliance is <strong>{compliance:.1f}%</strong>. This view provides operational monitoring visibility.</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with st.expander("⚠️ Important caveat"): 
        st.write("Financial impact represents control-identified impact, not confirmed revenue loss.")

# ============================================================
# FOOTER
# ============================================================
st.markdown('''
<div style="text-align:center; color:#64748b; padding:30px 24px; font-size:.82rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 40px;">
    Billing Assurance & Revenue Protection Control Tower<br>
    DuckDB • Python • Streamlit • Plotly<br><br>
    Financial impact represents control-identified impact, not confirmed revenue loss.
</div>
''', unsafe_allow_html=True)