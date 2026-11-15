"""Interfaz Streamlit del simulador de cliodinámica.

Ejecutar con:  streamlit run src/cliodinamica/ui/app.py   (o)   cliodinamica-app
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd
import streamlit as st

from cliodinamica.core import create_model
from cliodinamica.ml import FEATURE_COLUMNS, extract_features, label_trajectory
from cliodinamica.ml.dataset import INPUT_COLUMNS, PARAM_BOUNDS, STATE_BOUNDS
from cliodinamica.repositories import CsvRepository, SqliteRepository
from cliodinamica.services import SimulationService
from cliodinamica.ui import plots

MODEL = create_model("cliodinamica")
BASE = MODEL.default_params()
Y0_BASE = dict(zip(MODEL.state_names, map(float, MODEL.default_y0()), strict=True))

GROUPS = {
    "Demografía": [("r", "Crecimiento poblacional r"), ("kappa", "Población por recurso κ")],
    "Recursos": [("rho", "Regeneración ρ"), ("gamma", "Extracción por habitante γ")],
    "Desigualdad y Estado": [
        ("alpha", "Generación de desigualdad α"),
        ("delta", "Redistribución δ"),
        ("sigma", "Recuperación del Estado σ"),
        ("lam", "Erosión por desigualdad λ"),
    ],
}
STATE_LABELS = {"N": "Población N(0)", "R": "Recursos R(0)", "G": "Desigualdad G(0)",
                "S": "Estabilidad S(0)"}

PRESETS: dict[str, tuple[dict[str, float], dict[str, float]]] = {
    "Por defecto": ({}, {}),
    "Colapso por desigualdad": (
        {"lam": 0.9, "alpha": 0.15, "delta": 0.015, "sigma": 0.05}, {}),
    "Colapso por sobreexplotación": (
        {"r": 0.08, "gamma": 0.04, "rho": 0.02, "kappa": 2.5}, {}),
    "Crecimiento sostenido": (
        {"r": 0.05, "kappa": 2.5, "rho": 0.08, "gamma": 0.005, "lam": 0.1}, {"N": 0.2}),
    "Equilibrio estable": (
        {"r": 0.02, "kappa": 1.0, "rho": 0.06, "gamma": 0.01, "lam": 0.1}, {"N": 0.9}),
}

DEFAULTS: dict[str, float | int | str] = {
    **{f"p_{k}": float(getattr(BASE, k)) for k in PARAM_BOUNDS},
    **{f"y_{s}": v for s, v in Y0_BASE.items()},
    "t_end": 300,
}


def apply_preset() -> None:
    overrides, y_over = PRESETS[st.session_state["preset"]]
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    for k, v in overrides.items():
        st.session_state[f"p_{k}"] = float(v)
    for s, v in y_over.items():
        st.session_state[f"y_{s}"] = float(v)


@st.cache_resource
def load_classifier(path: str):
    from cliodinamica.ml.classifier import StateClassifier

    return StateClassifier.load(path)


def predict_proba(clf, kind: str, params, y0: dict[str, float], tray) -> dict[str, float]:
    if kind == "trayectoria":
        row = pd.DataFrame([extract_features(tray)])[list(FEATURE_COLUMNS)]
    else:
        values = {**asdict(params), **{f"y0_{s}": v for s, v in y0.items()}}
        row = pd.DataFrame([values])[list(INPUT_COLUMNS)]
    return {str(c): float(p) for c, p in zip(clf.classes_, clf.predict_proba(row)[0], strict=True)}


st.set_page_config(page_title="Simulador de cliodinámica", layout="wide")
for key, default in DEFAULTS.items():
    st.session_state.setdefault(key, default)

st.title("Simulador de cliodinámica y sistemas complejos")
st.caption("ODEs acopladas (población, recursos, desigualdad y estabilidad estatal) "
           "resueltas con SciPy y clasificadas por reglas y por un MLP.")

with st.sidebar:
    st.header("Panel de control")
    st.selectbox("Escenario", list(PRESETS), key="preset", on_change=apply_preset)
    for group, items in GROUPS.items():
        with st.expander(group, expanded=True):
            for key, label in items:
                lo, hi = PARAM_BOUNDS[key]
                st.slider(label, lo, hi, key=f"p_{key}", step=(hi - lo) / 200, format="%.3f")
    with st.expander("Estado inicial"):
        for s in MODEL.state_names:
            lo, hi = STATE_BOUNDS[f"y0_{s}"]
            st.slider(STATE_LABELS[s], lo, hi, key=f"y_{s}", step=(hi - lo) / 100,
                      format="%.2f")
    with st.expander("Simulación"):
        st.slider("Años de simulación", 50, 2000, key="t_end", step=50)
    with st.expander("Clasificador MLP"):
        kind_label = st.selectbox("Tipo", ["Ninguno", "Rasgos de trayectoria",
                                           "Entradas (sin simular)"])
        model_dir = st.text_input("Carpeta del modelo", "data")

params_over = {k: st.session_state[f"p_{k}"] for k in PARAM_BOUNDS}
y0 = {s: st.session_state[f"y_{s}"] for s in MODEL.state_names}
t_end = int(st.session_state["t_end"])

service = SimulationService()
result = service.run(
    "cliodinamica", params=params_over, y0=[y0[s] for s in MODEL.state_names],
    t_end=t_end, n_points=t_end + 1,
)
tray = result.trajectory
params = BASE.__class__(**result.params)
rule_label = label_trajectory(tray)

mlp_probs: dict[str, float] | None = None
if kind_label != "Ninguno":
    kind = "trayectoria" if kind_label.startswith("Rasgos") else "entradas"
    path = Path(model_dir) / f"clasificador_{kind}.joblib"
    if path.exists():
        mlp_probs = predict_proba(load_classifier(str(path)), kind, params, y0, tray)
    else:
        st.sidebar.info(f"No encontré {path}. Entrena con scripts/train_classifier.py.")
mlp_label = max(mlp_probs, key=mlp_probs.get) if mlp_probs else None
color = plots.CLASS_COLORS[mlp_label or rule_label]

c1, c2, c3 = st.columns(3)
c1.metric("Clase (reglas)", rule_label)
c2.metric("Clase (MLP)", mlp_label or "no disponible")
c3.metric("Estado final", f"N={tray.series('N')[-1]:.2f}  S={tray.series('S')[-1]:.2f}")
if mlp_probs:
    st.caption("Probabilidades del MLP: "
               + ", ".join(f"{c} {p:.0%}" for c, p in sorted(mlp_probs.items())))
st.caption("El MLP se entrenó con R₀ = 1 y con los rangos de los controles.")

tab_ts, tab_2d, tab_3d, tab_exp = st.tabs(
    ["Series de tiempo", "Plano de fase 2D", "Fase 3D", "Exportar"])

with tab_ts:
    st.plotly_chart(plots.timeseries_fig(tray, color), width="stretch")

with tab_2d:
    a, b = st.columns(2)
    x2 = a.selectbox("Eje X", MODEL.state_names, index=0, key="x2")
    y2 = b.selectbox("Eje Y", MODEL.state_names, index=1, key="y2")
    st.plotly_chart(plots.phase2d_fig(tray, x2, y2, color, MODEL, params), width="stretch")
    if (x2, y2) == ("N", "R"):
        st.caption("El plano (N, R) incluye campo de direcciones y nulclinas: dN/dt y dR/dt "
                   "no dependen de G ni de S.")

with tab_3d:
    a, b, c = st.columns(3)
    x3 = a.selectbox("Eje X", MODEL.state_names, index=0, key="x3")
    y3 = b.selectbox("Eje Y", MODEL.state_names, index=1, key="y3")
    z3 = c.selectbox("Eje Z", MODEL.state_names, index=3, key="z3")
    st.plotly_chart(plots.phase3d_fig(tray, x3, y3, z3, color), width="stretch")

with tab_exp:
    st.write(f"Simulación `{result.run_id}`  ({result.created_at})")
    st.download_button("Descargar CSV", CsvRepository.render(result),
                       file_name=f"{result.run_id}.csv", mime="text/csv")
    db_path = st.text_input("Base de datos SQLite local", "data/cliodinamica.sqlite")
    if st.button("Guardar en SQLite"):
        SimulationService(SqliteRepository(db_path)).save(result)
        st.success(f"Guardada en {db_path}")
    if Path(db_path).exists():
        runs = SqliteRepository(db_path).list_runs()
        if runs:
            st.dataframe(pd.DataFrame(
                [{"run_id": r["run_id"], "creada": r["created_at"], "modelo": r["model"],
                  "t_end": r["t_end"]} for r in runs]), hide_index=True)
