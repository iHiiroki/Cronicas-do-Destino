
// ============================================================
// -- dice.js: Animações de dados e lógica de rolagem
// -- Cada dado tem SVG único e correto para seu tipo:
// --   d4  → triângulo equilátero
// --   d6  → quadrado (cubo)
// --   d8  → losango (octaedro)
// --   d10 → pentagrama irregular
// --   d12 → pentágono (dodecaedro)
// --   d20 → triângulo hexagonal (icosaedro)
// --   d100→ círculo estilizado
// ============================================================

// ==========================================
// -- DEFINIÇÕES DOS SVGs DE CADA DADO
// -- Formas geometricamente corretas para cada poliedro
// ==========================================
const DICE_SVGS = {
  4: {
    // -- d4: Triângulo equilátero (Tetraedro) — CORRIGIDO
    label: 'd4',
    color: '#34d399',  // -- verde esmeralda
    shadow: 'rgba(52,211,153,0.4)',
    svg: (size = 140) => {
      const cx = size / 2, cy = size / 2, r = size * 0.42;
      // -- Vértices do triângulo equilátero
      const pts = [
        [cx, cy - r],                                      // topo
        [cx - r * Math.sin(Math.PI/3), cy + r * Math.cos(Math.PI/3)],  // esq-baixo
        [cx + r * Math.sin(Math.PI/3), cy + r * Math.cos(Math.PI/3)],  // dir-baixo
      ];
      const pts2 = pts.map(([x,y]) => `${x},${y}`).join(' ');
      // -- Linhas internas (arestas do tetraedro)
      const mx = (pts[1][0]+pts[2][0])/2, my = (pts[1][1]+pts[2][1])/2;
      return `
        <defs>
          <linearGradient id="g4" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%"   stop-color="#059669"/>
            <stop offset="100%" stop-color="#34d399"/>
          </linearGradient>
          <filter id="f4">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feFlood flood-color="rgba(52,211,153,0.5)" result="color"/>
            <feComposite in="color" in2="blur" operator="in" result="glow"/>
            <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <polygon points="${pts2}" fill="url(#g4)" stroke="#6ee7b7" stroke-width="2.5"
                 filter="url(#f4)" opacity="0.95"/>
        <!-- Linhas internas do tetraedro -->
        <line x1="${pts[0][0]}" y1="${pts[0][1]}" x2="${mx}" y2="${my}"
              stroke="#6ee7b7" stroke-width="1.5" opacity="0.5"/>
        <text x="${cx}" y="${cy + 8}" text-anchor="middle" fill="white"
              font-family="Cinzel,serif" font-size="${size * 0.2}" font-weight="700">4</text>
      `;
    },
  },

  6: {
    // -- d6: Quadrado com linhas de perspectiva (Cubo)
    label: 'd6',
    color: '#a78bfa',  // -- roxo
    shadow: 'rgba(167,139,250,0.4)',
    svg: (size = 140) => {
      const m = size * 0.12, s = size - m*2;
      const x = m, y = m;
      return `
        <defs>
          <linearGradient id="g6" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%"   stop-color="#6d28d9"/>
            <stop offset="100%" stop-color="#a78bfa"/>
          </linearGradient>
          <filter id="f6">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feFlood flood-color="rgba(139,92,246,0.5)" result="color"/>
            <feComposite in="color" in2="blur" operator="in" result="glow"/>
            <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <!-- Face frontal -->
        <rect x="${x}" y="${y}" width="${s}" height="${s}" rx="12"
              fill="url(#g6)" stroke="#c4b5fd" stroke-width="2.5" filter="url(#f6)"/>
        <!-- Pontos do dado -->
        ${diceDots(size, 6)}
      `;
    },
  },

  8: {
    // -- d8: Losango (Octaedro — visão de cima)
    label: 'd8',
    color: '#f59e0b',  // -- dourado
    shadow: 'rgba(245,158,11,0.4)',
    svg: (size = 140) => {
      const cx = size/2, cy = size/2, rx = size*0.44, ry = size*0.44;
      const pts = `${cx},${cy-ry} ${cx+rx},${cy} ${cx},${cy+ry} ${cx-rx},${cy}`;
      return `
        <defs>
          <linearGradient id="g8" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%"   stop-color="#b45309"/>
            <stop offset="100%" stop-color="#fbbf24"/>
          </linearGradient>
          <filter id="f8">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feFlood flood-color="rgba(245,158,11,0.5)" result="color"/>
            <feComposite in="color" in2="blur" operator="in" result="glow"/>
            <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <polygon points="${pts}" fill="url(#g8)" stroke="#fde68a" stroke-width="2.5"
                 filter="url(#f8)"/>
        <!-- Linhas de arestas internas do octaedro -->
        <line x1="${cx}" y1="${cy-ry}" x2="${cx}" y2="${cy+ry}"
              stroke="#fde68a" stroke-width="1.5" opacity="0.5"/>
        <line x1="${cx-rx}" y1="${cy}" x2="${cx+rx}" y2="${cy}"
              stroke="#fde68a" stroke-width="1.5" opacity="0.5"/>
        <text x="${cx}" y="${cy+8}" text-anchor="middle" fill="white"
              font-family="Cinzel,serif" font-size="${size*0.22}" font-weight="700">8</text>
      `;
    },
  },

  10: {
    // -- d10: Pentagono côncavo (visão do decaedro)
    label: 'd10',
    color: '#06b6d4',  // -- ciano
    shadow: 'rgba(6,182,212,0.4)',
    svg: (size = 140) => {
      const cx = size/2, cy = size/2, r = size*0.42;
      // -- Forma de d10: 5 pontos externos + 5 internos (estrela)
      const pts = [];
      for (let i = 0; i < 10; i++) {
        const angle = (i * Math.PI / 5) - Math.PI/2;
        const radius = i % 2 === 0 ? r : r * 0.5;
        pts.push([cx + radius*Math.cos(angle), cy + radius*Math.sin(angle)]);
      }
      const pStr = pts.map(([x,y]) => `${x},${y}`).join(' ');
      return `
        <defs>
          <linearGradient id="g10" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%"   stop-color="#0891b2"/>
            <stop offset="100%" stop-color="#22d3ee"/>
          </linearGradient>
          <filter id="f10">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feFlood flood-color="rgba(6,182,212,0.5)" result="color"/>
            <feComposite in="color" in2="blur" operator="in" result="glow"/>
            <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <polygon points="${pStr}" fill="url(#g10)" stroke="#67e8f9" stroke-width="2"
                 filter="url(#f10)"/>
        <text x="${cx}" y="${cy+8}" text-anchor="middle" fill="white"
              font-family="Cinzel,serif" font-size="${size*0.2}" font-weight="700">10</text>
      `;
    },
  },

  12: {
    // -- d12: Pentágono regular (face do dodecaedro)
    label: 'd12',
    color: '#f97316',  // -- laranja
    shadow: 'rgba(249,115,22,0.4)',
    svg: (size = 140) => {
      const cx = size/2, cy = size/2, r = size*0.43;
      // -- Pentágono regular: 5 vértices
      const pts = [];
      for (let i = 0; i < 5; i++) {
        const angle = (i * 2*Math.PI / 5) - Math.PI/2;
        pts.push([cx + r*Math.cos(angle), cy + r*Math.sin(angle)]);
      }
      const pStr = pts.map(([x,y]) => `${x},${y}`).join(' ');
      // -- Linhas internas (arestas visíveis do dodecaedro)
      const innerLines = pts.map((p, i) => {
        const next = pts[(i+2) % 5];
        return `<line x1="${p[0]}" y1="${p[1]}" x2="${next[0]}" y2="${next[1]}"
                      stroke="#fdba74" stroke-width="1.2" opacity="0.4"/>`;
      }).join('');
      return `
        <defs>
          <linearGradient id="g12" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%"   stop-color="#c2410c"/>
            <stop offset="100%" stop-color="#fb923c"/>
          </linearGradient>
          <filter id="f12">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feFlood flood-color="rgba(249,115,22,0.5)" result="color"/>
            <feComposite in="color" in2="blur" operator="in" result="glow"/>
            <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <polygon points="${pStr}" fill="url(#g12)" stroke="#fdba74" stroke-width="2.5"
                 filter="url(#f12)"/>
        ${innerLines}
        <text x="${cx}" y="${cy+8}" text-anchor="middle" fill="white"
              font-family="Cinzel,serif" font-size="${size*0.2}" font-weight="700">12</text>
      `;
    },
  },

  20: {
    // -- d20: CORRIGIDO — Triângulo com subdivisões (face do icosaedro, NÃO d4)
    // --       O d20 tem triângulos menores internos visíveis
    label: 'd20',
    color: '#ec4899',  // -- rosa/magenta
    shadow: 'rgba(236,72,153,0.4)',
    svg: (size = 140) => {
      const cx = size/2, cy = size/2, r = size*0.44;
      // -- Triângulo principal (face visível do icosaedro)
      const pts = [
        [cx, cy - r],
        [cx - r * Math.sin(Math.PI/3), cy + r * 0.5],
        [cx + r * Math.sin(Math.PI/3), cy + r * 0.5],
      ];
      const pStr = pts.map(([x,y]) => `${x},${y}`).join(' ');

      // -- Ponto médio de cada aresta (para subdivir em 4 triângulos menores)
      const m01 = [(pts[0][0]+pts[1][0])/2, (pts[0][1]+pts[1][1])/2];
      const m12 = [(pts[1][0]+pts[2][0])/2, (pts[1][1]+pts[2][1])/2];
      const m02 = [(pts[0][0]+pts[2][0])/2, (pts[0][1]+pts[2][1])/2];

      // -- O "20" fica ao centro, mas com visual de subdivição de icosaedro
      return `
        <defs>
          <linearGradient id="g20" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%"   stop-color="#be185d"/>
            <stop offset="100%" stop-color="#f472b6"/>
          </linearGradient>
          <radialGradient id="gr20" cx="40%" cy="35%" r="60%">
            <stop offset="0%"   stop-color="#f9a8d4" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#be185d" stop-opacity="0"/>
          </radialGradient>
          <filter id="f20">
            <feGaussianBlur stdDeviation="5" result="blur"/>
            <feFlood flood-color="rgba(236,72,153,0.6)" result="color"/>
            <feComposite in="color" in2="blur" operator="in" result="glow"/>
            <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <!-- Face principal -->
        <polygon points="${pStr}" fill="url(#g20)" stroke="#f9a8d4" stroke-width="2.5"
                 filter="url(#f20)"/>
        <!-- Overlay de brilho -->
        <polygon points="${pStr}" fill="url(#gr20)"/>
        <!-- Linhas de subdivisão do icosaedro (distingue do d4) -->
        <line x1="${m01[0]}" y1="${m01[1]}" x2="${m12[0]}" y2="${m12[1]}"
              stroke="#f9a8d4" stroke-width="1.5" opacity="0.6"/>
        <line x1="${m12[0]}" y1="${m12[1]}" x2="${m02[0]}" y2="${m02[1]}"
              stroke="#f9a8d4" stroke-width="1.5" opacity="0.6"/>
        <line x1="${m01[0]}" y1="${m01[1]}" x2="${m02[0]}" y2="${m02[1]}"
              stroke="#f9a8d4" stroke-width="1.5" opacity="0.6"/>
        <!-- Número "20" no centro -->
        <text x="${cx}" y="${cy + r*0.15 + 8}" text-anchor="middle" fill="white"
              font-family="Cinzel,serif" font-size="${size*0.21}" font-weight="900"
              text-decoration="underline">20</text>
      `;
    },
  },

  100: {
    // -- d100: Círculo estilizado (percentil)
    label: 'd100',
    color: '#94a3b8',
    shadow: 'rgba(148,163,184,0.4)',
    svg: (size = 140) => {
      const cx = size/2, cy = size/2, r = size*0.42;
      // -- Círculos concêntricos para visual de moeda percentual
      return `
        <defs>
          <radialGradient id="g100" cx="35%" cy="35%" r="65%">
            <stop offset="0%"   stop-color="#64748b"/>
            <stop offset="100%" stop-color="#1e293b"/>
          </radialGradient>
          <filter id="f100">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feFlood flood-color="rgba(148,163,184,0.4)" result="color"/>
            <feComposite in="color" in2="blur" operator="in" result="glow"/>
            <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#g100)"
                stroke="#94a3b8" stroke-width="2.5" filter="url(#f100)"/>
        <circle cx="${cx}" cy="${cy}" r="${r*0.7}" fill="none"
                stroke="#64748b" stroke-width="1.5" opacity="0.5"/>
        <text x="${cx}" y="${cy+9}" text-anchor="middle" fill="white"
              font-family="Cinzel,serif" font-size="${size*0.17}" font-weight="700">100</text>
      `;
    },
  },
};

// ==========================================
// -- UTILITÁRIO: Pontos do d6
// ==========================================
function diceDots(size, result) {
  const r = size * 0.055;
  const cx = size/2, cy = size/2;
  const gap = size * 0.25;
  const positions = {
    1: [[cx, cy]],
    2: [[cx-gap, cy], [cx+gap, cy]],
    3: [[cx-gap, cy-gap], [cx, cy], [cx+gap, cy+gap]],
    4: [[cx-gap,cy-gap],[cx+gap,cy-gap],[cx-gap,cy+gap],[cx+gap,cy+gap]],
    5: [[cx-gap,cy-gap],[cx+gap,cy-gap],[cx,cy],[cx-gap,cy+gap],[cx+gap,cy+gap]],
    6: [[cx-gap,cy-gap],[cx+gap,cy-gap],[cx-gap,cy],[cx+gap,cy],[cx-gap,cy+gap],[cx+gap,cy+gap]],
  };
  const pos = positions[Math.min(result, 6)] || positions[1];
  return pos.map(([x,y]) =>
    `<circle cx="${x}" cy="${y}" r="${r}" fill="white" opacity="0.9"/>`
  ).join('');
}

// ==========================================
// -- ESTADO GLOBAL DA PÁGINA DE DADOS
// ==========================================
let selectedFaces  = 20;   // -- Dado selecionado atualmente
let lastResult     = null; // -- Último resultado rolado
let rollHistory    = [];   // -- Histórico local de rolagens

// ==========================================
// -- INICIALIZAÇÃO
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  renderDiceSelector();
  selectDice(20);  // -- d20 selecionado por padrão
  loadHistory();
});

// -- Renderiza os botões de seleção de dado
function renderDiceSelector() {
  const el = document.getElementById('diceSelector');
  const faces = [4, 6, 8, 10, 12, 20, 100];
  el.innerHTML = faces.map(f => {
    const d = DICE_SVGS[f];
    return `
      <button class="dice-btn" id="diceBtn${f}" onclick="selectDice(${f})" title="${d.label}">
        <span style="font-size:10px; color:${d.color}; font-weight:900; letter-spacing:1px;">${d.label.toUpperCase()}</span>
      </button>
    `;
  }).join('');
}

// -- Muda o dado selecionado e atualiza o SVG exibido
function selectDice(faces) {
  selectedFaces = faces;

  // -- Atualiza botões
  document.querySelectorAll('.dice-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById(`diceBtn${faces}`);
  if (btn) btn.classList.add('active');

  // -- Atualiza o SVG do dado
  const d = DICE_SVGS[faces];
  if (!d) return;
  const svgEl = document.getElementById('currentDiceSvg');
  svgEl.innerHTML = d.svg(140);

  // -- Reseta estado de animação
  const wrapper = document.getElementById('diceSvgWrapper');
  wrapper.className = 'dice-svg-wrapper';
  wrapper.style.filter = `drop-shadow(0 0 12px ${d.shadow})`;

  // -- Reseta resultado
  document.getElementById('diceResult').className = 'dice-result-display';
  document.getElementById('diceResult').textContent = '—';
  document.getElementById('diceLabel').textContent = `Clique em Rolar Dado para lançar o ${d.label}`;
  document.getElementById('diceBanner').innerHTML = '';
}

// ==========================================
// -- ROLAGEM DO DADO ATUAL
// ==========================================
async function rollCurrentDice() {
  const modifier = parseInt(document.getElementById('modifierInput').value) || 0;
  const label    = document.getElementById('labelInput').value.trim();
  const notation = modifier >= 0
    ? `1d${selectedFaces}+${modifier}`
    : `1d${selectedFaces}${modifier}`;

  await performRoll(notation.replace('+0', ''), label || `Rolagem de d${selectedFaces}`);
}

// -- Rola notação personalizada
async function rollCustom() {
  const notation = document.getElementById('customNotation').value.trim();
  if (!notation) {
    toast.warning('Digite uma notação como 3d8+2.');
    return;
  }
  await performRoll(notation, notation);
}

// -- Rolagem rápida por botão
async function quickRoll(notation, label) {
  // -- Seleciona o dado correto se possível
  const match = notation.match(/d(\d+)/i);
  if (match) {
    const f = parseInt(match[1]);
    if (DICE_SVGS[f]) selectDice(f);
  }
  await performRoll(notation, label);
}

// ==========================================
// -- EXECUTA A ROLAGEM (chama API e anima)
// ==========================================
async function performRoll(notation, label) {
  const btn     = document.getElementById('rollBtn');
  const wrapper = document.getElementById('diceSvgWrapper');
  const resultEl = document.getElementById('diceResult');
  const labelEl  = document.getElementById('diceLabel');
  const bannerEl = document.getElementById('diceBanner');

  // -- Inicia animação de tremida
  btn.disabled = true;
  wrapper.className = 'dice-svg-wrapper rolling';

  try {
    const result = await api.post('/api/dice/roll', { notation, label });
    lastResult   = result;

    // -- Aguarda a animação de tremida terminar (800ms)
    await new Promise(r => setTimeout(r, 800));

    // -- Exibe o resultado
    const isCrit = result.critical;
    const isFail = result.criticalFail;

    resultEl.textContent = result.total;
    resultEl.className   = 'dice-result-display' + (isCrit ? ' crit' : isFail ? ' fail' : '');

    // -- Classe de animação de brilho pós-rolagem
    if (isCrit) {
      wrapper.className  = 'dice-svg-wrapper rolled-crit';
      bannerEl.innerHTML = `<span class="dice-crit-banner crit">✨ ACERTO CRÍTICO! ✨</span>`;
    } else if (isFail) {
      wrapper.className  = 'dice-svg-wrapper rolled-fail';
      bannerEl.innerHTML = `<span class="dice-crit-banner fail">💀 FALHA CRÍTICA</span>`;
    } else {
      wrapper.className  = 'dice-svg-wrapper rolled-normal';
      bannerEl.innerHTML = '';
    }

    // -- Rótulo com detalhes
    const rollDetails = result.rolls.length > 1
      ? `[${result.rolls.join(' + ')}]${result.modifier ? (result.modifier > 0 ? ' +'+result.modifier : ' '+result.modifier) : ''} = `
      : '';
    labelEl.textContent = `${label} — ${rollDetails}${result.total}`;

    // -- Atualiza SVG do d6 com o número de pontos real (apenas para d6)
    if (selectedFaces === 6 && result.rolls.length === 1) {
      const svgEl = document.getElementById('currentDiceSvg');
      const d = DICE_SVGS[6];
      const val = Math.min(result.rolls[0], 6);
      svgEl.innerHTML = d.svg(140).replace(diceDots(140, 6), diceDots(140, val));
    }

    // -- Adiciona ao histórico local
    rollHistory.unshift(result);
    if (rollHistory.length > 20) rollHistory.pop();
    renderHistory();

  } catch(e) {
    toast.error(e.message);
    wrapper.className = 'dice-svg-wrapper';
  } finally {
    btn.disabled = false;
  }
}

// ==========================================
// -- HISTÓRICO DE ROLAGENS
// ==========================================
async function loadHistory() {
  try {
    rollHistory = await api.get('/api/dice/history');
    renderHistory();
  } catch {}
}

function renderHistory() {
  const el = document.getElementById('rollHistory');
  if (rollHistory.length === 0) {
    el.innerHTML = `
      <div class="empty-state" style="padding:32px;">
        <div class="empty-state-icon">🎲</div>
        <p>Nenhuma rolagem ainda.</p>
      </div>`;
    return;
  }

  el.innerHTML = `<div class="history-list">` + rollHistory.slice(0, 15).map(r => {
    const cls    = r.critical ? 'crit' : r.criticalFail ? 'fail' : '';
    const badge  = r.critical ? ' ⭐' : r.criticalFail ? ' 💀' : '';
    return `
      <div class="history-item">
        <span class="roll-val ${cls}">${r.total}${badge}</span>
        <div style="flex:1; min-width:0;">
          <div style="font-size:13px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
            ${r.label}
          </div>
          <div style="font-size:11px; color:var(--text-faint);">
            ${r.dice} — [${r.rolls.join(', ')}]${r.modifier ? ` ${r.modifier > 0 ? '+':''}${r.modifier}` : ''}
          </div>
        </div>
        <span style="font-size:11px; color:var(--text-faint); white-space:nowrap;">
          ${new Date(r.timestamp).toLocaleTimeString('pt-BR', {hour:'2-digit',minute:'2-digit'})}
        </span>
      </div>
    `;
  }).join('') + `</div>`;
}

async function clearHistory() {
  try {
    await api.del('/api/dice/history');
    rollHistory = [];
    renderHistory();
    toast.success('Histórico limpo!');
  } catch(e) {
    toast.error(e.message);
  }
}
