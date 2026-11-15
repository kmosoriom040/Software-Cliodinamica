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

## Estructura

```
src/cliodinamica/
  core/          modelos ODE (Strategy), registro (Factory) y solver (Adapter sobre SciPy)
  services/      SimulationService (Facade)
  repositories/  exportación a CSV y SQLite (Repository)
tests/           pruebas con pytest
```

## Hoja de ruta

1. Núcleo numérico y pruebas (hecho)
2. Servicios (SimulationService) y exportación a CSV y SQLite (hecho)
3. Generación de datos, etiquetado y clasificador MLP
4. Interfaz Streamlit con gráficos Plotly
5. Docker, GitHub Actions y PyPI
