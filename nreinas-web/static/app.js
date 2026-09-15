/* =========================================================
   N-Reinas · frontend
   ========================================================= */

const $ = (id) => document.getElementById(id);

const form      = $('form');
const runBtn    = $('run');
const statusEl  = $('status');
const boardEl   = $('board');
const vectorEl  = $('vector');
const playerEl  = $('player');
const playBtn   = $('play');
const scrub     = $('scrub');
const genLabel  = $('gen-label');
const statsEl   = $('stats');
const mrOut     = $('mr-out');

let run = null;      // último resultado del servidor
let timer = null;    // temporizador de la animación

/* ---------------------------------------------------------
   Formulario
   --------------------------------------------------------- */
$('mutation_rate').addEventListener('input', (e) => {
  mrOut.textContent = Number(e.target.value).toFixed(2);
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  stopAnimation();

  runBtn.disabled = true;
  statusEl.className = 'status';
  statusEl.textContent = 'Ejecutando el algoritmo genético…';

  const payload = {
    n:               Number($('n').value),
    population_size: Number($('population_size').value),
    generations:     Number($('generations').value),
    mutation_rate:   Number($('mutation_rate').value),
    seed:            $('seed').value,
  };

  try {
    const res  = await fetch('/api/resolver', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok || !data.ok) throw new Error(data.error || 'Error en el servidor.');

    run = data;
    render(data);
  } catch (err) {
    statusEl.className = 'status warn';
    statusEl.textContent = err.message;
  } finally {
    runBtn.disabled = false;
  }
});

/* ---------------------------------------------------------
   Render general
   --------------------------------------------------------- */
function render(data) {
  const last = data.history.length - 1;

  if (data.found) {
    statusEl.className = 'status ok';
    statusEl.textContent = `¡Solución encontrada en la generación ${data.generation}!`;
  } else {
    statusEl.className = 'status warn';
    statusEl.textContent = `Sin solución en ${data.generations_run} generaciones. Se muestra el mejor tablero hallado.`;
  }

  statsEl.hidden = false;
  playerEl.hidden = false;
  scrub.max = String(last);
  scrub.value = String(last);

  showGeneration(last);
  drawChart(data.history);
  fillTable(data.history);
}

/* ---------------------------------------------------------
   Tablero
   --------------------------------------------------------- */
function showGeneration(idx) {
  if (!run) return;

  const board = run.snapshots[idx];
  const n = run.n;
  const attacks = -run.history[idx];
  const conflicted = conflictColumns(board);

  boardEl.style.gridTemplateColumns = `repeat(${n}, 1fr)`;
  boardEl.setAttribute('aria-label',
    `Tablero ${n}×${n}, generación ${idx + 1}, ${attacks} ataques`);

  let html = '';
  for (let row = 0; row < n; row++) {
    for (let col = 0; col < n; col++) {
      const shade   = (row + col) % 2 === 0 ? 'light' : 'dark';
      const isQueen = board[col] === row;
      const bad     = isQueen && conflicted.has(col);
      html += `<div class="sq ${shade}${bad ? ' attacked' : ''}">` +
              (isQueen ? '<span class="q">&#9819;</span>' : '') +
              '</div>';
    }
  }
  boardEl.innerHTML = html;

  genLabel.textContent = `gen ${idx + 1}`;
  $('s-gen').textContent = idx + 1;
  $('s-att').textContent = attacks;
  $('s-fit').textContent = run.history[idx];
  vectorEl.textContent = `Vector solución (fila por columna): [${board.join(', ')}]`;
}

function conflictColumns(board) {
  const bad = new Set();
  for (let i = 0; i < board.length; i++) {
    for (let j = i + 1; j < board.length; j++) {
      if (board[i] === board[j] || Math.abs(board[i] - board[j]) === Math.abs(i - j)) {
        bad.add(i); bad.add(j);
      }
    }
  }
  return bad;
}

/* ---------------------------------------------------------
   Animación
   --------------------------------------------------------- */
scrub.addEventListener('input', () => {
  stopAnimation();
  showGeneration(Number(scrub.value));
});

playBtn.addEventListener('click', () => {
  if (timer) { stopAnimation(); return; }
  if (!run) return;

  let i = Number(scrub.value);
  if (i >= run.history.length - 1) i = 0;

  playBtn.textContent = '❚❚ Pausar';
  const step = Math.max(1, Math.floor(run.history.length / 120));

  timer = setInterval(() => {
    i += step;
    if (i >= run.history.length - 1) { i = run.history.length - 1; stopAnimation(); }
    scrub.value = String(i);
    showGeneration(i);
  }, 90);
});

function stopAnimation() {
  if (timer) clearInterval(timer);
  timer = null;
  playBtn.textContent = '▶︎ Animar';
}

/* ---------------------------------------------------------
   Gráfica de convergencia (SVG, una sola serie)
   --------------------------------------------------------- */
const chartEl = $('chart');
let chartState = null;

function drawChart(history) {
  const W = 900, H = 320;
  const M = { top: 30, right: 22, bottom: 42, left: 56 };
  const iw = W - M.left - M.right;
  const ih = H - M.top - M.bottom;

  const yMin = Math.min(...history, -1);
  const yMax = 0;
  const xMax = Math.max(history.length - 1, 1);

  const x = (i) => M.left + (i / xMax) * iw;
  const y = (v) => M.top + ((yMax - v) / (yMax - yMin)) * ih;

  // Ticks "redondos" en Y
  const yTicks = niceTicks(yMin, yMax, 5);
  const xTicks = niceTicks(0, xMax, Math.min(6, xMax)).filter((t) => t >= 0 && t <= xMax);

  const line = history.map((v, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(2)},${y(v).toFixed(2)}`).join(' ');
  const area = `${line} L${x(xMax).toFixed(2)},${y(yMin).toFixed(2)} L${x(0).toFixed(2)},${y(yMin).toFixed(2)} Z`;

  const lastI = history.length - 1;
  const lastV = history[lastI];

  chartEl.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" role="img"
         aria-label="Curva del mejor fitness por generación; termina en ${lastV}">
      ${yTicks.map((t) => `
        <line class="grid-line" x1="${M.left}" x2="${W - M.right}" y1="${y(t).toFixed(2)}" y2="${y(t).toFixed(2)}"/>
        <text class="tick-text" x="${M.left - 10}" y="${(y(t) + 4).toFixed(2)}" text-anchor="end">${t}</text>
      `).join('')}

      <line class="axis-line" x1="${M.left}" x2="${W - M.right}" y1="${M.top + ih}" y2="${M.top + ih}"/>
      ${xTicks.map((t) => `
        <text class="tick-text" x="${x(t).toFixed(2)}" y="${M.top + ih + 20}" text-anchor="middle">${t + 1}</text>
      `).join('')}

      <text class="axis-title" x="${M.left + iw / 2}" y="${H - 6}" text-anchor="middle">Generación</text>
      <text class="axis-title" transform="translate(14 ${M.top + ih / 2}) rotate(-90)" text-anchor="middle">Mejor fitness</text>

      <path class="series-area" d="${area}"/>
      <path class="series-line" d="${line}"/>
      <circle class="end-dot" cx="${x(lastI).toFixed(2)}" cy="${y(lastV).toFixed(2)}" r="4.5"/>
      <text class="point-label" x="${(x(lastI) - 8).toFixed(2)}"
            y="${Math.max(y(lastV) - 12, 14).toFixed(2)}" text-anchor="end">${lastV}</text>

      <g id="hover-layer" opacity="0">
        <line class="hover-line" id="hover-line" y1="${M.top}" y2="${M.top + ih}"/>
        <circle class="hover-dot" id="hover-dot" r="5"/>
      </g>
      <rect id="hover-hit" x="${M.left}" y="${M.top}" width="${iw}" height="${ih}" fill="transparent"/>
    </svg>
    <div class="tooltip" id="tooltip"></div>
  `;

  chartState = { history, x, y, M, iw, W };
  bindHover();

  $('chart-note').textContent = history[lastI] === 0
    ? `Convergió a 0 ataques en ${history.length} generaciones.`
    : `Mejor valor alcanzado: ${Math.max(...history)} (${-Math.max(...history)} ataques) en ${history.length} generaciones.`;
}

function bindHover() {
  const svg     = chartEl.querySelector('svg');
  const hit     = $('hover-hit');
  const layer   = $('hover-layer');
  const hLine   = $('hover-line');
  const hDot    = $('hover-dot');
  const tooltip = $('tooltip');

  const move = (evt) => {
    const { history, x, y, M, iw, W } = chartState;
    const box = svg.getBoundingClientRect();
    const px  = ((evt.clientX - box.left) / box.width) * W;
    const i   = Math.round(((px - M.left) / iw) * (history.length - 1));
    const idx = Math.max(0, Math.min(history.length - 1, i));
    const v   = history[idx];

    layer.setAttribute('opacity', '1');
    hLine.setAttribute('x1', x(idx)); hLine.setAttribute('x2', x(idx));
    hDot.setAttribute('cx', x(idx));  hDot.setAttribute('cy', y(v));

    tooltip.style.opacity = '1';
    tooltip.style.left = `${(x(idx) / W) * 100}%`;
    tooltip.style.top  = `${(y(v) / 320) * 100}%`;
    tooltip.innerHTML  = `Gen <strong>${idx + 1}</strong> · fitness <strong>${v}</strong> · <strong>${-v}</strong> ataques`;
  };

  hit.addEventListener('mousemove', move);
  hit.addEventListener('click', (evt) => {
    move(evt);
    const { history, M, iw, W } = chartState;
    const box = svg.getBoundingClientRect();
    const px  = ((evt.clientX - box.left) / box.width) * W;
    const idx = Math.max(0, Math.min(history.length - 1,
      Math.round(((px - M.left) / iw) * (history.length - 1))));
    stopAnimation();
    scrub.value = String(idx);
    showGeneration(idx);
  });
  hit.addEventListener('mouseleave', () => {
    layer.setAttribute('opacity', '0');
    tooltip.style.opacity = '0';
  });
}

function niceTicks(min, max, count) {
  if (max === min) return [min];
  const raw  = (max - min) / Math.max(1, count);
  const mag  = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 5, 10].map((m) => m * mag).find((s) => s >= raw) || mag * 10;
  const out  = [];
  for (let t = Math.ceil(min / step) * step; t <= max + 1e-9; t += step) out.push(Math.round(t));
  if (out[out.length - 1] !== max) out.push(max);
  return [...new Set(out)];
}

/* ---------------------------------------------------------
   Tabla de datos
   --------------------------------------------------------- */
function fillTable(history) {
  const body = document.querySelector('#data-table tbody');
  body.innerHTML = history
    .map((v, i) => `<tr><td>${i + 1}</td><td>${v}</td><td>${-v}</td></tr>`)
    .join('');
}
