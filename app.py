import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Float Income Simulator",
    page_icon="💹",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="metric-container"] { background: #f5f4f0; border-radius: 8px; padding: 12px 16px; }
    .stTabs [data-baseweb="tab"] { font-size: 13px; }
</style>
""", unsafe_allow_html=True)

st.title("Float Income Simulator")
st.caption("Comparación de estrategias de inversión durante el período de float")

# ── Sidebar ───────────────────────────────────────────────────────────────────
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

    days = st.slider("Plazo (dias)", min_value=1, max_value=30, value=5)

    st.divider()
    st.subheader("Tasas anuales")
    r_br  = st.number_input("Brasil - CDI (%)",   min_value=0.0, max_value=50.0, value=14.00, step=0.25)
    r_mx  = st.number_input("Mexico - TIIE (%)",  min_value=0.0, max_value=50.0, value=6.75,  step=0.25)
    r_usd = st.number_input("USD benchmark (%)",  min_value=0.0, max_value=20.0, value=4.00,  step=0.25)

    st.divider()
    st.subheader("Estrategia A")
    fx_spread_bps = st.number_input(
        "FX spread cobrado al cliente (bps)",
        min_value=0.0, max_value=200.0, value=30.0, step=5.0,
        help="Spread en bps sobre el tipo de cambio que cobras al cliente cuando convierte al dia N"
    )

    st.divider()
    st.subheader("Estrategia B - escenario FX")
    fx_move = st.slider(
        "Movimiento BRL/USD dia 0 a dia N (%)",
        min_value=-5.0, max_value=5.0, step=0.1, value=0.0,
        help="Positivo = BRL se deprecia (ganas al haber convertido temprano). Negativo = BRL se aprecia (pierdes)."
    )
    st.caption("Positivo = depreciacion BRL (ganancia B) · Negativo = apreciacion BRL (perdida B)")

    st.divider()
    st.caption("Formula: Capital x Tasa x Dias / 365 (Act/365)")

# ── Calculos ──────────────────────────────────────────────────────────────────
def interest(cap, rate, d):
    return cap * (rate / 100) * d / 365

def sign_usd(n):
    return f"+${n:,.0f}" if n >= 0 else f"-${abs(n):,.0f}"

# Estrategia A
carry_br_a    = interest(capital, r_br,  days)
carry_mx_a    = interest(capital, r_mx,  days)
fx_spread_usd = capital * (fx_spread_bps / 10_000)

pnl_a_br = carry_br_a + fx_spread_usd
pnl_a_mx = carry_mx_a + fx_spread_usd

eff_a_br = pnl_a_br / capital * 100
eff_a_mx = pnl_a_mx / capital * 100

# Estrategia B
carry_usd_b = interest(capital, r_usd, days)
fx_pnl_b    = capital * (fx_move / 100)
pnl_b       = carry_usd_b + fx_pnl_b
eff_b       = pnl_b / capital * 100

# Punto de indiferencia
indif_br = (pnl_a_br - carry_usd_b) / capital * 100
indif_mx = (pnl_a_mx - carry_usd_b) / capital * 100

# ── Header: cards estrategias ─────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown(f"""
    <div style="background:#E1F5EE; border:0.5px solid #9FE1CB; border-radius:12px; padding:20px 24px; height:100%;">
        <div style="font-size:11px; color:#5F5E5A; font-weight:500; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:8px;">
            Estrategia A — Invertir en moneda local
        </div>
        <div style="font-size:12px; color:#0F6E56; margin-bottom:16px;">
            Recibis BRL/MXN → invertis local → cliente convierte al dia {days} → cobras FX spread · Sin riesgo cambiario
        </div>
        <div style="display:flex; gap:32px;">
            <div>
                <div style="font-size:12px; color:#5F5E5A;">Brasil (CDI {r_br:.2f}%)</div>
                <div style="font-size:30px; font-weight:600; color:#0F6E56;">{sign_usd(pnl_a_br)}</div>
                <div style="font-size:11px; color:#0F6E56;">carry {sign_usd(carry_br_a)} + FX spread {sign_usd(fx_spread_usd)}</div>
                <div style="font-size:11px; color:#5F5E5A;">{eff_a_br:.4f}% ef. {days}d</div>
            </div>
            <div>
                <div style="font-size:12px; color:#5F5E5A;">Mexico (TIIE {r_mx:.2f}%)</div>
                <div style="font-size:30px; font-weight:600; color:#185FA5;">{sign_usd(pnl_a_mx)}</div>
                <div style="font-size:11px; color:#185FA5;">carry {sign_usd(carry_mx_a)} + FX spread {sign_usd(fx_spread_usd)}</div>
                <div style="font-size:11px; color:#5F5E5A;">{eff_a_mx:.4f}% ef. {days}d</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    pnl_b_color = "#3B6D11" if pnl_b >= 0 else "#A32D2D"
    fx_label = "BRL se deprecio, ganas" if fx_move > 0 else "BRL se aprecio, pierdes" if fx_move < 0 else "Sin movimiento FX"
    st.markdown(f"""
    <div style="background:#E6F1FB; border:0.5px solid #B5D4F4; border-radius:12px; padding:20px 24px; height:100%;">
        <div style="font-size:11px; color:#5F5E5A; font-weight:500; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:8px;">
            Estrategia B — Convertir en dia 0 e invertir en USD
        </div>
        <div style="font-size:12px; color:#185FA5; margin-bottom:16px;">
            Recibis BRL/MXN → convertis a USD en dia 0 → invertis en USD → asumis riesgo FX
        </div>
        <div style="display:flex; gap:32px;">
            <div>
                <div style="font-size:12px; color:#5F5E5A;">P&L total (USD {r_usd:.2f}%)</div>
                <div style="font-size:30px; font-weight:600; color:{pnl_b_color};">{sign_usd(pnl_b)}</div>
                <div style="font-size:11px; color:#185FA5;">carry {sign_usd(carry_usd_b)} + P&L FX {sign_usd(fx_pnl_b)}</div>
                <div style="font-size:11px; color:#5F5E5A;">{eff_b:.4f}% ef. {days}d</div>
            </div>
            <div style="margin-top:24px;">
                <div style="font-size:11px; color:#5F5E5A;">FX move: <strong>{fx_move:+.1f}%</strong></div>
                <div style="font-size:11px; color:{pnl_b_color}; margin-top:4px;">{fx_label}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Diferencial ───────────────────────────────────────────────────────────────
st.subheader("Diferencial: A vs B")

diff_br = pnl_a_br - pnl_b
diff_mx = pnl_a_mx - pnl_b

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("A (Brasil) − B", sign_usd(diff_br),
              "A conviene" if diff_br > 0 else "B conviene",
              delta_color="normal" if diff_br > 0 else "inverse")
with c2:
    st.metric("A (Mexico) − B", sign_usd(diff_mx),
              "A conviene" if diff_mx > 0 else "B conviene",
              delta_color="normal" if diff_mx > 0 else "inverse")
with c3:
    st.metric("Indiferencia Brasil", f"{indif_br:+.3f}%",
              f"BRL debe depreciarse mas de {indif_br:.3f}% para que B supere a A",
              delta_color="off")
with c4:
    st.metric("Indiferencia Mexico", f"{indif_mx:+.3f}%",
              f"BRL debe depreciarse mas de {indif_mx:.3f}% para que B supere a A",
              delta_color="off")

st.divider()

# ── Grafico P&L vs FX move ────────────────────────────────────────────────────
st.subheader("P&L por escenario de movimiento FX")

fx_range      = [x / 10 for x in range(-50, 51)]
pnl_b_range   = [carry_usd_b + capital * (f / 100) for f in fx_range]
line_a_br     = [pnl_a_br] * len(fx_range)
line_a_mx     = [pnl_a_mx] * len(fx_range)

fig = go.Figure()
fig.add_trace(go.Scatter(x=fx_range, y=pnl_b_range,
    name="Estrategia B", line=dict(color="#185FA5", width=2),
    hovertemplate="FX: %{x:+.1f}%<br>B: $%{y:,.0f}<extra></extra>"))
fig.add_trace(go.Scatter(x=fx_range, y=line_a_br,
    name="A — Brasil", line=dict(color="#0F6E56", width=2, dash="dash"),
    hovertemplate="A Brasil: $%{y:,.0f}<extra></extra>"))
fig.add_trace(go.Scatter(x=fx_range, y=line_a_mx,
    name="A — Mexico", line=dict(color="#185FA5", width=2, dash="dot"),
    hovertemplate="A Mexico: $%{y:,.0f}<extra></extra>"))

fig.add_vline(x=fx_move, line_dash="dot", line_color="rgba(0,0,0,0.3)",
              annotation_text=f"actual ({fx_move:+.1f}%)", annotation_position="top right")
fig.add_vline(x=indif_br, line_dash="longdash", line_color="#0F6E56",
              annotation_text=f"indif. BR ({indif_br:+.3f}%)",
              annotation_position="bottom right", annotation_font_color="#0F6E56")
fig.add_vline(x=indif_mx, line_dash="longdash", line_color="#185FA5",
              annotation_text=f"indif. MX ({indif_mx:+.3f}%)",
              annotation_position="bottom left", annotation_font_color="#185FA5")

fig.update_layout(
    xaxis_title="Movimiento FX BRL/USD (%)",
    yaxis_title="P&L (USD)",
    yaxis_tickformat="$,.0f",
    xaxis_tickformat="+.1f",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(l=0, r=0, t=40, b=0),
    height=360,
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)
st.caption("A la derecha del punto de indiferencia: B supera a A. A la izquierda: A supera a B.")

st.divider()

# ── Tabla de escenarios ───────────────────────────────────────────────────────
st.subheader("Tabla comparativa por escenario FX")

fx_steps = [-3.0, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0]
snap_fx  = min(fx_steps, key=lambda x: abs(x - fx_move))

def build_table(pnl_a, label_a):
    rows = []
    for fx_s in fx_steps:
        carry_b = interest(capital, r_usd, days)
        fx_pl   = capital * (fx_s / 100)
        p_b     = carry_b + fx_pl
        diff    = pnl_a - p_b
        rows.append({
            "FX move": f"{fx_s:+.1f}%",
            f"P&L A ({label_a})": pnl_a,
            "Carry B": carry_b,
            "P&L FX (B)": fx_pl,
            "P&L B total": p_b,
            "A - B": diff,
            "Conviene": "A" if diff > 0 else ("B" if diff < 0 else "="),
        })
    return pd.DataFrame(rows)

def style_table(df, snap):
    fmt = {
        df.columns[1]: lambda x: sign_usd(x),
        "Carry B":      lambda x: sign_usd(x),
        "P&L FX (B)":   lambda x: sign_usd(x),
        "P&L B total":  lambda x: sign_usd(x),
        "A - B":        lambda x: sign_usd(x),
    }
    def color_rows(row):
        is_cur = row["FX move"] == f"{snap:+.1f}%"
        bg = "background-color: #faeeda" if is_cur else ""
        diff_c = "color: #3B6D11; font-weight:600" if row["A - B"] > 0 else "color: #A32D2D; font-weight:600"
        return [bg] * (len(row) - 2) + [diff_c, bg]
    return df.style.apply(color_rows, axis=1).format(fmt)

tab_br, tab_mx = st.tabs(["vs Brasil (CDI)", "vs Mexico (TIIE)"])
with tab_br:
    st.dataframe(style_table(build_table(pnl_a_br, "BR"), snap_fx), use_container_width=True, hide_index=True)
with tab_mx:
    st.dataframe(style_table(build_table(pnl_a_mx, "MX"), snap_fx), use_container_width=True, hide_index=True)

st.caption("Fila resaltada = escenario FX actualmente seleccionado.")
st.divider()
st.caption(
    "Estrategia A: carry en moneda local + FX spread cobrado al cliente. Sin riesgo cambiario. "
    "Estrategia B: convertis a USD en dia 0, invertis a tasa benchmark, asumis riesgo FX. "
    "Formula: Capital x Tasa x Dias / 365 (Act/365). Analisis informativo."
)
