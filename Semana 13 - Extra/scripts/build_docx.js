const fs = require('fs');
const path = require('path');
const {
  AlignmentType,
  Document,
  HeadingLevel,
  ImageRun,
  LevelFormat,
  Packer,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType,
} = require('docx');

const root = path.resolve(__dirname, '..');
const mdPath = path.join(root, 'ENTREGABLE.md');
const outPath = path.join(root, 'ENTREGABLE.docx');
const lines = fs.readFileSync(mdPath, 'utf8').split(/\r?\n/);
const children = [];

function inlineRuns(text) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter((part) => part !== '');
  return parts.map((part) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return new TextRun({ text: part.slice(2, -2), bold: true });
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return new TextRun({ text: part.slice(1, -1), font: 'Consolas', size: 18 });
    }
    return new TextRun({ text: part });
  });
}

function heading(line) {
  const level = line.match(/^(#+)/)[1].length;
  const map = { 1: HeadingLevel.HEADING_1, 2: HeadingLevel.HEADING_2, 3: HeadingLevel.HEADING_3 };
  children.push(new Paragraph({ heading: map[level] || HeadingLevel.HEADING_4, children: inlineRuns(line.slice(level + 1)) }));
}

function tableRow(line) {
  return line.split('|').slice(1, -1).map((cell) => cell.trim());
}

function isSeparator(line) {
  return /^\|[\s:\-|]+\|$/.test(line.trim());
}

function addTable(rows) {
  if (rows.length < 2) return;
  const cols = rows[0].length;
  const widths = Array.from({ length: cols }, () => Math.floor(9000 / cols));
  const tableRows = rows.map((cells, index) => {
    const padded = Array.from({ length: cols }, (_, i) => cells[i] || '');
    return new TableRow({
      tableHeader: index === 0,
      children: padded.map((cell) => new TableCell({
        width: { size: widths[0], type: WidthType.DXA },
        shading: index === 0 ? { type: ShadingType.CLEAR, fill: 'DCE6F1', color: 'auto' } : undefined,
        children: [new Paragraph({ children: inlineRuns(cell) })],
      })),
    });
  });
  children.push(new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: widths,
    rows: tableRows,
  }));
}

let i = 0;
while (i < lines.length) {
  const line = lines[i];
  const trimmed = line.trim();

  if (trimmed.startsWith('```')) {
    i += 1;
    const code = [];
    while (i < lines.length && !lines[i].trim().startsWith('```')) {
      code.push(lines[i]);
      i += 1;
    }
    code.forEach((text) => children.push(new Paragraph({
      children: [new TextRun({ text, font: 'Consolas', size: 18 })],
    })));
    children.push(new Paragraph({ children: [new TextRun({ text: '' })] }));
  } else if (/^#{1,6}\s/.test(trimmed)) {
    heading(trimmed);
  } else if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
    const rows = [];
    while (i < lines.length && lines[i].trim().startsWith('|')) {
      if (!isSeparator(lines[i])) rows.push(tableRow(lines[i]));
      i += 1;
    }
    addTable(rows);
    continue;
  } else if (/^[-*]\s/.test(trimmed)) {
    children.push(new Paragraph({
      numbering: { reference: 'bullets', level: 0 },
      children: inlineRuns(trimmed.slice(2)),
    }));
  } else if (trimmed === '') {
    children.push(new Paragraph({ children: [new TextRun({ text: '' })] }));
  } else {
    children.push(new Paragraph({ children: inlineRuns(trimmed) }));
    const imageMatch = trimmed.match(/`([^`]+\.png)`/);
    if (trimmed.includes('Captura del resultado') && imageMatch) {
      const imgPath = path.join(root, imageMatch[1]);
      if (fs.existsSync(imgPath)) {
        children.push(new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new ImageRun({
            type: 'png',
            data: fs.readFileSync(imgPath),
            transformation: { width: 520, height: 260 },
          })],
        }));
      }
    }
  }
  i += 1;
}

const doc = new Document({
  numbering: {
    config: [{
      reference: 'bullets',
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: '•',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } },
      }],
    }],
  },
  sections: [{ children }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outPath, buffer);
  console.log(`Wrote ${outPath} (${buffer.length} bytes)`);
});
