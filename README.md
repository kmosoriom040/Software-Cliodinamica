# cliodinamica

Simulador dinámico de sistemas complejos y cliodinámica. Resuelve ODEs acopladas con SciPy
(población, recursos, desigualdad y estabilidad estatal) y, en etapas posteriores, clasifica
el estado del sistema (crecimiento, estancamiento, colapso) con un MLP.

## Inicio rápido

```bash
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Uso

```python
from cliodinamica.core import create_model, simulate

modelo = create_model("cliodinamica")
tray = simulate(modelo, t_end=300)
print(tray.state_names, tray.y.shape)
```

Con el servicio y exportación:

```python
from cliodinamica.repositories import CsvRepository
from cliodinamica.services import SimulationService

svc = SimulationService(CsvRepository("data/runs"))
resultado = svc.run(params={"lam": 0.5}, save=True)
```

## Interfaz

```bash
pip install -e ".[dev,ml,app]"
streamlit run src/cliodinamica/ui/app.py   # o: cliodinamica-app
```

## Análisis científico

```python
from cliodinamica.analysis import analyze_equilibrium, elasticities, regime_map, run_ensemble
from cliodinamica.core import create_model

m = create_model("cliodinamica")
p = m.default_params()
print(analyze_equilibrium(m, p).kind)   # tipo de equilibrio según los autovalores
print(elasticities(m, p)["lam"])        # sensibilidad del estado final a λ
ens = run_ensemble(m, p, n_runs=200)    # incertidumbre en los parámetros
print(ens.class_probabilities())
```

## Entrenar el clasificador

```bash
pip install -e ".[dev,ml]"
python scripts/train_classifier.py --n 3000 --out data
```

## Estructura

```
src/cliodinamica/
  core/          modelos ODE (Strategy), registro (Factory) y solver (Adapter sobre SciPy)
  services/      SimulationService (Facade)
  repositories/  exportación a CSV y SQLite (Repository)
  analysis/      estabilidad, sensibilidad, barridos de parámetros y ensamble Monte Carlo
  ui/            interfaz Streamlit (app.py) y gráficos Plotly (plots.py)
  ml/            rasgos, etiquetado, dataset (Latin Hypercube) y clasificador MLP
scripts/         train_classifier.py (genera el dataset y entrena el MLP)
tests/           pruebas con pytest
```

## Hoja de ruta

1. Núcleo numérico y pruebas (hecho)
2. Servicios (SimulationService) y exportación a CSV y SQLite (hecho)
3. Generación de datos, etiquetado y clasificador MLP (hecho)
4. Interfaz Streamlit con gráficos Plotly (hecho)
5. Docker, GitHub Actions y PyPI
