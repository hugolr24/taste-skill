// Builds nexora-presentation.pptx: dark Nexora theme, looping 3D clips, Morph-ready shared objects.
// The animation plan (entrance effects per slide) is written to anim-plan.json for post.py.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const sharp = require("sharp");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const fa = require("react-icons/fa6");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const MEDIA = path.join(__dirname, "media");
const OUT = path.join(__dirname, process.env.OUT_NAME || "nexora-presentation.pptx");

const THEME = {
  name: "Nexora",
  headFontFace: "Arial Black",
  bodyFontFace: "Arial",
  colors: {
    dk1: "0D1015", lt1: "EDF0F3", dk2: "151A21", lt2: "8E97A3",
    accent1: "F4B23E", accent2: "A9D6E5", accent3: "1D232C", accent4: "2A313B", accent5: "E5574B", accent6: "C98A10",
    hlink: "F4B23E", folHlink: "A9D6E5",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "Nexora Web";
pres.author = "Nexora";
pres.company = "Nexora";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

// ---------------------------------------------------------------- assets
async function icon(name, color = HEX.accent1, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fa[name], { color: "#" + color, size }));
  const buf = await sharp(Buffer.from(svg)).resize(size, size).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}
async function background() {
  const W = 1920, H = 1080, lines = [];
  for (let x = 0; x <= W; x += 96) lines.push(`<line x1="${x}" y1="0" x2="${x}" y2="${H}"/>`);
  for (let y = 0; y <= H; y += 96) lines.push(`<line x1="0" y1="${y}" x2="${W}" y2="${y}"/>`);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
    <defs><radialGradient id="g" cx="78%" cy="45%" r="60%"><stop offset="0" stop-color="#F4B23E" stop-opacity=".10"/><stop offset="1" stop-color="#0D1015" stop-opacity="0"/></radialGradient>
    <linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".75" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <mask id="m"><rect width="${W}" height="${H}" fill="url(#f)"/></mask></defs>
    <rect width="${W}" height="${H}" fill="#0D1015"/>
    <g stroke="#2A313B" stroke-width="1" opacity=".55" mask="url(#m)">${lines.join("")}</g>
    <rect width="${W}" height="${H}" fill="url(#g)"/></svg>`;
  return "image/png;base64," + (await sharp(Buffer.from(svg)).png().toBuffer()).toString("base64");
}
const poster = name => "data:image/jpeg;base64," + fs.readFileSync(path.join(MEDIA, name + ".jpg")).toString("base64");

// ---------------------------------------------------------------- shared Morph objects
// Objects whose names start with "!!" morph from slide to slide in PowerPoint.
const FRAME = { x: 8.55, y: 0.45, w: 3.94, h: 7.0 }; // 9:16 panel on the right
function frame(slide, f = FRAME, rr = 0.25) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { ...f, rectRadius: rr, fill: { color: C.text2 }, line: { color: C.accent1, width: 1.25, transparency: 40 }, objectName: "!!frame" });
}
function glows(slide, a, b) {
  slide.addShape(pres.shapes.OVAL, { ...a, fill: { color: C.accent1, transparency: 94 }, line: { type: "none" }, objectName: "!!glow1" });
  slide.addShape(pres.shapes.OVAL, { ...b, fill: { color: C.accent2, transparency: 96 }, line: { type: "none" }, objectName: "!!glow2" });
}
function logo(slide, opt) { slide.addImage({ path: path.join(MEDIA, "nmark.png"), ...opt, objectName: "!!nmark", altText: "Logo Nexora" }); }
function video(slide, clip, f = FRAME) {
  const inset = 0.08;
  slide.addMedia({ type: "video", path: path.join(MEDIA, clip + ".mp4"), cover: poster(clip), x: f.x + inset, y: f.y + inset, w: f.w - 2 * inset, h: f.h - 2 * inset, objectName: "Clip 3D" });
}

const plan = []; // [{ slide, anims: [[objectName, effect, delayMs]], video: bool }]
function anims(list, hasVideo = true) { plan.push({ anims: list, video: hasVideo }); }

// ---------------------------------------------------------------- layouts
async function main() {
  const BG = await background();
  pres.defineSlideMaster({
    title: "NX_CONTENT",
    background: { data: BG },
    objects: [
      { text: { text: "NEXORA", options: { x: 1.02, y: 6.85, w: 2.5, h: 0.3, fontFace: "Arial Black", fontSize: 10, color: C.accent1, charSpacing: 4, margin: 0 } } },
      { text: { text: "nexora-web.fr", options: { x: 3.2, y: 6.85, w: 3.0, h: 0.3, fontFace: "Courier New", fontSize: 10, color: C.background2, margin: 0 } } },
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.75, w: 7.6, h: 1.6, fontFace: "Arial Black", fontSize: 34, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
    ],
    slideNumber: { x: 7.4, y: 6.85, w: 0.8, h: 0.3, fontFace: "Courier New", fontSize: 10, color: C.background2, align: "right" },
  });
  pres.defineSlideMaster({ title: "NX_COVER", background: { data: BG }, objects: [] });

  const ICONS = {
    phone: await icon("FaMobileScreen"), search: await icon("FaMagnifyingGlass"), cal: await icon("FaCalendarXmark"),
    bolt: await icon("FaBolt"), tag: await icon("FaTag"), pin: await icon("FaLocationDot"), wand: await icon("FaWandMagicSparkles"),
    msg: await icon("FaCommentDots"), user: await icon("FaUserCheck"),
  };
  const kicker = (s, text, name, y = 0.45) => s.addText(text.toUpperCase(), { x: 0.6, y, w: 7.6, h: 0.3, fontFace: "Courier New", fontSize: 12, bold: true, color: C.accent1, charSpacing: 3, margin: 0, isTextBox: true, objectName: name });
  const body = (s, text, opt, name) => s.addText(text, { fontFace: "Arial", fontSize: 16, color: C.background2, margin: 0, valign: "top", isTextBox: true, ...opt, objectName: name });

  // ============ 1. Cover
  pres.addSection({ title: "Nexora" });
  let s = pres.addSlide({ masterName: "NX_COVER", sectionTitle: "Nexora" });
  glows(s, { x: 7.2, y: -1.2, w: 7, h: 7 }, { x: -2, y: 4.5, w: 6, h: 6 });
  frame(s);
  video(s, "c1-nmark");
  logo(s, { x: 0.6, y: 0.7, w: 0.9, h: 0.9 });
  s.addText("CRÉATION DE SITES WEB · CHAMBÉRY · SAVOIE", { x: 0.6, y: 2.05, w: 7.6, h: 0.3, fontFace: "Courier New", fontSize: 12, bold: true, color: C.accent1, charSpacing: 3, margin: 0, isTextBox: true, objectName: "Kicker" });
  s.addText("Nexora Web", { x: 0.6, y: 2.45, w: 7.8, h: 1.5, fontFace: "Arial Black", fontSize: 66, color: C.background1, margin: 0, isTextBox: true, objectName: "Titre" });
  s.addText([{ text: "Des sites qui font venir des clients. ", options: { color: C.background1 } }, { text: "Pour les pros de Savoie.", options: { color: C.accent1 } }], { x: 0.6, y: 4.05, w: 7.4, h: 1.0, fontFace: "Arial", fontSize: 24, bold: true, margin: 0, valign: "top", isTextBox: true, objectName: "Accroche" });
  s.addText("Présentation de l'agence · 2026", { x: 0.6, y: 6.6, w: 6, h: 0.35, fontFace: "Courier New", fontSize: 12, color: C.background2, margin: 0, isTextBox: true, objectName: "Date" });
  s.addNotes("Nexora Web : un studio de création de sites web basé à Chambéry, pour les artisans et commerces de Savoie. Le N doré à droite est notre logo : un seul trait, un N et une crête de montagne.");
  anims([["Kicker", "fadeUp", 200], ["Titre", "zoom", 300], ["Accroche", "fadeUp", 300], ["Date", "fade", 200]]);

  // ============ 2. Le constat
  pres.addSection({ title: "Le constat" });
  s = pres.addSlide({ masterName: "NX_CONTENT", sectionTitle: "Le constat" });
  glows(s, { x: 8.5, y: 3.5, w: 6, h: 6 }, { x: -1.5, y: -2, w: 5, h: 5 });
  frame(s); video(s, "c3-shatter");
  logo(s, { x: 0.6, y: 6.8, w: 0.32, h: 0.32 });
  kicker(s, "Le constat", "Kicker");
  s.addText([{ text: "Ton commerce est excellent. ", options: { color: C.background1 } }, { text: "Ton site, pas toujours", options: { color: C.accent1 } }], { placeholder: "title" });
  const pains = [["phone", "Illisible sur téléphone", "Texte minuscule, boutons trop petits : le client zoome, puis abandonne."], ["search", "Introuvable sur Google", "Pas de fiche reliée, pas de mots-clés locaux : c'est le concurrent qui sort."], ["cal", "Aucune action possible", "Pas de bouton d'appel, pas de réservation, pas de commande en ligne."]];
  pains.forEach(([ic, h, t], i) => {
    const y = 2.75 + i * 1.3;
    s.addShape(pres.shapes.OVAL, { x: 0.6, y, w: 0.7, h: 0.7, fill: { color: C.text2 }, line: { color: C.accent1, width: 1 }, objectName: `Pastille ${i + 1}` });
    s.addImage({ data: ICONS[ic], x: 0.78, y: y + 0.18, w: 0.34, h: 0.34, objectName: `Icône ${i + 1}`, altText: h });
    s.addText(h, { x: 1.55, y: y - 0.02, w: 6.4, h: 0.4, fontFace: "Arial", fontSize: 18, bold: true, color: C.background1, margin: 0, isTextBox: true, objectName: `Point ${i + 1}` });
    body(s, t, { x: 1.55, y: y + 0.4, w: 6.4, h: 0.6, fontSize: 14 }, `Détail ${i + 1}`);
  });
  s.addNotes("Le problème qu'on règle : beaucoup de commerces de Savoie font un travail remarquable, mais leur site est daté, illisible sur mobile ou introuvable. À droite, ce vieux site explose en morceaux.");
  anims([["Kicker", "fade", 0], ["Titre", "fadeUp", 100], ...[1, 2, 3].flatMap(i => [[`Pastille ${i}`, "zoom", 250], [`Icône ${i}`, "zoomWith", 0], [`Point ${i}`, "fadeUpWith", 0], [`Détail ${i}`, "fadeUpWith", 0]])]);

  // ============ 3. Qui on est
  pres.addSection({ title: "L'agence" });
  s = pres.addSlide({ masterName: "NX_CONTENT", sectionTitle: "L'agence" });
  glows(s, { x: 6.5, y: -2.5, w: 7, h: 7 }, { x: 0, y: 4, w: 5, h: 5 });
  frame(s); video(s, "c2-savoie");
  logo(s, { x: 0.6, y: 6.8, w: 0.32, h: 0.32 });
  kicker(s, "L'agence", "Kicker");
  s.addText([{ text: "Le studio web des ", options: { color: C.background1 } }, { text: "pros de Savoie", options: { color: C.accent1 } }], { placeholder: "title" });
  body(s, "Nexora conçoit des sites au niveau des grandes agences, pour les boulangers, restaurateurs, coiffeurs et artisans de Chambéry, d'Aix-les-Bains et des alentours.", { x: 0.6, y: 2.6, w: 7.4, h: 1.1, fontSize: 18, color: C.background1 }, "Intro");
  const facts = [["45.56° N", "Basé à Chambéry, on se déplace dans tout le 73"], ["1", "Un seul interlocuteur, du premier appel à la mise en ligne"], ["0", "Jargon technique : on parle de tes clients, pas de code"]];
  facts.forEach(([n, t], i) => {
    const x = 0.6 + i * 2.55;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.1, w: 2.35, h: 2.35, rectRadius: 0.12, fill: { color: C.text2 }, line: { color: C.accent4, width: 1 }, objectName: `Carte ${i + 1}` });
    s.addText(n, { x: x + 0.22, y: 4.3, w: 2.0, h: 0.8, fontFace: "Arial Black", fontSize: i ? 40 : 24, color: C.accent1, margin: 0, valign: "middle", isTextBox: true, objectName: `Chiffre ${i + 1}` });
    body(s, t, { x: x + 0.22, y: 5.2, w: 1.95, h: 1.1, fontSize: 13 }, `Texte ${i + 1}`);
  });
  s.addNotes("Qui on est : un studio local, à Chambéry. Un seul interlocuteur, pas de sous-traitance cachée, et un vocabulaire simple.");
  anims([["Kicker", "fade", 0], ["Titre", "fadeUp", 100], ["Intro", "fadeUp", 200], ...[1, 2, 3].flatMap(i => [[`Carte ${i}`, "riseUp", 200], [`Chiffre ${i}`, "zoomWith", 100], [`Texte ${i}`, "fadeWith", 150]])]);

  // ============ 4. Offres
  pres.addSection({ title: "Les offres" });
  s = pres.addSlide({ masterName: "NX_CONTENT", sectionTitle: "Les offres" });
  glows(s, { x: 9.5, y: 2.5, w: 6, h: 6 }, { x: 2, y: -3, w: 6, h: 6 });
  frame(s); video(s, "c5-shop");
  logo(s, { x: 0.6, y: 6.8, w: 0.32, h: 0.32 });
  kicker(s, "Les offres", "Kicker");
  s.addText([{ text: "Trois formules, ", options: { color: C.background1 } }, { text: "un seul objectif", options: { color: C.accent1 } }], { placeholder: "title" });
  const offers = [["Essentiel", "Site vitrine", "dès 400 €", "Ton activité, tes horaires, tes photos et un bouton pour t'appeler."], ["Boutique", "E-commerce", "sur devis", "Vente en ligne, click & collect, paiement sécurisé, stocks."], ["Signature", "Motion design", "sur devis", "Un site sur mesure, animé, pour marquer les esprits."]];
  offers.forEach(([n, k, p, t], i) => {
    const x = 0.6 + i * 2.55, sig = i === 2;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.55, w: 2.35, h: 3.95, rectRadius: 0.12, fill: { color: sig ? C.accent1 : C.text2 }, line: { color: sig ? C.accent1 : C.accent4, width: 1 }, shadow: { type: "outer", color: "000000", opacity: 0.45, blur: 18, offset: 6, angle: 90 }, objectName: `Offre ${i + 1}` });
    s.addText(k.toUpperCase(), { x: x + 0.22, y: 2.8, w: 1.95, h: 0.3, fontFace: "Courier New", fontSize: 11, bold: true, color: sig ? C.text1 : C.accent1, charSpacing: 2, margin: 0, isTextBox: true, objectName: `Type ${i + 1}` });
    s.addText(n, { x: x + 0.22, y: 3.15, w: 2.0, h: 0.5, fontFace: "Arial Black", fontSize: 20, color: sig ? C.text1 : C.background1, margin: 0, isTextBox: true, objectName: `Nom ${i + 1}` });
    s.addText(p, { x: x + 0.22, y: 3.75, w: 2.0, h: 0.6, fontFace: "Arial Black", fontSize: 24, color: sig ? C.text1 : C.accent1, margin: 0, isTextBox: true, objectName: `Prix ${i + 1}` });
    body(s, t, { x: x + 0.22, y: 4.6, w: 1.95, h: 1.7, fontSize: 13, color: sig ? C.text1 : C.background2 }, `Desc ${i + 1}`);
  });
  s.addNotes("Trois formules. Essentiel dès 400 euros pour un site vitrine. Boutique pour vendre en ligne. Signature pour un site sur mesure avec du motion design, comme les animations de cette présentation.");
  anims([["Kicker", "fade", 0], ["Titre", "fadeUp", 100], ...[1, 2, 3].flatMap(i => [[`Offre ${i}`, "riseUp", 250], [`Type ${i}`, "fadeWith", 100], [`Nom ${i}`, "fadeUpWith", 100], [`Prix ${i}`, "zoomWith", 200], [`Desc ${i}`, "fadeWith", 250]])]);

  // ============ 5. Pourquoi Nexora
  pres.addSection({ title: "Pourquoi Nexora" });
  s = pres.addSlide({ masterName: "NX_CONTENT", sectionTitle: "Pourquoi Nexora" });
  glows(s, { x: 7.5, y: -1.5, w: 7, h: 7 }, { x: -2, y: 3.5, w: 6, h: 6 });
  frame(s); video(s, "c6-motion");
  logo(s, { x: 0.6, y: 6.8, w: 0.32, h: 0.32 });
  kicker(s, "Pourquoi nous", "Kicker");
  s.addText([{ text: "Six raisons de ", options: { color: C.background1 } }, { text: "passer par Nexora", options: { color: C.accent1 } }], { placeholder: "title" });
  const why = [["bolt", "Rapide", "En ligne en 1 à 2 semaines."], ["tag", "Prix clair", "Dès 400 €, devis ligne par ligne."], ["pin", "Local", "Basé à Chambéry, disponible en vrai."], ["phone", "Pensé mobile", "Lisible et rapide sur téléphone."], ["wand", "Motion design", "Des animations qui marquent."], ["msg", "Suivi", "Tu demandes, je modifie."]];
  why.forEach(([ic, h, t], i) => {
    const x = 0.6 + (i % 2) * 3.8, y = 2.6 + Math.floor(i / 2) * 1.35;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.6, h: 1.15, rectRadius: 0.1, fill: { color: C.text2 }, line: { color: C.accent4, width: 1 }, objectName: `Raison ${i + 1}` });
    s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: y + 0.25, w: 0.65, h: 0.65, fill: { color: C.accent3 }, line: { color: C.accent1, width: 1 }, objectName: `Rond ${i + 1}` });
    s.addImage({ data: ICONS[ic], x: x + 0.365, y: y + 0.415, w: 0.32, h: 0.32, objectName: `Picto ${i + 1}`, altText: h });
    s.addText(h, { x: x + 1.05, y: y + 0.18, w: 2.4, h: 0.38, fontFace: "Arial", fontSize: 16, bold: true, color: C.background1, margin: 0, isTextBox: true, objectName: `Raison titre ${i + 1}` });
    body(s, t, { x: x + 1.05, y: y + 0.58, w: 2.45, h: 0.45, fontSize: 13 }, `Raison texte ${i + 1}`);
  });
  s.addNotes("Les six raisons de nous choisir : la rapidité, la transparence sur les prix, la proximité, le mobile d'abord, le motion design et le suivi.");
  anims([["Kicker", "fade", 0], ["Titre", "fadeUp", 100], ...[1, 2, 3, 4, 5, 6].flatMap(i => [[`Raison ${i}`, "zoom", 150], [`Rond ${i}`, "zoomWith", 50], [`Picto ${i}`, "spinWith", 50], [`Raison titre ${i}`, "fadeWith", 100], [`Raison texte ${i}`, "fadeWith", 150]])]);

  // ============ 6. Méthode (the frame morphs into the timeline track)
  pres.addSection({ title: "La méthode" });
  s = pres.addSlide({ masterName: "NX_CONTENT", sectionTitle: "La méthode" });
  glows(s, { x: 3.5, y: 3.8, w: 6.5, h: 6.5 }, { x: 9, y: -3, w: 6, h: 6 });
  frame(s, { x: 0.6, y: 4.15, w: 12.13, h: 0.12 }, 0.5);
  logo(s, { x: 0.6, y: 6.8, w: 0.32, h: 0.32 });
  kicker(s, "La méthode", "Kicker");
  s.addText([{ text: "De l'appel à la mise en ligne : ", options: { color: C.background1 } }, { text: "14\u00A0jours", options: { color: C.accent1 } }], { placeholder: "title", w: 11.5 });
  const steps = [["Jour 1", "Appel de 20 min", "Ton métier, tes clients, ce que tu veux."], ["Jour 3", "Maquette", "Tu vois ton site avant qu'il existe."], ["Jour 4 à 12", "Création", "Textes, photos, téléphone, Google."], ["Jour 14", "En ligne", "Et je reste là si tu as besoin."]];
  steps.forEach(([d, h, t], i) => {
    const x = 0.6 + i * 3.1;
    s.addShape(pres.shapes.OVAL, { x, y: 3.86, w: 0.7, h: 0.7, fill: { color: i === 3 ? C.accent1 : C.text1 }, line: { color: C.accent1, width: 2 }, objectName: `Étape ${i + 1}` });
    s.addText(String(i + 1), { x, y: 3.86, w: 0.7, h: 0.7, fontFace: "Arial Black", fontSize: 18, color: i === 3 ? C.text1 : C.accent1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `Num ${i + 1}` });
    s.addText(d.toUpperCase(), { x, y: 2.95, w: 2.8, h: 0.35, fontFace: "Courier New", fontSize: 13, bold: true, color: C.accent1, margin: 0, isTextBox: true, objectName: `Jour ${i + 1}` });
    s.addText(h, { x, y: 4.85, w: 2.8, h: 0.45, fontFace: "Arial", fontSize: 18, bold: true, color: C.background1, margin: 0, isTextBox: true, objectName: `Étape titre ${i + 1}` });
    body(s, t, { x, y: 5.35, w: 2.7, h: 0.8, fontSize: 14 }, `Étape texte ${i + 1}`);
  });
  s.addNotes("La méthode en quatre étapes : un appel, une maquette au troisième jour, la création, puis la mise en ligne au bout de deux semaines maximum. Le cadre de la slide précédente s'est transformé en ligne du temps.");
  anims([["Kicker", "fade", 0], ["Titre", "fadeUp", 100], ...[1, 2, 3, 4].flatMap(i => [[`Étape ${i}`, "zoom", 350], [`Num ${i}`, "zoomWith", 0], [`Jour ${i}`, "fadeDownWith", 100], [`Étape titre ${i}`, "fadeUpWith", 100], [`Étape texte ${i}`, "fadeWith", 200]])], false);

  // ============ 7. Chiffres clés
  pres.addSection({ title: "En chiffres" });
  s = pres.addSlide({ masterName: "NX_CONTENT", sectionTitle: "En chiffres" });
  glows(s, { x: 7.5, y: 1, w: 7, h: 7 }, { x: -1, y: -2.5, w: 5, h: 5 });
  frame(s); video(s, "c8-coin");
  logo(s, { x: 0.6, y: 6.8, w: 0.32, h: 0.32 });
  kicker(s, "En chiffres", "Kicker");
  s.addText([{ text: "Simple, rapide, ", options: { color: C.background1 } }, { text: "transparent", options: { color: C.accent1 } }], { placeholder: "title" });
  const stats = [["14", "jours maximum", "pour être en ligne"], ["400 €", "pour commencer", "site vitrine Essentiel"], ["1", "interlocuteur", "du devis au suivi"]];
  stats.forEach(([n, l1, l2], i) => {
    const y = 2.55 + i * 1.4;
    s.addText(n, { x: 0.6, y, w: 3.4, h: 1.1, fontFace: "Arial Black", fontSize: 60, color: C.accent1, margin: 0, valign: "middle", isTextBox: true, objectName: `Stat ${i + 1}` });
    s.addText([{ text: l1, options: { bold: true, color: C.background1, breakLine: true } }, { text: l2, options: { color: C.background2 } }], { x: 4.2, y: y + 0.15, w: 3.9, h: 0.85, fontFace: "Arial", fontSize: 18, margin: 0, valign: "middle", isTextBox: true, objectName: `Légende ${i + 1}` });
  });
  s.addNotes("Les trois chiffres à retenir : en ligne en 14 jours maximum, à partir de 400 euros, et un seul interlocuteur.");
  anims([["Kicker", "fade", 0], ["Titre", "fadeUp", 100], ...[1, 2, 3].flatMap(i => [[`Stat ${i}`, "zoom", 300], [`Légende ${i}`, "fadeLeftWith", 150]])]);

  // ============ 8. Google
  pres.addSection({ title: "Visibilité" });
  s = pres.addSlide({ masterName: "NX_CONTENT", sectionTitle: "Visibilité" });
  glows(s, { x: 9, y: -2, w: 6.5, h: 6.5 }, { x: 1, y: 4, w: 6, h: 6 });
  frame(s); video(s, "c7-google");
  logo(s, { x: 0.6, y: 6.8, w: 0.32, h: 0.32 });
  kicker(s, "Visibilité", "Kicker");
  s.addText([{ text: "Trouvé sur Google. ", options: { color: C.background1 } }, { text: "Appelé dans la foulée", options: { color: C.accent1 } }], { placeholder: "title" });
  const seo = [["Mots-clés locaux", "« boulangerie Chambéry », « coiffeur Aix-les-Bains » : ton site parle comme tes clients cherchent."], ["Fiche Google reliée", "Horaires, photos, avis et site travaillent ensemble pour te faire remonter."], ["Un bouton, un appel", "Le numéro et l'itinéraire sont à un geste, dès l'ouverture de la page."]];
  seo.forEach(([h, t], i) => {
    const y = 2.65 + i * 1.3;
    s.addText(`0${i + 1}`, { x: 0.6, y, w: 0.9, h: 0.5, fontFace: "Arial Black", fontSize: 22, color: C.accent1, margin: 0, isTextBox: true, objectName: `Index ${i + 1}` });
    s.addText(h, { x: 1.5, y, w: 6.5, h: 0.4, fontFace: "Arial", fontSize: 18, bold: true, color: C.background1, margin: 0, isTextBox: true, objectName: `SEO titre ${i + 1}` });
    body(s, t, { x: 1.5, y: y + 0.42, w: 6.5, h: 0.75, fontSize: 14 }, `SEO texte ${i + 1}`);
  });
  s.addNotes("La visibilité : un site bien fait est relié à la fiche Google, utilise les mots que les clients tapent vraiment, et met le bouton d'appel en évidence.");
  anims([["Kicker", "fade", 0], ["Titre", "fadeUp", 100], ...[1, 2, 3].flatMap(i => [[`Index ${i}`, "zoom", 300], [`SEO titre ${i}`, "fadeLeftWith", 50], [`SEO texte ${i}`, "fadeWith", 150]])]);

  // ============ 9. Pack Suivi
  pres.addSection({ title: "Suivi" });
  s = pres.addSlide({ masterName: "NX_CONTENT", sectionTitle: "Suivi" });
  glows(s, { x: 7, y: 2.5, w: 6.5, h: 6.5 }, { x: -1.5, y: -2, w: 5.5, h: 5.5 });
  frame(s); video(s, "c4-phone");
  logo(s, { x: 0.6, y: 6.8, w: 0.32, h: 0.32 });
  kicker(s, "Pack Suivi", "Kicker");
  s.addText([{ text: "Tu demandes. ", options: { color: C.background1 } }, { text: "Je modifie", options: { color: C.accent1 } }], { placeholder: "title" });
  const chat = [["me", "TOI · 18:42", "Nouveau menu demain, tu peux le mettre en ligne ?"], ["nx", "NEXORA · 19:05", "C'est en ligne ✓"], ["me", "TOI · 19:06", "Parfait, merci !"]];
  chat.forEach(([who, meta, t], i) => {
    const me = who === "me", y = 2.55 + i * 1.08, w = me ? 4.9 : 3.0, x = me ? 8.1 - w : 0.6;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.9, rectRadius: 0.25, fill: { color: me ? C.accent3 : C.accent1 }, line: { type: "none" }, shadow: { type: "outer", color: "000000", opacity: 0.4, blur: 14, offset: 5, angle: 90 }, objectName: `Bulle ${i + 1}` });
    s.addText([{ text: meta, options: { fontFace: "Courier New", fontSize: 10, color: me ? C.background2 : C.text1, breakLine: true } }, { text: t, options: { fontFace: "Arial", fontSize: 15, bold: !me, color: me ? C.background1 : C.text1 } }], { x: x + 0.25, y: y + 0.08, w: w - 0.5, h: 0.74, margin: 0, valign: "middle", isTextBox: true, objectName: `Message ${i + 1}` });
  });
  body(s, "Textes, photos, horaires, promos : un forfait par mois, et ton site reste à jour sans que tu touches à rien.", { x: 0.6, y: 5.95, w: 7.5, h: 0.7, fontSize: 15, color: C.background1 }, "Résumé");
  s.addNotes("Le Pack Suivi : un abonnement mensuel. Le client envoie un message pour changer un texte, une photo ou ses horaires, et c'est fait.");
  anims([["Kicker", "fade", 0], ["Titre", "fadeUp", 100], ...[1, 2, 3].flatMap(i => [[`Bulle ${i}`, "pop", 500], [`Message ${i}`, "fadeWith", 100]]), ["Résumé", "fadeUp", 300]]);

  // ============ 10. Démos
  pres.addSection({ title: "Démos" });
  s = pres.addSlide({ masterName: "NX_CONTENT", sectionTitle: "Démos" });
  glows(s, { x: 3, y: 3.5, w: 7, h: 7 }, { x: 9, y: -2.5, w: 5.5, h: 5.5 });
  frame(s, { x: 0.45, y: 2.35, w: 12.43, h: 4.3 }, 0.08);
  logo(s, { x: 0.6, y: 6.8, w: 0.32, h: 0.32 });
  kicker(s, "Démos", "Kicker");
  s.addText([{ text: "Ce que ça donne, ", options: { color: C.background1 } }, { text: "en vrai", options: { color: C.accent1 } }], { placeholder: "title", w: 11.5 });
  const demos = [["demo-boulangerie", "Boulangerie", "Le Fournil d'Alix"], ["demo-resto", "Restaurant", "La Table du Lac"], ["demo-coiffure", "Salon de coiffure", "Maison Céleste"]];
  demos.forEach(([img, k, n], i) => {
    const x = 0.75 + i * 4.1;
    s.addImage({ path: path.join(MEDIA, img + ".jpg"), x, y: 2.6, w: 1.85, h: 3.29, rounding: false, objectName: `Démo ${i + 1}`, altText: `Démo ${k} : ${n}` });
    s.addText(k.toUpperCase(), { x: x + 2.0, y: 2.75, w: 1.9, h: 0.3, fontFace: "Courier New", fontSize: 11, bold: true, color: C.accent1, margin: 0, isTextBox: true, objectName: `Démo type ${i + 1}` });
    s.addText(n, { x: x + 2.0, y: 3.1, w: 1.9, h: 0.9, fontFace: "Arial", fontSize: 17, bold: true, color: C.background1, margin: 0, valign: "top", isTextBox: true, objectName: `Démo nom ${i + 1}` });
  });
  s.addText("Projets de démonstration, commerces fictifs.", { x: 0.75, y: 6.05, w: 8, h: 0.35, fontFace: "Courier New", fontSize: 11, color: C.background2, margin: 0, isTextBox: true, objectName: "Mention" });
  s.addNotes("Trois démos : une boulangerie, un restaurant à Aix-les-Bains et un salon de coiffure avec prise de rendez-vous. Ce sont des commerces fictifs créés pour montrer le savoir-faire.");
  anims([["Kicker", "fade", 0], ["Titre", "fadeUp", 100], ...[1, 2, 3].flatMap(i => [[`Démo ${i}`, "riseUp", 300], [`Démo type ${i}`, "fadeWith", 150], [`Démo nom ${i}`, "fadeUpWith", 200]]), ["Mention", "fade", 200]], false);

  // ============ 11. Contact
  pres.addSection({ title: "Contact" });
  s = pres.addSlide({ masterName: "NX_COVER", sectionTitle: "Contact" });
  glows(s, { x: 7.2, y: -1.2, w: 7, h: 7 }, { x: -2, y: 4.5, w: 6, h: 6 });
  frame(s); video(s, "c9-outro");
  logo(s, { x: 0.6, y: 0.7, w: 0.9, h: 0.9 });
  s.addText("PROCHAINE ÉTAPE", { x: 0.6, y: 2.05, w: 7.6, h: 0.3, fontFace: "Courier New", fontSize: 12, bold: true, color: C.accent1, charSpacing: 3, margin: 0, isTextBox: true, objectName: "Kicker" });
  s.addText("Parlons de ton site", { x: 0.6, y: 2.45, w: 7.8, h: 1.3, fontFace: "Arial Black", fontSize: 50, color: C.background1, margin: 0, isTextBox: true, objectName: "Titre" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 3.95, w: 4.3, h: 0.75, rectRadius: 0.37, fill: { color: C.accent1 }, line: { type: "none" }, objectName: "Bouton" });
  s.addText("DEVIS GRATUIT EN MESSAGE", { x: 0.6, y: 3.95, w: 4.3, h: 0.75, fontFace: "Courier New", fontSize: 15, bold: true, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "Bouton texte" });
  const contact = [["Site", "nexora-web.fr"], ["Instagram", "@nexora_web_design"], ["Zone", "Chambéry, Aix-les-Bains, Savoie (73)"]];
  contact.forEach(([k, v], i) => {
    s.addText(k.toUpperCase(), { x: 0.6, y: 5.05 + i * 0.5, w: 1.6, h: 0.35, fontFace: "Courier New", fontSize: 12, color: C.background2, margin: 0, isTextBox: true, objectName: `Contact clé ${i + 1}` });
    s.addText(v, { x: 2.2, y: 5.05 + i * 0.5, w: 5.8, h: 0.35, fontFace: "Arial", fontSize: 16, bold: true, color: C.background1, margin: 0, isTextBox: true, objectName: `Contact ${i + 1}` });
  });
  s.addNotes("Pour conclure : on propose un devis gratuit, par message sur Instagram ou via le site nexora-web.fr.");
  anims([["Kicker", "fade", 0], ["Titre", "zoom", 100], ["Bouton", "pop", 300], ["Bouton texte", "fadeWith", 100], ...[1, 2, 3].flatMap(i => [[`Contact clé ${i}`, "fadeLeft", 150], [`Contact ${i}`, "fadeLeftWith", 50]])]);

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  fs.writeFileSync(path.join(__dirname, "anim-plan.json"), JSON.stringify(plan, null, 1));
  console.log("wrote", OUT, plan.length, "slides");
}
main().catch(e => { console.error(e); process.exit(1); });
