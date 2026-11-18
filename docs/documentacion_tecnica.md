# Documentación técnica — Cliodinámica

## 1. Arquitectura

El paquete está organizado por responsabilidades:

- \`core/\`: modelos de ecuaciones diferenciales ordinarias (ODE), registro/fábrica de modelos y solver.
- \`services/\`: coordinación de simulaciones y casos de uso.
- \`repositories/\`: persistencia y exportación (CSV y SQLite).
- \`analysis/\`: análisis de equilibrio, estabilidad, sensibilidad, barridos y ensambles.
- \`ml/\`: generación de datasets sintéticos, extracción de rasgos, etiquetado y clasificadores.
- \`ui/\`: aplicación Streamlit y visualizaciones Plotly.
- \`scripts/\`: utilidades ejecutables desde el repositorio, incluido el entrenamiento del clasificador.
- \`tests/\`: pruebas automatizadas.

El núcleo registra modelos y permite consultarlos mediante una interfaz de fábrica: \`available_models()\` lista los modelos registrados y \`create_model(name)\` crea una instancia. La interfaz gráfica actual está enfocada en el modelo Cliodinámica; la existencia de otros modelos en el núcleo no implica que puedan seleccionarse desde la UI.

## 2. Modelo dinámico Cliodinámica

El estado se representa mediante:

$$
\mathbf{x}(t) = \begin{pmatrix}N(t)\\R(t)\\G(t)\\S(t)\end{pmatrix}.
$$

Donde:

- $N$: población.
- $R$: recursos.
- $G$: desigualdad.
- $S$: estabilidad estatal.

La formulación implementada es:

$$
\frac{dN}{dt}=rN(1-\psi),
$$

$$
\frac{dR}{dt}=\rho R\left(1-\frac{R}{R_0}\right)-\gamma NR,
$$

$$
\frac{dG}{dt}=\alpha\psi(1-G)-\delta G,
$$

$$
\frac{dS}{dt}=\sigma(1-S)-\lambda G\psi S,
$$

con:

$$
\psi=\frac{N}{\kappa R}.
$$

En la evaluación numérica se protege el denominador de recursos mediante un valor mínimo ($\epsilon$), evitando dividir directamente por cero.

Los parámetros controlan tasas de crecimiento, capacidad de recursos, interacción población-recursos, dinámica de desigualdad y estabilidad. Sus nombres y valores por defecto se encuentran en la definición del modelo en el código fuente. No deben interpretarse como estimaciones empíricas salvo que se realice un proceso explícito de calibración, que no está incluido en esta versión.

### 2.1 Interpretación cualitativa

- La población crece cuando el factor $(1-\psi)$ es positivo y disminuye cuando es negativo.
- Los recursos tienen un término logístico y un término de consumo/interacción con la población.
- La desigualdad combina un término impulsado por $\psi$ y otro de relajación.
- La estabilidad estatal tiene una tendencia de relajación hacia 1 y un término de disminución acoplado a desigualdad y presión poblacional.

Esta lectura describe los términos matemáticos; no demuestra causalidad social en sistemas reales.

## 3. Integración numérica

El solver utiliza la infraestructura de integración de SciPy (\`solve_ivp\`), con LSODA como método predeterminado en la configuración documentada. El integrador produce una trayectoria temporal que contiene los tiempos, los valores de las variables y sus nombres.

La calidad de una simulación depende de la formulación, condiciones iniciales, parámetros, intervalo temporal, tolerancias y comportamiento numérico del integrador. Una integración exitosa no valida por sí misma el modelo conceptual.

## 4. Equilibrio y estabilidad local

Un equilibrio $\mathbf{x}^*$ satisface:

$$
\mathbf{f}(\mathbf{x}^*;\mathbf{p})=\mathbf{0}.
$$

La matriz Jacobiana es:

$$
J(\mathbf{x}^*) =
\left[
\frac{\partial f_i}{\partial x_j}
\right]_{\mathbf{x}=\mathbf{x}^*}.
$$

Los autovalores de $J$ permiten caracterizar la dinámica linealizada cerca del equilibrio. En términos generales, partes reales negativas indican modos que decaen localmente; una parte real positiva indica al menos una dirección localmente inestable. Los casos con partes reales nulas requieren análisis adicional y no deben clasificarse concluyentemente solo con la linealización.

La pestaña de estabilidad expone los resultados numéricos disponibles: equilibrio, Jacobiana, autovalores y tipo de equilibrio. La interpretación siempre es local y condicionada por el equilibrio encontrado y los parámetros.

## 5. Sensibilidad

El análisis de elasticidades estima cómo responde el estado final ante perturbaciones relativas de parámetros, mediante diferencias finitas centrales. La implementación utiliza un paso relativo por defecto de 0.02 y omite parámetros cuyo valor base es cero, porque una perturbación relativa respecto de cero no está definida.

Una elasticidad aproximada compara el cambio porcentual de una salida con el cambio porcentual de un parámetro. Se define como:

$$
E_{p,x}=\frac{\partial x}{\partial p}\frac{p}{x}.
$$

Es una medida local alrededor de la configuración analizada; no es una prueba causal ni una garantía de comportamiento fuera de ese entorno.

## 6. Barridos y regímenes

El barrido unidimensional recorre valores de un parámetro, ejecuta una simulación para cada valor y resume el estado final y el comportamiento en una ventana final de la trayectoria (por defecto, el último 20%). El mapa de regímenes repite el procedimiento sobre una malla de dos parámetros.

Las clases crecimiento/estancamiento/colapso son etiquetas operacionales determinadas por reglas de clasificación de trayectorias. Los mapas permiten comparar escenarios del modelo, no identificar automáticamente regímenes de una sociedad real.

## 7. Ensambles Monte Carlo

El módulo de ensambles genera múltiples simulaciones a partir de variaciones de parámetros. Los resultados permiten construir distribuciones, bandas de percentiles y probabilidades de las clases definidas por el sistema.

La interpretación requiere documentar:

1. parámetros que se variaron;
2. distribuciones y rangos usados;
3. número de realizaciones;
4. condiciones iniciales y horizonte temporal;
5. tratamiento de integraciones fallidas.

La probabilidad de una clase es condicional al diseño del ensamble y al clasificador de trayectorias empleado.

## 8. Aprendizaje automático

El flujo de ML incluye generación de datos sintéticos mediante muestreo Latin Hypercube, simulación de trayectorias, extracción de rasgos y asignación de etiquetas por reglas. Se implementa un MLP y funciones de evaluación/comparación con Random Forest y regresión logística. La evaluación incluye validación cruzada estratificada y matriz de confusión; también se dispone de importancia por permutación.

El script \`scripts/train_classifier.py\` permite controlar cantidad de muestras, semilla y directorio de salida. Por defecto usa 3000 muestras y semilla 0. Produce un dataset y artefactos de modelos para dos conjuntos de características: basadas en trayectoria y basadas en entradas.

**Limitación metodológica fundamental:** las etiquetas de entrenamiento provienen de reglas aplicadas a resultados sintéticos del propio modelo. Las métricas miden qué tan bien el clasificador reproduce esas etiquetas bajo el esquema de evaluación; no constituyen validación externa ni evidencia de predicción histórica.

## 9. Persistencia y distribución

Los repositorios CSV y SQLite desacoplan el almacenamiento del servicio de simulación. La interfaz permite exportar resultados. La imagen Docker expone Streamlit en el puerto 8501; Compose monta el directorio local \`data/\` en \`/app/data\`.

La distribución Python se publica en PyPI. La instalación de la interfaz y de las capacidades de ML se realiza mediante extras:

\`\`\`bash
pip install "cliodinamica[ml,app]"
\`\`\`

## 10. Modelo de referencia Lotka–Volterra

El núcleo incluye también una implementación Lotka–Volterra como modelo de referencia. Está registrada en la biblioteca, pero la interfaz Streamlit actual está construida alrededor del modelo Cliodinámica y no ofrece un selector para alternar entre ambos. No se debe presentar la UI como un simulador gráfico multimodelo.

## 11. Pruebas y límites

El repositorio incluye pruebas automatizadas con pytest y configuración de integración continua para Python 3.10 y 3.12. Las pruebas verifican aspectos de implementación y comportamiento esperado; no sustituyen la validación científica con datos independientes.

Fuera del alcance de esta versión están la calibración con series históricas reales, la validación predictiva externa y la interpretación causal de parámetros. Cualquier extensión empírica requiere definir indicadores observables, fuentes de datos, estimación de parámetros, incertidumbre de medición y protocolos de validación.
