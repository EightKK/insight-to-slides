#!/usr/bin/env python3
"""Render a PDF/PPTX to page PNGs, a contact sheet and conservative text-layer heuristics.

Usage: python3 scripts/render_review.py deck.pptx|deck.pdf --out QA_DIR [--dpi 150]

Uses PyMuPDF and Pillow; PPTX input is converted with LibreOffice (soffice or
libreoffice on PATH, or the SOFFICE environment variable). Heuristic findings are
reported for review; they do not change the exit code (0 = rendered, 1 = error).
Does not perform OCR, semantic evaluation, image overlap detection, or human comprehension tests.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_PASS, Parser, dumps, load_pymupdf, run, write_text

fitz = load_pymupdf()
from PIL import Image, ImageDraw  # noqa: E402


def find_office():
    """Locate the LibreOffice CLI (soffice on Windows/macOS, often libreoffice on Linux)."""
    for candidate in (os.environ.get('SOFFICE'), 'soffice', 'libreoffice',
                      r'C:\Program Files\LibreOffice\program\soffice.exe',
                      '/Applications/LibreOffice.app/Contents/MacOS/soffice'):
        if candidate and (shutil.which(candidate) or Path(candidate).is_file()):
            return shutil.which(candidate) or candidate
    raise ValueError('LibreOffice not found: install it or set SOFFICE to the soffice executable')


def convert_pptx(path: Path, out: Path) -> Path:
    with tempfile.TemporaryDirectory(prefix='lo_profile_') as profile:
        subprocess.run([find_office(), f'-env:UserInstallation={Path(profile).resolve().as_uri()}',
                        '--headless', '--convert-to', 'pdf', '--outdir', str(out), str(path)],
                       check=True, capture_output=True, timeout=180)
    return out / (path.stem + '.pdf')


def low_contrast_vector_text(page, tolerance=.20):
    """Warn if text shares a near-identical color with an overlapping filled shape.

    Uses the exported PDF vector graphics and text layer. This is intentionally
    narrow: no OCR, no bitmap background analysis, and not a WCAG contrast audit.
    """
    import math
    fills=[]
    for item in page.get_drawings():
        rect,col=item['rect'],item.get('fill')
        if (col and rect.width>=24 and rect.height>=10 and
                max(col)-min(col) >= .15 and rect.get_area() < .22 * page.rect.get_area()):
            fills.append((rect,tuple(float(x) for x in col)))
    warnings=[]
    for block in page.get_text('dict')['blocks']:
        for ln in block.get('lines',[]):
            for sp in ln.get('spans',[]):
                t=sp.get('text','').strip()
                if not t:continue
                box=fitz.Rect(sp['bbox'])
                rgb=sp.get('color',0)
                ink=((rgb>>16 & 255)/255.,(rgb>>8 & 255)/255.,(rgb & 255)/255.)
                for rect,col in fills:
                    overlap=box & rect
                    if overlap.is_empty or overlap.get_area()/max(1,box.get_area())<.16:continue
                    distance=math.sqrt(sum((a-b)**2 for a,b in zip(ink,col)))
                    if distance<=tolerance:
                        warnings.append({'text':t[:46], 'overlap_fraction':round(overlap.get_area()/max(1,box.get_area()),2),
                                         'ink_fill_color_distance':round(distance,3)})
                        break
    return warnings


def render_file(path, out, dpi=150):
    path, out = Path(path).resolve(), Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    pdf = path
    if path.suffix.lower() == '.pptx':
        pdf = convert_pptx(path, out)
    if pdf.suffix.lower() != '.pdf' or not pdf.exists():
        raise ValueError('Expected an existing PPTX or PDF')

    doc = fitz.open(pdf)
    if len(doc) == 0:
        raise ValueError('PDF has no pages')
    pages = []
    images = []
    for idx, p in enumerate(doc):
        img_path = out / f'page-{idx + 1:02d}.png'
        pix = p.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
        pix.save(img_path)
        with Image.open(img_path) as raw:
            img = raw.convert('RGB')
        images.append(img)
        spans = []
        boxes_for_overlap = []
        clip_warnings = []
        small_spans = []
        for block_index, b in enumerate(p.get_text('dict')['blocks']):
            for line_index, line in enumerate(b.get('lines', [])):
                for s in line.get('spans', []):
                    txt = s['text'].strip()
                    if not txt:
                        continue
                    box = fitz.Rect(s['bbox'])
                    if box.x0 < -1 or box.y0 < -1 or box.x1 > p.rect.width + 1 or box.y1 > p.rect.height + 1:
                        clip_warnings.append({'text': txt[:50], 'bbox': list(box)})
                    if s['size'] < 9.0:
                        small_spans.append({'text': txt[:50], 'size_pt': round(s['size'], 1)})
                    spans.append({'text': txt, 'size_pt': round(s['size'], 1), 'bbox': list(box)})
                    boxes_for_overlap.append((block_index, line_index, txt, box))
        collisions=[]
        for a_i, a in enumerate(boxes_for_overlap):
            for b_item in boxes_for_overlap[a_i+1:]:
                if a[:2] == b_item[:2]:
                    continue
                overlap = a[3] & b_item[3]
                if overlap.get_area() <= 2 or overlap.width <= 2 or overlap.height <= 2:
                    continue
                portion = overlap.get_area() / max(1, min(a[3].get_area(), b_item[3].get_area()))
                if portion > 0.28:
                    collisions.append({'texts':[a[2][:42],b_item[2][:42]],'overlap_fraction':round(portion,3)})
        low_contrast=low_contrast_vector_text(p)
        pages.append({'page': idx+1, 'file': str(img_path), 'span_count': len(spans),
                      'low_contrast_shape_text_warnings':low_contrast,
                      'text_overlap_warnings':collisions,
                      'page_outside_text': clip_warnings, 'small_text_under_9pt': small_spans,
                      'min_text_pt': min((v['size_pt'] for v in spans), default=None)})
    doc.close()
    columns = 2 if len(images) < 4 else 3
    thumbw = 560
    thumbh = int(thumbw * (images[0].height / images[0].width)) if images else 315
    pad = 22
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new('RGB', (columns * (thumbw + pad) + pad, rows * (thumbh + pad + 28) + pad), '#EAF0F4')
    draw = ImageDraw.Draw(sheet)
    for i, img in enumerate(images):
        x = pad+(i%columns)*(thumbw+pad)
        y = pad+(i//columns)*(thumbh+pad+28)
        sheet.paste(img.resize((thumbw,thumbh),Image.Resampling.LANCZOS),(x,y))
        draw.text((x,y+thumbh+3), f'PAGE {i+1:02d}',fill='#263649')
    contact = out / 'contact-sheet.png'
    sheet.save(contact)
    # Full render plus half-sized thumbnail for narrative review, without pretending to time human understanding.
    first_glance = out / 'first-glance.png'
    first_glance_w = 340
    tiny = Image.new('RGB', (columns*(first_glance_w+12)+12,rows*(round(first_glance_w*thumbh/thumbw)+38)+12),'#EFF3F6')
    for i, img in enumerate(images):
        h = round(first_glance_w*img.height/img.width)
        x = 12+(i%columns)*(first_glance_w+12)
        y = 12+(i//columns)*(h+38)
        tiny.paste(img.resize((first_glance_w,h),Image.Resampling.LANCZOS),(x,y))
    tiny.save(first_glance)
    report = {'artifact': str(path), 'rendered_pdf': str(pdf), 'pages': pages,
              'contact_sheet': str(contact), 'first_glance_proxy': str(first_glance),
              'machine_checks': {'page_count': len(pages),
                'page_outside_text_count': sum(len(p['page_outside_text']) for p in pages),
                'small_text_under_9pt_count': sum(len(p['small_text_under_9pt']) for p in pages),
                'text_overlap_warning_count':sum(len(p['text_overlap_warnings']) for p in pages),
                'low_contrast_shape_text_count':sum(len(p['low_contrast_shape_text_warnings']) for p in pages)},
              'ai_semantic_visual_review': 'NOT PERFORMED by this script',
              'human_two_second_test': 'NOT PERFORMED'}
    write_text(out / 'render-review.json', dumps(report) + '\n')
    return report

def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--out', required=True)
    parser.add_argument('--dpi', type=int, default=150)
    args = parser.parse_args(argv)
    report = render_file(args.source, args.out, args.dpi)
    m = report['machine_checks']
    print(dumps({'pages': m['page_count'], 'out_of_page_text': m['page_outside_text_count'],
                 'small_text_spans': m['small_text_under_9pt_count'],
                 'text_overlap_warnings': m['text_overlap_warning_count'],
                 'low_contrast_warnings': m['low_contrast_shape_text_count'],
                 'sheet': report['contact_sheet']}))
    return EXIT_PASS


if __name__ == '__main__':
    run(main)
