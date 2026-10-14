const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const cl = x => Math.max(0, Math.min(1, x));
const P = (t, a, d) => cl((t - a) / d);
const eo = x => 1 - Math.pow(1 - x, 4);
const eio = x => x < .5 ? 8 * x * x * x * x : 1 - Math.pow(-2 * x + 2, 4) / 2;
const back = x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const lerp = (a, b, x) => a + (b - a) * x;
function st(el, o) { if (typeof el === 'string') el = $(el); if (el) Object.assign(el.style, o); }
// masked line reveal: lines under sel rise in at a (stagger s) and leave at o
function lines(sel, t, a, o, s = .25) {
  $$(sel + ' .ln > *').forEach((el, i) => { const k = eo(P(t, a + i * s, .45)); const x = eio(P(t, o, .35)); st(el, { display: 'inline-block', transform: `translateY(${(1 - k) * 110 - x * 110}%)` }); });
}
function drawPath(el, t, a, d) { el = typeof el === 'string' ? $(el) : el; const L = el.getTotalLength(); st(el, { strokeDasharray: L, strokeDashoffset: L * (1 - eio(P(t, a, d))) }); }
function bg(t, dur) {
  st('#grid', { opacity: .18 * eo(P(t, .1, 1.0)), backgroundPosition: `0 ${-t * 14}px` });
  st('#glow', { opacity: .6 + .4 * Math.sin(t * 1.3), transform: `translateY(${Math.sin(t * .5) * 60}px)` });
  st('#progi', { width: (cl(t / dur) * 100) + '%' });
}
