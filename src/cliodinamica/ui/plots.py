"""Figuras de Plotly: series de tiempo y gráficos de fase 2D y 3D."""

from __future__ import annotations

from typing import Any

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from cliodinamica.core import Trajectory

CLASS_COLORS = {
    "crecimiento": "#2ca02c",
    "estancamiento": "#1f77b4",
    "colapso": "#d62728",
}
STATE_LABELS = {
    "N": "Población N",
    "R": "Recursos R",
    "G": "Desigualdad G",
    "S": "Estabilidad S",
}


def _label(name: str) -> str:
    return STATE_LABELS.get(name, name)


def timeseries_fig(tray: Trajectory, color: str = "#1f77b4") -> go.Figure:
    names = tray.state_names
    rows, cols = (2, 2) if len(names) > 2 else (1, len(names))
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[_label(n) for n in names])
    for i, name in enumerate(names):
        fig.add_trace(
            go.Scatter(x=tray.t, y=tray.series(name), mode="lines", line={"color": color},
                       name=name, showlegend=False),
            row=i // cols + 1,
            col=i % cols + 1,
        )
    fig.update_xaxes(title_text="Años")
    fig.update_layout(height=520, margin={"t": 50, "b": 40})
    return fig


def _field_and_nullclines(
    fig: go.Figure, model: Any, params: Any, xmax: float, ymax: float, grid: int = 18
) -> None:
    """Campo de direcciones, nulclinas y equilibrio del plano (N, R).

    dN/dt y dR/dt no dependen de G ni de S, así que este plano es exacto.
    """
    xs = np.linspace(xmax * 0.03, xmax, grid)
    ys = np.linspace(ymax * 0.03, ymax, grid)
    seg_x: list[float | None] = []
    seg_y: list[float | None] = []
    head_x: list[float] = []
    head_y: list[float] = []
    for n in xs:
        for r in ys:
            dn, dr = model.rhs(0.0, np.array([n, r, 0.0, 1.0]), params)[:2]
            vx, vy = dn / xmax, dr / ymax
            norm = float(np.hypot(vx, vy))
            if norm < 1e-12:
                continue
            ux, uy = vx / norm * 0.035 * xmax, vy / norm * 0.035 * ymax
            seg_x += [n, n + ux, None]
            seg_y += [r, r + uy, None]
            head_x.append(n + ux)
            head_y.append(r + uy)
    fig.add_trace(go.Scatter(x=seg_x, y=seg_y, mode="lines", line={"color": "#bbbbbb", "width": 1},
                             hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=head_x, y=head_y, mode="markers",
                             marker={"size": 3, "color": "#888"},
                             hoverinfo="skip", showlegend=False))

    r_line = np.linspace(0.0, ymax, 100)
    fig.add_trace(go.Scatter(x=params.kappa * r_line, y=r_line, mode="lines",
                             line={"dash": "dot", "color": "#9467bd"}, name="dN/dt = 0"))
    r_pos = np.linspace(0.0, min(ymax, params.R0), 100)
    fig.add_trace(go.Scatter(x=params.rho * (1 - r_pos / params.R0) / params.gamma, y=r_pos,
                             mode="lines", line={"dash": "dot", "color": "#ff7f0e"},
                             name="dR/dt = 0"))
    eq = model.equilibrium(params)
    fig.add_trace(go.Scatter(x=[eq[0]], y=[eq[1]], mode="markers", name="Equilibrio",
                             marker={"symbol": "x", "size": 11, "color": "black"}))


def phase2d_fig(
    tray: Trajectory,
    x: str = "N",
    y: str = "R",
    color: str = "#1f77b4",
    model: Any = None,
    params: Any = None,
) -> go.Figure:
    fig = go.Figure()
    xs, ys = tray.series(x), tray.series(y)
    if (x, y) == ("N", "R") and model is not None and params is not None:
        xmax = max(float(xs.max()), float(model.equilibrium(params)[0])) * 1.1
        ymax = max(float(ys.max()), float(model.equilibrium(params)[1])) * 1.1
        _field_and_nullclines(fig, model, params, xmax, ymax)
        fig.update_xaxes(range=[0, xmax])
        fig.update_yaxes(range=[0, ymax])
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line={"color": color, "width": 3},
                             name="Trayectoria"))
    fig.add_trace(go.Scatter(x=[xs[0]], y=[ys[0]], mode="markers", name="Inicio",
                             marker={"color": "black", "size": 9}))
    fig.add_trace(go.Scatter(x=[xs[-1]], y=[ys[-1]], mode="markers", name="Final",
                             marker={"color": color, "size": 12, "symbol": "diamond"}))
    fig.update_layout(xaxis_title=_label(x), yaxis_title=_label(y), height=560,
                      margin={"t": 30})
    return fig


def phase3d_fig(
    tray: Trajectory, x: str = "N", y: str = "R", z: str = "S", color: str = "#1f77b4"
) -> go.Figure:
    xs, ys, zs = tray.series(x), tray.series(y), tray.series(z)
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line={"color": color, "width": 5},
                               name="Trayectoria"))
    fig.add_trace(go.Scatter3d(x=[xs[0]], y=[ys[0]], z=[zs[0]], mode="markers", name="Inicio",
                               marker={"color": "black", "size": 5}))
    fig.add_trace(go.Scatter3d(x=[xs[-1]], y=[ys[-1]], z=[zs[-1]], mode="markers", name="Final",
                               marker={"color": color, "size": 7, "symbol": "diamond"}))
    fig.update_layout(
        height=600,
        margin={"t": 10, "l": 0, "r": 0, "b": 0},
        scene={"xaxis_title": _label(x), "yaxis_title": _label(y), "zaxis_title": _label(z)},
    )
    return fig
