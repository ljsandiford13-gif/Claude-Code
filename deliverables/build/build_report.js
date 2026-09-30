const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType,
  AlignmentType, ShadingType, BorderStyle, ImageRun, PageBreak, LevelFormat, Footer, Header,
  PageNumber, TableLayoutType, VerticalAlign,
} = require("docx");

const S = JSON.parse(fs.readFileSync(path.join(__dirname, "stats.json"), "utf8"));
const A = S.storeA, B = S.storeB;
const O = S.overall, C = S.cats;
const CH = (n) => fs.readFileSync(path.join(__dirname, "charts", n));
const OUT = process.argv[2];

const NAVY = "184F95", GREY = "F2F2F2", PALE_BLUE = "E3EEFB", PALE_RED = "FBE3E3", INK2 = "52514E";
const FONT = "Arial";

// ---------- helpers ----------
const pct = (x, d = 1) => (x > 0 ? "+" : x < 0 ? "−" : "") + (Math.abs(x) * 100).toFixed(d) + "%";
const pctPlain = (x, d = 1) => (x * 100).toFixed(d) + "%";
const money = (x) => x.toFixed(2);
const run = (t, o = {}) => new TextRun({ text: t, font: FONT, size: 20, ...o });
const P = (children, o = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, ...o, children: Array.isArray(children) ? children : [run(children)] });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160 }, children: [new TextRun({ text: t, font: FONT, size: 28, bold: true, color: NAVY })] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 }, children: [new TextRun({ text: t, font: FONT, size: 22, bold: true, color: NAVY })] });
const note = (t) => new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: t, font: FONT, size: 17, italics: true, color: INK2 })] });
const bullet = (t, ref = 0) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 80, line: 276 }, children: typeof t === "string" ? [run(t)] : t });
const bold = (t) => run(t, { bold: true });
const img = (name, w, h) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, children: [new ImageRun({ type: "png", data: CH(name), transformation: { width: w, height: h } })] });
const caption = (t) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: t, font: FONT, size: 17, italics: true, color: INK2 })] });

const thin = { style: BorderStyle.SINGLE, size: 4, color: "D9D9D9" };
const borders = { top: thin, bottom: thin, left: thin, right: thin, insideHorizontal: thin, insideVertical: thin };

function cell(text, w, o = {}) {
  const { hdr = false, align = AlignmentType.LEFT, fill = null, boldText = false, size = 18 } = o;
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    verticalAlign: VerticalAlign.CENTER,
    shading: hdr ? { type: ShadingType.CLEAR, fill: NAVY, color: "auto" } : fill ? { type: ShadingType.CLEAR, fill, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 80, right: 80 },
    children: [new Paragraph({ alignment: align, spacing: { after: 0 }, children: [new TextRun({ text: String(text), font: FONT, size, bold: hdr || boldText, color: hdr ? "FFFFFF" : "000000" })] })],
  });
}
function table(headers, rows, widths, opts = {}) {
  const { aligns = [], fills = null, size = 18 } = opts;
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, borders,
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true, children: headers.map((h, i) => cell(h, widths[i], { hdr: true, size, align: aligns[i] || AlignmentType.LEFT })) }),
      ...rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((v, i) => cell(v, widths[i], { size, align: aligns[i] || AlignmentType.LEFT, fill: fills ? fills(ri, i, v) : null, boldText: opts.boldRows && opts.boldRows.includes(ri) })) })),
    ],
  });
}
const spacer = () => new Paragraph({ spacing: { after: 120 }, children: [] });
const pctFill = (v) => (typeof v === "string" && v.startsWith("−")) ? PALE_BLUE : (typeof v === "string" && v.startsWith("+")) ? PALE_RED : null;

// ---------- content ----------
const CATS = ["Vegetables", "Fruits", "Grocery"];
const catLabel = (c) => c;
const items = S.items;
const inc = items.filter((d) => d.include === "Y");
const byItem = (n) => items.find((d) => d.item === n);
const mango = byItem("Mangoes"), redOnion = byItem("Red Onions"), jal = byItem("Jalapeno Peppers"), lemons = byItem("Lemons");

const ffCheapestPct = O.cheapest["Food First"] / O.n;

const doc = new Document({
  creator: "HSFB",
  title: "Food First Supermarket Price Comparison",
  styles: {
    default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 28, bold: true, color: NAVY }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 22, bold: true, color: NAVY }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1200, left: 1300, right: 1300 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Food First Supermarket Price Comparison  |  Heart & Stroke Foundation of Barbados", font: FONT, size: 16, color: INK2 })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Page ", font: FONT, size: 16, color: INK2 }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: INK2 })] })] }) },
    children: [
      // ---------- Title block ----------
      new Paragraph({ spacing: { before: 1200, after: 200 }, children: [new TextRun({ text: "FOOD FIRST SUPERMARKET PRICE COMPARISON", font: FONT, size: 44, bold: true, color: NAVY })] }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: `A like-for-like price analysis of Food First against two Barbados supermarkets`, font: FONT, size: 26, color: INK2 })] }),
      new Paragraph({ spacing: { after: 600 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY, space: 8 } }, children: [new TextRun({ text: "Revised and consolidated edition, verified 38-item like-for-like record", font: FONT, size: 20, italics: true, color: INK2 })] }),
      P([bold("Prepared for: "), run("Heart & Stroke Foundation of Barbados (HSFB)")]),
      P([bold("Prepared by: "), run("Ms. Clarke, HSFB intern")]),
      P([bold("Date: "), run("September 2026")]),
      P([bold("Companion file: "), run("Food_First_Price_Comparison_Workbook.xlsx (source record, formulas and charts)")]),
      spacer(),
      P([bold("Note on anonymity. "), run(`In keeping with HSFB's undertaking to the retailers who facilitated the price collection, the two supermarkets are not named in this report or its workbook. They are referred to as ${A} and ${B}. Food First is named because it is the subject of the comparison.`)]),

      // ---------- Executive summary ----------
      H1("Executive summary"),
      P(`This report compares Food First's prices for fresh produce and grocery items with the prices of the same items at two established Barbados supermarkets, using standardised, like-for-like unit prices. Of 42 items recorded, 38 could be compared on an identical price basis; four were excluded because the retailers price them on different bases. Every figure has been recomputed independently from the recorded shelf prices and matches the companion workbook.`),
      bullet([bold("Food First was the cheapest of the three stores for "), run(`${O.cheapest["Food First"]} of ${O.n} items (${pctPlain(ffCheapestPct, 0)}). `), run(`${A} was cheapest for ${O.cheapest[A]} items and ${B} for ${O.cheapest[B]}.`)]),
      bullet([bold("Typical saving. "), run(`The median item was ${pctPlain(-O.medA)} cheaper at Food First than at ${A} and ${pctPlain(-O.medB)} cheaper than at ${B}. Means were ${pct(O.meanA)} and ${pct(O.meanB)}, pulled toward zero by a few items where Food First is much dearer.`)]),
      bullet([bold("Strongest in vegetables and grocery. "), run(`Food First was cheaper than both supermarkets on ${C.Vegetables.both} of ${C.Vegetables.n} vegetables (median ${pct(C.Vegetables.medA)} vs ${A}, ${pct(C.Vegetables.medB)} vs ${B}) and on ${C.Grocery.both} of ${C.Grocery.n} grocery items (median ${pct(C.Grocery.medA)} and ${pct(C.Grocery.medB)}).`)]),
      bullet([bold("Fruit is mixed. "), run(`Food First was cheaper on ${C.Fruits.both} of ${C.Fruits.n} fruit items but markedly dearer on Mangoes (${pct(mango.ff_a, 0)} vs ${A}), Red Apples and Blueberries. Outside fruit, Cucumbers and Pepper Mash were also dearer at Food First.`)]),
      bullet([bold("Indicative basket. "), run(`Summing the 38 standardised prices gives BBD ${money(O.sumFF)} at Food First, BBD ${money(O.sumA)} at ${A} and BBD ${money(O.sumB)} at ${B}: ${pct(O.basketA)} and ${pct(O.basketB)} respectively.`)]),
      bullet([bold("The two supermarkets are close to each other. "), run(`Across the 38 items the mean difference between ${A} and ${B} was ${pct(O.meanAB)}; ${A} was cheaper on ${O.ltAB} items and ${B} on ${O.gtAB}.`)]),
      P(`For HSFB the practical message is that, at the time of the survey, a supplier importing directly from the EU offered whole foods, and especially everyday vegetables, at prices at or below the supermarket benchmark. Price is not the only barrier to a healthier diet, but on this evidence it need not be the binding one for these items.`),

      // ---------- 1 Background ----------
      H1("1. Background and context"),
      P(`Barbados is fighting a sustained battle against non-communicable diseases (NCDs). NCDs accounted for an estimated 82.8% of all deaths in 2019 [1], and the Ministry of Health and Wellness has put the figure at around 80% [2]. Their economic burden has been estimated at between $375 million and $825 million a year, with NCD care absorbing roughly 70% of the Queen Elizabeth Hospital's operating budget [3]. Two in three Barbadians aged 15 and over (67.2% in 2022) are overweight or obese [1].`),
      P(`The trend begins in childhood. HSFB and the Barbados Childhood Obesity Prevention Coalition report that an estimated 42% of children in Barbados are now overweight or obese, up from 33% in earlier surveys [4][5]. Childhood obesity is directly linked to the onset of diabetes, hypertension, heart disease and some cancers later in life, which is why HSFB continues to urge parents to increase their children's intake of whole foods, including fresh fruit and vegetables [5].`),
      P(`Affordability shapes what families buy. Barbados imports roughly 85% of the food it consumes [6], and food made up 22.7% of all goods imports in 2024 [7]. The Central Bank of Barbados reports that food-related inflation has contributed significantly to price increases over the past two years, with vegetables, dairy, eggs and meats among the categories rising fastest; food and non-alcoholic beverages carry about 30% of the weight in the consumer price basket [8]. Against that backdrop, any supply channel that brings whole foods to market at lower prices is directly relevant to HSFB's nutrition advocacy.`),
      P(`Food First is a Barbados-based supplier that imports fruit, vegetables and a small grocery range directly from the European Union, offering an alternative to the established supermarket chains. This study asks whether that channel is, in practice, cheaper for the consumer.`),

      // ---------- 2 Aim ----------
      H1("2. Aim and hypotheses"),
      P([bold("Aim. "), run(`To determine whether Food First's prices for matched fresh-produce and grocery items are, on average, higher or lower than the prices of the same items at two Barbados supermarkets, overall and by category (Vegetables, Fruits, Grocery), using standardised, like-for-like unit prices.`)]),
      P([bold("H₁ (research hypothesis). "), run(`Food First's standardised prices for matched items are, on average, lower than those of the two supermarkets, reflecting a pricing advantage from direct EU import and a shorter supply chain.`)]),
      P([bold("H₀ (null hypothesis). "), run(`There is no consistent difference between Food First's prices and the supermarkets' prices across the matched items.`)]),
      P(`A secondary expectation was that any advantage would be strongest for everyday vegetables and staple grocery items, and weakest, or reversed, for premium or delicate imported fruit.`),

      // ---------- 3 Methods ----------
      H1("3. Data and methods"),
      H2("3.1 Data collection"),
      P(`Shelf prices were recorded in person by the HSFB intern during store visits over the holiday period, as a single point-in-time snapshot. For each item the product, pack size or unit sold, and displayed shelf price were recorded at Food First and at both supermarkets. No product photographs were taken. Promotional prices were not separated from list prices. The collection date should be added to the workbook's Read Me tab for the record.`),
      H2("3.2 Standardised prices"),
      P(`Every comparison is made on the same basis: BBD per kilogram, per litre, per unit, per head, per pack or per dozen, matching how Food First sells the product. Where a supermarket pack differed, the shelf price was divided by the pack quantity expressed in the basis unit. For example, a 340 g pack of jalapeños at BBD ${money(jal.b_shelf)} is BBD ${money(jal.b)} per kg (${money(jal.b_shelf)} ÷ 0.34), and a 1 lb pack of carrots at BBD 3.89 is BBD 8.58 per kg (3.89 ÷ 0.4536). Each pack quantity is shown beside its shelf price in the workbook so that every conversion can be checked.`),
      P(`Three conversions rest on stated assumptions: lemons and limes at ${A} are sold per kg and were converted to a per-fruit price at an assumed 10 fruit per kg; the Food First strawberry "unit" was taken to be the same 1 lb pack sold by both supermarkets; and pepper mash was converted at 26 oz = 0.7371 kg and 750 ml = 0.75 kg.`),
      H2("3.3 Matching rules and exclusions"),
      P(`Items were matched on the same product at each store. An item was included only when all three prices could be placed on an identical basis. Four of the 42 recorded items failed that test and are excluded from every statistic. They remain visible in the workbook, flagged N with the reason, and would re-enter the analysis automatically if the flag were changed once the source data is corrected.`),
      table(["Excluded item", "Reason"], S.excluded.map((d) => [d.item, d.note.replace("EXCLUDED: ", "")]), [2400, 6900]),
      note(`Two further items compare per-head or per-pack prices where the retailers' pack weights differ slightly (Romaine Lettuce, sold as one head; Strawberries, sold as a 1 lb pack). Both are included because that is the unit the consumer actually buys.`),
      H2("3.4 Price difference"),
      P([run(`For every included item and each pair of stores:  `), run(`% difference = (Food First price − Comparator price) ÷ Comparator price × 100`, { italics: true })]),
      P(`A negative value means Food First is cheaper; a positive value means Food First is more expensive. The same formula compares ${A} with ${B} directly. Both the mean and the median difference are reported: the median describes the typical item, while the mean is sensitive to a few very large gaps.`),
      H2("3.5 Verification and changes from the previous edition"),
      P(`Every standardised price, percentage difference, count, mean, median and basket total in this report was recomputed independently in Python from the recorded shelf prices and compared with the workbook's formulas; all 42 rows and every summary figure agree exactly. Three corrections were made to the earlier edition:`),
      bullet(`The earlier report treated all 42 items as like-for-like. Four are not (Section 3.3) and are now excluded. This reduces the headline mean saving slightly (from −17.7% to ${pct(O.meanA)} against ${A}) but does not change the direction of any finding.`),
      bullet(`Lemons and limes used rough estimates in the earlier report (lemons at 13.20 per kg; limes compared per fruit against per-kg prices, giving a spurious −91%). They now use the workbook's recorded values on a per-fruit basis.`),
      bullet(`The workbook's summary and category tabs still carried figures from an earlier 78-product dataset. They have been rebuilt as live formulas over the 42-item record, and the broken Healthy Basket tab has been removed.`),

      // ---------- 4 Results ----------
      H1("4. Results"),
      H2("4.1 Overall comparison"),
      table(["Metric", `Food First vs ${A}`, `Food First vs ${B}`],
        [
          ["Items compared (like-for-like)", O.n, O.n],
          ["Food First cheaper (items)", O.ltA, O.ltB],
          ["Same price (items)", O.eqA, O.eqB],
          ["Food First more expensive (items)", O.gtA, O.gtB],
          ["Share of items where Food First is cheaper", pctPlain(O.ltA / O.n, 0), pctPlain(O.ltB / O.n, 0)],
          ["Mean % difference", pct(O.meanA), pct(O.meanB)],
          ["Median % difference", pct(O.medA), pct(O.medB)],
          ["Largest saving at Food First", pct(O.minA), pct(O.minB)],
          ["Largest premium at Food First", pct(O.maxA), pct(O.maxB)],
          ["Matched-basket total, Food First (BBD)", money(O.sumFF), money(O.sumFF)],
          ["Matched-basket total, comparator (BBD)", money(O.sumA), money(O.sumB)],
          ["Basket-total difference", pct(O.basketA), pct(O.basketB)],
        ], [4300, 2500, 2500], { aligns: [AlignmentType.LEFT, AlignmentType.RIGHT, AlignmentType.RIGHT], fills: (r, c, v) => (c > 0 ? pctFill(v) : null) }),
      note(`Blue shading = Food First cheaper; red shading = Food First dearer. Between the two supermarkets, ${A} was cheaper on ${O.ltAB} items and ${B} on ${O.gtAB} (mean ${pct(O.meanAB)}, median ${pct(O.medAB)}, negative = ${A} cheaper).`),
      P(`Food First was the single cheapest of the three stores for ${O.cheapest["Food First"]} of ${O.n} items (${pctPlain(ffCheapestPct, 0)}); ${A} was cheapest for ${O.cheapest[A]} and ${B} for ${O.cheapest[B]}.`),
      img("chart_cheapest.png", 440, 194),
      caption("Figure 1. Number of items for which each store had the lowest standardised price (38 like-for-like items)."),

      H2("4.2 Comparison by category"),
      table(["Category", "Listed", "Compared", "Mean vs Store A", "Median vs Store A", "Mean vs Store B", "Median vs Store B", "FF cheaper than both"],
        [...CATS.map((c) => [c, C[c].listed, C[c].n, pct(C[c].meanA), pct(C[c].medA), pct(C[c].meanB), pct(C[c].medB), `${C[c].both} of ${C[c].n}`]),
         ["All", items.length, O.n, pct(O.meanA), pct(O.medA), pct(O.meanB), pct(O.medB), `${O.both} of ${O.n}`]],
        [1300, 750, 950, 1200, 1200, 1200, 1200, 1300],
        { size: 16, aligns: [AlignmentType.LEFT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.RIGHT], fills: (r, c, v) => (c >= 3 && c <= 6 ? pctFill(v) : null), boldRows: [3] }),
      note(`Store A = ${A}, Store B = ${B}. Category labels follow the source record: tomatoes, sweet peppers and jalapeños are listed under Fruits and local onions under Grocery. No seasonings or herbs could be compared because no supermarket prices were recorded for that category.`),
      img("chart_category.png", 600, 250),
      caption("Figure 2. Mean and median price difference by category, Food First relative to each supermarket."),

      H2("4.3 Matched-basket total"),
      P(`Summing the standardised prices of the 38 included items gives an indicative basket for each store. It is an equal-weighted sum of unit prices rather than a realistic weekly shop, but it shows the cumulative effect of the item-level differences.`),
      img("chart_basket.png", 440, 211),
      caption(`Figure 3. Sum of standardised prices, 38 included items. Food First ${pct(O.basketA)} vs ${A} and ${pct(O.basketB)} vs ${B}.`),

      H2("4.4 Item-level results"),
      P(`Figure 4 ranks the 38 included items by their difference against ${A}. The picture is consistent: a long run of items where Food First is 20% to 75% cheaper, a middle band of near-parity, and a short tail where Food First is clearly dearer: Pepper Mash, Cucumbers, Red Apples and Mangoes against both supermarkets, and Blueberries against ${B}.`),
      img("chart_items.png", 560, 700),
      caption("Figure 4. Item-level price difference for the 38 like-for-like items, sorted by difference against Supermarket A."),

      P([bold("Full item-level record. "), run(`Standardised prices in BBD on the basis shown; Store A = ${A}, Store B = ${B}. Excluded items are listed for completeness with no percentages.`)]),
      table(["Category", "Item", "Basis", "Food First", "Store A", "Store B", "FF vs A", "FF vs B", "Cheapest"],
        CATS.flatMap((c) => items.filter((d) => d.cat === c).sort((x, y) => x.item.localeCompare(y.item)).map((d) => [
          d.cat, d.item, d.basis, money(d.ff), money(d.a), money(d.b),
          d.include === "Y" ? pct(d.ff_a) : "excluded", d.include === "Y" ? pct(d.ff_b) : "excluded", d.include === "Y" ? d.cheapest : "—",
        ])),
        [1100, 1650, 850, 750, 850, 850, 900, 900, 1300],
        { size: 16, aligns: [AlignmentType.LEFT, AlignmentType.LEFT, AlignmentType.LEFT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.LEFT],
          fills: (r, c, v) => (v === "excluded" || v === "—" ? GREY : c === 6 || c === 7 ? pctFill(v) : null) }),
      note(`Blackberries, Red Currants, Pineapple and Baby Spinach are excluded because Food First and the supermarkets price them on different bases (see Section 3.3); their supermarket prices are shown on the supermarkets' own basis.`),

      // ---------- 5 Worked examples ----------
      H1("5. Worked examples"),
      P([bold("5.1 Percentage difference. "), run(`Red Onions: Food First BBD ${money(redOnion.ff)} per kg, ${A} BBD ${money(redOnion.a)} per kg.`)]),
      P([run(`% difference = (${money(redOnion.ff)} − ${money(redOnion.a)}) ÷ ${money(redOnion.a)} × 100 = ${pct(redOnion.ff_a)}`, { italics: true })]),
      P(`Food First's red onions were ${pctPlain(-redOnion.ff_a)} cheaper per kilogram than ${A}'s.`),
      P([bold("5.2 A pack-size conversion. "), run(`${B} sells jalapeño peppers in a 340 g pack at BBD ${money(jal.b_shelf)}. Standardised price = ${money(jal.b_shelf)} ÷ 0.340 = BBD ${money(jal.b)} per kg. Against Food First's BBD ${money(jal.ff)} per kg:`)]),
      P([run(`% difference = (${money(jal.ff)} − ${money(jal.b)}) ÷ ${money(jal.b)} × 100 = ${pct(jal.ff_b)}`, { italics: true })]),
      P([bold("5.3 A unit conversion resting on an assumption. "), run(`${A} sells lemons at BBD ${money(lemons.a_shelf)} per kg. At an assumed 10 lemons per kg this is BBD ${money(lemons.a)} per lemon, against Food First's BBD ${money(lemons.ff)}: ${pct(lemons.ff_a)}. If the true count were 8 per kg the ${A} price would be BBD 1.50 and Food First's advantage would widen to −33%; at 12 per kg it would narrow to 0%. The assumption is flagged in the workbook so it can be replaced with a weighed count.`)]),
      P([bold("5.4 Basket total. "), run(`Food First BBD ${money(O.sumFF)}, ${A} BBD ${money(O.sumA)}: (${money(O.sumFF)} − ${money(O.sumA)}) ÷ ${money(O.sumA)} × 100 = ${pct(O.basketA)}.`)]),
      P([bold("5.5 Mean versus median. "), run(`Against ${A} the mean difference is ${pct(O.meanA)} but the median is ${pct(O.medA)}. The gap is caused by Mangoes (${pct(mango.ff_a)}), Red Apples (${pct(byItem("Red Apples").ff_a)}) and Cucumbers (${pct(byItem("Cucumbers").ff_a)}), whose large premiums pull the average toward zero. The median is unaffected by them and is the better guide to a typical item.`)]),

      // ---------- 6 Discussion ----------
      H1("6. Discussion"),
      P(`The results support H₁. Food First was the cheapest of the three stores for ${pctPlain(ffCheapestPct, 0)} of like-for-like items, was cheaper than ${A} on ${O.ltA} of ${O.n} items and cheaper than ${B} on ${O.ltB}, and its typical price sat a fifth to a quarter below both benchmarks (median ${pct(O.medA)} and ${pct(O.medB)}). The two supermarkets, by contrast, were close to one another on average, so the Food First result is not an artefact of one unusually expensive comparator.`),
      P(`The advantage was strongest and most consistent in vegetables. Food First was cheaper than both supermarkets on ${C.Vegetables.both} of ${C.Vegetables.n} vegetables, with savings of 43% to 66% against both supermarkets on cabbage, zucchini, red onions and pumpkin, and 53% on carrots against ${A}. Cucumbers were the lone exception, at roughly half as much again as the supermarket price. Grocery items followed the same pattern, with whole milk and creams 41% to 52% cheaper, and oat milk and eggs at near-parity with ${A}; pepper mash was the only grocery item where Food First was clearly dearer.`),
      P(`Fruit was mixed. Food First held a clear advantage on apples (Gala and green), pears, oranges, watermelon and dragonfruit, was at or a little below ${A}'s price on grapes, strawberries and tomatoes, and was markedly dearer on mangoes, red apples and blueberries against both supermarkets, and modestly dearer on kiwis, grapefruit and sweet peppers against ${A}. Several of the dearer items are tropical fruit that the supermarkets can source regionally or locally, while Food First imports from Europe; the pattern is consistent with the secondary expectation that an EU-import channel is least competitive on produce that grows nearby.`),
      P(`For HSFB's nutrition advocacy the relevance is direct. The vegetables on which Food First was cheapest, including cabbage, carrots, pumpkin, onions, zucchini, cauliflower and lettuce, are exactly the whole foods that HSFB encourages families to put on children's plates in place of ultra-processed alternatives. With 42% of children overweight or obese and food inflation concentrated in vegetables, dairy and eggs [4][8], evidence that an alternative channel supplies these staples at lower prices strengthens the case that healthier eating can be made affordable, and gives HSFB a concrete example to cite in its work with parents, schools and policymakers.`),

      H1("7. Limitations"),
      bullet(`Single snapshot. Prices reflect one visit to each store. Promotions could not be distinguished from list prices, and seasonal movements in produce prices are not captured. Repeat visits would be needed to test whether the differences persist.`),
      bullet(`Coverage. The record contains 42 items, of which 38 were comparable; seasonings and herbs are absent because no supermarket prices were recorded for them. The excluded items include the berries and stone fruit where Food First's positioning may differ most.`),
      bullet(`Unit assumptions. Four items rely on stated assumptions (lemons, limes, strawberries, pepper mash; Section 3.2). Weighing a sample at the point of sale would remove this uncertainty.`),
      bullet(`Equal weighting. Means, medians and the basket total treat every item as equally important. A household-weighted basket, using typical purchase quantities, would give a better estimate of the saving on an actual weekly shop.`),
      bullet(`Quality and origin were not assessed. The comparison is on price alone; freshness, grade, country of origin and shelf life were not recorded.`),

      H1("8. Conclusion and recommendations"),
      P(`Across 38 verified, like-for-like items, Food First was the cheapest of the three retailers for ${O.cheapest["Food First"]} items (${pctPlain(ffCheapestPct, 0)}) and was, on both a mean and a median basis, meaningfully cheaper than either supermarket, with a typical saving of about a fifth to a quarter. The research hypothesis is supported. The advantage is broad-based across vegetables and grocery staples and weaker, or reversed, for a small group of mostly tropical fruit.`),
      P(`Recommended next steps:`),
      bullet(`Record the collection date and, for lemons, limes and strawberries, weigh or count a sample so the remaining unit assumptions can be replaced with measurements.`),
      bullet(`Re-check the Food First blackberry price and the pack weights for baby spinach, red currants and pineapple so the four excluded items can be brought into the comparison.`),
      bullet(`Repeat the survey at two or three further dates across the year, using the same workbook, to test whether the price advantage is stable.`),
      bullet(`Add a household-weighted "healthy basket" of the vegetables and staples HSFB promotes, so the saving can be expressed as dollars per week for a typical family.`),

      H1("References"),
      ...[
        `[1] Pan American Health Organization, Health in the Americas country profile: Barbados. NCDs 82.8% of deaths (2019); overweight and obesity 67.2% of persons aged 15+ (2022). https://hia.paho.org/en/node/191`,
        `[2] Government of Barbados, Ministry of Health and Wellness, press release "NCD Statistics Still A Major Concern To Government". https://health.gov.bb/News/Press-Releases/NCD-Statistics-Still-A-Major-Conce`,
        `[3] Central Bank of Barbados, Caribbean Economic Forum, "Managing the Costs of and Economic Fallout from Non-Communicable Diseases in the Caribbean". https://www.centralbank.org.bb/news/caribbean-economic-forum/managing-the-costs-of-and-economic-fallout-from-non-communicable-diseases-in-the-caribbean`,
        `[4] Barbados Today, 10 June 2026, "Enough is enough, say advocates as childhood obesity climbs" (Heart & Stroke Foundation of Barbados campaign launch; 42% of children overweight or obese, up from 33%). https://barbadostoday.bb/2026/06/10/enough-is-enough-say-advocates-as-childhood-obesity-climbs/`,
        `[5] Heart & Stroke Foundation of Barbados, correspondence to participating retailers introducing the price study, 2026; and Childhood Obesity Prevention Programme. https://hsfbarbados.org/the-childhood-obesity-prevention-program/`,
        `[6] Food and Agriculture Organization of the United Nations, "State of Food Insecurity in SIDS and Vision for the Future" (Barbados imports about 85% of its food). https://sustainabledevelopment.un.org/content/documents/19516Session%201%20Ms.%20Semedo%20Presentation%20%20FAO.pdf`,
        `[7] World Bank, World Development Indicators via CEIC: Barbados food imports as % of merchandise imports, 22.7% (2024). https://www.ceicdata.com/en/barbados/imports/bb-imports--of-goods-imports-food`,
        `[8] Central Bank of Barbados, "Factors Influencing Barbados' Inflation Rates", as reported in Nation News, 13 February 2026, "Food-related inflation impacts prices". https://www.centralbank.org.bb/news/general-press-release/factors-influencing-barbados-inflation-rates`,
      ].map((t) => new Paragraph({ spacing: { after: 100 }, indent: { left: 400, hanging: 400 }, children: [new TextRun({ text: t, font: FONT, size: 17 })] })),
      note(`Web references were located through search-engine summaries in September 2026; the figures quoted should be spot-checked against the source pages before publication.`),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT); });
