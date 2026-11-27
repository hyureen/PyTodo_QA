// Small helper layer over docx-js for the PyTodo Pro QA report.
const fs = require("fs");
const {
  Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, ImageRun, PageBreak, LevelFormat,
} = require("docx");

const FONT = "Times New Roman";
const CONTENT_W = 9026; // A4 with 2.54 cm margins (11906 - 2*1440)
const STATUS_FILL = { Pass: "E3F4E3", Fail: "FBE3E3", "Not Run": "EEEEEE", Blocked: "FFF3D6",
  Critical: "F6C9C9", Major: "FBE3E3", Moderate: "FFF3D6", Minor: "EEF4FB",
  High: "FBE3E3", Medium: "FFF3D6", Low: "EEF4FB", Covered: "E3F4E3", GAP: "FBE3E3" };

// "**bold** and `code`" -> runs
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0, m;
  const s = String(text);
  while ((m = re.exec(s))) {
    if (m.index > last) out.push(new TextRun({ text: s.slice(last, m.index), font: FONT, ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, font: FONT, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), font: "Courier New", size: (base.size || 24) - 4, ...base, }));
    last = m.index + t.length;
  }
  if (last < s.length) out.push(new TextRun({ text: s.slice(last), font: FONT, ...base }));
  return out;
}

const P = (text, opts = {}) => new Paragraph({ children: runs(text, opts.run || {}), spacing: { before: 80, after: 120, line: 252 },
  alignment: opts.align || AlignmentType.JUSTIFIED, keepNext: opts.keepNext });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })], pageBreakBefore: true });
const H1nb = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })] });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text: t, font: FONT })] });
const bullets = (items, level = 0) => items.map((t) => new Paragraph({ children: runs(t), numbering: { reference: "bul", level },
  spacing: { after: 40, line: 252 } }));
const numbered = (items, ref = "num") => items.map((t) => new Paragraph({ children: runs(t), numbering: { reference: ref, level: 0 },
  spacing: { after: 40, line: 252 } }));
const { SimpleField } = require("docx");
const SEQ_COUNT = { Table: 0, Figure: 0 };
// Captions use Word SEQ fields so the List of Tables / Figures can be generated automatically.
const seqCaption = (label, t, keepNext) => new Paragraph({ style: "Caption", keepNext,
  alignment: label === "Figure" ? AlignmentType.CENTER : AlignmentType.LEFT,
  spacing: label === "Figure" ? { before: 60, after: 200 } : { before: 160, after: 60 },
  children: [new TextRun({ text: `${label} `, font: FONT, size: 20, bold: true }),
    (() => { SEQ_COUNT[label] += 1; return new SimpleField(`SEQ ${label} \\* ARABIC`, String(SEQ_COUNT[label])); })(),
    new TextRun({ text: `: ${t}`, font: FONT, size: 20, bold: label === "Table" })] });
const caption = (t) => seqCaption("Figure", t, false);
const tcap = (t) => seqCaption("Table", t, true);
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

function pngSize(path) {
  const b = fs.readFileSync(path);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function img(path, widthPt = 400, cap) {
  const { w, h } = pngSize(path);
  const width = Math.round(widthPt * 1.333);
  const height = Math.round(width * h / w);
  const out = [new Paragraph({ children: [new ImageRun({ type: "png", data: fs.readFileSync(path),
    transformation: { width, height }, altText: { title: cap || "figure", description: cap || "figure", name: "fig" } })],
    alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120 } })];
  if (cap) out.push(caption(cap));
  return out;
}

const border = { style: BorderStyle.SINGLE, size: 4, color: "C9C8C2" };
const borders = { top: border, bottom: border, left: border, right: border };

// headers: array of strings; rows: array of arrays; widths: relative numbers
function table(headers, rows, widths, opts = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cols = widths.map((w) => Math.floor((w / total) * CONTENT_W));
  cols[cols.length - 1] += CONTENT_W - cols.reduce((a, b) => a + b, 0);
  const size = opts.size || 20;
  const fillCols = opts.fillCols || [];
  const cell = (text, i, header) => {
    const val = text === null || text === undefined ? "" : String(text);
    const fill = header ? "1B3A5C" : (fillCols.includes(i) && STATUS_FILL[val] ? STATUS_FILL[val] : (opts.zebra ? undefined : undefined));
    return new TableCell({
      width: { size: cols[i], type: WidthType.DXA }, borders,
      shading: fill ? { fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
      margins: { top: 30, bottom: 30, left: 70, right: 70 },
      children: val.split("\n").map((line) => new Paragraph({ children: runs(line, { size, bold: header, color: header ? "FFFFFF" : undefined }),
        spacing: { after: 0, line: 228 } })),
    });
  };
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: cols,
    rows: [new TableRow({ tableHeader: true, cantSplit: true, children: headers.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, i, false)) }))],
  });
}

const spacer = () => new Paragraph({ children: [], spacing: { after: 80 } });

const numberingConfig = {
  config: [
    { reference: "bul", levels: [
      { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
      { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1000, hanging: 270 } } } }] },
    ...["num", "num2", "num3", "num4", "num5", "num6", "num7", "num8"].map((ref) => ({ reference: ref, levels: [
      { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] })),
  ],
};

module.exports = { tcap, seqCaption, P, H1, H1nb, H2, H3, bullets, numbered, caption, img, table, pageBreak, spacer, runs, numberingConfig, FONT, CONTENT_W };
