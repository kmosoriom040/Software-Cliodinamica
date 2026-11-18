# Manual de usuario — Cliodinámica

## 1. Introducción

Cliodinámica es una aplicación de simulación y análisis exploratorio de un sistema dinámico que representa la interacción entre cuatro variables:

| Símbolo | Variable | Interpretación dentro del modelo |
|---|---|---|
| \(N\) | Población | Nivel o tamaño relativo de la población. |
| \(R\) | Recursos | Disponibilidad relativa de recursos. |
| \(G\) | Desigualdad | Nivel de desigualdad representado por el modelo. |
| \(S\) | Estabilidad estatal | Indicador de estabilidad del Estado. |

La aplicación permite configurar parámetros y condiciones iniciales, ejecutar simulaciones y explorar los resultados mediante gráficos y herramientas de análisis.

**Alcance:** se trata de un modelo matemático conceptual y exploratorio. Sus resultados dependen de las ecuaciones, parámetros, condiciones iniciales y reglas implementadas. No constituye una predicción validada de la evolución de países o sociedades reales ni reemplaza un análisis basado en datos históricos.

## 2. Requisitos e instalación

La biblioteca requiere Python 3.10 o posterior. Para utilizar la interfaz gráfica también se necesita instalar el extra \`app\`; para las funcionalidades de aprendizaje automático se necesita el extra \`ml\`.

### 2.1 Instalación desde PyPI (recomendada)

Se recomienda crear un entorno virtual para aislar las dependencias del proyecto.

**Linux / macOS:**

\`\`\`bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install "cliodinamica[ml,app]"
\`\`\`

**Windows PowerShell:**

\`\`\`powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install "cliodinamica[ml,app]"
\`\`\`

Iniciar la aplicación:

\`\`\`bash
cliodinamica-app
\`\`\`

Streamlit mostrará en la terminal la dirección local de la aplicación. Normalmente se abre en el navegador automáticamente.

### 2.2 Ejecución desde el repositorio

Clonar el repositorio y entrar en su carpeta:

\`\`\`bash
git clone https://github.com/kmosoriom040/Software-Cliodinamica.git
cd Software-Cliodinamica
\`\`\`

Crear y activar un entorno virtual, e instalar las dependencias:

\`\`\`bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[ml,app]"
\`\`\`

En Windows PowerShell, la activación es \`.venv\\Scripts\\Activate.ps1\`.

Ejecutar la interfaz:

\`\`\`bash
streamlit run src/cliodinamica/ui/app.py
\`\`\`

### 2.3 Ejecución con Docker

Con Docker Engine y Docker Compose instalados, desde la raíz del repositorio ejecutar:

\`\`\`bash
docker compose up --build
\`\`\`

Abrir [http://localhost:8501](http://localhost:8501) en el navegador. Para detener los servicios:

\`\`\`bash
docker compose down
\`\`\`

El directorio local \`data/\` se monta dentro del contenedor en \`/app/data\`, de modo que los archivos guardados allí persisten fuera del ciclo de vida del contenedor.

## 3. Primer recorrido por la aplicación

La interfaz se divide en dos zonas:

- **Panel lateral:** contiene los escenarios predefinidos, parámetros, condiciones iniciales, duración de la simulación y selector del clasificador MLP.
- **Área principal:** contiene indicadores de resultado y siete pestañas de visualización y análisis.

La simulación principal se actualiza cuando Streamlit vuelve a ejecutar la aplicación al cambiar controles. No hay un botón general de «Ejecutar simulación». En cambio, las operaciones más costosas de las pestañas Regímenes e Incertidumbre sí tienen botones propios para iniciar sus cálculos.

### 3.1 Escenarios predefinidos

El selector **Escenario** permite partir de configuraciones preparadas:

- **Por defecto:** restablece los parámetros y condiciones iniciales predeterminados.
- **Colapso por desigualdad:** configura valores que intensifican la generación de desigualdad y su efecto sobre la estabilidad.
- **Colapso por sobreexplotación:** configura una combinación de crecimiento poblacional, extracción y regeneración de recursos.
- **Crecimiento sostenido:** establece una combinación orientada a explorar una trayectoria de crecimiento.
- **Equilibrio estable:** establece otra combinación de parámetros y población inicial para explorar el equilibrio del modelo.

Al seleccionar un escenario, la aplicación restablece primero los controles a sus valores predeterminados y después aplica los cambios del escenario elegido. Los nombres describen el propósito de las configuraciones de ejemplo; no garantizan que todos los resultados posibles sean iguales ni representan escenarios históricos observados.

### 3.2 Parámetros del modelo

Los controles están agrupados en el panel lateral.

| Grupo | Parámetro | Significado |
|---|---|---|
| Demografía | \(r\) | Tasa de crecimiento poblacional. |
| Demografía | \(\kappa\) | Escala de población sostenible por unidad de recurso; interviene en la presión demográfica. |
| Recursos | \(\rho\) | Tasa de regeneración de recursos. |
| Recursos | \(\gamma\) | Intensidad de extracción o interacción entre población y recursos. |
| Desigualdad y Estado | \(\alpha\) | Intensidad de generación de desigualdad asociada a la presión demográfica. |
| Desigualdad y Estado | \(\delta\) | Tasa de reducción o amortiguación de la desigualdad. |
| Desigualdad y Estado | \(\sigma\) | Tendencia de recuperación de la estabilidad estatal. |
| Desigualdad y Estado | \(\lambda\) | Intensidad del efecto de erosión de estabilidad asociado a desigualdad y presión demográfica. |

El parámetro \(R_0\), que representa la capacidad de carga o escala de referencia de los recursos, forma parte del modelo, pero no aparece como un control independiente en el panel lateral actual. La interfaz muestra un aviso de que el clasificador MLP se entrenó con \(R_0=1\) y con los rangos de los controles.

**Recomendación:** para estudiar el efecto de un parámetro, cambiar inicialmente un solo control y observar qué sucede. Si se cambian varios a la vez, será más difícil atribuir el cambio de la trayectoria a un parámetro específico.

### 3.3 Condiciones iniciales

El apartado **Estado inicial** permite establecer los valores desde los cuales comienza la simulación:

- \(N(0)\): población inicial.
- \(R(0)\): recursos iniciales.
- \(G(0)\): desigualdad inicial.
- \(S(0)\): estabilidad estatal inicial.

Las condiciones iniciales no son parámetros: representan el estado del sistema en el instante inicial. Dos simulaciones con los mismos parámetros pueden producir trayectorias diferentes si parten de estados iniciales distintos.

### 3.4 Duración

El control **Años de simulación** define el horizonte temporal de la simulación principal. La interfaz permite seleccionar entre 50 y 2000 años, en incrementos de 50.

Al modificarlo, se actualiza la trayectoria principal y las pestañas que dependen de ella. Los cálculos de barridos, mapas y ensambles se ejecutan por separado mediante sus botones.

### 3.5 Indicadores superiores

En la parte superior del área principal se presentan:

- **Clase (reglas):** clasificación de la trayectoria mediante reglas definidas en el programa.
- **Clase (MLP):** clasificación del modelo neuronal, cuando se selecciona y se encuentra el archivo del clasificador.
- **Estado final:** valores finales de población \(N\) y estabilidad \(S\).

Las clases utilizadas son crecimiento, estancamiento y colapso. Son etiquetas operacionales aplicadas a la trayectoria simulada, no diagnósticos de sociedades reales.

## 4. Pestañas de visualización y análisis

### 4.1 Series de tiempo

Es la vista inicial de la aplicación. Presenta cuatro gráficos, uno por variable:

- Población \(N\).
- Recursos \(R\).
- Desigualdad \(G\).
- Estabilidad estatal \(S\).

En los cuatro gráficos:

- El eje horizontal representa el tiempo en años.
- El eje vertical representa el valor de la variable correspondiente.
- La curva representa la trayectoria calculada a partir de las condiciones iniciales y los parámetros seleccionados.

**Cómo interpretar esta vista:** observar si cada variable aumenta, disminuye, presenta un máximo o mínimo, o parece acercarse a un valor aproximadamente constante. Comparar las cuatro curvas permite estudiar cómo evolucionan conjuntamente las variables del modelo.

Las gráficas son interactivas. Las herramientas de Plotly permiten acercar o alejar una región, desplazar la vista, restablecer los ejes y descargar una imagen del gráfico. Estas acciones cambian la visualización, no los parámetros ni los resultados numéricos de la simulación.

### 4.2 Plano de fase 2D

Esta pestaña representa una variable en función de otra, en lugar de representar ambas contra el tiempo.

Los selectores **Eje X** y **Eje Y** permiten elegir las variables. Por ejemplo, al seleccionar \(N\) en X y \(R\) en Y, cada punto de la curva representa el estado conjunto de población y recursos en un instante.

En el plano \(N\)-\(R\), la aplicación añade elementos específicos:

- **Trayectoria:** recorrido del sistema en el plano.
- **Inicio:** posición inicial de la simulación.
- **Final:** posición al terminar el intervalo simulado.
- **Campo direccional:** flechas que indican la dirección local en la que evolucionan población y recursos.
- **Nulclina \(dN/dt=0\):** conjunto de puntos donde la tasa de cambio de población es cero.
- **Nulclina \(dR/dt=0\):** conjunto de puntos donde la tasa de cambio de recursos es cero.
- **Equilibrio:** referencia del equilibrio calculado para el modelo.

La intersección de las dos nulclinas identifica un punto donde las derivadas de \(N\) y \(R\) se anulan. Como esta vista es una proyección sobre dos variables, no debe confundirse automáticamente con un análisis completo del equilibrio de las cuatro variables.

Al elegir otros pares de variables, la aplicación muestra la trayectoria en ese plano, pero el campo direccional y las nulclinas especiales se añaden únicamente para el plano \(N\)-\(R\).

### 4.3 Fase 3D

Permite seleccionar tres variables mediante los controles **Eje X**, **Eje Y** y **Eje Z**. La gráfica muestra la trayectoria tridimensional, su punto inicial y su punto final.

Esta vista ayuda a observar relaciones que pueden ser difíciles de apreciar en gráficos separados. Se puede rotar y acercar la visualización con el ratón.

El modelo tiene cuatro variables, por lo que cualquier representación 3D omite una de ellas. Es una proyección útil para explorar la dinámica, no una representación completa del estado de cuatro dimensiones.

### 4.4 Estabilidad

Esta pestaña reúne dos análisis relacionados, pero diferentes: el análisis local del equilibrio y la sensibilidad del estado final.

**A. Equilibrio y autovalores**

Un equilibrio es un estado en el que las tasas de cambio de las variables son cero. La aplicación calcula el equilibrio interior del modelo para los parámetros actuales y presenta:

- Los valores de las cuatro variables en el equilibrio.
- El tipo de equilibrio.
- Las partes real e imaginaria de sus autovalores.

Para determinar la estabilidad local se construye el Jacobiano, una matriz que describe cómo cambian las tasas de las variables ante pequeñas variaciones del estado. Sus autovalores permiten estudiar si pequeñas perturbaciones alrededor del equilibrio tienden a disminuir o crecer.

Interpretación general:

- **Estable (nodo):** las partes reales de todos los autovalores son negativas y no hay componentes imaginarias significativas.
- **Estable (foco):** las partes reales son negativas y existen componentes imaginarias significativas; la aproximación lineal presenta modos oscilatorios amortiguados.
- **Inestable:** al menos un autovalor tiene parte real positiva.
- **Marginal (centro o no hiperbólico):** el criterio implementado no encuentra todos los autovalores con parte real negativa ni alguno con parte real claramente positiva. Este caso requiere cautela y análisis adicional.

La clasificación se refiere al comportamiento local alrededor del equilibrio calculado. No significa que cualquier condición inicial termine necesariamente en ese punto.

**Nota sobre la interfaz:** el cálculo utiliza el Jacobiano, pero la vista actual presenta los valores del equilibrio, el tipo y las partes real e imaginaria de los autovalores; no muestra la matriz Jacobiana completa como una tabla.

**B. Sensibilidad del estado final**

Debajo del análisis de equilibrio aparece un mapa de calor de elasticidades.

- Las filas representan parámetros del modelo.
- Las columnas representan las variables finales \(N\), \(R\), \(G\) y \(S\).
- Cada celda indica la sensibilidad relativa de una variable final frente a un parámetro.

Una elasticidad positiva indica que un aumento pequeño del parámetro se asocia con un aumento de la variable final; una negativa indica una relación inversa local; un valor cercano a cero indica poca sensibilidad local en esa configuración.

Por ejemplo, una elasticidad de \(0.5\) significa que un aumento de 1 % en el parámetro se asocia aproximadamente con un aumento de 0.5 % en la variable final, cerca de la configuración evaluada.

El cálculo se estima mediante diferencias centrales. En la implementación actual usa por defecto un horizonte de 500 años y un paso relativo de 2 %; por tanto, este análisis no necesariamente utiliza el mismo horizonte que el control principal de años de simulación.

### 4.5 Regímenes

Esta pestaña permite explorar cómo cambia la clasificación de las trayectorias al modificar parámetros.

**A. Mapa de regímenes 2D**

El mapa evalúa combinaciones de dos parámetros:

1. Elegir un parámetro en **Parámetro X**.
2. Elegir otro parámetro diferente en **Parámetro Y**.
3. Seleccionar la **Resolución** de la cuadrícula.
4. Presionar **Calcular mapa**.
5. Esperar a que terminen las simulaciones y observar el mapa.

La resolución determina cuántos valores se prueban en cada eje. Por ejemplo, una resolución de 20 genera una cuadrícula de \(20\times20\), es decir, hasta 400 combinaciones de parámetros.

Cada punto de la cuadrícula representa una simulación con esa combinación de parámetros. El color representa la clase asignada por las reglas del programa: crecimiento, estancamiento o colapso. La estrella blanca marca la combinación correspondiente a los valores actuales de los parámetros seleccionados.

Debajo del mapa se presenta la fracción de la cuadrícula perteneciente a cada clase. Esas fracciones describen los puntos calculados de la malla, no probabilidades empíricas de que ocurra un fenómeno social.

Si se cambian los controles después de calcular el mapa, la aplicación avisa que el resultado corresponde a una configuración anterior. En ese caso, presionar de nuevo **Calcular mapa** para actualizarlo.

**B. Barrido de un parámetro**

El barrido 1D estudia el efecto de variar un único parámetro:

1. Elegir el parámetro en **Parámetro**.
2. Elegir la variable que se quiere observar en **Estado**.
3. Seleccionar la cantidad de valores en **Valores**.
4. Presionar **Calcular barrido**.

El programa ejecuta una simulación para cada valor del parámetro. El gráfico presenta el valor final de la variable seleccionada y una banda que representa sus valores mínimo y máximo en la parte final de cada trayectoria. El color de los puntos indica la clase asignada a cada simulación.

Este gráfico ayuda a identificar cambios de comportamiento al variar un parámetro. Es un análisis exploratorio de barrido; no demuestra por sí solo una bifurcación matemática formal.

### 4.6 Incertidumbre

Esta pestaña ejecuta un ensamble Monte Carlo. En lugar de producir una sola trayectoria, realiza muchas simulaciones perturbando aleatoriamente los parámetros del modelo.

Controles disponibles:

- **Incertidumbre relativa:** magnitud de la dispersión aplicada a los parámetros. El control permite valores entre 0.01 y 0.50.
- **Número de corridas:** cantidad de simulaciones del ensamble, entre 20 y 400.
- **Estado:** variable cuya evolución se mostrará en el gráfico de abanico.

Para ejecutar el análisis:

1. Configurar la incertidumbre relativa.
2. Elegir el número de corridas.
3. Seleccionar la variable que se desea visualizar.
4. Presionar **Ejecutar ensamble**.
5. Esperar a que terminen las simulaciones.

La implementación perturba todos los parámetros mediante un factor aleatorio lognormal. Las condiciones iniciales se mantienen iguales a las de la configuración principal.

La pestaña presenta dos resultados:

**A. Gráfico de abanico (Fan Chart)**

Muestra la mediana de las trayectorias y dos bandas de percentiles:

- Banda 5–95 %: contiene el intervalo entre los percentiles 5 y 95 de las simulaciones.
- Banda 25–75 %: contiene el intervalo entre los percentiles 25 y 75.

Una banda más amplia indica mayor dispersión de los resultados simulados en ese instante. No es un intervalo de confianza estimado a partir de observaciones históricas.

**B. Probabilidades de clasificación**

Muestra la proporción de simulaciones del ensamble clasificadas como crecimiento, estancamiento o colapso. Por ejemplo, si 30 de 100 simulaciones se clasifican como colapso, la proporción mostrada para esa clase será 30 %.

Estas proporciones dependen de la magnitud de perturbación, el modelo, las condiciones iniciales, el horizonte y las reglas de clasificación. No deben interpretarse como probabilidades reales de colapso de una sociedad.

Si se cambian los parámetros o controles después de ejecutar el ensamble, la aplicación avisa que los resultados guardados corresponden a una configuración anterior. Presionar **Ejecutar ensamble** para recalcular.

### 4.7 Exportar

La pestaña permite descargar o almacenar los resultados de la simulación principal.

**A. Descargar CSV**

Presionar **Descargar CSV** para descargar la serie temporal. El archivo contiene una columna de tiempo (\`t\`) y una columna por variable del modelo (\`N\`, \`R\`, \`G\`, \`S\`). Puede abrirse con una hoja de cálculo, Python, R u otra herramienta compatible con CSV.

**B. Guardar en SQLite**

1. En **Base de datos SQLite local**, indicar la ruta y el nombre del archivo de base de datos. Por defecto es \`data/cliodinamica.sqlite\`.
2. Presionar **Guardar en SQLite**.
3. La aplicación mostrará un mensaje de confirmación y la ruta utilizada.
4. Si la base de datos contiene simulaciones, se presenta una tabla con identificador, fecha de creación, modelo y horizonte temporal.

SQLite almacena los metadatos de la ejecución y los valores de las series temporales. Es una base de datos local en un archivo; no requiere instalar un servidor de base de datos independiente.

En Docker, utilizar una ruta dentro de \`/app/data\` para aprovechar el volumen persistente configurado en Compose.

## 5. Clasificador MLP

El panel lateral incluye el apartado **Clasificador MLP**. El selector ofrece tres opciones:

- **Ninguno:** no utiliza un clasificador neuronal.
- **Rasgos de trayectoria:** clasifica utilizando características calculadas a partir de la trayectoria simulada.
- **Entradas (sin simular):** clasifica utilizando los parámetros y las condiciones iniciales, sin necesitar una trayectoria como entrada del clasificador.

Cuando se selecciona una de las dos opciones del MLP, la aplicación busca en la carpeta indicada el archivo correspondiente:

- \`clasificador_trayectoria.joblib\`
- \`clasificador_entradas.joblib\`

Si el archivo no existe, se muestra un aviso indicando que debe entrenarse el clasificador desde el repositorio.

### 5.1 Entrenamiento desde el repositorio

El script de entrenamiento se encuentra en \`scripts/train_classifier.py\`. No debe suponerse que ese script está incluido en la instalación del paquete desde PyPI.

Desde la raíz del repositorio, con el entorno virtual activo:

\`\`\`bash
pip install -e ".[ml]"
python scripts/train_classifier.py --n 3000 --seed 0 --out data
\`\`\`

El script genera un conjunto de datos sintético y guarda los clasificadores en el directorio indicado. Después, en el panel lateral de la aplicación, establecer **Carpeta del modelo** en \`data\` para que pueda localizar los archivos.

### 5.2 Cómo interpretar el resultado

El MLP devuelve una clase y probabilidades asociadas a las clases disponibles. La aplicación muestra la clasificación del MLP por separado de la clasificación por reglas.

El clasificador se entrenó con datos sintéticos generados por el propio modelo y etiquetas asignadas mediante reglas. Por eso, sus resultados indican qué tan bien reproduce esas categorías en el contexto de entrenamiento; no demuestran capacidad para predecir acontecimientos históricos reales.

La aplicación también informa que el clasificador fue entrenado con \(R_0=1\) y con los rangos de los controles. Si se cambia el dominio de aplicación o se modifican esos supuestos, el clasificador puede no ser adecuado sin un nuevo proceso de generación de datos y entrenamiento.

## 6. Flujo de trabajo recomendado

Para realizar una exploración ordenada:

1. Seleccionar **Por defecto** o un escenario predefinido.
2. Revisar los parámetros y las condiciones iniciales.
3. Observar las cuatro series temporales.
4. Explorar el plano de fase 2D y la vista 3D.
5. Consultar el equilibrio y la sensibilidad en **Estabilidad**.
6. Ejecutar un barrido 1D o un mapa 2D en **Regímenes**.
7. Ejecutar un ensamble Monte Carlo en **Incertidumbre**.
8. Descargar el CSV o guardar la simulación principal en SQLite.
9. Registrar los parámetros y condiciones iniciales si se desea comparar el experimento posteriormente.

Para comprender el efecto de un parámetro, conviene modificar uno por vez. Para comparar escenarios, mantener constantes las condiciones que no se desean estudiar.

## 7. Solución de problemas

| Problema | Qué revisar |
|---|---|
| El comando \`cliodinamica-app\` no se reconoce | Verificar que el entorno virtual esté activo y que se instaló el extra \`app\`. Como alternativa, ejecutar Streamlit desde el repositorio. |
| La aplicación no inicia | Revisar la salida de la terminal, la versión de Python y la instalación de dependencias. |
| Docker no conecta con el daemon | Verificar que Docker Engine esté iniciado y que el usuario tenga permisos para utilizarlo. |
| El navegador no abre la aplicación | Comprobar que Streamlit inició correctamente y abrir manualmente \`http://localhost:8501\`. |
| El MLP aparece como no disponible | Comprobar que se entrenaron los archivos \`.joblib\` y que **Carpeta del modelo** apunta al directorio que los contiene. |
| El mapa o el ensamble tarda | Reducir la resolución del mapa o el número de corridas. Cada punto o corrida requiere una simulación adicional. |
| No se encuentra el archivo SQLite | Comprobar la ruta configurada y los permisos de escritura. En Docker, utilizar el directorio persistente \`/app/data\`. |
| Los resultados del mapa o ensamble parecen antiguos | Revisar el aviso de configuración modificada y volver a presionar el botón de cálculo correspondiente. |

## 8. Glosario breve

- **Condición inicial:** valor de una variable al comienzo de la simulación.
- **Parámetro:** constante que determina propiedades de las ecuaciones del modelo.
- **Trayectoria:** evolución de las variables a lo largo del tiempo.
- **Plano de fase:** representación de una variable en función de otra.
- **Equilibrio:** estado en el que las tasas de cambio del sistema son cero.
- **Jacobiano:** matriz de derivadas parciales que describe la dinámica local alrededor de un estado.
- **Autovalores:** valores que permiten estudiar la estabilidad local de un equilibrio.
- **Elasticidad:** medida de cuánto cambia relativamente una salida ante un cambio relativo de un parámetro.
- **Barrido de parámetros:** conjunto de simulaciones realizadas con distintos valores de uno o más parámetros.
- **Monte Carlo:** procedimiento que utiliza múltiples simulaciones con variaciones aleatorias para estudiar la dispersión de los resultados.
- **MLP:** perceptrón multicapa, un tipo de red neuronal artificial.

## 9. Alcance y limitaciones

Cliodinámica está diseñada para simulación y análisis exploratorio de un modelo matemático. Las salidas dependen de las ecuaciones implementadas, los parámetros elegidos, las condiciones iniciales, el horizonte temporal y las reglas de clasificación.

Para utilizar el modelo como herramienta empírica sobre sociedades reales se necesitarían, entre otros elementos, definir indicadores observables, recopilar datos apropiados, estimar y calibrar parámetros, estudiar la identificabilidad y realizar validación independiente. Estos procesos no forman parte de la versión actual.

El modelo y el clasificador deben presentarse como herramientas de exploración computacional, no como sistemas que predicen de manera validada el futuro de una sociedad.
