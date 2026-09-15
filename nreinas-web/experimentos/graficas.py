"""Genera las graficas del analisis experimental."""

import json
import statistics as st

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

SURFACE = '#fcfcfb'
INK = '#0b0b0b'
INK2 = '#52514e'
MUTED = '#898781'
GRID = '#e1e0d9'
AXIS = '#c3c2b7'
S = ['#2a78d6', '#eb6834', '#1baf7a']   # azul, naranja, aqua

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 9.5,
    'figure.facecolor': SURFACE,
    'axes.facecolor': SURFACE,
    'axes.edgecolor': AXIS,
    'axes.labelcolor': INK2,
    'text.color': INK,
    'xtick.color': MUTED,
    'ytick.color': MUTED,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.color': GRID,
    'grid.linewidth': 0.8,
    'legend.frameon': False,
})

datos = json.load(open('resultados.json'))
ga = datos['ga']
alea = {r['n']: r for r in datos['aleatoria']}

def sel(variante=None, n=None, pob=None, mut=None):
    out = ga
    if variante is not None: out = [r for r in out if r['variante'] == variante]
    if n is not None:        out = [r for r in out if r['n'] == n]
    if pob is not None:      out = [r for r in out if r['poblacion'] == pob]
    if mut is not None:      out = [r for r in out if abs(r['mutacion'] - mut) < 1e-9]
    return out

NS = [6, 8, 12]
POBS = [20, 50, 100, 200]
MUTS = [0.05, 0.10, 0.20]


def guardar(fig, nombre):
    fig.savefig(nombre, dpi=200, bbox_inches='tight', facecolor=SURFACE)
    plt.close(fig)
    print('->', nombre)


# ---------------------------------------------------------------- A
# Generaciones medias vs tamano de poblacion (mutacion 0.10)
fig, ax = plt.subplots(figsize=(6.6, 3.5))
for i, n in enumerate(NS):
    ys = [sel('intercambio', n, p, 0.10)[0]['gen_media'] for p in POBS]
    ax.plot(POBS, ys, color=S[i], lw=2, marker='o', ms=6.5,
            mec=SURFACE, mew=1.6, label=f'N = {n}', zorder=3)
ax.set_xlabel('Tamaño de población')
ax.set_ylabel('Generaciones promedio')
ax.set_xticks(POBS)
ax.set_xlim(10, 240)
ax.legend(loc='upper right', ncol=3, fontsize=8.5, labelcolor=INK2)
ax.set_ylim(bottom=0)
ax.set_title('Generaciones necesarias según el tamaño de la población',
             color=INK, fontsize=10.5, fontweight='bold', loc='left', pad=30)
ax.text(0, 1.02, 'tasa de mutación 0.10 · 30 ejecuciones por configuración',
        transform=ax.transAxes, color=MUTED, fontsize=8.5, va='bottom')
guardar(fig, 'fig_poblacion.png')


# ---------------------------------------------------------------- B
# Tasa de exito vs tasa de mutacion (poblacion 50)
fig, ax = plt.subplots(figsize=(6.6, 3.4))
ancho = 0.26
for i, n in enumerate(NS):
    ys = [sel('intercambio', n, 50, m)[0]['tasa_exito'] * 100 for m in MUTS]
    xs = [k + (i - 1) * (ancho + 0.015) for k in range(len(MUTS))]
    ax.bar(xs, ys, width=ancho, color=S[i], label=f'N = {n}', zorder=3,
           edgecolor=SURFACE, linewidth=1.4)
    for x, y in zip(xs, ys):
        ax.text(x, y + 2, f'{y:.0f}', ha='center', va='bottom',
                fontsize=8.5, color=INK2)
ax.set_xticks(range(len(MUTS)))
ax.set_xticklabels([f'{m:.2f}' for m in MUTS])
ax.set_xlabel('Tasa de mutación')
ax.set_ylabel('Tasa de éxito (%)')
ax.set_ylim(0, 132)
ax.set_yticks([0, 25, 50, 75, 100])
ax.legend(loc='upper center', ncol=3, fontsize=8.5, labelcolor=INK2)
ax.set_title('Efecto de la tasa de mutación sobre la tasa de éxito',
             color=INK, fontsize=10.5, fontweight='bold', loc='left', pad=30)
ax.text(0, 1.02, 'población 50 · máximo 500 generaciones · 30 ejecuciones',
        transform=ax.transAxes, color=MUTED, fontsize=8.5, va='bottom')
guardar(fig, 'fig_mutacion.png')


# ---------------------------------------------------------------- C
# Evaluaciones: mejor configuracion evolutiva vs busqueda aleatoria
mejores = {}
for n in NS:
    cands = [r for r in sel('intercambio', n) if r['tasa_exito'] == 1.0]
    if not cands:
        cands = sorted(sel('intercambio', n), key=lambda r: -r['tasa_exito'])[:3]
    mejores[n] = min(cands, key=lambda r: r['eval_media_exitos'])

fig, ax = plt.subplots(figsize=(6.6, 3.4))
xs = range(len(NS))
ev_ga = [mejores[n]['eval_media_exitos'] for n in NS]
ev_al = [alea[n]['eval_media'] for n in NS]
b1 = ax.bar([x - 0.19 for x in xs], ev_ga, width=0.36, color=S[0], zorder=3,
            edgecolor=SURFACE, linewidth=1.4, label='Algoritmo evolutivo')
b2 = ax.bar([x + 0.19 for x in xs], ev_al, width=0.36, color=S[1], zorder=3,
            edgecolor=SURFACE, linewidth=1.4, label='Búsqueda aleatoria')
for barras, vals in ((b1, ev_ga), (b2, ev_al)):
    for b, v in zip(barras, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.12, f'{v:,.0f}'.replace(',', ' '),
                ha='center', va='bottom', fontsize=8.5, color=INK2)
ax.set_yscale('log')
ax.set_ylim(60, 120000)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'.replace(',', ' ')))
ax.set_xticks(list(xs))
ax.set_xticklabels([f'N = {n}' for n in NS])
ax.set_ylabel('Evaluaciones de aptitud (escala log)')
ax.legend(loc='upper left', ncol=2, fontsize=8.5, labelcolor=INK2)
ax.set_title('Costo real: evaluaciones hasta encontrar una solución',
             color=INK, fontsize=10.5, fontweight='bold', loc='left', pad=30)
ax.text(0, 1.02, 'evolutivo en su mejor configuración por N · 30 ejecuciones',
        transform=ax.transAxes, color=MUTED, fontsize=8.5, va='bottom')
guardar(fig, 'fig_aleatoria.png')


# ---------------------------------------------------------------- D
# Mutacion por intercambio vs mutacion guiada
fig, ax = plt.subplots(figsize=(6.6, 3.4))
med_int = [st.mean([r['tasa_exito'] for r in sel('intercambio', n)]) * 100 for n in NS]
med_gui = [st.mean([r['tasa_exito'] for r in sel('guiada', n)]) * 100 for n in NS]
b1 = ax.bar([x - 0.19 for x in xs], med_int, width=0.36, color=S[0], zorder=3,
            edgecolor=SURFACE, linewidth=1.4, label='Intercambio aleatorio')
b2 = ax.bar([x + 0.19 for x in xs], med_gui, width=0.36, color=S[2], zorder=3,
            edgecolor=SURFACE, linewidth=1.4, label='Intercambio guiado')
for barras, vals in ((b1, med_int), (b2, med_gui)):
    for b, v in zip(barras, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f'{v:.1f}',
                ha='center', va='bottom', fontsize=8.5, color=INK2)
ax.set_xticks(list(xs))
ax.set_xticklabels([f'N = {n}' for n in NS])
ax.set_ylabel('Tasa de éxito promedio (%)')
ax.set_ylim(0, 130)
ax.set_yticks([0, 25, 50, 75, 100])
ax.legend(loc='upper center', ncol=2, fontsize=8.5, labelcolor=INK2)
ax.set_title('Mutación guiada frente a mutación aleatoria',
             color=INK, fontsize=10.5, fontweight='bold', loc='left', pad=30)
ax.text(0, 1.02, 'promedio de las 12 configuraciones de población y mutación de cada N',
        transform=ax.transAxes, color=MUTED, fontsize=8.5, va='bottom')
guardar(fig, 'fig_guiada.png')


# ---------------------------------------------------------------- resumen
print('\nMejor configuracion por N (evolutivo):')
for n in NS:
    m = mejores[n]
    print(f"  N={n}: pob={m['poblacion']} mut={m['mutacion']} -> "
          f"{m['eval_media_exitos']} evals, {m['gen_media']} gen, exito {m['tasa_exito']*100:.0f}%")
print('\nPromedio tasa de exito por N:')
for n, a, b in zip(NS, med_int, med_gui):
    print(f"  N={n}: intercambio {a:.1f}%  guiada {b:.1f}%  (+{b-a:.1f} pts)")
