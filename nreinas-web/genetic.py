"""
Algoritmo Genetico para el problema de las N-Reinas.

Es el mismo algoritmo del script original; los unicos cambios son:
  * no imprime ni grafica nada (eso ahora lo hace la pagina web),
  * guarda un "snapshot" del mejor tablero de cada generacion para poder
    animar la evolucion en el navegador,
  * acepta una semilla (seed) para poder reproducir una corrida.
"""

import numpy as np


# -------------------------------
# Funcion de evaluacion (fitness)
# -------------------------------
def fitness(board):
    """ Calcula el numero de ataques entre reinas. """
    n = len(board)
    attacks = 0

    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                attacks += 1

    return -attacks  # Se devuelve el negativo porque queremos minimizar los ataques


def attacking_pairs(board):
    """ Devuelve la lista de parejas de columnas (i, j) que se atacan entre si. """
    n = len(board)
    pairs = []

    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                pairs.append((i, j))

    return pairs


# -------------------------------
# Funciones de Algoritmo Genetico
# -------------------------------

def create_population(size, n):
    """ Crea una poblacion inicial de tableros aleatorios. """
    return [np.random.permutation(n) for _ in range(size)]


def selection(population, fitness_values, num_parents):
    """ Selecciona los mejores individuos basados en su aptitud (fitness). """
    sorted_indices = np.argsort(fitness_values)[-num_parents:]  # Mejores num_parents individuos
    return [population[i] for i in sorted_indices]


def crossover(parent1, parent2):
    """ Cruce de un punto: combina dos padres para generar un hijo. """
    n = len(parent1)
    point = np.random.randint(1, n - 1)  # Punto de cruce
    child = np.concatenate((parent1[:point], parent2[point:]))

    # Arreglar duplicados y valores faltantes
    unique_values = set(child)
    missing_values = list(set(range(n)) - unique_values)
    np.random.shuffle(missing_values)

    for i in range(n):
        if list(child).count(child[i]) > 1:  # Si hay duplicados
            child[i] = missing_values.pop()  # Reemplazamos por un valor unico

    return child


def mutation(board, mutation_rate=0.2):
    """ Aplica mutacion intercambiando dos posiciones con probabilidad mutation_rate. """
    if np.random.rand() < mutation_rate:
        i, j = np.random.randint(0, len(board), size=2)
        board[i], board[j] = board[j], board[i]
    return board


# -------------------------------
# Algoritmo Genetico para N-Reinas
# -------------------------------

def genetic_algorithm(n, population_size=100, generations=500, mutation_rate=0.2,
                      seed=None, keep_snapshots=True):
    """
    Algoritmo Genetico para resolver el problema de las N-Reinas.

    Devuelve un diccionario con:
        found            -> True si encontro una solucion sin ataques
        solution         -> lista con la fila de la reina de cada columna (o None)
        generation       -> generacion en la que se encontro (1-indexada) o None
        history          -> mejor fitness de cada generacion (0 = sin ataques)
        snapshots        -> mejor tablero de cada generacion (para animar)
        generations_run  -> cuantas generaciones se ejecutaron realmente
    """
    if seed is not None:
        np.random.seed(int(seed))

    population = create_population(population_size, n)
    best_fitness_values = []   # Para graficar
    snapshots = []             # Mejor tablero de cada generacion

    for gen in range(generations):
        # Evaluar aptitud de la poblacion
        fitness_values = np.array([fitness(ind) for ind in population])

        # Guardar mejor valor para graficar
        best_index = int(np.argmax(fitness_values))
        best_fitness_values.append(int(np.max(fitness_values)))
        if keep_snapshots:
            snapshots.append([int(x) for x in population[best_index]])

        # Si encontramos una solucion optima (sin ataques)
        if np.max(fitness_values) == 0:
            return {
                "found": True,
                "solution": [int(x) for x in population[best_index]],
                "generation": gen + 1,
                "history": best_fitness_values,
                "snapshots": snapshots,
                "generations_run": gen + 1,
            }

        # Seleccion de los mejores padres
        parents = selection(population, fitness_values, max(2, population_size // 2))

        # Generacion de nueva poblacion con crossover y mutacion
        new_population = []
        for _ in range(population_size):
            idx1, idx2 = np.random.choice(len(parents), size=2, replace=False)  # Seleccion de indices
            parent1, parent2 = parents[idx1], parents[idx2]  # Obtener padres
            child = crossover(parent1, parent2)              # Cruzar padres
            child = mutation(child, mutation_rate)           # Aplicar mutacion
            new_population.append(child)

        population = new_population  # Reemplazo de la poblacion

    # No se encontro solucion: devolvemos el mejor tablero visto
    best_gen = int(np.argmax(best_fitness_values))
    return {
        "found": False,
        "solution": snapshots[best_gen] if snapshots else None,
        "generation": None,
        "history": best_fitness_values,
        "snapshots": snapshots,
        "generations_run": generations,
    }


def board_matrix(solution):
    """ Matriz n x n con 1 donde hay una reina (equivalente al 'tablero visual'). """
    n = len(solution)
    matrix = np.zeros((n, n), dtype=int)
    for i in range(n):
        matrix[solution[i], i] = 1
    return matrix
