"""Ejecuta la malla completa de experimentos y guarda los resultados en JSON/CSV."""

import json
import statistics as st
import time

from motor import (busqueda_aleatoria, genetic_algorithm, mutation,
                   mutation_guiada)

NS = [6, 8, 12]
POBLACIONES = [20, 50, 100, 200]
MUTACIONES = [0.05, 0.10, 0.20]
EJECUCIONES = 30
MAX_GEN = 500
MAX_EVAL_ALEATORIA = 500_000


def resumir(registros):
    exitos = [r for r in registros if r[0]]
    gens = [r[1] for r in exitos]
    evals_ok = [r[2] for r in exitos]
    todas_evals = [r[2] for r in registros]
    return {
        'ejecuciones': len(registros),
        'exitos': len(exitos),
        'tasa_exito': len(exitos) / len(registros),
        'gen_media': round(st.mean(gens), 2) if gens else None,
        'gen_mediana': st.median(gens) if gens else None,
        'gen_desv': round(st.stdev(gens), 2) if len(gens) > 1 else 0.0,
        'gen_min': min(gens) if gens else None,
        'gen_max': max(gens) if gens else None,
        'eval_media_exitos': round(st.mean(evals_ok), 1) if evals_ok else None,
        'eval_media_total': round(st.mean(todas_evals), 1),
    }


def malla(operador, etiqueta):
    filas = []
    for n in NS:
        for pob in POBLACIONES:
            for mut in MUTACIONES:
                regs = [genetic_algorithm(n, pob, MAX_GEN, mut, seed=s,
                                          operador_mutacion=operador)
                        for s in range(EJECUCIONES)]
                fila = {'variante': etiqueta, 'n': n, 'poblacion': pob, 'mutacion': mut}
                fila.update(resumir(regs))
                filas.append(fila)
                print(f"  {etiqueta} N={n:>2} pob={pob:>3} mut={mut:.2f} -> "
                      f"exito {fila['tasa_exito']*100:5.1f}%  gen media {fila['gen_media']}  "
                      f"evals {fila['eval_media_exitos']}")
    return filas


t0 = time.time()
print('== Algoritmo genetico, mutacion por intercambio ==')
base = malla(mutation, 'intercambio')

print('\n== Algoritmo genetico, mutacion guiada ==')
guiada = malla(mutation_guiada, 'guiada')

print('\n== Busqueda aleatoria ==')
aleatoria = []
for n in NS:
    regs = [busqueda_aleatoria(n, MAX_EVAL_ALEATORIA, seed=1000 + s) for s in range(EJECUCIONES)]
    exitos = [r for r in regs if r[0]]
    evs = [r[1] for r in exitos]
    fila = {
        'n': n,
        'ejecuciones': len(regs),
        'exitos': len(exitos),
        'tasa_exito': len(exitos) / len(regs),
        'eval_media': round(st.mean(evs), 1) if evs else None,
        'eval_mediana': st.median(evs) if evs else None,
        'eval_desv': round(st.stdev(evs), 1) if len(evs) > 1 else 0.0,
        'eval_max': max(evs) if evs else None,
    }
    aleatoria.append(fila)
    print(f"  N={n:>2} -> exito {fila['tasa_exito']*100:5.1f}%  evaluaciones media {fila['eval_media']}")

datos = {'ga': base + guiada, 'aleatoria': aleatoria,
         'config': {'ejecuciones': EJECUCIONES, 'max_generaciones': MAX_GEN,
                    'max_eval_aleatoria': MAX_EVAL_ALEATORIA}}
with open('resultados.json', 'w') as f:
    json.dump(datos, f, indent=1)

print(f"\nTiempo total: {time.time() - t0:.1f}s  ->  resultados.json")
