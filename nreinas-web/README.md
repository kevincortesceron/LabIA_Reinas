# N-Reinas · Algoritmo Genético (web)

Aplicación web en Flask para visualizar el tablero de las N-Reinas resuelto con
el algoritmo genético.

## Cómo ejecutarla

```bash
cd nreinas-web
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Luego abre **http://127.0.0.1:5000** en el navegador.

## Estructura

| Archivo | Qué hace |
|---|---|
| `genetic.py` | El algoritmo genético (fitness, selección, cruce, mutación). Es tu código original, sin `print` ni `matplotlib`. |
| `app.py` | Servidor Flask. Sirve la página y expone `POST /api/resolver`. |
| `templates/index.html` | La página. |
| `static/style.css` | Estilos (tema claro y oscuro automáticos). |
| `static/app.js` | Dibuja el tablero, la animación y la gráfica de convergencia. |

## Qué hace la página

- Formulario con N, tamaño de población, generaciones, tasa de mutación y semilla.
- Tablero de ajedrez con las reinas; las que se atacan se marcan en rojo.
- Reproductor para **animar generación por generación** cómo evoluciona el mejor tablero.
- Gráfica de convergencia del mejor fitness con tooltip al pasar el mouse
  (haz clic en un punto y el tablero salta a esa generación) y vista en tabla.

## La API

`POST /api/resolver`

```json
{ "n": 8, "population_size": 100, "generations": 500, "mutation_rate": 0.2, "seed": 42 }
```

Respuesta:

```json
{
  "ok": true,
  "found": true,
  "generation": 37,
  "solution": [3, 1, 6, 2, 5, 7, 4, 0],
  "history": [-5, -4, "...", 0],
  "snapshots": [[...], "..."],
  "conflicts": [],
  "matrix": [[0,0,0,"..."]],
  "n": 8
}
```

`solution[i]` es la **fila** de la reina que está en la **columna** `i`
(igual que en el script original).

## Notas sobre el algoritmo

- El fitness es negativo a propósito: `0` significa cero ataques (solución óptima).
- El cruce de un punto usa `np.random.randint(1, n - 1)`, así que **N debe ser ≥ 4**
  (la app ya valida ese rango, hasta 20).
- Con N grande o población pequeña puede no converger; la app muestra entonces el
  mejor tablero encontrado en lugar de fallar.
