"""
Comprueba que el motor experimental es equivalente al algoritmo entregado.

    python verificar.py

Verifica dos cosas:
  1. Que las dos implementaciones de la funcion de aptitud dan el mismo valor.
  2. Que el motor experimental y genetic.py encuentran la solucion en la misma
     generacion para las mismas semillas.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genetic  # el modulo que usa la aplicacion web
import motor

fallos = 0

# --- 1. equivalencia de la funcion de aptitud -------------------------------
np.random.seed(0)
distintos = 0
for _ in range(3000):
    n = np.random.randint(4, 13)
    tablero = np.random.randint(0, n, size=n)
    if motor.fitness_pares(tablero) != motor.fitness_diagonales(tablero):
        distintos += 1
print(f'1. Aptitud O(N^2) vs O(N) sobre 3000 tableros: '
      f'{"IDENTICAS" if distintos == 0 else f"{distintos} DIFERENCIAS"}')
fallos += distintos

# --- 2. misma trayectoria que el algoritmo entregado ------------------------
comparaciones = 0
diferencias = 0
for n in (6, 8, 12):
    for poblacion in (20, 50, 100):
        for mutacion in (0.05, 0.10, 0.20):
            for semilla in range(5):
                a = motor.genetic_algorithm(n, poblacion, 500, mutacion, seed=semilla)
                b = genetic.genetic_algorithm(n, poblacion, 500, mutacion, seed=semilla)
                comparaciones += 1
                gen_motor = a[1] if a[0] else None
                if a[0] != b['found'] or gen_motor != b['generation']:
                    diferencias += 1
                    print(f'   DIFIERE N={n} pob={poblacion} mut={mutacion} '
                          f'semilla={semilla}: {gen_motor} vs {b["generation"]}')
print(f'2. Trayectoria frente a genetic.py en {comparaciones} casos: '
      f'{"IDENTICA" if diferencias == 0 else f"{diferencias} DIFERENCIAS"}')
fallos += diferencias

print('\nResultado:', 'todo correcto' if fallos == 0 else f'{fallos} problemas')
sys.exit(1 if fallos else 0)
