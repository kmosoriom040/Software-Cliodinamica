# cliodinamica

Simulador dinámico de sistemas complejos y cliodinámica. Resuelve ODEs acopladas con SciPy para estudiar la interacción entre población, recursos, desigualdad y estabilidad estatal. Incluye análisis de estabilidad, sensibilidad, barridos de parámetros, ensambles Monte Carlo, una interfaz Streamlit y herramientas de clasificación mediante MLP.

## Documentación

- [Manual de usuario](docs/manual_usuario.md)
- [Documentación técnica](docs/documentacion_tecnica.md)
- [Guía de sustentación](docs/guia_sustentacion.md)

## Inicio rápido

```bash
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Uso como biblioteca

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

## Interfaz local

```bash
pip install -e ".[dev,ml,app]"
streamlit run src/cliodinamica/ui/app.py   # o: cliodinamica-app
```

## Ejecutar con Docker

Requisitos: Docker Engine y el complemento Docker Compose.

Construir la imagen e iniciar la aplicación:

```bash
docker compose up --build
```

Abrir la aplicación en el navegador:

```text
http://localhost:8501
```

Detener el contenedor:

```bash
docker compose down
```

La configuración de Compose monta el directorio local `data/` en `/app/data` para conservar datasets y modelos entrenados fuera del contenedor. Si no existen, pueden crearse al ejecutar los comandos correspondientes.

También se puede construir y ejecutar la imagen directamente:

```bash
docker build -t cliodinamica:local .
docker run --rm -p 8501:8501 -v "$(pwd)/data:/app/data" cliodinamica:local
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

El clasificador se entrena con datos sintéticos generados por el propio modelo. Sus métricas evalúan la reproducción de las etiquetas definidas para esos datos; no constituyen por sí solas validación predictiva sobre sociedades o series históricas reales.

## Estructura

```text
src/cliodinamica/
  core/          modelos ODE, registro y solver numérico
  services/      SimulationService
  repositories/  exportación a CSV y SQLite
  analysis/      estabilidad, sensibilidad, barridos y ensambles Monte Carlo
  ui/            interfaz Streamlit y gráficos Plotly
  ml/             extracción de rasgos, dataset y clasificador MLP
scripts/          entrenamiento del clasificador
tests/            pruebas con pytest
```

## Alcance y limitaciones

El proyecto proporciona un entorno computacional para simular y analizar sistemas dinámicos de inspiración cliodinámica. Los resultados dependen de la formulación matemática, los parámetros y las condiciones iniciales seleccionadas. La aplicación no debe interpretarse como un predictor empírico validado de trayectorias históricas.

La calibración y validación con series históricas reales, así como la ampliación con indicadores nacionales, quedan fuera del alcance de esta versión.

## Desarrollo y CI

La integración continua ejecuta Ruff y pytest en Python 3.10 y 3.12 mediante GitHub Actions.

## Hoja de ruta

1. Núcleo numérico y pruebas.
2. Servicios y persistencia CSV/SQLite.
3. Generación de datos sintéticos y clasificador MLP.
4. Interfaz Streamlit y visualizaciones Plotly.
5. Contenedor Docker y preparación de distribución en PyPI.
