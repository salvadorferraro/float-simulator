import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Float Income Simulator",
    page_icon="💹",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .metric-label { font-size: 12px !important; }
    div[data-testid="metric-container"] { background: #f5f4f0; border-radius: 8px; padding: 12px 16px; }
    .stTabs [data-baseweb="tab"] { font-size: 13px; }
</style>
""", unsafe_allow_html=True)

st.title("Float Income Simulator")
st.caption("Brasil (BRL) · México (MXN) · USD — retorno por inversión local durante el período de float")

st.divider()

# ── Sidebar: parámetros ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("Parámetros")

    st.markdown("**Capital (USD equiv.)**")
    cap_col1, cap_col2 = st.columns([2, 1])
    with cap_col1:
        cap_slider = st.slider(
            "slider", label_visibility="collapsed",
            min_value=100_000, max_value=20_000_000,
            step=100_000, value=1_000_000,
            key="cap_slider"
        )
    with cap_col2:
        cap_input = st.number_input(
            "o escribi", label_visibility="visible",
            min_value=1, max_value=500_000_000,
            value=cap_slider, step=100_000,
            key="cap_input"
        )
    capital = cap_input

    days = st.slider("Plazo (días)", min_value=1, max_value=30, value=5)

    fx = st.slider(
        "Movimiento FX (%)",
        min_value=-3.0, max_value=2.0, step=0.1, value=0.0,
        help="Positivo = apreciación moneda local vs USD · Negativo = depreciación"
    )

    st.divider()
    st.subheader("Tasas anuales")

    r_br  = st.number_input("Brasil — CDI (%)",      min_value=0.0, max_value=50.0, value=14.00, step=0.25)
    r_mx  = st.number_input("México — TIIE fondeo (%)", min_value=0.0, max_value=50.0, value=6.75, step=0.25)
    r_usd = st.number_input("USD benchmark (%)",     min_value=0.0, max_value=20.0, value=4.00, step=0.25)

    st.divider()
    st.caption("Fórmula: Capital × Tasa × Días / 365 (Act/365, sin capitalización)")

# ── Cálculos core ─────────────────────────────────────────────────────────────
def interest(cap, rate, d): return cap * (rate / 100) * d / 365
def net_usd(cap, rate, d, fx_pct): return interest(cap, rate, d) + cap * (fx_pct / 100)
def breakeven(cap, rate, d, r_usd_):
    return -((interest(cap, rate, d) - interest(cap, r_usd_, d)) / cap) * 100

i_br  = interest(capital, r_br,  days)
i_mx  = interest(capital, r_mx,  days)
i_usd = interest(capital, r_usd, days)

n_br  = net_usd(capital, r_br,  days, fx)
n_mx  = net_usd(capital, r_mx,  days, fx)

be_br = breakeven(capital, r_br,  days, r_usd)
be_mx = breakeven(capital, r_mx,  days, r_usd)

eff_br  = i_br  / capital * 100
eff_mx  = i_mx  / capital * 100
eff_usd = i_usd / capital * 100

def sign(n): return f"+${n:,.0f}" if n >= 0 else f"-${abs(n):,.0f}"
def pct(n):  return f"+{n:.4f}%" if n >= 0 else f"{n:.4f}%"

# ── Spread destacado ──────────────────────────────────────────────────────────
spread_br_pct = eff_br - eff_usd          # diferencia en %
spread_mx_pct = eff_mx - eff_usd
spread_br_bps = spread_br_pct * 100       # en bps
spread_mx_bps = spread_mx_pct * 100

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #E1F5EE 0%, #E6F1FB 100%);
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 1.5rem;
    border: 0.5px solid #9FE1CB;
">
    <p style="margin:0 0 12px 0; font-size:12px; color:#5F5E5A; font-weight:500; letter-spacing:0.05em; text-transform:uppercase;">
        Spread ganado sobre benchmark USD — {days} día{'s' if days != 1 else ''} · ${capital:,.0f}
    </p>
    <div style="display:flex; gap:40px; flex-wrap:wrap; align-items:flex-end;">
        <div>
            <div style="font-size:11px; color:#0F6E56; margin-bottom:4px;">Brasil (CDI {r_br:.2f}% a.a.)</div>
            <span style="font-size:32px; font-weight:600; color:#0F6E56;">{spread_br_pct:+.4f}%</span>
            <span style="font-size:16px; color:#0F6E56; margin-left:10px; font-weight:500;">{spread_br_bps:+.1f} bps</span>
            <div style="font-size:11px; color:#5F5E5A; margin-top:2px;">Tasa ef. {days}d: {eff_br:.4f}%</div>
        </div>
        <div style="width:1px; background:#9FE1CB; align-self:stretch;"></div>
        <div>
            <div style="font-size:11px; color:#185FA5; margin-bottom:4px;">México (TIIE {r_mx:.2f}% a.a.)</div>
            <span style="font-size:32px; font-weight:600; color:#185FA5;">{spread_mx_pct:+.4f}%</span>
            <span style="font-size:16px; color:#185FA5; margin-left:10px; font-weight:500;">{spread_mx_bps:+.1f} bps</span>
            <div style="font-size:11px; color:#5F5E5A; margin-top:2px;">Tasa ef. {days}d: {eff_mx:.4f}%</div>
        </div>
        <div style="width:1px; background:#9FE1CB; align-self:stretch;"></div>
        <div>
            <div style="font-size:11px; color:#888780; margin-bottom:4px;">USD benchmark ({r_usd:.2f}% a.a.)</div>
            <span style="font-size:32px; font-weight:600; color:#888780;">{eff_usd:.4f}%</span>
            <span style="font-size:16px; color:#888780; margin-left:10px; font-weight:500;">0 bps</span>
            <div style="font-size:11px; color:#5F5E5A; margin-top:2px;">Base de comparación</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Vista 1: Moneda local ─────────────────────────────────────────────────────
st.subheader("Retorno en moneda local (sin efecto FX)")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Brasil — BRL", sign(i_br), f"{pct(eff_br)} ef. {days}d")
with col2:
    st.metric("México — MXN", sign(i_mx), f"{pct(eff_mx)} ef. {days}d")
with col3:
    st.metric("USD benchmark", sign(i_usd), f"{pct(eff_usd)} ef. {days}d")

st.divider()

# ── Vista 2: Neto USD ─────────────────────────────────────────────────────────
st.subheader(f"Retorno convertido a USD  ·  FX supuesto: {fx:+.1f}%")
col4, col5, col6 = st.columns(3)

vs_br = n_br - i_usd
vs_mx = n_mx - i_usd

with col4:
    st.metric("Brasil — neto USD", sign(n_br), f"vs benchmark: {sign(vs_br)}")
with col5:
    st.metric("México — neto USD", sign(n_mx), f"vs benchmark: {sign(vs_mx)}")
with col6:
    st.metric("USD benchmark", sign(i_usd), "base de comparación")

col_be1, col_be2, _ = st.columns([1, 1, 2])
with col_be1:
    st.info(f"**Breakeven BRL:** {be_br:.3f}%  \nDepreciación máx. tolerable")
with col_be2:
    st.info(f"**Breakeven MXN:** {be_mx:.3f}%  \nDepreciación máx. tolerable")

st.divider()

# ── Gráfico evolución por plazo ───────────────────────────────────────────────
st.subheader("Evolución del retorno neto USD por plazo (1–30 días)")

day_range = list(range(1, 31))
y_br  = [net_usd(capital, r_br,  d, fx) for d in day_range]
y_mx  = [net_usd(capital, r_mx,  d, fx) for d in day_range]
y_usd = [interest(capital, r_usd, d)     for d in day_range]

fig = go.Figure()
fig.add_trace(go.Scatter(x=day_range, y=y_br,  name="Brasil",        line=dict(color="#0F6E56", width=2)))
fig.add_trace(go.Scatter(x=day_range, y=y_mx,  name="México",        line=dict(color="#185FA5", width=2)))
fig.add_trace(go.Scatter(x=day_range, y=y_usd, name="USD benchmark", line=dict(color="#888780", width=2, dash="dash")))

fig.add_vline(x=days, line_dash="dot", line_color="rgba(0,0,0,0.3)", annotation_text=f"día {days}")

fig.update_layout(
    xaxis_title="Días",
    yaxis_title="USD",
    yaxis_tickformat="$,.0f",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(l=0, r=0, t=40, b=0),
    height=320,
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)
st.caption("FX fijo al supuesto actual · Act/365 sin capitalización intradía")

st.divider()

# ── Tabla de escenarios FX ────────────────────────────────────────────────────
st.subheader("Tabla de escenarios FX")

fx_steps = [-3.0, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]

tab_br, tab_mx = st.tabs(["Brasil (BRL)", "México (MXN)"])

def build_scenario_df(rate, cap, d, r_usd_, fx_steps):
    rows = []
    usd_inc = interest(cap, r_usd_, d)
    for fx_s in fx_steps:
        int_   = interest(cap, rate, d)
        fx_pl  = cap * (fx_s / 100)
        net    = int_ + fx_pl
        vs     = net - usd_inc
        rows.append({
            "Escenario FX": f"{fx_s:+.1f}%",
            "Interés (USD)": int_,
            "P&L FX (USD)": fx_pl,
            "Neto USD": net,
            "vs benchmark": vs,
        })
    return pd.DataFrame(rows)

def style_df(df, cur_fx, fx_steps):
    snap = min(fx_steps, key=lambda x: abs(x - cur_fx))

    def color_row(row):
        is_cur = row["Escenario FX"] == f"{snap:+.1f}%"
        bg = "background-color: #faeeda" if is_cur else ""
        vs = row["vs benchmark"]
        vc = "color: #3B6D11; font-weight:600" if vs >= 0 else "color: #A32D2D; font-weight:600"
        return [bg, "", "", vc, vc]

    fmt = {
        "Interés (USD)": lambda x: f"+${x:,.0f}",
        "P&L FX (USD)":  lambda x: f"+${x:,.0f}" if x >= 0 else f"-${abs(x):,.0f}",
        "Neto USD":      lambda x: f"+${x:,.0f}" if x >= 0 else f"-${abs(x):,.0f}",
        "vs benchmark":  lambda x: f"+${x:,.0f}" if x >= 0 else f"-${abs(x):,.0f}",
    }
    return df.style.apply(color_row, axis=1).format(fmt)

with tab_br:
    df_br = build_scenario_df(r_br, capital, days, r_usd, fx_steps)
    st.dataframe(style_df(df_br, fx, fx_steps), use_container_width=True, hide_index=True)

with tab_mx:
    df_mx = build_scenario_df(r_mx, capital, days, r_usd, fx_steps)
    st.dataframe(style_df(df_mx, fx, fx_steps), use_container_width=True, hide_index=True)

st.caption("Fila resaltada = escenario FX actualmente seleccionado. Verde = supera benchmark · Rojo = queda por debajo.")

st.divider()
st.caption(
    "Fuentes: Brasil CDI ~14,00% (SELIC 14,75% – COPOM 18-mar-2026) · "
    "México TIIE fondeo ~6,75% (Banxico mar-2026) · USD benchmark 4,00%. "
    "Simulador informativo — confirmar tasas y spreads FX con tesorería."
)
