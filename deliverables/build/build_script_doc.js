const fs = require("fs");
const path = require("path");
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, AlignmentType, ShadingType, BorderStyle, TableLayoutType, VerticalAlign } = require("docx");

const notes = JSON.parse(fs.readFileSync(path.join(__dirname, "deck_script.json"), "utf8"));
const OUT = process.argv[2];
const FONT = "Calibri", GREEN = "2C5F2D", MUTED = "5C6B5C", PALE = "EEF4E8";
const run = (t, o = {}) => new TextRun({ text: t, font: FONT, size: 22, ...o });
const P = (children, o = {}) => new Paragraph({ spacing: { after: 140, line: 300 }, ...o, children: Array.isArray(children) ? children : [run(children)] });
const thin = { style: BorderStyle.SINGLE, size: 4, color: "D9D9D9" };
const borders = { top: thin, bottom: thin, left: thin, right: thin, insideHorizontal: thin, insideVertical: thin };

const toSec = (t) => { const [m, s] = t.split(":").map(Number); return m * 60 + s; };
const total = notes.reduce((a, b) => a + toSec(b.time), 0);
const words = notes.reduce((a, b) => a + b.text.split(/\s+/).length, 0);

function cell(text, w, o = {}) {
  return new TableCell({ width: { size: w, type: WidthType.DXA }, verticalAlign: VerticalAlign.TOP,
    shading: o.hdr ? { type: ShadingType.CLEAR, fill: GREEN, color: "auto" } : o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: "auto" } : undefined,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [new Paragraph({ spacing: { after: 0, line: 280 }, children: [new TextRun({ text, font: FONT, size: o.size || 20, bold: !!o.hdr || !!o.bold, color: o.hdr ? "FFFFFF" : "000000" })] })] });
}

const children = [
  new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "The Great Grocery Showdown", font: FONT, size: 40, bold: true, color: GREEN })] }),
  new Paragraph({ spacing: { after: 300 }, children: [new TextRun({ text: "Presenter script for the HSFB Food First price comparison deck", font: FONT, size: 24, color: MUTED })] }),
  P([run("Presenter: ", { bold: true }), run("Ms. Daniella Clarke, HSFB intern")]),
  P([run("Running time: ", { bold: true }), run(`about ${Math.floor(total / 60)}\u00bd minutes (${words} words at a relaxed 150 words per minute). Timings below are a guide; trim the "fine print" slide or the grocery slide if you are running long.`)]),
  P([run("How to use this: ", { bold: true }), run("Each slide's script is also in the PowerPoint speaker notes, so you can present from Presenter View. Edit either copy freely. Square brackets mark things to adapt on the day. The numbers are the beats to land; everything else can be said in your own words.")]),
  P([run("Tone: ", { bold: true }), run("conversational and a little playful. It's a showdown, so lean into the sport commentary: rounds, champions, rebels, the scoreboard. Keep the numbers precise and the delivery light.")]),
  new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 160 }, children: [new TextRun({ text: "Run of show", font: FONT, size: 28, bold: true, color: GREEN })] }),
  new Table({ width: { size: 9000, type: WidthType.DXA }, columnWidths: [700, 5300, 1500, 1500], layout: TableLayoutType.FIXED, borders, rows: [
    new TableRow({ tableHeader: true, children: [cell("#", 700, { hdr: true }), cell("Slide", 5300, { hdr: true }), cell("Time", 1500, { hdr: true }), cell("Cumulative", 1500, { hdr: true })] }),
    ...notes.map((n, i) => {
      const cum = notes.slice(0, i + 1).reduce((a, b) => a + toSec(b.time), 0);
      return new TableRow({ children: [cell(String(i + 1), 700), cell(n.title, 5300), cell(n.time, 1500), cell(`${Math.floor(cum / 60)}:${String(cum % 60).padStart(2, "0")}`, 1500)] });
    }),
  ] }),
  new Paragraph({ spacing: { after: 200 }, children: [] }),
  new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 160 }, children: [new TextRun({ text: "Script", font: FONT, size: 28, bold: true, color: GREEN })] }),
];
notes.forEach((n, i) => {
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 80 }, keepNext: true,
    children: [new TextRun({ text: `Slide ${i + 1}: ${n.title}`, font: FONT, size: 24, bold: true, color: GREEN }), new TextRun({ text: `   (${n.time})`, font: FONT, size: 20, color: MUTED })] }));
  // split into sentences for readability: paragraph per 2-3 sentences
  const sentences = n.text.match(/[^.!?]+[.!?]+["”]?\s*/g) || [n.text];
  for (let k = 0; k < sentences.length; k += 3) {
    children.push(P(sentences.slice(k, k + 3).join("").trim()));
  }
});
children.push(new Paragraph({ spacing: { before: 300 }, children: [new TextRun({ text: "All figures in this script match the companion workbook (36 like-for-like items, August 2026 prices).", font: FONT, size: 18, italics: true, color: MUTED })] }));

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 28, bold: true, color: GREEN }, paragraph: { spacing: { before: 300, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, color: GREEN }, paragraph: { spacing: { before: 280, after: 80 }, outlineLevel: 1 } },
    ] },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1200, left: 1300, right: 1300 } } }, children }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("wrote", OUT, "total seconds", total, "words", words); });
