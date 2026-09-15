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

## Despliegue

> **Netlify no sirve para este proyecto.** Netlify solo ejecuta funciones en
> JavaScript/TypeScript y Go; no tiene runtime de Python, así que un backend Flask
> no puede correr ahí. Solo serviría si el algoritmo se reescribe en JavaScript.

### Render (recomendado — gratis, sin tarjeta)

1. Sube esta carpeta a un repositorio de GitHub.
2. En [render.com](https://render.com) → **New → Web Service** → conecta el repo.
3. Render detecta `render.yaml` y ya queda configurado. Si lo haces a mano:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app --timeout 120`

El plan gratuito da 750 horas al mes, pero el servicio **se duerme tras 15 minutos
sin visitas** y la primera carga tarda ~30–50 s en despertar.

### PythonAnywhere (gratis, siempre encendido)

Una app web gratis, sin Docker, ideal para mostrar el proyecto en clase porque no
se duerme. El límite es de **100 segundos de CPU al día**, suficiente para este
algoritmo salvo que hagas muchas corridas pesadas (N grande + muchas generaciones).

### Otras opciones

| Plataforma | Nota |
|---|---|
| Vercel | Corre Flask con su runtime de Python, pero pide tarjeta para el plan gratis y las funciones tienen límite de tiempo de ejecución. |
| Railway | Ya no tiene plan gratis permanente (créditos de prueba y luego suscripción mínima). |
| Google Cloud Run | Capa gratuita generosa, pero exige tarjeta y configurar un contenedor. |

`Procfile` y `render.yaml` ya están incluidos, así que el proyecto también funciona
tal cual en cualquier plataforma tipo Heroku.

## Estructura

| Archivo | Qué hace |
|---|---|
| `genetic.py` | El algoritmo genético (fitness, selección, cruce, mutación). Es tu código original, sin `print` ni `matplotlib`. |
| `app.py` | Servidor Flask. Sirve la página y expone `POST /api/resolver`. |
| `templates/index.html` | La página. |
| `static/style.css` | Estilos (tema claro y oscuro automáticos). |
| `static/app.js` | Dibuja el tablero, la animación y la gráfica de convergencia. |
| `experimentos/` | Los scripts que generan el análisis experimental de la Parte 3 del informe. |

## Reproducir los resultados del informe

Todos los números, tablas y figuras de la Parte 3 salen de `experimentos/`:

```bash
cd experimentos
pip install numpy matplotlib
python verificar.py   # comprueba que el motor experimental equivale a genetic.py
python correr.py      # ~4-5 min. Reproduce resultados.json
python graficas.py    # Figuras 1 a 4
```

Cada ejecución usa una semilla fija, así que los resultados son reproducibles
bit a bit. `experimentos/README.md` explica el diseño experimental y la relación
entre `motor.py` y `genetic.py`.

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
