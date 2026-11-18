# Datos ambientales de Colombia: metodología de integración

## Objetivo

Construir una serie anual nacional del estado relativo del capital natural (R) y
compararla con la variable R simulada por el modelo Cliodinamica. Este documento
separa los datos observados, las decisiones de transformación y los resultados
del modelo.

## Fuentes oficiales iniciales

| Dimensión | Fuente / operación | Cobertura identificada inicialmente | Uso previsto |
|---|---|---:|---|
| Ecosistemas | DANE, Cuenta Ambiental y Económica de Extensión de los Ecosistemas (CAE-EE) | Resultados experimentales 2011-2018; antecedentes 2007 y 2011 | Extensión y condición de ecosistemas; revisar solapamiento con bosque |
| Bosques | DANE, Cuenta Ambiental y Económica de Bosque (CAE-B) | Serie 2012-2018 | Activos forestales; posible subíndice de bosque |
| Minerales y energía | DANE, Cuenta Ambiental y Económica de Activos de Recursos Minerales y Energéticos (CAE-ARME) | Publicaciones históricas desde 2014, con actualizaciones recientes | Existencias físicas por recurso; no sumar toneladas, barriles y pies cúbicos directamente |
| Agua | DANE, Cuenta Ambiental y Económica de Flujos del Agua / cuentas relacionadas | Pendiente de verificar tabla, variable y cobertura comparable | Disponibilidad o condición hídrica; no sustituir automáticamente por consumo |
| Flujos energéticos | DANE, Cuenta Ambiental y Económica de Flujos de Energía (CAE-FE) | Serie 2005-2024 provisional en publicación consultada | Variable de presión/flujo; no equivale a stock de energía |

Enlaces de referencia:
- DANE, Cuentas de los Ecosistemas: https://www.dane.gov.co/index.php/estadisticas-por-tema/cuentas-nacionales/cuentas-satelite/cuenta-satelite-ambiental-csa/cuentas-de-los-ecosistemas
- DANE, Cuenta Satélite Ambiental: https://www.dane.gov.co/index.php/estadisticas-por-tema-2/cuentas-nacionales/cuentas-satelite/cuenta-satelite-ambiental-csa
- DANE, Cuenta Ambiental y Económica de Bosque: https://www.dane.gov.co/index.php/comunicados-y-boletines/cuentas-y-sintesis-nacionales/ambiente

Las coberturas anteriores son pistas de búsqueda, no una afirmación de que todas las
variables estén disponibles anualmente o sean comparables entre versiones. Antes
de seleccionar el periodo común se deben descargar anexos, fichas metodológicas y
notas de revisión de cada operación.

## Criterios de selección de indicadores

1. Preferir existencias físicas y medidas de condición/estado.
2. Mantener flujos de extracción, consumo y residuos como indicadores de presión
   separados, salvo que exista una justificación conceptual explícita.
3. No sumar magnitudes heterogéneas (hectáreas, metros cúbicos, toneladas, barriles).
4. Evitar doble conteo entre cobertura boscosa y extensión de ecosistemas.
5. Documentar cambios de metodología, revisiones, años provisionales y estimaciones.
6. Utilizar únicamente datos nacionales o agregados nacionales coherentes en el
   periodo seleccionado.

## Formato de datos

Cada indicador se almacena en un CSV UTF-8 con columnas:

```csv
year,value
2012,123.4
2013,
2014,120.1
```

Un valor vacío significa dato no disponible. No significa cero.

Los metadatos se registran en la configuración del conjunto de datos y deben incluir:
nombre, unidad, fuente, URL, metodología, sentido de interpretación, fecha de
descarga, versión de la publicación y cualquier transformación aplicada.

## Normalización y agregación

Cada indicador se normaliza usando límites de referencia externos, documentados y
fijos. No se deben estimar los límites con el mínimo y máximo de la muestra histórica
si se pretende comparar actualizaciones futuras.

Se calculan dos índices:
- Media aritmética ponderada: permite compensación entre dimensiones.
- Media geométrica ponderada: penaliza valores bajos en alguna dimensión.

El análisis de sensibilidad muestrea pesos en el simplex mediante una distribución
Dirichlet. Sus percentiles describen sensibilidad a la elección de pesos; no son
intervalos de confianza de los datos ni incertidumbre total del índice.

No se imputan valores faltantes ni se renormalizan los pesos año a año. Un índice
anual solo se calcula cuando todos sus componentes están disponibles.

## Periodo común

El periodo de análisis se define como la intersección de años observados de los
indicadores seleccionados, después de verificar que las definiciones sean comparables.
La intersección computacional es necesaria, pero no suficiente: la comparabilidad
metodológica requiere revisión documental.

## Separación entre observación y simulación

- R observado: índice calculado a partir de las series documentadas.
- R simulado: estado del recurso generado por las ecuaciones diferenciales.

La calibración compara ambas series. No se debe presentar el ajuste histórico como
predicción validada del futuro ni como prueba causal.
