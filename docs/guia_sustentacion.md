# Guía de sustentación — Cliodinámica

## 1. Presentación breve del proyecto

Cliodinámica es un software de simulación y análisis de sistemas dinámicos de inspiración cliodinámica. Implementa un modelo de cuatro variables acopladas —población, recursos, desigualdad y estabilidad estatal— mediante ecuaciones diferenciales ordinarias. Sobre las trayectorias calculadas ofrece visualizaciones, análisis de estabilidad, sensibilidad, barridos de parámetros, ensambles Monte Carlo y herramientas de clasificación con aprendizaje automático.

El objetivo del software es explorar las consecuencias de una formulación matemática bajo diferentes parámetros y condiciones iniciales. No pretende, en su versión actual, predecir empíricamente la historia de una sociedad.

## 2. Guion sugerido (8–10 minutos)

1. **Problema y motivación (1 min):** explicar por qué resulta útil representar interacciones entre variables sociales mediante un sistema dinámico.
2. **Objetivo (30 s):** presentar la herramienta como entorno reproducible de simulación y análisis.
3. **Modelo (2 min):** introducir las cuatro variables, explicar la presión (psi=N/(kappa R)) y describir cualitativamente cada ecuación.
4. **Arquitectura (1 min):** mostrar separación entre núcleo numérico, análisis, persistencia, ML e interfaz.
5. **Demostración (2–3 min):** configurar un escenario, observar series temporales, plano de fase y al menos una herramienta de análisis.
6. **Capacidades complementarias (1 min):** explicar barridos, Monte Carlo y clasificador sintético.
7. **Limitaciones y trabajo futuro (1 min):** enfatizar la falta de calibración/validación histórica y proponer datos reales como extensión.

## 3. Orden recomendado para la demostración

- Abrir la interfaz y ubicar el panel de parámetros y condiciones iniciales.
- Mostrar las series temporales para identificar la evolución de N, R, G y S.
- Ir al plano de fase N-R y explicar trayectoria, campo vectorial y nulclinas.
- Mostrar estabilidad: equilibrio, Jacobiana y autovalores. Aclarar que es análisis local.
- Mostrar un barrido o mapa de regímenes para ilustrar el efecto de cambiar parámetros.
- Si hay tiempo, mostrar incertidumbre como ensamble de simulaciones.
- Terminar con exportación y reproducibilidad.

No intentes mostrar todas las pestañas si el tiempo es corto. Es preferible explicar con claridad tres resultados que recorrer la interfaz sin interpretarlos.

## 4. Conceptos que debes dominar

### ¿Por qué ecuaciones diferenciales?

Porque las variables se representan como funciones del tiempo y sus derivadas expresan tasas de cambio. El sistema permite estudiar cómo las interacciones entre variables generan trayectorias.

### ¿Qué representa (psi)?

(psi=N/(kappa R)) es una medida interna de presión poblacional relativa a los recursos disponibles, escalada por (kappa). En el modelo afecta la dinámica de población, desigualdad y estabilidad estatal.

### ¿Qué hace el solver?

Resuelve numéricamente el sistema de ODEs para aproximar los valores de las variables en el tiempo. No obtiene una solución analítica general ni valida que las ecuaciones representen fielmente una sociedad.

### ¿Qué es un equilibrio?

Un estado en el que las cuatro derivadas son cero. Si el sistema llega a él, las variables dejan de cambiar en el modelo. La estabilidad indica qué ocurre ante perturbaciones pequeñas alrededor de ese punto.

### ¿Qué es la Jacobiana?

La matriz de derivadas parciales de las funciones dinámicas respecto a las variables de estado. Describe la dinámica linealizada cerca del equilibrio; sus autovalores informan sobre estabilidad local.

### ¿Qué mide la sensibilidad?

Cuánto cambia una salida cuando se modifica un parámetro. La implementación usa diferencias finitas centrales para aproximar elasticidades. No es causalidad.

### ¿Para qué sirve Monte Carlo?

Para estudiar la variabilidad de los resultados cuando se ejecutan muchas simulaciones con parámetros distintos. Las conclusiones dependen de los rangos y distribuciones asignados.

### ¿Qué hace el MLP?

Aprende patrones en características derivadas de simulaciones sintéticas y trata de reproducir etiquetas asignadas por reglas. No está entrenado con una base de datos de sociedades históricas reales.

## 5. Preguntas probables y respuestas

**¿El software predice el colapso de una civilización?**

No. Simula un modelo conceptual y permite explorar escenarios. No se ha calibrado ni validado con series históricas reales, así que no se presenta como predictor empírico.

**¿De dónde salen los parámetros?**

Son parámetros de la formulación y configuración del experimento. En esta versión no deben presentarse como estimaciones estadísticas de parámetros sociales reales.

**¿Cómo se resuelve el sistema?**

Con integración numérica de ODEs usando SciPy `solve_ivp`; LSODA es el método predeterminado configurado.

**¿Qué diferencia hay entre simulación y análisis de estabilidad?**

La simulación calcula una trayectoria desde condiciones iniciales. El análisis de estabilidad estudia el comportamiento local alrededor de un equilibrio mediante la Jacobiana y sus autovalores.

**¿Qué significa una nulclina?**

Es el conjunto de puntos donde la derivada de una variable es cero. En el plano N-R, cada nulclina indica dónde se anula la tasa de cambio de una de esas dos variables.

**¿Por qué incluir sensibilidad?**

Porque permite identificar qué parámetros tienen mayor influencia local sobre las salidas y priorizar qué supuestos conviene examinar.

**¿Qué aporta Monte Carlo si el modelo es determinista?**

Cada simulación individual es determinista para sus parámetros y condiciones iniciales. El ensamble introduce variación entre ejecuciones para explorar cómo la incertidumbre de parámetros afecta los resultados.

**¿El clasificador aprende de datos reales?**

No en el flujo actual. Se entrena con datos sintéticos generados por el modelo y etiquetas definidas mediante reglas. Por tanto, sus métricas no prueban capacidad predictiva sobre datos históricos.

**¿Por qué usar aprendizaje automático si ya hay reglas?**

Como herramienta exploratoria para estudiar si un clasificador puede aproximar las etiquetas del procedimiento de simulación a partir de rasgos o entradas. No reemplaza las reglas ni añade evidencia empírica externa.

**¿Qué limitaciones tiene?**

La principal es la ausencia de calibración y validación con datos históricos reales. También dependen de supuestos la elección de parámetros, condiciones iniciales, reglas de etiquetado y distribuciones del ensamble.

**¿Qué trabajo futuro sería razonable?**

Definir indicadores observables, recopilar series históricas comparables, establecer un método de estimación de parámetros, analizar identificabilidad y validar en periodos o casos no usados para calibración.

## 6. Qué no afirmar durante la sustentación

- No decir que el sistema predice el comportamiento de países o civilizaciones.
- No presentar parámetros como valores empíricamente estimados si no existe calibración.
- No confundir las etiquetas sintéticas con clases históricas observadas.
- No afirmar que la UI permite seleccionar Lotka–Volterra: el modelo existe en el núcleo, pero la interfaz actual usa Cliodinámica.
- No interpretar estabilidad local como garantía global.
- No afirmar que una buena métrica del MLP valida el modelo social.

## 7. Preparación rápida antes de exponer

1. Ejecutar una simulación desde cero y verificar que la interfaz abre.
2. Elegir un escenario que produzca gráficas legibles.
3. Anotar los parámetros y condiciones iniciales que se mostrarán.
4. Practicar la explicación de cada ecuación en una frase.
5. Practicar la diferencia entre equilibrio, estabilidad, sensibilidad y Monte Carlo.
6. Tener capturas o una explicación alternativa por si falla la conexión o la interfaz.
7. Priorizar las limitaciones con honestidad: reconocerlas demuestra criterio científico y técnico.

## 8. Cierre sugerido

“Cliodinámica integra un modelo de ecuaciones diferenciales con herramientas de análisis numérico y una interfaz para explorar escenarios de forma reproducible. Su aporte actual es ofrecer un entorno computacional modular para estudiar las consecuencias de los supuestos del modelo. La siguiente etapa científica sería contrastar y calibrar la formulación con datos históricos independientes antes de plantear cualquier uso predictivo.”
