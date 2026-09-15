"""Exporta los resultados a datos.js para que el generador del informe los consuma."""

import json
import statistics as st
import time

import numpy as np

from motor import fitness_diagonales, fitness_pares

datos = json.load(open('resultados.json'))
ga = datos['ga']
alea = {r['n']: r for r in datos['aleatoria']}

NS = [6, 8, 12]
POBS = [20, 50, 100, 200]
MUTS = [0.05, 0.10, 0.20]


def sel(variante, n, pob, mut):
    for r in ga:
        if (r['variante'] == variante and r['n'] == n and r['poblacion'] == pob
                and abs(r['mutacion'] - mut) < 1e-9):
            return r
    raise KeyError((variante, n, pob, mut))


def pct(x):
    return f'{x * 100:.1f} %'


def num(x):
    if x is None:
        return '—'
    return f'{x:,.0f}'.replace(',', ' ') if x >= 1000 else f'{x:g}'


# --- Tabla 1: efecto del tamano de poblacion (mutacion 0.10) ---------------
t_poblacion = [['N', 'Población', 'Tasa de éxito', 'Gen. media', 'Gen. mediana', 'Desv. est.', 'Evaluaciones']]
for n in NS:
    for pob in POBS:
        r = sel('intercambio', n, pob, 0.10)
        t_poblacion.append([str(n), str(pob), pct(r['tasa_exito']), num(r['gen_media']),
                            num(r['gen_mediana']), num(r['gen_desv']), num(r['eval_media_exitos'])])

# --- Tabla 2: efecto de la tasa de mutacion (poblacion 50) -----------------
t_mutacion = [['N', 'Mutación', 'Tasa de éxito', 'Gen. media', 'Gen. mediana', 'Desv. est.', 'Evaluaciones']]
for n in NS:
    for mut in MUTS:
        r = sel('intercambio', n, 50, mut)
        t_mutacion.append([str(n), f'{mut:.2f}', pct(r['tasa_exito']), num(r['gen_media']),
                           num(r['gen_mediana']), num(r['gen_desv']), num(r['eval_media_exitos'])])

# --- Tabla 3: evolutivo vs busqueda aleatoria ------------------------------
mejores = {}
for n in NS:
    cands = [r for r in ga if r['variante'] == 'intercambio' and r['n'] == n and r['tasa_exito'] == 1.0]
    mejores[n] = min(cands, key=lambda r: r['eval_media_exitos'])

t_aleatoria = [['N', 'Método', 'Tasa de éxito', 'Evaluaciones medias', 'Mediana', 'Aprovecha soluciones previas']]
for n in NS:
    m = mejores[n]
    a = alea[n]
    t_aleatoria.append([str(n), 'Algoritmo evolutivo', pct(m['tasa_exito']),
                        num(m['eval_media_exitos']), '—', 'Sí'])
    t_aleatoria.append(['', 'Búsqueda aleatoria', pct(a['tasa_exito']),
                        num(a['eval_media']), num(a['eval_mediana']), 'No'])

# --- Tabla 4: mutacion guiada ---------------------------------------------
t_guiada = [['N', 'Éxito con intercambio', 'Éxito con intercambio guiado', 'Diferencia']]
comparacion = []
for n in NS:
    i = st.mean([r['tasa_exito'] for r in ga if r['variante'] == 'intercambio' and r['n'] == n])
    g = st.mean([r['tasa_exito'] for r in ga if r['variante'] == 'guiada' and r['n'] == n])
    comparacion.append((n, i, g))
    signo = '+' if g >= i else '−'
    t_guiada.append([str(n), pct(i), pct(g), f'{signo}{abs(g - i) * 100:.1f} puntos'])

# --- Tabla 5: mejor configuracion -----------------------------------------
t_mejor = [['N', 'Población', 'Mutación', 'Tasa de éxito', 'Gen. media', 'Evaluaciones medias']]
for n in NS:
    m = mejores[n]
    t_mejor.append([str(n), str(m['poblacion']), f"{m['mutacion']:.2f}", pct(m['tasa_exito']),
                    num(m['gen_media']), num(m['eval_media_exitos'])])

# --- Tabla 6: costo de la funcion de aptitud ------------------------------
np.random.seed(7)
t_costo = [['N', 'Aptitud O(N²)', 'Aptitud O(N)', 'Aceleración']]
for n in (8, 12, 20, 50):
    tab = [np.random.permutation(n) for _ in range(3000)]
    t0 = time.time(); [fitness_pares(b) for b in tab]; a = time.time() - t0
    t0 = time.time(); [fitness_diagonales(b) for b in tab]; c = time.time() - t0
    t_costo.append([str(n), f'{a * 1000:.0f} ms', f'{c * 1000:.0f} ms', f'×{a / c:.1f}'])

# --- Anexo: malla completa ------------------------------------------------
t_anexo = [['N', 'Población', 'Mutación', 'Éxito', 'Gen. media', 'Mediana', 'Desv.', 'Evaluaciones']]
for n in NS:
    for pob in POBS:
        for mut in MUTS:
            r = sel('intercambio', n, pob, mut)
            t_anexo.append([str(n), str(pob), f'{mut:.2f}', pct(r['tasa_exito']),
                            num(r['gen_media']), num(r['gen_mediana']),
                            num(r['gen_desv']), num(r['eval_media_exitos'])])

salida = {
    'tPoblacion': t_poblacion,
    'tMutacion': t_mutacion,
    'tAleatoria': t_aleatoria,
    'tGuiada': t_guiada,
    'tMejor': t_mejor,
    'tCosto': t_costo,
    'tAnexo': t_anexo,
    'config': datos['config'],
    'mejores': {str(n): mejores[n] for n in NS},
    'aleatoria': {str(n): alea[n] for n in NS},
    'comparacionGuiada': [{'n': n, 'intercambio': i, 'guiada': g} for n, i, g in comparacion],
}

with open('datos.js', 'w') as f:
    f.write('module.exports = ' + json.dumps(salida, ensure_ascii=False, indent=1) + ';\n')

print('datos.js generado')
for fila in t_mejor:
    print(' ', ' | '.join(fila))
print()
for fila in t_costo:
    print(' ', ' | '.join(fila))
