# Cliodinámica

**Cliodinámica** es una herramienta en Python para la simulación y el análisis exploratorio de un modelo conceptual de dinámica social. Permite estudiar las interacciones entre población, recursos, desigualdad y estabilidad estatal mediante un sistema de ecuaciones diferenciales ordinarias (EDO) acopladas.

El proyecto combina una biblioteca de computación científica reutilizable con una interfaz web interactiva construida con Streamlit. La interfaz permite configurar escenarios, ejecutar simulaciones y examinar resultados sin necesidad de escribir código.

[English](README.md) | [Español](README.es.md)

> **Alcance del modelo:** Cliodinámica es una herramienta computacional exploratoria. Sus resultados dependen de las ecuaciones, parámetros, condiciones iniciales y reglas de clasificación seleccionadas. No es un sistema de predicción histórica validado empíricamente.

## Características principales

- **Simulación dinámica:** resuelve un modelo EDO de cuatro variables: población (N), recursos (R), desigualdad (G) y estabilidad estatal (S).
- **Exploración interactiva:** permite configurar escenarios, parámetros, condiciones iniciales y horizonte temporal mediante una interfaz Streamlit.
- **Visualización científica:** presenta series temporales y trayectorias en planos de fase 2D y proyecciones 3D.
- **Análisis de estabilidad y sensibilidad:** examina un equilibrio interior, su clasificación local mediante autovalores y las elasticidades de los parámetros.
- **Exploración del espacio de parámetros:** ejecuta barridos de un parámetro y mapas de regímenes de dos parámetros.
- **Análisis de incertidumbre:** ejecuta ensambles Monte Carlo y visualiza bandas de percentiles y proporciones de clasificación.
- **Exportación de datos:** permite descargar series temporales en CSV o almacenar simulaciones en una base de datos SQLite local.
- **Aprendizaje automático:** permite entrenar y utilizar un clasificador MLP con datos sintéticos generados por el modelo.

## Tecnologías

| Área | Tecnologías |
|---|---|
| Lenguaje | Python 3.10+ |
| Computación numérica | NumPy, SciPy |
| Manipulación de datos | Pandas |
| Aprendizaje automático | scikit-learn, MLP |
| Interfaz interactiva | Streamlit |
| Visualización | Plotly |
| Persistencia | CSV, SQLite |
| Despliegue | Docker, Docker Compose |
| Pruebas y calidad | pytest, Ruff, GitHub Actions |
| Distribución | PyPI |

## Documentación

- **[Manual de usuario (Markdown)](docs/manual_usuario.md):** instalación, recorrido por la interfaz, flujos de análisis, exportación, uso del MLP y solución de problemas.
- **[Documentación técnica](docs/documentacion_tecnica.md):** formulación matemática, arquitectura, métodos numéricos, módulos de análisis y limitaciones metodológicas.
- **[Manual de usuario en PDF]:** guía ilustrada con capturas de pantalla; estará disponible en la carpeta de documentación cuando se suba al repositorio.

## Inicio rápido

Se requiere Python 3.10 o posterior.

### Instalar desde PyPI

La instalación recomendada incluye las dependencias de la interfaz y de aprendizaje automático.

**Linux / macOS**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install "cliodinamica[ml,app]"
cliodinamica-app
```

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install "cliodinamica[ml,app]"
cliodinamica-app
```

Cuando Streamlit inicie, abre la dirección local que aparece en la terminal (normalmente http://localhost:8501).

### Ejecutar con Docker

Se requiere Docker Engine y Docker Compose. Desde la raíz del repositorio:

```bash
docker compose up --build
```

Abre http://localhost:8501. Para detener la aplicación:

```bash
docker compose down
```

La configuración de Compose monta el directorio local "data/" en "/app/data" para conservar los datos y modelos generados fuera del contenedor.

## Uso como biblioteca Python

El núcleo numérico puede utilizarse independientemente de la interfaz gráfica.

```bash
pip install cliodinamica
```

```python
from cliodinamica.core import create_model, simulate

model = create_model("cliodinamica")
trajectory = simulate(model, t_end=300)

print(trajectory.state_names)
print(trajectory.y.shape)
```

La fábrica obtiene un modelo registrado y "simulate" calcula su trayectoria durante el intervalo solicitado.

## Clasificador de aprendizaje automático

El clasificador MLP opcional utiliza conjuntos de datos sintéticos generados al simular el modelo y asignar etiquetas mediante reglas predefinidas. Para entrenar los clasificadores, clona el repositorio y ejecuta el script desde su directorio raíz:

```bash
pip install -e ".[ml]"
python scripts/train_classifier.py --n 3000 --seed 0 --out data
```

Los archivos generados se guardan en "data/". En la aplicación, establece la carpeta del modelo en "data" y selecciona rasgos de trayectoria o rasgos basados únicamente en las entradas.

**Importante:** el clasificador aprende a reproducir las etiquetas asignadas a resultados sintéticos del modelo. Sus métricas no demuestran validez predictiva sobre datos históricos o sociedades reales.

## Estructura del repositorio

```text
src/cliodinamica/
├── core/          Modelos EDO, registro de modelos y solver numérico
├── services/      Coordinación de casos de uso y simulaciones
├── repositories/  Exportación CSV y persistencia SQLite
├── analysis/      Estabilidad, sensibilidad, barridos y ensambles Monte Carlo
├── ml/            Datos sintéticos, extracción de rasgos y clasificadores
└── ui/            Aplicación Streamlit y visualizaciones Plotly

scripts/           Utilidades del repositorio, incluido el entrenamiento del clasificador
tests/             Pruebas automatizadas
docs/              Manual de usuario y documentación técnica
```

## Entorno de desarrollo

Clona el repositorio e instala las dependencias de desarrollo, ML e interfaz:

```bash
git clone https://github.com/kmosoriom040/Software-Cliodinamica.git
cd Software-Cliodinamica

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,ml,app]"
```

Ejecutar las pruebas:

```bash
pytest
```

Ejecutar la interfaz desde el código fuente:

```bash
streamlit run src/cliodinamica/ui/app.py
```

El flujo de GitHub Actions ejecuta comprobaciones de calidad y pruebas automatizadas en Python 3.10 y 3.12.

## Resumen de arquitectura

El código separa el núcleo matemático de la interfaz y las funcionalidades complementarias:

- "core" define los modelos EDO, el registro/fábrica de modelos y la integración numérica.
- "services" coordina los casos de uso de simulación.
- "analysis" contiene análisis de equilibrio, estabilidad, sensibilidad, barridos y ensambles.
- "ml" gestiona la generación de datos sintéticos, extracción de características, etiquetas por reglas y clasificadores.
- "repositories" proporciona persistencia CSV y SQLite.
- "ui" contiene la aplicación Streamlit y las gráficas Plotly.

El núcleo también incluye un modelo de referencia Lotka–Volterra. La interfaz gráfica actual está enfocada en Cliodinámica y no ofrece un selector para alternar a Lotka–Volterra.

## Limitaciones

- El modelo es un sistema conceptual de cuatro variables, no una representación exhaustiva de una sociedad.
- Los parámetros son ilustrativos y no están calibrados con observaciones históricas en esta versión.
- El análisis de estabilidad describe el comportamiento local alrededor del equilibrio calculado.
- Las etiquetas de régimen son categorías operacionales asignadas por las reglas del proyecto.
- Las proporciones Monte Carlo dependen del esquema de perturbación de parámetros y no son probabilidades empíricas de eventos.
- El MLP se entrena con simulaciones sintéticas y etiquetas derivadas de reglas.
- La calibración histórica y la validación predictiva independiente están fuera del alcance de esta versión.

## Enlaces

- **Código fuente:** https://github.com/kmosoriom040/Software-Cliodinamica
- **Paquete PyPI:** https://pypi.org/project/cliodinamica/
- **Licencia:** MIT
