/* =====================================================================
   Atelier Vernaz — shared behaviour (all pages)
   ===================================================================== */
(() => {
  const root = document.documentElement;
  const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const SVGNS = 'http://www.w3.org/2000/svg';
  const TAU = Math.PI * 2;

  /* ---------- Mobile menu ---------- */
  const btn = document.querySelector('.menu-btn');
  const panel = document.getElementById('menu');
  if (btn && panel) {
    const setOpen = (open) => {
      root.classList.toggle('menu-open', open);
      btn.setAttribute('aria-expanded', String(open));
      btn.querySelector('span').textContent = open ? 'Fermer' : 'Menu';
      panel.toggleAttribute('inert', !open);
      if (open) panel.querySelector('a')?.focus();
    };
    panel.setAttribute('inert', '');
    btn.addEventListener('click', () => setOpen(!root.classList.contains('menu-open')));
    panel.addEventListener('click', (e) => { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && root.classList.contains('menu-open')) { setOpen(false); btn.focus(); }
    });
  }

  /* ---------- Solid nav after scrolling (inner pages) ---------- */
  const nav = document.querySelector('.nav');
  if (nav && !document.body.classList.contains('home')) {
    const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 40);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---------- Reveal on scroll ---------- */
  const revealEls = document.querySelectorAll('[data-reveal]');
  if (revealEls.length) {
    if (!('IntersectionObserver' in window) || REDUCED) {
      revealEls.forEach((el) => el.classList.add('is-in'));
    } else {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((en) => {
          if (!en.isIntersecting) return;
          const delay = +(en.target.dataset.reveal || 0);
          setTimeout(() => en.target.classList.add('is-in'), delay);
          io.unobserve(en.target);
        });
      }, { rootMargin: '0px 0px -12% 0px' });
      revealEls.forEach((el) => io.observe(el));
    }
  }

  /* ---------- Procedural SVG (gears, craft drawings) ---------- */
  const svg = (vb = '0 0 100 100') => {
    const s = document.createElementNS(SVGNS, 'svg');
    s.setAttribute('viewBox', vb);
    s.setAttribute('fill', 'none');
    s.setAttribute('aria-hidden', 'true');
    return s;
  };
  const el = (name, attrs, parent) => {
    const n = document.createElementNS(SVGNS, name);
    Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v));
    parent.appendChild(n);
    return n;
  };
  const f = (n) => n.toFixed(2);

  function gearPath(cx, cy, R, teeth, depth) {
    const rr = R - depth, step = TAU / teeth;
    let d = '';
    for (let i = 0; i < teeth; i++) {
      const a = i * step;
      [[rr, a], [R, a + step * .2], [R, a + step * .48], [rr, a + step * .68]].forEach(([r, ang], j) => {
        d += `${i === 0 && j === 0 ? 'M' : 'L'}${f(cx + Math.cos(ang) * r)} ${f(cy + Math.sin(ang) * r)}`;
      });
    }
    return d + 'Z';
  }

  function drawGear(host, teeth, spokes) {
    const s = svg('0 0 200 200');
    const stroke = { stroke: 'rgba(255,237,215,.32)', 'stroke-width': .35 };
    el('path', { d: gearPath(100, 100, 98, teeth, 5), ...stroke }, s);
    el('circle', { cx: 100, cy: 100, r: 76, ...stroke }, s);
    el('circle', { cx: 100, cy: 100, r: 18, ...stroke }, s);
    el('circle', { cx: 100, cy: 100, r: 6, ...stroke }, s);
    for (let k = 0; k < spokes; k++) {
      const a = k / spokes * TAU, w = .09;
      const p = (r, ang) => `${f(100 + Math.cos(ang) * r)} ${f(100 + Math.sin(ang) * r)}`;
      el('path', { d: `M${p(18, a - w * 2)}L${p(76, a - w / 2)}M${p(18, a + w * 2)}L${p(76, a + w / 2)}`, ...stroke }, s);
    }
    for (let k = 0; k < 120; k++) {
      const a = k / 120 * TAU;
      el('line', { x1: f(100 + Math.cos(a) * 80), y1: f(100 + Math.sin(a) * 80), x2: f(100 + Math.cos(a) * (k % 10 ? 82 : 86)), y2: f(100 + Math.sin(a) * (k % 10 ? 82 : 86)), ...stroke }, s);
    }
    host.appendChild(s);
  }
  document.querySelectorAll('[data-gear]').forEach((host) => {
    drawGear(host, 96, 6);
    drawGear(host, 40, 5);
  });

  const ART = {
    // Anglage: a bridge outline with its hand-bevelled inner edge
    anglage(s) {
      const d = 'M14 62 C14 40 30 30 50 30 L74 30 C84 30 88 36 88 44 C88 52 82 56 74 56 L58 56 C52 56 50 60 50 66 L50 74 C50 82 44 86 36 86 L28 86 C20 86 14 80 14 72 Z';
      el('path', { d, stroke: 'var(--gold)', 'stroke-width': 1.2 }, s);
      const inner = el('path', { d, stroke: 'rgba(255,237,215,.45)', 'stroke-width': .8 }, s);
      inner.setAttribute('transform', 'translate(50 58) scale(.9) translate(-50 -58)');
      [[30, 44], [76, 43], [32, 72]].forEach(([x, y]) => {
        el('circle', { cx: x, cy: y, r: 3.2, stroke: 'var(--gold)', 'stroke-width': 1 }, s);
        el('line', { x1: x - 2.2, y1: y, x2: x + 2.2, y2: y, stroke: 'var(--gold)', 'stroke-width': 1 }, s);
      });
    },
    // Guillochage: rose-engine pattern of offset circles
    guillochage(s) {
      for (let i = 0; i < 48; i++) {
        const a = i / 48 * TAU;
        el('circle', { cx: f(50 + Math.cos(a) * 9), cy: f(50 + Math.sin(a) * 9), r: 30, stroke: i % 2 ? 'rgba(243,207,159,.55)' : 'rgba(255,237,215,.25)', 'stroke-width': .6 }, s);
      }
      el('circle', { cx: 50, cy: 50, r: 44, stroke: 'var(--gold)', 'stroke-width': 1.2 }, s);
    },
    // Émail grand feu: dial with minute track and sunray
    email(s) {
      el('circle', { cx: 50, cy: 50, r: 44, stroke: 'var(--gold)', 'stroke-width': 1.2 }, s);
      for (let i = 0; i < 60; i++) {
        const a = i / 60 * TAU, five = i % 5 === 0;
        el('line', { x1: f(50 + Math.sin(a) * 40), y1: f(50 - Math.cos(a) * 40), x2: f(50 + Math.sin(a) * (five ? 34 : 37.5)), y2: f(50 - Math.cos(a) * (five ? 34 : 37.5)), stroke: five ? 'var(--gold)' : 'rgba(255,237,215,.5)', 'stroke-width': five ? 1.4 : .6 }, s);
      }
      for (let i = 0; i < 72; i++) {
        const a = i / 72 * TAU;
        el('line', { x1: 50, y1: 50, x2: f(50 + Math.cos(a) * 30), y2: f(50 + Math.sin(a) * 30), stroke: 'rgba(255,237,215,.08)', 'stroke-width': .5 }, s);
      }
      el('line', { x1: 50, y1: 50, x2: 50, y2: 22, stroke: 'var(--cream)', 'stroke-width': 1.4 }, s);
      el('line', { x1: 50, y1: 50, x2: 68, y2: 58, stroke: 'var(--cream)', 'stroke-width': 1.8 }, s);
      el('circle', { cx: 50, cy: 50, r: 2, fill: 'var(--gold)' }, s);
    },
    // Perlage: overlapping circular grains
    perlage(s) {
      for (let row = 0; row < 7; row++) {
        for (let col = 0; col < 7; col++) {
          const x = 14 + col * 12 + (row % 2) * 6, y = 14 + row * 12;
          if (Math.hypot(x - 50, y - 50) > 40) continue;
          el('circle', { cx: x, cy: y, r: 8, stroke: 'rgba(255,237,215,.4)', 'stroke-width': .6 }, s);
          el('circle', { cx: x, cy: y, r: 3.5, stroke: 'rgba(243,207,159,.6)', 'stroke-width': .6 }, s);
        }
      }
      el('circle', { cx: 50, cy: 50, r: 44, stroke: 'var(--gold)', 'stroke-width': 1.2 }, s);
    },
  };
  document.querySelectorAll('[data-art]').forEach((host) => {
    const s = svg();
    ART[host.dataset.art]?.(s);
    host.appendChild(s);
  });

  /* ---------- Calendly, loaded only after consent ---------- */
  const cal = document.querySelector('[data-calendly]');
  if (cal) {
    const KEY = 'vernaz-calendly-consent';
    const store = {
      get() { try { return localStorage.getItem(KEY) === '1'; } catch { return false; } },
      set(v) { try { v ? localStorage.setItem(KEY, '1') : localStorage.removeItem(KEY); } catch { /* private mode */ } },
    };
    const params = new URLSearchParams({
      hide_gdpr_banner: '1',
      background_color: '170d07',
      text_color: 'ffedd7',
      primary_color: 'f3cf9f',
    });
    const load = () => {
      store.set(true);
      const box = cal.querySelector('.cal-embed');
      box.innerHTML = '';
      const w = document.createElement('div');
      w.className = 'calendly-inline-widget';
      w.dataset.url = `${cal.dataset.calendly}?${params}`;
      w.dataset.resize = 'true';
      box.appendChild(w);
      const sc = document.createElement('script');
      sc.src = 'https://assets.calendly.com/assets/external/widget.js';
      sc.async = true;
      box.appendChild(sc);
      cal.classList.add('is-loaded');
    };
    cal.querySelector('[data-cal-load]')?.addEventListener('click', load);
    cal.querySelector('[data-cal-forget]')?.addEventListener('click', () => {
      store.set(false);
      window.location.reload();
    });
    if (store.get()) load();
  }
})();
