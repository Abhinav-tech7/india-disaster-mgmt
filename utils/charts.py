"""
utils/charts.py — All Plotly chart builders.
"""

import plotly.graph_objects as go
import pandas as pd


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


_CARD = "#111827"
_GRID = "#1e2d4a"
_TEXT = "#94a3b8"
_FONT = "Space Grotesk, system-ui, sans-serif"


def _base() -> dict:
    return dict(
        paper_bgcolor=_CARD,
        plot_bgcolor =_CARD,
        font=dict(family=_FONT, color=_TEXT, size=12),
        # t=80 gives enough room for title + legend row without overlapping the chart line
        margin=dict(l=50, r=20, t=80, b=40),
        hovermode="x unified",
        xaxis=dict(gridcolor=_GRID, linecolor=_GRID, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=_GRID, linecolor=_GRID, showgrid=True, zeroline=False),
    )


# ── 1. Historical + Forecast ──────────────────────────────────────────────────
def historical_forecast_chart(hist_df, pred_df, disaster, color, title):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist_df["date"], y=hist_df["value"],
        name="Historical", mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=hex_to_rgba(color, 0.12),
        hovertemplate="%{y:.1f}<extra>Historical</extra>",
    ))

    x_band = list(pred_df["date"]) + list(reversed(list(pred_df["date"])))
    y_band = list(pred_df["ci_upper"]) + list(reversed(list(pred_df["ci_lower"])))
    fig.add_trace(go.Scatter(
        x=x_band, y=y_band,
        fill="toself", fillcolor=hex_to_rgba(color, 0.08),
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))

    fig.add_trace(go.Scatter(
        x=pred_df["date"], y=pred_df["value"],
        name="ML Forecast", mode="lines",
        line=dict(color=color, width=2, dash="dot"),
        hovertemplate="%{y:.1f}<extra>ML Forecast</extra>",
    ))

    threshold = max(float(hist_df["value"].mean()) * 1.8,
                    float(pred_df["value"].max()) * 0.9)
    all_x = list(hist_df["date"]) + list(pred_df["date"])
    fig.add_trace(go.Scatter(
        x=all_x, y=[threshold] * len(all_x),
        name="Alert Threshold", mode="lines",
        line=dict(color="#ef4444", width=1, dash="dash"),
        hoverinfo="skip",
    ))

    today_str = pd.Timestamp(hist_df["date"].iloc[-1]).strftime("%Y-%m-%d")
    fig.add_shape(type="line",
                  x0=today_str, x1=today_str, y0=0, y1=1,
                  xref="x", yref="paper",
                  line=dict(color="#475569", width=1, dash="dash"))
    fig.add_annotation(x=today_str, y=0.99, xref="x", yref="paper",
                       text="Today", showarrow=False,
                       xanchor="left", yanchor="top",
                       font=dict(color="#64748b", size=11))

    layout = _base()
    # Title at top — pad y so it sits well above the plot area
    layout["title"] = dict(
        text=title,
        font=dict(size=14, color="#e2e8f0"),
        x=0, xanchor="left",
        y=0.97, yanchor="top",   # explicit y so legend row below doesn't overlap
    )
    layout["height"] = 300   # taller chart so title + legend + plot all have room
    layout["showlegend"] = True
    # Legend placed BELOW title, still inside the top margin — y=0.88 keeps it
    # between the title (0.97) and the plot area (which starts ~0.82 with t=80)
    layout["legend"] = dict(
        orientation="h",
        yanchor="top", y=0.88,
        xanchor="left", x=0,
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=11, color=_TEXT),
    )
    fig.update_layout(**layout)
    return fig


# ── 2. Multi-disaster trend ───────────────────────────────────────────────────
def multi_forecast_chart(forecasts, colors):
    fig = go.Figure()
    for d, df in forecasts.items():
        c = colors.get(d, "#3b82f6")
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["value"],
            name=d.capitalize(), mode="lines",
            line=dict(color=c, width=2),
            hovertemplate=f"%{{y:.1f}}<extra>{d.capitalize()}</extra>",
        ))
    layout = _base()
    layout["height"] = 300
    layout["showlegend"] = True
    layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.01,
                             xanchor="right", x=1,
                             bgcolor="rgba(0,0,0,0)",
                             font=dict(size=11, color=_TEXT))
    fig.update_layout(**layout)
    return fig


# ── 3. Radar chart ────────────────────────────────────────────────────────────
def radar_chart(state, risk_dict, colors):
    labels = [k.capitalize() for k in risk_dict]
    values = list(risk_dict.values())
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]], theta=labels + [labels[0]],
        fill="toself", fillcolor="rgba(59,130,246,0.15)",
        line=dict(color="#3b82f6", width=2),
        marker=dict(color="#3b82f6", size=6), name=state,
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=_CARD,
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=_GRID,
                            tickfont=dict(color=_TEXT, size=10)),
            angularaxis=dict(tickfont=dict(color=_TEXT, size=11), gridcolor=_GRID),
        ),
        paper_bgcolor=_CARD,
        font=dict(family=_FONT, color=_TEXT),
        margin=dict(l=30, r=30, t=30, b=30),
        height=280, showlegend=False,
    )
    return fig


# ── 4. Monthly heatmap ────────────────────────────────────────────────────────
def monthly_heatmap(matrix_df):
    fig = go.Figure(go.Heatmap(
        z=matrix_df.values.T.tolist(),
        x=matrix_df.index.tolist(),
        y=[c.capitalize() for c in matrix_df.columns],
        colorscale=[[0,"#1e3a5f"],[0.3,"#1d4ed8"],[0.6,"#f59e0b"],[0.8,"#ef4444"],[1,"#7f1d1d"]],
        zmin=0, zmax=100, hoverongaps=False,
        hovertemplate="Month:%{x}<br>%{y}: %{z:.0f}<extra></extra>",
        showscale=True,
        colorbar=dict(tickfont=dict(color=_TEXT, size=10), bgcolor=_CARD,
                      bordercolor=_GRID, len=0.8),
    ))
    layout = _base()
    layout["height"] = 280
    layout["showlegend"] = False
    layout["xaxis"] = dict(side="bottom", gridcolor="rgba(0,0,0,0)")
    layout["yaxis"] = dict(gridcolor="rgba(0,0,0,0)")
    fig.update_layout(**layout)
    return fig


# ── 5. Rainfall bar chart ─────────────────────────────────────────────────────
def rainfall_comparison_chart(actual, normal, flood_thresh, drought_thresh):
    cats = ["Normal Rainfall", "Actual Rainfall", "Flood Threshold", "Drought Threshold"]
    vals = [normal, actual, flood_thresh, drought_thresh]
    bcolors = [
        "#3b82f6",
        "#ef4444" if actual > flood_thresh else "#f59e0b" if actual > normal else "#10b981",
        "#f59e0b", "#f97316",
    ]
    fig = go.Figure(go.Bar(
        x=cats, y=vals,
        marker=dict(color=bcolors, line=dict(color=bcolors, width=1.5), opacity=0.85),
        text=[f"{v:.1f}" for v in vals], textposition="outside",
        textfont=dict(color=_TEXT, size=11),
        hovertemplate="%{x}: %{y:.1f} mm<extra></extra>",
    ))
    layout = _base()
    layout["height"] = 260
    layout["showlegend"] = False
    layout["yaxis"] = dict(title="Rainfall (mm)", gridcolor=_GRID, linecolor=_GRID,
                            showgrid=True, zeroline=False,
                            title_font=dict(color=_TEXT, size=12))
    fig.update_layout(**layout)
    return fig


# ── 6. Risk gauge ─────────────────────────────────────────────────────────────
def risk_gauge(score, label):
    color = ("#10b981" if score < 35 else "#3b82f6" if score < 55
             else "#f59e0b" if score < 75 else "#ef4444")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=score,
        delta=dict(reference=50, valueformat=".1f", font=dict(color=color, size=14)),
        title=dict(text=label, font=dict(size=13, color=_TEXT)),
        gauge=dict(
            axis=dict(range=[0,100], tickcolor=_TEXT, tickfont=dict(size=10, color=_TEXT)),
            bar=dict(color=color, thickness=0.25),
            bgcolor=_CARD, borderwidth=0,
            steps=[
                dict(range=[0,  35], color="rgba(16,185,129,0.15)"),
                dict(range=[35, 55], color="rgba(59,130,246,0.15)"),
                dict(range=[55, 75], color="rgba(245,158,11,0.15)"),
                dict(range=[75,100], color="rgba(239,68,68,0.15)"),
            ],
            threshold=dict(line=dict(color=color, width=3), thickness=0.75, value=score),
        ),
        number=dict(font=dict(color=color, size=32), suffix="/100"),
    ))
    fig.update_layout(paper_bgcolor=_CARD, font=dict(family=_FONT, color=_TEXT),
                      margin=dict(l=20, r=20, t=40, b=10), height=220)
    return fig


# ── 7. Alert donut ────────────────────────────────────────────────────────────
def alert_donut(counts):
    labels = list(counts.keys())
    values = list(counts.values())
    palette = ["#3b82f6","#10b981","#8b5cf6","#ef4444","#f59e0b","#06b6d4"]
    total = sum(values)

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.60,
        marker=dict(
            colors=palette[:len(labels)],
            line=dict(color="#0a0e1a", width=2),
        ),
        # Show only percentage inside slices — no label inside (prevents overlap/cutoff)
        textinfo="percent",
        textposition="inside",
        textfont=dict(size=11, color="#ffffff"),  # white text on coloured slices
        insidetextorientation="horizontal",
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
        # Pull the Tsunami slice slightly so its thin sliver is visible
        pull=[0.04 if lbl == "Tsunami" else 0 for lbl in labels],
        direction="clockwise",
        sort=True,
    ))

    fig.update_layout(
        paper_bgcolor=_CARD,
        font=dict(family=_FONT, color=_TEXT),
        # More bottom margin for legend
        margin=dict(l=10, r=10, t=10, b=10),
        height=280,
        # Legend below the donut — each entry shows colour square + label
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.22,
            xanchor="center", x=0.5,
            font=dict(size=11, color="#e2e8f0"),
            bgcolor="rgba(0,0,0,0)",
            itemsizing="constant",
            tracegroupgap=4,
        ),
    )
    return fig


# ── 8. Composite risk bar ─────────────────────────────────────────────────────
def composite_risk_bar(table_df):
    bcolors = [
        "#ef4444" if v >= 75 else "#f59e0b" if v >= 55
        else "#3b82f6" if v >= 35 else "#10b981"
        for v in table_df["Composite Risk"]
    ]
    fig = go.Figure(go.Bar(
        x=table_df["Date"], y=table_df["Composite Risk"],
        marker=dict(color=bcolors, opacity=0.85),
        hovertemplate="%{x}<br>Risk:%{y:.1f}<extra></extra>",
    ))
    for yv, lc, txt in [(55,"#f59e0b","HIGH"),(75,"#ef4444","SEVERE")]:
        fig.add_shape(type="line", x0=0, x1=1, y0=yv, y1=yv,
                      xref="paper", yref="y",
                      line=dict(color=lc, width=1, dash="dash"))
        fig.add_annotation(x=0.99, y=yv, xref="paper", yref="y",
                           text=txt, showarrow=False, xanchor="right", yanchor="bottom",
                           font=dict(color=lc, size=10))
    layout = _base()
    layout["height"] = 220
    layout["showlegend"] = False
    layout["xaxis"] = dict(tickangle=-45, tickfont=dict(size=9),
                            gridcolor=_GRID, linecolor=_GRID, showgrid=True, zeroline=False)
    layout["yaxis"] = dict(range=[0,110], gridcolor=_GRID, linecolor=_GRID,
                            showgrid=True, zeroline=False)
    fig.update_layout(**layout)
    return fig
