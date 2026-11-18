# Manual de usuario — Cliodinámica

## 1. ¿Qué es Cliodinámica?

Cliodinámica es una herramienta computacional para explorar un sistema dinámico de cuatro variables: población (N), recursos (R), desigualdad (G) y estabilidad estatal (S). Permite modificar parámetros y condiciones iniciales, integrar las ecuaciones diferenciales y estudiar las trayectorias mediante visualizaciones y análisis numéricos.

Es un modelo conceptual. No es un sistema calibrado ni validado para predecir la evolución de países o sociedades reales.

## 2. Instalación

### Opción A. Instalar desde PyPI

Se recomienda crear un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install "cliodinamica[ml,app]"
```

Iniciar la interfaz:

```bash
cliodinamica-app
```

Si el comando no está disponible, desde un clon del repositorio puede ejecutarse:

```bash
streamlit run src/cliodinamica/ui/app.py
```

### Opción B. Docker

Con Docker Engine y Docker Compose instalados, desde la raíz del repositorio:

```bash
docker compose up --build
```

Abrir `http://localhost:8501`. Para detener:

```bash
docker compose down
```

## 3. Recorrido de la interfaz

La interfaz organiza los resultados en siete pestañas. Los controles del panel lateral permiten definir el escenario de simulación; las pestañas muestran distintos análisis de ese escenario.

### 3.1 Configurar una simulación

1. Seleccionar un escenario predefinido, si se desea partir de una configuración inicial.
2. Revisar y ajustar los parámetros del modelo.
3. Definir las condiciones iniciales de N, R, G y S.
4. Elegir la duración temporal.
5. Ejecutar o actualizar la simulación según los controles de la aplicación.

Conviene modificar uno o pocos parámetros a la vez para entender qué cambios producen en los resultados. Los valores iniciales y parámetros son supuestos del experimento numérico, no observaciones históricas.

### 3.2 Series temporales

Muestra la evolución de las cuatro variables en función del tiempo. Sirve para identificar tendencias, transitorios, estabilización, oscilaciones o cambios de régimen en la trayectoria simulada.

Preguntas útiles: ¿qué variable aumenta o disminuye?, ¿la trayectoria parece acercarse a un estado estacionario?, ¿cuánto tarda en cambiar?

### 3.3 Plano de fase 2D

Representa la dinámica en el plano población-recursos (N-R). Incluye trayectorias, campo direccional, nulclinas y una referencia al equilibrio calculado.

- Una trayectoria muestra cómo cambia el par (N,R) a lo largo del tiempo.
- El campo direccional representa la dirección local del cambio.
- Una nulclina de N corresponde a los puntos donde dN/dt = 0.
- Una nulclina de R corresponde a los puntos donde dR/dt = 0.
- La intersección de nulclinas puede señalar un equilibrio para esas dos ecuaciones; no debe confundirse automáticamente con el equilibrio completo de cuatro dimensiones.

### 3.4 Fase 3D

Permite observar una trayectoria en una representación tridimensional de variables del sistema. Es una vista complementaria: una proyección 3D no contiene toda la información de un estado de cuatro dimensiones.

### 3.5 Estabilidad

Calcula y presenta información local alrededor del equilibrio: ubicación del equilibrio, matriz Jacobiana, autovalores y clasificación basada en estos últimos. También se presentan elasticidades/sensibilidades disponibles.

La clasificación local describe el comportamiento cerca del equilibrio bajo la formulación matemática y los parámetros usados. No garantiza que toda trayectoria, desde cualquier condición inicial, tenga ese comportamiento.

### 3.6 Regímenes

Explora cómo cambia el resultado cuando se barre uno o dos parámetros. En el barrido 1D se estudia un parámetro; en el mapa 2D se evalúa una malla de combinaciones.

Las etiquetas como crecimiento, estancamiento o colapso son categorías operacionales asignadas por reglas del programa a las trayectorias simuladas. No son diagnósticos históricos ni categorías universales.

### 3.7 Incertidumbre

Ejecuta múltiples simulaciones variando parámetros para construir un ensamble. Presenta bandas o resúmenes estadísticos y probabilidades de las clases resultantes.

La dispersión representa la incertidumbre introducida en el experimento numérico. Su interpretación depende de los rangos y distribuciones asignados a los parámetros; no equivale automáticamente a incertidumbre estadística estimada a partir de datos reales.

### 3.8 Exportar

La aplicación ofrece mecanismos de exportación y persistencia, incluidos CSV y SQLite. CSV permite inspeccionar resultados tabulares con otras herramientas; SQLite permite almacenar resultados en una base de datos local.

La ubicación y el nombre de los archivos dependen de la configuración de ejecución. En Docker, el directorio local `data/` se monta en `/app/data` para conservar los archivos fuera del contenedor.

## 4. Clasificador de aprendizaje automático

El proyecto incluye herramientas para generar datos sintéticos y entrenar/evaluar clasificadores, entre ellos un MLP. El conjunto se construye a partir de simulaciones del modelo y etiquetas asignadas mediante reglas.

Desde un clon del repositorio:

```bash
pip install -e ".[ml]"
python scripts/train_classifier.py --n 3000 --seed 0 --out data
```

El script guarda el dataset y modelos entrenados en el directorio indicado. También calcula métricas de evaluación y comparaciones con otros clasificadores.

**Interpretación correcta:** el clasificador aprende a reproducir las etiquetas del conjunto sintético. Una buena métrica no demuestra que prediga correctamente el comportamiento de sociedades reales. El script de entrenamiento está en el repositorio; no se debe asumir que el archivo `scripts/train_classifier.py` queda incluido al instalar únicamente el wheel de PyPI.

## 5. Consejos de uso

- Cambiar una variable o parámetro por vez para interpretar los efectos.
- Registrar los parámetros y condiciones iniciales al comparar escenarios.
- Verificar si una conclusión se mantiene al cambiar las condiciones iniciales.
- Usar el análisis de estabilidad como diagnóstico local, no como garantía global.
- Interpretar Monte Carlo según los rangos/distribuciones seleccionados.
- Distinguir siempre resultados sintéticos de datos empíricos.

## 6. Solución de problemas

- **La interfaz no inicia:** verificar que el entorno virtual esté activo y que se instaló el extra `app`; probar `streamlit run src/cliodinamica/ui/app.py` desde el repositorio.
- **Falla la instalación de extras:** actualizar pip con `python -m pip install --upgrade pip` y repetir la instalación.
- **Docker no conecta:** comprobar que Docker Engine esté iniciado y que el usuario tenga permisos para usar el daemon.
- **No aparecen archivos exportados:** revisar el directorio de datos y los permisos de escritura; con Compose comprobar el montaje de `data/`.

## 7. Alcance

Cliodinámica es una plataforma de simulación y análisis exploratorio. Para usarla como modelo empírico harían falta, entre otras cosas, operacionalización de variables, datos históricos, estimación de parámetros, análisis de identificabilidad y validación independiente. Esos elementos no forman parte de la versión documentada aquí.
