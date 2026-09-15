"""
Servidor web (Flask) para visualizar el tablero de las N-Reinas
resuelto con un Algoritmo Genetico.

Uso:
    pip install -r requirements.txt
    python app.py
    -> abrir http://127.0.0.1:5000
"""

from flask import Flask, jsonify, render_template, request

from genetic import attacking_pairs, board_matrix, genetic_algorithm

app = Flask(__name__)

# Limites para que el navegador no se quede esperando una eternidad
LIMITS = {
    "n": (4, 20),
    "population_size": (10, 500),
    "generations": (10, 2000),
    "mutation_rate": (0.0, 1.0),
}


def _read_int(data, key):
    low, high = LIMITS[key]
    try:
        value = int(data.get(key))
    except (TypeError, ValueError):
        raise ValueError(f"'{key}' debe ser un numero entero.")
    if not low <= value <= high:
        raise ValueError(f"'{key}' debe estar entre {low} y {high}.")
    return value


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/resolver")
def resolver():
    data = request.get_json(silent=True) or {}

    try:
        n = _read_int(data, "n")
        population_size = _read_int(data, "population_size")
        generations = _read_int(data, "generations")
        mutation_rate = float(data.get("mutation_rate", 0.2))
    except ValueError as err:
        return jsonify({"ok": False, "error": str(err)}), 400

    low, high = LIMITS["mutation_rate"]
    if not low <= mutation_rate <= high:
        return jsonify({"ok": False, "error": "La tasa de mutacion debe estar entre 0 y 1."}), 400

    seed = data.get("seed")
    seed = int(seed) if str(seed).strip() not in ("", "None", "null") else None

    result = genetic_algorithm(
        n=n,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate,
        seed=seed,
    )

    solution = result["solution"]
    result["ok"] = True
    result["n"] = n
    result["conflicts"] = attacking_pairs(solution) if solution else []
    result["matrix"] = board_matrix(solution).tolist() if solution else []

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
