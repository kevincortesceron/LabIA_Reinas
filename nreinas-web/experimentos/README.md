# Experimentos del análisis (Parte 3 del informe)

Todo lo que aparece en la Parte 3 del informe se genera con estos scripts. Los
resultados son **reproducibles bit a bit**: cada ejecución usa una semilla fija
(`np.random.seed`), así que volver a correrlos produce exactamente los mismos
números que están en el documento.

## Cómo reproducirlos

```bash
cd experimentos
pip install numpy matplotlib
python correr.py      # ~4-5 minutos. Genera resultados.json
python graficas.py    # Genera las cuatro figuras .png
python exportar.py    # Genera datos.js con las tablas del informe
```

## Qué hace cada archivo

| Archivo | Función |
|---|---|
| `motor.py` | Los operadores del algoritmo genético, instrumentados para contar evaluaciones de aptitud. Incluye también la búsqueda aleatoria, la variante de mutación guiada y las dos versiones de la función de aptitud. |
| `correr.py` | Ejecuta la malla completa: N ∈ {6, 8, 12} × población ∈ {20, 50, 100, 200} × mutación ∈ {0.05, 0.10, 0.20}, con 30 ejecuciones por configuración y un máximo de 500 generaciones. Repite todo con los dos operadores de mutación y añade la búsqueda aleatoria. En total 2 250 ejecuciones. |
| `graficas.py` | Produce las figuras 1 a 4 del informe. |
| `exportar.py` | Convierte `resultados.json` en las tablas que aparecen en el documento. |
| `resultados.json` | Resultados crudos de la corrida reportada en el informe. |

## Relación con `genetic.py`

`motor.py` reimplementa los mismos operadores que `../genetic.py` (el módulo que
usa la aplicación web) con dos diferencias, ninguna de las cuales altera el
comportamiento del algoritmo:

1. **Instrumentación.** Devuelve el conteo de evaluaciones de la función de
   aptitud, que es la métrica con la que se comparan las configuraciones.

2. **Función de aptitud en O(N).** En lugar de recorrer todos los pares de
   columnas, cuenta cuántas reinas ocupan cada fila y cada diagonal
   (`fila − columna` y `fila + columna`) y suma C(k, 2) por cada grupo con k
   reinas. El valor devuelto es idéntico y no consume números aleatorios, de
   modo que la trayectoria del algoritmo no cambia.

Ambas afirmaciones están verificadas:

- `fitness_pares` y `fitness_diagonales` coinciden en 3 000 tableros aleatorios
  con N entre 4 y 12.
- `motor.genetic_algorithm` y `genetic.genetic_algorithm` encuentran la solución
  en la **misma generación** para las 135 combinaciones de N, población, tasa de
  mutación y semilla que se probaron.

El script `verificar.py` vuelve a correr ambas comprobaciones.

## Nota sobre las medias de generaciones

Las estadísticas de generaciones se calculan únicamente sobre las ejecuciones
que encontraron solución. Por eso deben leerse siempre junto a la tasa de éxito:
una configuración que solo triunfa el 40 % de las veces promedia nada más sus
corridas afortunadas, lo que la hace parecer más rápida de lo que es.
