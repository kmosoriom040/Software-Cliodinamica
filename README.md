# Cliodinámica

**Cliodinámica** es una aplicación de simulación y análisis exploratorio de sistemas dinámicos. Permite estudiar, mediante un modelo matemático, la interacción entre población, recursos, desigualdad y estabilidad estatal.

El proyecto combina una biblioteca Python para resolver y analizar ecuaciones diferenciales con una interfaz gráfica construida con Streamlit. La interfaz permite explorar escenarios sin tener que escribir código.

> **Alcance del modelo:** Cliodinámica es una herramienta computacional exploratoria. Sus resultados dependen de las ecuaciones, los parámetros y las condiciones iniciales seleccionadas. No es un predictor histórico validado ni permite inferir directamente el comportamiento de sociedades reales.

---

## 1. ¿Qué permite hacer?

- Simular la evolución temporal de cuatro variables: población (\`N\`), recursos (\`R\`), desigualdad (\`G\`) y estabilidad estatal (\`S\`).
- Cambiar escenarios, parámetros y condiciones iniciales desde una interfaz gráfica.
- Visualizar series temporales y trayectorias en planos de fase 2D y 3D.
- Examinar equilibrios y estabilidad local mediante autovalores del Jacobiano.
- Estimar sensibilidad de los resultados frente a cambios en los parámetros.
- Explorar barridos de parámetros y mapas de regímenes.
- Ejecutar ensambles Monte Carlo para observar la dispersión de resultados.
- Exportar simulaciones a CSV y almacenarlas en SQLite.
- Utilizar un clasificador MLP entrenado con datos sintéticos generados por el modelo.

## 2. Documentación

| Documento | Para qué sirve |
|---|---|
| [Manual de usuario](docs/manual_usuario.md) | Instalación, recorrido por la interfaz, explicación de las pestañas, ejemplos de uso y solución de problemas. |
| [Documentación técnica](docs/documentacion_tecnica.md) | Arquitectura del proyecto, formulación matemática, solver, análisis numérico, aprendizaje automático y limitaciones. |

## 3. Instalar y ejecutar la aplicación

La forma más sencilla de probar Cliodinámica es instalarla desde PyPI. Se requiere Python 3.10 o posterior.

### Linux

\`\`\`bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install "cliodinamica[ml,app]"
cliodinamica-app
\`\`\`

### Windows (PowerShell)

\`\`\`powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install "cliodinamica[ml,app]"
cliodinamica-app
\`\`\`

Cuando Streamlit inicie, abrir la dirección que aparece en la terminal. Normalmente es:

\`\`\`text
http://localhost:8501
\`\`\`

La instalación incluye los extras \`app\` (interfaz) y \`ml\` (funciones de aprendizaje automático).

## 4. Ejecutar con Docker

Como alternativa, se puede ejecutar la interfaz en un contenedor. Se necesita Docker Engine y Docker Compose.

Desde la raíz del repositorio:

\`\`\`bash
docker compose up --build
\`\`\`

Abrir [http://localhost:8501](http://localhost:8501). Para detener la aplicación:

\`\`\`bash
docker compose down
\`\`\`

Compose monta el directorio local \`data/\` dentro del contenedor en \`/app/data\`, para conservar los datos y modelos almacenados allí.

## 5. Usar Cliodinámica como biblioteca Python

También es posible utilizar el núcleo sin abrir la interfaz gráfica.

Instalar la biblioteca:

\`\`\`bash
pip install cliodinamica
\`\`\`

Ejemplo mínimo de simulación:

\`\`\`python
from cliodinamica.core import create_model, simulate

model = create_model("cliodinamica")
trajectory = simulate(model, t_end=300)

print(trajectory.state_names)
print(trajectory.y.shape)
\`\`\`

La función \`create_model\` obtiene una instancia del modelo registrado y \`simulate\` calcula su trayectoria durante el intervalo solicitado.

Para consultar las opciones de análisis, persistencia y sus argumentos, revisar la [documentación técnica](docs/documentacion_tecnica.md) y los módulos del paquete.

## 6. Entrenar el clasificador MLP

El clasificador es opcional. La interfaz puede ejecutarse con **Ninguno** en el selector del panel lateral. Para utilizar las opciones MLP se necesitan los archivos del modelo entrenado.

El script de entrenamiento se ejecuta desde un clon del repositorio:

\`\`\`bash
pip install -e ".[ml]"
python scripts/train_classifier.py --n 3000 --seed 0 --out data
\`\`\`

Los archivos generados se guardan en \`data/\`. En la interfaz, indicar esa carpeta en **Carpeta del modelo** y seleccionar el tipo de rasgos deseado.

**Importante:** el clasificador se entrena con simulaciones y etiquetas sintéticas producidas por el propio modelo. Sus resultados no equivalen a predicciones validadas sobre datos históricos reales.

## 7. Estructura del proyecto

\`\`\`text
src/cliodinamica/
├── core/          Modelos diferenciales, registro y solver numérico
├── services/      Servicios que coordinan las simulaciones
├── repositories/  Persistencia y exportación CSV / SQLite
├── analysis/      Estabilidad, sensibilidad, barridos y ensambles
├── ml/            Datos sintéticos, rasgos y clasificación
└── ui/            Interfaz Streamlit y gráficos Plotly

scripts/           Herramientas ejecutables desde el repositorio
tests/             Pruebas automatizadas
docs/              Manual de usuario y documentación técnica
\`\`\`

## 8. Desarrollo y pruebas

Para trabajar sobre el código fuente:

\`\`\`bash
git clone https://github.com/kmosoriom040/Software-Cliodinamica.git
cd Software-Cliodinamica

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,ml,app]"
\`\`\`

Ejecutar las pruebas:

\`\`\`bash
pytest
\`\`\`

Ejecutar la interfaz directamente desde el repositorio:

\`\`\`bash
streamlit run src/cliodinamica/ui/app.py
\`\`\`

La integración continua del repositorio ejecuta comprobaciones de estilo y pruebas automatizadas en Python 3.10 y 3.12.

## 9. Limitaciones conocidas

- El modelo representa un sistema conceptual de cuatro variables; no es una descripción completa de una sociedad.
- Los parámetros no deben interpretarse como estimaciones empíricas calibradas.
- Los resultados de estabilidad son locales al equilibrio analizado.
- Los mapas de regímenes y las clases son resultados de las reglas implementadas.
- Los ensambles Monte Carlo describen la variabilidad bajo las perturbaciones configuradas, no probabilidades históricas.
- El MLP reproduce etiquetas construidas a partir de datos sintéticos del modelo.
- La calibración con datos históricos y la validación predictiva externa no forman parte de esta versión.

## 10. Repositorio y distribución

- **Código fuente:** [GitHub — Software-Cliodinamica](https://github.com/kmosoriom040/Software-Cliodinamica)
- **Paquete:** [PyPI — cliodinamica](https://pypi.org/project/cliodinamica/)
- **Interfaz:** Streamlit
- **Licencia:** MIT
