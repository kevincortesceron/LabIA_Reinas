"""
Motor experimental para el Taller 1 de Inteligencia Artificial.

Reproduce exactamente los operadores del algoritmo genetico entregado
(seleccion por truncamiento, cruce de un punto con reparacion, mutacion por
intercambio) e instrumenta el conteo de evaluaciones de la funcion de aptitud.

La unica diferencia con el codigo original es que la funcion de aptitud se
calcula contando reinas por diagonal, en O(N) en lugar de O(N^2). El resultado
numerico es identico y no consume numeros aleatorios, asi que la trayectoria
del algoritmo no cambia.
"""

from math import comb

import numpy as np

# ---------------------------------------------------------------------------
# Funciones de aptitud
# ---------------------------------------------------------------------------


def fitness_pares(board):
    """Version original: compara todos los pares de columnas. O(N^2)."""
    n = len(board)
    attacks = 0
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                attacks += 1
    return -attacks


def fitness_diagonales(board):
    """Version optimizada: cuenta reinas por diagonal. O(N)."""
    n = len(board)
    filas = {}
    d1 = {}   # fila - columna
    d2 = {}   # fila + columna
    for col in range(n):
        fila = int(board[col])
        filas[fila] = filas.get(fila, 0) + 1
        a = fila - col
        b = fila + col
        d1[a] = d1.get(a, 0) + 1
        d2[b] = d2.get(b, 0) + 1
    ataques = 0
    for conteo in (filas, d1, d2):
        for k in conteo.values():
            if k > 1:
                ataques += comb(k, 2)
    return -ataques


# ---------------------------------------------------------------------------
# Operadores (identicos a los del proyecto)
# ---------------------------------------------------------------------------


def create_population(size, n):
    return [np.random.permutation(n) for _ in range(size)]


def selection(population, fitness_values, num_parents):
    sorted_indices = np.argsort(fitness_values)[-num_parents:]
    return [population[i] for i in sorted_indices]


def crossover(parent1, parent2):
    n = len(parent1)
    point = np.random.randint(1, n - 1)
    child = np.concatenate((parent1[:point], parent2[point:]))

    unique_values = set(child)
    missing_values = list(set(range(n)) - unique_values)
    np.random.shuffle(missing_values)

    for i in range(n):
        if list(child).count(child[i]) > 1:
            child[i] = missing_values.pop()
    return child


def mutation(board, mutation_rate=0.2):
    """Mutacion por intercambio, tal cual el codigo original."""
    if np.random.rand() < mutation_rate:
        i, j = np.random.randint(0, len(board), size=2)
        board[i], board[j] = board[j], board[i]
    return board


def columnas_en_conflicto(board):
    n = len(board)
    malas = set()
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                malas.add(i)
                malas.add(j)
    return sorted(malas)


def mutation_guiada(board, mutation_rate=0.2):
    """Variante informada: al menos una de las dos posiciones esta en conflicto."""
    if np.random.rand() < mutation_rate:
        malas = columnas_en_conflicto(board)
        if malas:
            i = malas[np.random.randint(0, len(malas))]
            j = np.random.randint(0, len(board))
            if i != j:
                board[i], board[j] = board[j], board[i]
        else:
            i, j = np.random.randint(0, len(board), size=2)
            board[i], board[j] = board[j], board[i]
    return board


# ---------------------------------------------------------------------------
# Algoritmo genetico instrumentado
# ---------------------------------------------------------------------------


def genetic_algorithm(n, population_size, generations, mutation_rate,
                      seed=None, operador_mutacion=mutation):
    """Devuelve (exito, generaciones_usadas, evaluaciones_de_fitness, mejor_aptitud)."""
    if seed is not None:
        np.random.seed(int(seed))

    population = create_population(population_size, n)
    evaluaciones = 0
    mejor_global = -10**9

    for gen in range(generations):
        fitness_values = np.array([fitness_diagonales(ind) for ind in population])
        evaluaciones += population_size
        mejor = int(np.max(fitness_values))
        mejor_global = max(mejor_global, mejor)

        if mejor == 0:
            return True, gen + 1, evaluaciones, 0

        parents = selection(population, fitness_values, max(2, population_size // 2))

        new_population = []
        for _ in range(population_size):
            idx1, idx2 = np.random.choice(len(parents), size=2, replace=False)
            child = crossover(parents[idx1], parents[idx2])
            child = operador_mutacion(child, mutation_rate)
            new_population.append(child)
        population = new_population

    return False, generations, evaluaciones, mejor_global


def busqueda_aleatoria(n, max_evaluaciones, seed=None):
    """Genera permutaciones al azar hasta hallar una solucion."""
    if seed is not None:
        np.random.seed(int(seed))
    for k in range(1, max_evaluaciones + 1):
        board = np.random.permutation(n)
        if fitness_diagonales(board) == 0:
            return True, k
    return False, max_evaluaciones
