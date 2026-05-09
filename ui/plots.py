import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from ui.simulation import SimulationResult


_DARK_BG = "#1a2236"


def _apply_dark_theme(fig: go.Figure, height: int = 480) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=16, r=16, t=30, b=16),
        paper_bgcolor=_DARK_BG,
        plot_bgcolor=_DARK_BG,
    )
    return fig


def make_prices_chart(prices: np.ndarray) -> go.Figure:
    fig = px.bar(
        x=list(range(24)),
        y=prices,
        labels={"x": "Час", "y": "Цена за кВт·ч"},
        text=prices,
    )
    fig.update_traces(
        marker_color="#3b82f6",
        textposition="outside",
        textfont_size=14,
    )
    _apply_dark_theme(fig, height=420)
    fig.update_layout(
        showlegend=False,
        xaxis=dict(tickmode="linear", dtick=1, title_font_size=14),
        yaxis=dict(range=[0, max(prices) * 1.2], title_font_size=14),
    )
    return fig


def make_policy_heatmap(policy: np.ndarray, max_battery: int) -> go.Figure:
    heatmap = go.Heatmap(
        z=policy.T,
        x=list(range(24)),
        y=list(range(max_battery + 1)),
        colorscale=[
            [0.0, "#b91c1c"],
            [0.25, "#ef4444"],
            [0.5, "#475569"],
            [0.75, "#3b82f6"],
            [1.0, "#1d4ed8"],
        ],
        zmin=-2,
        zmax=2,
        showscale=True,
        colorbar=dict(
            tickvals=[-2, -1, 0, 1, 2],
            ticktext=["Продать 2", "Продать 1", "Ничего", "Купить 1", "Купить 2"],
            title="Действие",
            len=0.8,
            title_font_size=13,
            bgcolor=_DARK_BG,
        ),
    )
    fig = go.Figure(data=heatmap)
    _apply_dark_theme(fig, height=500)
    fig.update_layout(
        xaxis=dict(tickmode="linear", dtick=1, title="Час", title_font_size=14),
        yaxis=dict(dtick=1, title="Заряд батареи, кВт·ч", title_font_size=14),
    )
    return fig


def make_value_heatmap(V: np.ndarray, max_battery: int) -> go.Figure:
    fig = px.imshow(
        V.T,
        labels=dict(x="Час", y="Заряд батареи", color="Ценность"),
        x=list(range(24)),
        y=list(range(max_battery + 1)),
        origin="lower",
        aspect="auto",
        color_continuous_scale="YlOrRd",
    )
    _apply_dark_theme(fig, height=480)
    fig.update_layout(
        xaxis=dict(tickmode="linear", dtick=1, title_font_size=14),
        yaxis=dict(dtick=1, title_font_size=14),
    )
    return fig


def make_simulation_chart(sim: SimulationResult) -> go.Figure:
    x = np.arange(len(sim.history_b))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=sim.history_b,
            mode="lines+markers",
            name="Заряд батареи",
            line=dict(width=3, color="#38bdf8"),
            marker=dict(size=6, color="#38bdf8"),
        )
    )
    fig.add_trace(
        go.Bar(
            x=x,
            y=sim.history_a,
            name="Действие (покупка/продажа)",
            marker_color="#94a3b8",
            opacity=0.55,
            width=0.8,
        )
    )
    _apply_dark_theme(fig, height=520)
    fig.update_layout(
        xaxis_title="Час от старта",
        yaxis_title="кВт·ч / действие",
        legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center", font_size=13),
        xaxis=dict(title_font_size=14),
        yaxis=dict(title_font_size=14),
    )
    return fig


def make_balance_chart(sim: SimulationResult) -> go.Figure:
    x = np.arange(len(sim.history_money))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=sim.history_money,
            mode="lines",
            name="Баланс",
            line=dict(width=3.5, color="#10b981"),
            fill="tozeroy",
            fillcolor="rgba(16,185,129,0.12)",
        )
    )
    _apply_dark_theme(fig, height=520)
    fig.update_layout(
        xaxis_title="Час от старта",
        yaxis_title="Накоплено, у.е.",
        showlegend=False,
        xaxis=dict(title_font_size=14),
        yaxis=dict(title_font_size=14),
    )
    return fig
