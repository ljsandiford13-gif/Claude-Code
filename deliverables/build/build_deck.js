const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const Fa = require("react-icons/fa");

const S = JSON.parse(fs.readFileSync(path.join(__dirname, "stats2.json"), "utf8"));
const O = S.overall, C = S.cats, A = S.storeA, B = S.storeB, items = S.items;
const OUT_PPTX = process.argv[2], OUT_SCRIPT = process.argv[3];

// ---------- palette (fresh-produce theme) ----------
const GREEN = "2C5F2D", MOSS = "97BC62", PALE = "EEF4E8", WHITE = "FFFFFF", INK = "1F2A1F", MUTED = "5C6B5C";
const ORANGE = "EB6834", SLATE = "4A6FA5", TOMATO = "D7263D", GOLD = "F2C14E", LIGHT = "F6F8F3";
const FONT = "Calibri";
const by = (n) => items.find((d) => d.item === n);
const pct = (x, d = 0) => (x > 0 ? "+" : x < 0 ? "−" : "") + (Math.abs(x) * 100).toFixed(d) + "%";
const pp = (x, d = 0) => (Math.abs(x) * 100).toFixed(d) + "%";
const money = (x) => "BBD " + x.toFixed(2);
const n = O.n, ffc = O.cheapest["Food First"];

// ---------- icons ----------
async function icon(Comp, color) {
  let svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { size: 256 }));
  svg = svg.replace(/currentColor/g, "#" + color);
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "Heart & Stroke Foundation of Barbados";
pres.title = "The Great Grocery Showdown";

const W = 13.33, H = 7.5;
const notes = []; // {title, time, text}

function base(dark = false) {
  const s = pres.addSlide();
  s.background = { color: dark ? GREEN : WHITE };
  return s;
}
function title(s, text, dark = false, y = 0.45) {
  s.addText(text, { x: 0.6, y, w: W - 1.2, h: 0.9, fontFace: FONT, fontSize: 36, bold: true, color: dark ? WHITE : GREEN, isTextBox: true, margin: 0 });
}
function sub(s, text, dark = false, y = 1.3) {
  s.addText(text, { x: 0.6, y, w: W - 1.2, h: 0.5, fontFace: FONT, fontSize: 16, color: dark ? "DCE8D4" : MUTED, isTextBox: true, margin: 0 });
}
function iconCircle(s, data, x, y, d, circleColor) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: circleColor }, line: { color: circleColor } });
  const pad = d * 0.25;
  s.addImage({ data, x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad });
}
function card(s, x, y, w, h, fill = PALE) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.15 });
}
function footer(s, dark = false) {
  s.addText("Food First vs two Barbados supermarkets  |  Heart & Stroke Foundation of Barbados  |  prices recorded August 2026",
    { x: 0.6, y: H - 0.45, w: W - 1.2, h: 0.3, fontFace: FONT, fontSize: 9, color: dark ? "B9CDB0" : "9AA79A", isTextBox: true, margin: 0 });
}
function note(s, t, time, text) { s.addNotes(text); notes.push({ title: t, time, text }); }

(async () => {
  const I = {
    basket: await icon(Fa.FaShoppingBasket, WHITE), child: await icon(Fa.FaChild, WHITE), heart: await icon(Fa.FaHeartbeat, WHITE),
    ship: await icon(Fa.FaShip, WHITE), question: await icon(Fa.FaQuestion, WHITE), secret: await icon(Fa.FaUserSecret, WHITE),
    list: await icon(Fa.FaClipboardList, WHITE), store: await icon(Fa.FaStore, WHITE), scale: await icon(Fa.FaBalanceScale, WHITE),
    calc: await icon(Fa.FaCalculator, WHITE), trophy: await icon(Fa.FaTrophy, WHITE), carrot: await icon(Fa.FaCarrot, WHITE),
    apple: await icon(Fa.FaAppleAlt, WHITE), leaf: await icon(Fa.FaLeaf, WHITE), warn: await icon(Fa.FaExclamationTriangle, WHITE),
    bulb: await icon(Fa.FaLightbulb, WHITE), road: await icon(Fa.FaRoute, WHITE), cheese: await icon(Fa.FaCheese, WHITE),
    tag: await icon(Fa.FaTags, WHITE), school: await icon(Fa.FaSchool, WHITE), users: await icon(Fa.FaUsers, WHITE),
    basketGreen: await icon(Fa.FaShoppingBasket, GREEN),
  };

  // =============================== 1. Title
  {
    const s = base(true);
    s.addShape(pres.shapes.OVAL, { x: 9.0, y: 1.2, w: 3.6, h: 3.6, fill: { color: MOSS }, line: { color: MOSS } });
    s.addImage({ data: I.basketGreen, x: 9.8, y: 2.0, w: 2.0, h: 2.0 });
    s.addText("THE GREAT", { x: 0.8, y: 0.95, w: 7.8, h: 0.6, fontFace: FONT, fontSize: 28, bold: true, color: GOLD, isTextBox: true, margin: 0, charSpacing: 6 });
    s.addText("Grocery Showdown", { x: 0.8, y: 1.55, w: 8.0, h: 2.1, fontFace: FONT, fontSize: 54, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(`Food First vs two Barbados supermarkets: who really has the better prices on whole foods?`,
      { x: 0.8, y: 3.85, w: 7.6, h: 1.0, fontFace: FONT, fontSize: 20, color: "DCE8D4", isTextBox: true, margin: 0 });
    s.addText([
      { text: "Ms. Daniella Clarke, HSFB intern", options: { bold: true, breakLine: true } },
      { text: "Heart & Stroke Foundation of Barbados  |  2026", options: {} },
    ], { x: 0.8, y: 5.4, w: 8, h: 0.9, fontFace: FONT, fontSize: 16, color: WHITE, isTextBox: true, margin: 0 });
    note(s, "Title", "0:40",
      `Good [morning/afternoon] everyone. Thank you for having me. My name is Daniella Clarke and this summer I interned with the Heart & Stroke Foundation of Barbados. ` +
      `For the next ten minutes I want to take you grocery shopping. Not literally, but close. We asked a simple question that every Barbadian household asks on a Saturday morning: where is the food cheapest? ` +
      `Specifically, we wanted to know whether Food First, a supplier that imports fruit, vegetables and a few dairy items directly from Europe, can beat our two biggest supermarket chains on price. ` +
      `I'll show you how we checked, what we found, and why it matters for the Foundation's work on healthy eating. Spoiler: there's a clear winner, but with some interesting exceptions.`);
  }

  // =============================== 2. Why we went shopping
  {
    const s = base();
    title(s, "Why we went shopping");
    sub(s, "Barbados is fighting non-communicable diseases, and the fight starts on the plate");
    const tiles = [
      [I.child, "42%", "of children in Barbados are overweight or obese, up from 33%", GREEN],
      [I.heart, "82.8%", "of all deaths in Barbados are from non-communicable diseases", TOMATO],
      [I.ship, "~85%", "of the food we eat is imported, so prices follow the world market", SLATE],
    ];
    tiles.forEach(([ic, big, txt, col], i) => {
      const x = 0.6 + i * 4.1;
      card(s, x, 2.1, 3.85, 3.9);
      iconCircle(s, ic, x + 0.35, 2.4, 0.9, col);
      s.addText(big, { x: x + 0.35, y: 3.45, w: 3.2, h: 1.0, fontFace: FONT, fontSize: 54, bold: true, color: col, isTextBox: true, margin: 0 });
      s.addText(txt, { x: x + 0.35, y: 4.5, w: 3.2, h: 1.3, fontFace: FONT, fontSize: 15, color: INK, isTextBox: true, margin: 0, valign: "top" });
    });
    s.addText("Sources: HSFB and the Barbados Childhood Obesity Prevention Coalition (2026); PAHO country profile (2019 and 2022); FAO.",
      { x: 0.6, y: 6.25, w: 12, h: 0.4, fontFace: FONT, fontSize: 11, color: MUTED, italic: true, isTextBox: true, margin: 0 });
    footer(s);
    note(s, "Why we went shopping", "0:50",
      `First, why does a heart foundation care about grocery prices? Three numbers tell the story. ` +
      `Forty-two percent of children in Barbados are now overweight or obese. That figure was thirty-three percent not long ago, so it is moving in the wrong direction. ` +
      `Those children grow into adults, and today more than eight in ten deaths in Barbados are from non-communicable diseases: diabetes, hypertension, heart disease and some cancers. ` +
      `And about eighty-five percent of the food we eat is imported, which means our grocery bills rise and fall with the world market. ` +
      `HSFB keeps urging parents to feed children more whole foods, more fruit and vegetables. But the honest reply we hear is: "that's expensive". So we decided to find out whether it has to be.`);
  }

  // =============================== 3. The big question
  {
    const s = base();
    title(s, "The big question");
    iconCircle(s, I.question, 0.6, 1.6, 1.1, GOLD);
    s.addText("If a supplier brings whole foods straight from Europe to Barbados, is it actually cheaper for a family than the supermarket?",
      { x: 2.0, y: 1.5, w: 10.7, h: 1.4, fontFace: FONT, fontSize: 26, bold: true, color: INK, isTextBox: true, margin: 0, valign: "middle" });
    card(s, 0.6, 3.3, 5.9, 2.1);
    s.addText([
      { text: "Our bet (H₁)", options: { bold: true, color: GREEN, fontSize: 18, breakLine: true } },
      { text: "Food First's prices are, on average, lower than the supermarkets', because of direct EU import and a shorter supply chain.", options: { fontSize: 15, color: INK } },
    ], { x: 0.9, y: 3.5, w: 5.3, h: 1.8, fontFace: FONT, isTextBox: true, margin: 0, valign: "top" });
    card(s, 6.8, 3.3, 5.9, 2.1);
    s.addText([
      { text: "The sceptic's view (H₀)", options: { bold: true, color: TOMATO, fontSize: 18, breakLine: true } },
      { text: "There is no consistent difference. Any saving is luck of the draw, item by item.", options: { fontSize: 15, color: INK } },
    ], { x: 7.1, y: 3.5, w: 5.3, h: 1.8, fontFace: FONT, isTextBox: true, margin: 0, valign: "top" });
    iconCircle(s, I.secret, 0.6, 5.75, 0.6, SLATE);
    s.addText("Undercover rule: the two supermarkets agreed to help on condition they are not named. They are Supermarket A and Supermarket B throughout.",
      { x: 1.4, y: 5.7, w: 11.3, h: 0.7, fontFace: FONT, fontSize: 13, color: MUTED, italic: true, isTextBox: true, margin: 0, valign: "middle" });
    note(s, "The big question", "0:40",
      `So here is the question in one sentence: if a supplier brings whole foods straight from Europe, is it actually cheaper for a family than the supermarket? ` +
      `We went in with a hypothesis. Our bet was yes: direct import and a shorter supply chain should mean lower prices. ` +
      `The sceptic's view, our null hypothesis, is that there is no consistent difference and any saving is just luck of the draw. ` +
      `One ground rule before we go on. The two supermarkets facilitated the study on the understanding that they would not be named. So you'll hear me say Supermarket A and Supermarket B. Food First is named because it is the subject of the comparison.`);
  }

  // =============================== 4. How we did it
  {
    const s = base();
    title(s, "How we did it");
    sub(s, "Same product, same unit, same week: a like-for-like comparison");
    const steps = [
      [I.list, "1. The list", "Food First's own price list: 95 products, priced per kg, per litre or per unit."],
      [I.store, "2. The shop", "In-store visits to Supermarket A and B in August 2026. Shelf price and pack size noted for every match."],
      [I.scale, "3. Standardise", "Every price converted to Food First's unit, so a 340 g pack becomes a per-kg price."],
      [I.calc, "4. Compare", `${n} items matched at all three stores on an identical basis. The rest were excluded.`],
    ];
    steps.forEach(([ic, h, t], i) => {
      const x = 0.6 + i * 3.1;
      card(s, x, 2.0, 2.9, 3.1);
      iconCircle(s, ic, x + 0.3, 2.25, 0.8, GREEN);
      s.addText(h, { x: x + 0.3, y: 3.15, w: 2.4, h: 0.4, fontFace: FONT, fontSize: 17, bold: true, color: GREEN, isTextBox: true, margin: 0 });
      s.addText(t, { x: x + 0.3, y: 3.6, w: 2.4, h: 1.4, fontFace: FONT, fontSize: 13, color: INK, isTextBox: true, margin: 0, valign: "top" });
    });
    card(s, 0.6, 5.35, 12.1, 1.3, GREEN);
    s.addText([
      { text: "% difference = (Food First price − Supermarket price) ÷ Supermarket price", options: { bold: true, fontSize: 17, color: WHITE, breakLine: true } },
      { text: "Negative = Food First cheaper.  Positive = Food First dearer.  We report the median (the typical item) as well as the mean.", options: { fontSize: 13, color: "DCE8D4" } },
    ], { x: 0.9, y: 5.45, w: 11.5, h: 1.1, fontFace: FONT, isTextBox: true, margin: 0, valign: "middle" });
    footer(s);
    note(s, "How we did it", "0:55",
      `How did we do it? Four steps. One: we started from Food First's own price list, ninety-five products, each priced per kilogram, per litre or per unit. ` +
      `Two: I visited Supermarket A and Supermarket B in August and recorded the shelf price and pack size of every product I could match. No photographs, just a notebook and a lot of patience in the produce aisle. ` +
      `Three: we standardised everything to the same unit. If a supermarket sells jalapeños in a 340 gram pack, we convert that to a per-kilogram price so it lines up with Food First. ` +
      `Four: we kept only the items that could be compared at all three stores on an identical basis. That left thirty-six items; the rest were excluded, either because the supermarkets didn't stock them or because the units couldn't be reconciled. ` +
      `The maths is one line: Food First price minus supermarket price, divided by the supermarket price. Negative means Food First is cheaper. And because a few wild outliers can drag an average around, we lean on the median, the typical item.`);
  }

  // =============================== 5. Scoreboard
  {
    const s = base();
    title(s, "The scoreboard");
    sub(s, `For each of the ${n} items: which store had the lowest standardised price?`);
    s.addChart(pres.charts.BAR, [{ name: "Items where this store was cheapest", labels: ["Food First", A, B], values: [ffc, O.cheapest[A], O.cheapest[B]] }],
      { x: 0.6, y: 1.9, w: 7.4, h: 4.6, barDir: "bar", chartColors: [GREEN, ORANGE, SLATE], chartColorsOpacity: 100,
        showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 14, dataLabelColor: INK, dataLabelFontBold: true,
        catAxisLabelFontSize: 14, catAxisLabelColor: INK, valAxisLabelFontSize: 11, valAxisLabelColor: MUTED, valAxisMaxVal: 36, valAxisMinVal: 0,
        valGridLine: { color: "E3E8DF", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 60,
        showTitle: false, catAxisOrientation: "maxMin" });
    card(s, 8.4, 1.9, 4.3, 4.6, PALE);
    iconCircle(s, I.trophy, 8.75, 2.2, 0.9, GOLD);
    s.addText(pp(ffc / n), { x: 8.75, y: 3.2, w: 3.7, h: 1.2, fontFace: FONT, fontSize: 66, bold: true, color: GREEN, isTextBox: true, margin: 0 });
    s.addText(`Food First was the cheapest of the three stores on ${ffc} of ${n} items. ${A} won ${O.cheapest[A]}, ${B} won ${O.cheapest[B]}.`,
      { x: 8.75, y: 4.45, w: 3.6, h: 1.8, fontFace: FONT, fontSize: 15, color: INK, isTextBox: true, margin: 0, valign: "top" });
    footer(s);
    note(s, "The scoreboard", "0:45",
      `Let's start with the simplest scoreboard. For each of the thirty-six items, which store had the lowest price? ` +
      `Food First won ${ffc} of them. That's ${pp(ffc / n)}. Supermarket A took ${O.cheapest[A]}, and Supermarket B just ${O.cheapest[B]}. ` +
      `So on three out of every four items, the direct importer beat both supermarkets. That already tells us this isn't a coin flip. But "cheapest" could mean cheaper by a cent. The next question is: by how much?`);
  }

  // =============================== 6. How much cheaper
  {
    const s = base();
    title(s, "How much cheaper?");
    sub(s, "The typical item (median) costs about a quarter less at Food First");
    const tiles = [
      [pct(O.medA, 1), `median vs ${A}`, `mean ${pct(O.meanA, 1)}  |  cheaper on ${O.ltA} of ${n} items`, ORANGE],
      [pct(O.medB, 1), `median vs ${B}`, `mean ${pct(O.meanB, 1)}  |  cheaper on ${O.ltB} of ${n} items`, SLATE],
    ];
    tiles.forEach(([big, lab, small, col], i) => {
      const x = 0.6 + i * 6.2;
      card(s, x, 2.0, 5.9, 3.1);
      s.addText(big, { x: x + 0.4, y: 2.2, w: 5.2, h: 1.5, fontFace: FONT, fontSize: 72, bold: true, color: GREEN, isTextBox: true, margin: 0 });
      s.addText(lab, { x: x + 0.4, y: 3.7, w: 5.2, h: 0.5, fontFace: FONT, fontSize: 20, bold: true, color: col, isTextBox: true, margin: 0 });
      s.addText(small, { x: x + 0.4, y: 4.25, w: 5.2, h: 0.6, fontFace: FONT, fontSize: 14, color: MUTED, isTextBox: true, margin: 0 });
    });
    iconCircle(s, I.bulb, 0.6, 5.45, 0.8, GOLD);
    s.addText(`Why median and not mean? A handful of items, led by mangoes at ${pct(by("Mangoes").ff_a)}, drag the average toward zero. The median ignores the outliers and tells you what a typical item does.`,
      { x: 1.6, y: 5.35, w: 11.1, h: 1.0, fontFace: FONT, fontSize: 14, color: INK, isTextBox: true, margin: 0, valign: "middle" });
    footer(s);
    note(s, "How much cheaper?", "0:45",
      `By how much? Take the typical item, the median. At Food First it costs ${pp(-O.medA, 1)} less than at Supermarket A and ${pp(-O.medB, 1)} less than at Supermarket B. Roughly a quarter off. ` +
      `The simple averages are a little smaller, ${pct(O.meanA, 1)} and ${pct(O.meanB, 1)}, and that gap is worth a word. A few items, led by mangoes at more than double the supermarket price, pull the average towards zero. ` +
      `The median doesn't care about outliers, which is why we lead with it. Either way, the direction is the same: Food First is cheaper, and not by a little.`);
  }

  // =============================== 7. Category showdown
  {
    const s = base();
    title(s, "Round by round: the categories");
    sub(s, "Median price difference, Food First relative to each supermarket (negative = Food First cheaper)");
    const cats = ["Vegetables", "Fruits", "Grocery", "All"];
    const vA = cats.map((c) => +(((c === "All" ? O : C[c]).medA) * 100).toFixed(1));
    const vB = cats.map((c) => +(((c === "All" ? O : C[c]).medB) * 100).toFixed(1));
    s.addChart(pres.charts.BAR, [
      { name: `vs ${A}`, labels: cats, values: vA },
      { name: `vs ${B}`, labels: cats, values: vB },
    ], { x: 0.6, y: 1.9, w: 8.0, h: 4.7, barDir: "col", barGrouping: "clustered", chartColors: [ORANGE, SLATE],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"%"', dataLabelFontSize: 11, dataLabelColor: INK,
      catAxisLabelFontSize: 13, catAxisLabelColor: INK, valAxisLabelFontSize: 11, valAxisLabelColor: MUTED, valAxisLabelFormatCode: '0"%"',
      valAxisMaxVal: 0, valAxisMinVal: -50, valGridLine: { color: "E3E8DF", size: 0.5 }, catGridLine: { style: "none" },
      showLegend: true, legendPos: "b", legendFontSize: 12, legendColor: INK, barGapWidthPct: 70, showTitle: false });
    const side = [
      [I.carrot, "Vegetables", `${C.Vegetables.both} of ${C.Vegetables.n} cheaper at Food First`, GREEN],
      [I.cheese, "Grocery", `${C.Grocery.both} of ${C.Grocery.n} cheaper at Food First`, GREEN],
      [I.apple, "Fruits", `${C.Fruits.both} of ${C.Fruits.n} cheaper; the mixed bag`, TOMATO],
    ];
    side.forEach(([ic, h, t, col], i) => {
      const y = 2.0 + i * 1.55;
      card(s, 8.9, y, 3.8, 1.35);
      iconCircle(s, ic, 9.1, y + 0.3, 0.75, col);
      s.addText(h, { x: 10.0, y: y + 0.2, w: 2.6, h: 0.4, fontFace: FONT, fontSize: 16, bold: true, color: INK, isTextBox: true, margin: 0 });
      s.addText(t, { x: 10.0, y: y + 0.62, w: 2.6, h: 0.65, fontFace: FONT, fontSize: 12, color: MUTED, isTextBox: true, margin: 0, valign: "top" });
    });
    footer(s);
    note(s, "Round by round: the categories", "0:50",
      `Now let's go round by round. Vegetables are the knockout: the typical vegetable is ${pp(-C.Vegetables.medA)} cheaper at Food First than at Supermarket A and ${pp(-C.Vegetables.medB)} cheaper than at Supermarket B. Food First beat both supermarkets on ${C.Vegetables.both} of ${C.Vegetables.n} vegetables. ` +
      `Grocery and dairy are just as strong: medians of ${pp(-C.Grocery.medA)} and ${pp(-C.Grocery.medB)}, with Food First cheaper than both stores on ${C.Grocery.both} of ${C.Grocery.n} items. ` +
      `Fruit is where it gets interesting. Against Supermarket A the typical fruit is basically a draw, about ${pp(-C.Fruits.medA)} cheaper; against Supermarket B it's ${pp(-C.Fruits.medB)}. Food First won on ${C.Fruits.both} of ${C.Fruits.n}, so it still wins more than it loses, but this is the category with real exceptions. Let's look at the winners and losers.`);
  }

  // =============================== 8. Vegetables
  {
    const s = base();
    title(s, "Vegetables: the heavyweight champions");
    sub(s, `Food First was cheaper than both supermarkets on ${C.Vegetables.both} of ${C.Vegetables.n} vegetables`);
    const veg = items.filter((d) => d.cat === "Vegetables").sort((a, b) => a.ff_a - b.ff_a);
    s.addChart(pres.charts.BAR, [
      { name: `vs ${A}`, labels: veg.map((d) => d.item), values: veg.map((d) => +(d.ff_a * 100).toFixed(1)) },
      { name: `vs ${B}`, labels: veg.map((d) => d.item), values: veg.map((d) => +(d.ff_b * 100).toFixed(1)) },
    ], { x: 0.6, y: 1.85, w: 8.3, h: 4.8, barDir: "bar", barGrouping: "clustered", chartColors: [ORANGE, SLATE],
      showValue: false, catAxisLabelFontSize: 11, catAxisLabelColor: INK, valAxisLabelFontSize: 10, valAxisLabelColor: MUTED, valAxisLabelFormatCode: '0"%"',
      valAxisMinVal: -80, valAxisMaxVal: 80, valGridLine: { color: "E3E8DF", size: 0.5 }, catGridLine: { style: "none" }, catAxisOrientation: "maxMin",
      showLegend: true, legendPos: "b", legendFontSize: 11, legendColor: INK, barGapWidthPct: 40, showTitle: false, catAxisLabelPos: "low" });
    const picks = [["Zucchini", GREEN], ["Red Onions", GREEN], ["Pumpkin", GREEN], ["Cucumbers", TOMATO]];
    picks.forEach(([name, col], i) => {
      const d = by(name); const y = 1.9 + i * 1.2;
      card(s, 9.3, y, 3.4, 1.05, col === TOMATO ? "FBE7E9" : PALE);
      s.addText(name, { x: 9.55, y: y + 0.12, w: 3.0, h: 0.35, fontFace: FONT, fontSize: 15, bold: true, color: col, isTextBox: true, margin: 0 });
      s.addText(`${pct(d.ff_a)} vs A   ${pct(d.ff_b)} vs B`, { x: 9.55, y: y + 0.5, w: 3.0, h: 0.4, fontFace: FONT, fontSize: 13, color: INK, isTextBox: true, margin: 0 });
    });
    footer(s);
    note(s, "Vegetables: the heavyweights", "0:45",
      `Here are all twelve vegetables, sorted. Almost every bar points left, meaning cheaper at Food First. Zucchini is ${pp(-by("Zucchini").ff_a)} cheaper than Supermarket A and ${pp(-by("Zucchini").ff_b)} cheaper than Supermarket B. Red onions, pumpkin and cabbage are all forty to sixty percent cheaper. Even humble carrots are half the price of Supermarket A. ` +
      `There is one rebel: cucumbers. Food First's cucumbers cost about half as much again as the supermarkets'. Every champion has an off night. ` +
      `But look at what's on that list: cabbage, carrots, pumpkin, onions, lettuce. These are exactly the everyday vegetables HSFB wants on children's plates, and they are where the saving is biggest.`);
  }

  // =============================== 9. Fruit
  {
    const s = base();
    title(s, "Fruit: the mixed bag");
    sub(s, `Food First cheaper than both supermarkets on ${C.Fruits.both} of ${C.Fruits.n} fruit items, but with loud exceptions`);
    const win = ["Gala Apple", "Pears", "Oranges", "Watermelon"], lose = ["Mangoes", "Red Apples", "Kiwis", "Grapefruit"];
    const col = (x, hdr, list, colr, ic) => {
      card(s, x, 1.9, 5.9, 4.3);
      iconCircle(s, ic, x + 0.3, 2.15, 0.7, colr);
      s.addText(hdr, { x: x + 1.15, y: 2.2, w: 4.5, h: 0.6, fontFace: FONT, fontSize: 20, bold: true, color: colr, isTextBox: true, margin: 0, valign: "middle" });
      list.forEach((nm, i) => {
        const d = by(nm); const y = 3.0 + i * 0.75;
        s.addText(nm, { x: x + 0.35, y, w: 1.9, h: 0.5, fontFace: FONT, fontSize: 15, color: INK, isTextBox: true, margin: 0, valign: "middle" });
        s.addText(`${pct(d.ff_a)} vs A`, { x: x + 2.25, y, w: 1.7, h: 0.5, fontFace: FONT, fontSize: 15, bold: true, color: colr, isTextBox: true, margin: 0, valign: "middle", align: "right" });
        s.addText(`${pct(d.ff_b)} vs B`, { x: x + 3.95, y, w: 1.7, h: 0.5, fontFace: FONT, fontSize: 15, bold: true, color: colr, isTextBox: true, margin: 0, valign: "middle", align: "right" });
      });
    };
    col(0.6, "Food First wins", win, GREEN, I.apple);
    col(6.8, "Supermarkets win", lose, TOMATO, I.tag);
    iconCircle(s, I.bulb, 0.6, 6.4, 0.6, GOLD);
    s.addText("Pattern: temperate fruit shipped from Europe (apples, pears) is cheaper at Food First; tropical fruit the supermarkets can source regionally (mangoes) is not.",
      { x: 1.4, y: 6.3, w: 11.3, h: 0.8, fontFace: FONT, fontSize: 13, color: MUTED, italic: true, isTextBox: true, margin: 0, valign: "middle" });
    note(s, "Fruit: the mixed bag", "0:50",
      `Fruit is the mixed bag, and it's the most interesting slide. On the left, the wins: a Gala apple is ${pp(-by("Gala Apple").ff_a)} cheaper at Food First, pears ${pp(-by("Pears").ff_a)} cheaper, oranges and watermelon a third cheaper. ` +
      `On the right, the losses, and they are loud. Mangoes at Food First cost more than double the Supermarket A price: ${pct(by("Mangoes").ff_a)}. Red apples are ${pct(by("Red Apples").ff_a)}. Kiwis and grapefruit are a bit dearer against Supermarket A. ` +
      `There is a pattern here. The fruit that grows in temperate Europe, apples and pears, is cheaper when it comes straight from Europe. The fruit that grows in the tropics, like mangoes, is cheaper at the supermarkets that can buy it regionally. Which makes sense: you don't want to fly a mango across the Atlantic to sell it in Barbados.`);
  }

  // =============================== 10. Grocery
  {
    const s = base();
    title(s, "Grocery and dairy: quiet but consistent");
    sub(s, `Food First cheaper than both supermarkets on ${C.Grocery.both} of ${C.Grocery.n} items`);
    const gro = ["Whole Milk", "Cooking Cream", "Whipping Cream", "Local Onions", "Eggs", "Oat Milk"];
    gro.forEach((nm, i) => {
      const d = by(nm); const x = 0.6 + (i % 3) * 4.1, y = 2.0 + Math.floor(i / 3) * 2.2;
      const strong = d.ff_a < -0.2;
      card(s, x, y, 3.85, 1.95);
      iconCircle(s, I.cheese, x + 0.3, y + 0.3, 0.7, strong ? GREEN : MUTED);
      s.addText(nm, { x: x + 1.15, y: y + 0.3, w: 2.5, h: 0.7, fontFace: FONT, fontSize: 18, bold: true, color: INK, isTextBox: true, margin: 0, valign: "middle" });
      s.addText([
        { text: `${pct(d.ff_a)}`, options: { bold: true, color: d.ff_a < 0 ? GREEN : TOMATO, fontSize: 22 } },
        { text: ` vs A    `, options: { color: MUTED, fontSize: 13 } },
        { text: `${pct(d.ff_b)}`, options: { bold: true, color: d.ff_b < 0 ? GREEN : TOMATO, fontSize: 22 } },
        { text: ` vs B`, options: { color: MUTED, fontSize: 13 } },
      ], { x: x + 0.3, y: y + 1.1, w: 3.3, h: 0.7, fontFace: FONT, isTextBox: true, margin: 0, valign: "middle" });
    });
    s.addText("Milk and cream are priced per litre, eggs per dozen, onions per kg.", { x: 0.6, y: 6.45, w: 12, h: 0.35, fontFace: FONT, fontSize: 11, color: MUTED, italic: true, isTextBox: true, margin: 0 });
    footer(s);
    note(s, "Grocery and dairy", "0:35",
      `The grocery and dairy items are the quiet achievers. Whole milk is ${pp(-by("Whole Milk").ff_a)} cheaper per litre. Cooking cream and whipping cream are forty to fifty percent cheaper. Local onions are ${pp(-by("Local Onions").ff_a)} cheaper. ` +
      `Eggs are almost a tie, a few cents a dozen. And oat milk is the one item where Supermarket A edges it, by less than one percent. ` +
      `So five of six grocery items cheaper, and nothing here where Food First is clearly worse. For a family's weekly staples, that matters as much as the produce.`);
  }

  // =============================== 11. Fill the basket
  {
    const s = base();
    title(s, "Fill the basket");
    sub(s, `Buy one unit of all ${n} items. What does the basket cost at each store?`);
    s.addChart(pres.charts.BAR, [{ name: "Basket (BBD)", labels: ["Food First", A, B], values: [+O.sumFF.toFixed(2), +O.sumA.toFixed(2), +O.sumB.toFixed(2)] }],
      { x: 0.6, y: 1.9, w: 7.4, h: 4.6, barDir: "col", chartColors: [GREEN, ORANGE, SLATE],
        showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '"BBD "#,##0.00', dataLabelFontSize: 14, dataLabelColor: INK, dataLabelFontBold: true,
        catAxisLabelFontSize: 14, catAxisLabelColor: INK, valAxisLabelFontSize: 11, valAxisLabelColor: MUTED, valAxisMinVal: 0, valAxisMaxVal: 500,
        valGridLine: { color: "E3E8DF", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 80, showTitle: false });
    card(s, 8.4, 1.9, 4.3, 4.6, PALE);
    iconCircle(s, I.basket, 8.75, 2.2, 0.9, GREEN);
    s.addText(`${money(O.sumA - O.sumFF)} less`, { x: 8.75, y: 3.25, w: 3.7, h: 0.6, fontFace: FONT, fontSize: 26, bold: true, color: ORANGE, isTextBox: true, margin: 0 });
    s.addText(`than ${A} (${pct(O.basketA)})`, { x: 8.75, y: 3.8, w: 3.7, h: 0.4, fontFace: FONT, fontSize: 14, color: MUTED, isTextBox: true, margin: 0 });
    s.addText(`${money(O.sumB - O.sumFF)} less`, { x: 8.75, y: 4.4, w: 3.7, h: 0.6, fontFace: FONT, fontSize: 26, bold: true, color: SLATE, isTextBox: true, margin: 0 });
    s.addText(`than ${B} (${pct(O.basketB)})`, { x: 8.75, y: 4.95, w: 3.7, h: 0.4, fontFace: FONT, fontSize: 14, color: MUTED, isTextBox: true, margin: 0 });
    s.addText("Indicative only: one unit of each item, not a real weekly shop.", { x: 8.75, y: 5.6, w: 3.7, h: 0.7, fontFace: FONT, fontSize: 11, italic: true, color: MUTED, isTextBox: true, margin: 0 });
    footer(s);
    note(s, "Fill the basket", "0:40",
      `Let's make it concrete. Imagine you put one unit of each of the thirty-six items in a basket: a kilo of this, a litre of that, a dozen eggs. ` +
      `At Food First the basket comes to ${money(O.sumFF)}. At Supermarket A it's ${money(O.sumA)}, and at Supermarket B ${money(O.sumB)}. ` +
      `That's ${money(O.sumA - O.sumFF)} saved against Supermarket A and ${money(O.sumB - O.sumFF)} against Supermarket B, roughly nineteen and twenty-nine percent. ` +
      `A caveat: this is one unit of everything, not a realistic family shop. But the direction and the size of the gap are clear.`);
  }

  // =============================== 12. What it means for HSFB
  {
    const s = base();
    title(s, "What this means for HSFB");
    sub(s, "Healthier eating can be made affordable, and here is a worked example");
    const cards = [
      [I.leaf, "The right foods are the cheapest", "Cabbage, carrots, pumpkin, onions, zucchini, lettuce and milk: the whole foods HSFB promotes are exactly where Food First's saving is largest."],
      [I.users, "A reply to “it's too expensive”", "On this evidence price need not be the binding barrier. The typical whole-food item was about a quarter cheaper through the direct-import channel."],
      [I.school, "A concrete story to tell", "Parents, schools and policymakers respond to real numbers. Thirty-six items, three stores, one clear pattern."],
    ];
    cards.forEach(([ic, h, t], i) => {
      const x = 0.6 + i * 4.1;
      card(s, x, 2.0, 3.85, 4.3);
      iconCircle(s, ic, x + 0.35, 2.3, 0.9, GREEN);
      s.addText(h, { x: x + 0.35, y: 3.35, w: 3.2, h: 0.8, fontFace: FONT, fontSize: 18, bold: true, color: GREEN, isTextBox: true, margin: 0, valign: "top" });
      s.addText(t, { x: x + 0.35, y: 4.2, w: 3.2, h: 2.0, fontFace: FONT, fontSize: 14, color: INK, isTextBox: true, margin: 0, valign: "top" });
    });
    footer(s);
    note(s, "What this means for HSFB", "0:50",
      `So what does this mean for the Foundation? Three things. ` +
      `First, the foods where Food First is cheapest are the foods we most want families to buy: cabbage, carrots, pumpkin, onions, zucchini, lettuce, milk. The saving lands exactly where it does the most good. ` +
      `Second, it gives us an honest answer to "healthy food is too expensive". It can be expensive. But on this evidence, with this channel, the typical whole-food item is about a quarter cheaper. Price doesn't have to be the thing that stops a family. ` +
      `Third, it's a story we can tell. Parents, teachers and policymakers respond to real numbers from real shelves, and this gives HSFB a concrete example to point to in its advocacy and its childhood obesity prevention work.`);
  }

  // =============================== 13. Fine print
  {
    const s = base();
    title(s, "The fine print");
    sub(s, "What this study can and cannot tell you");
    const pts = [
      ["One snapshot", "Prices from one visit per store in August 2026. Promotions and seasonal swings are not captured."],
      [`${n} of 95 items`, "Only items sold on an identical basis at all three stores. Berries, seasonings and sauces are missing."],
      ["Equal weighting", "Every item counts the same. A real weekly basket would weight staples more heavily."],
      ["Price only", "Freshness, grade, origin and shelf life were not assessed."],
    ];
    pts.forEach(([h, t], i) => {
      const x = 0.6 + (i % 2) * 6.2, y = 2.0 + Math.floor(i / 2) * 2.15;
      card(s, x, y, 5.9, 1.9);
      iconCircle(s, I.warn, x + 0.3, y + 0.3, 0.7, GOLD);
      s.addText(h, { x: x + 1.2, y: y + 0.25, w: 4.4, h: 0.5, fontFace: FONT, fontSize: 18, bold: true, color: INK, isTextBox: true, margin: 0 });
      s.addText(t, { x: x + 1.2, y: y + 0.8, w: 4.4, h: 1.0, fontFace: FONT, fontSize: 13, color: MUTED, isTextBox: true, margin: 0, valign: "top" });
    });
    footer(s);
    note(s, "The fine print", "0:40",
      `Now the fine print, because good evidence is honest about its limits. ` +
      `This is one snapshot: one visit per store in August. Promotions and seasonal swings aren't captured; mango prices in May could look very different. ` +
      `It covers thirty-six of Food First's ninety-five products, only those sold on an identical basis at all three stores. Berries, seasonings and sauces are missing. ` +
      `Every item counts equally, whereas a real family buys a lot more onions than dragonfruit. ` +
      `And we compared price only, not freshness, grade or origin. None of this overturns the result, but it tells us what to do next.`);
  }

  // =============================== 14. Where next + thank you
  {
    const s = base(true);
    title(s, "Where next?", true);
    const steps = [
      "Repeat the survey two or three more times across the year to test whether the gap holds.",
      "Record pack weights for per-unit items so more of the 95 products can be compared.",
      "Build a household-weighted “healthy basket” to express the saving in dollars per week.",
      "Share the findings with parents, schools and policymakers as a worked example.",
    ];
    steps.forEach((t, i) => {
      const y = 1.5 + i * 1.05;
      s.addShape(pres.shapes.OVAL, { x: 0.7, y: y + 0.08, w: 0.6, h: 0.6, fill: { color: GOLD }, line: { color: GOLD } });
      s.addText(String(i + 1), { x: 0.7, y: y + 0.08, w: 0.6, h: 0.6, fontFace: FONT, fontSize: 18, bold: true, color: GREEN, align: "center", valign: "middle", isTextBox: true, margin: 0 });
      s.addText(t, { x: 1.55, y, w: 6.6, h: 0.8, fontFace: FONT, fontSize: 17, color: WHITE, isTextBox: true, margin: 0, valign: "middle" });
    });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.7, y: 1.5, w: 4.0, h: 4.2, fill: { color: MOSS }, line: { color: MOSS }, rectRadius: 0.2 });
    s.addImage({ data: I.basketGreen, x: 9.9, y: 1.85, w: 1.6, h: 1.6 });
    s.addText("Thank you", { x: 8.9, y: 3.6, w: 3.6, h: 0.7, fontFace: FONT, fontSize: 30, bold: true, color: GREEN, align: "center", isTextBox: true, margin: 0 });
    s.addText("Questions welcome.\nFull report and workbook available from HSFB.", { x: 8.9, y: 4.35, w: 3.6, h: 1.1, fontFace: FONT, fontSize: 14, color: INK, align: "center", isTextBox: true, margin: 0 });
    s.addText("Ms. Daniella Clarke  |  Heart & Stroke Foundation of Barbados  |  2026", { x: 0.7, y: 6.3, w: 12, h: 0.4, fontFace: FONT, fontSize: 13, color: "DCE8D4", isTextBox: true, margin: 0 });
    note(s, "Where next? Thank you", "0:45",
      `So where next? Four things. Repeat the survey two or three more times across the year to see whether the gap holds through the seasons. Record pack weights for the per-unit items so we can bring more of the ninety-five products into the comparison. ` +
      `Build a household-weighted healthy basket, so we can say "this family saves X dollars a week" rather than quoting percentages. And share the findings, because this is a story worth telling. ` +
      `To sum up: on thirty-six like-for-like items, Food First was cheapest three times out of four, the typical item was about a quarter cheaper, and the biggest savings were on exactly the vegetables and staples we want on children's plates. ` +
      `Thank you for listening. The full report and workbook are available from the Foundation, and I'm happy to take questions.`);
  }

  await pres.writeFile({ fileName: OUT_PPTX });
  fs.writeFileSync(path.join(__dirname, "deck_script.json"), JSON.stringify(notes, null, 1));
  console.log("wrote", OUT_PPTX, "slides", notes.length, "words", notes.reduce((a, b) => a + b.text.split(/\s+/).length, 0));
})();
