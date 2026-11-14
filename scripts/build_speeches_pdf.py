#!/usr/bin/env python3
"""
Genera versiones en PDF (y DOCX intermedio opcional) de los guiones de exposición:
- docs/SPEECH_PERSONA_1.md -> docs/SPEECH_PERSONA_1.pdf
- docs/SPEECH_PERSONA_2.md -> docs/SPEECH_PERSONA_2.pdf
"""

from pathlib import Path
import re
import subprocess
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"


def set_paragraph_shading(paragraph, fill_hex: str) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    p_pr.append(shd)


def set_paragraph_left_border(paragraph, color_hex: str, sz: str = "18") -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), sz)
    left.set(qn("w:space"), "8")
    left.set(qn("w:color"), color_hex)
    p_bdr.append(left)
    p_pr.append(p_bdr)


TOKEN_RE = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)")


def add_formatted_runs(
    paragraph,
    text: str,
    base_size: float = 11.0,
    base_color: RGBColor = RGBColor(0x1E, 0x29, 0x3B),
    base_italic: bool = False,
) -> None:
    parts = TOKEN_RE.split(text)
    for part in parts:
        if not part:
            continue
        run = paragraph.add_run()
        run.font.size = Pt(base_size)
        run.font.color.rgb = base_color
        run.italic = base_italic

        if part.startswith("`") and part.endswith("`") and len(part) >= 2:
            run.text = part[1:-1]
            run.font.name = "DejaVu Sans Mono"
            run.font.size = Pt(base_size - 0.5)
            run.font.color.rgb = RGBColor(0x0F, 0x52, 0x57)
            run.bold = True
        elif part.startswith("**") and part.endswith("**") and len(part) >= 4:
            run.text = part[2:-2].replace("`", "")
            run.font.name = "Liberation Sans"
            run.bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) >= 2:
            run.text = part[1:-1].replace("`", "")
            run.font.name = "Liberation Sans"
            run.italic = True
        else:
            run.text = part
            run.font.name = "Liberation Sans"


def markdown_to_docx(md_path: Path, docx_path: Path) -> None:
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Liberation Sans"
    normal_style.font.size = Pt(11)

    lines = md_path.read_text(encoding="utf-8").splitlines()

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped == "---":
            continue

        # H1
        if stripped.startswith("# "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(8)
            run = p.add_run(stripped[2:].strip())
            run.font.name = "Liberation Sans"
            run.font.size = Pt(18)
            run.bold = True
            run.font.color.rgb = RGBColor(0x0B, 0x3C, 0x49)
            continue

        # H2 (Bloque)
        if stripped.startswith("## "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            set_paragraph_shading(p, "E6F4F1")
            set_paragraph_left_border(p, "0D9488", sz="24")
            run = p.add_run("  " + stripped[3:].strip())
            run.font.name = "Liberation Sans"
            run.font.size = Pt(13.5)
            run.bold = True
            run.font.color.rgb = RGBColor(0x0F, 0x52, 0x57)
            continue

        # H3 (Diapositiva)
        if stripped.startswith("### "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            h3_clean = stripped[4:].strip().replace("`", "").replace("*", "")
            run = p.add_run(h3_clean)
            run.font.name = "Liberation Sans"
            run.font.size = Pt(12.5)
            run.bold = True
            run.font.color.rgb = RGBColor(0x1D, 0x4E, 0x89)
            continue

        # Blockquote (spoken text or metadata)
        if stripped.startswith(">"):
            content = stripped.lstrip(">").strip()
            if not content:
                continue

            is_bullet = content.startswith("- ")
            if is_bullet:
                content = "• " + content[2:].strip()

            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25 if not is_bullet else 0.4)
            p.paragraph_format.right_indent = Inches(0.1)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.22
            set_paragraph_shading(p, "F8FAFC")
            set_paragraph_left_border(p, "2563EB", sz="12")
            add_formatted_runs(
                p,
                content,
                base_size=11.0,
                base_color=RGBColor(0x0F, 0x17, 0x2A),
                base_italic=False,
            )
            continue

        # Regular bullet list (Conceptos clave, checklist)
        if stripped.startswith("- "):
            content = stripped[2:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.first_line_indent = Inches(-0.15)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.18
            bullet_run = p.add_run("• ")
            bullet_run.font.name = "Liberation Sans"
            bullet_run.font.size = Pt(10.5)
            bullet_run.bold = True
            bullet_run.font.color.rgb = RGBColor(0x0D, 0x94, 0x88)
            add_formatted_runs(
                p,
                content,
                base_size=10.5,
                base_color=RGBColor(0x1E, 0x29, 0x3B),
            )
            continue

        # Regular paragraph (Qué se ve en pantalla, Conceptos clave header, Qué decir header)
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.18
        add_formatted_runs(
            p,
            stripped,
            base_size=10.5,
            base_color=RGBColor(0x33, 0x41, 0x55),
        )

    doc.save(str(docx_path))


def build_pdfs() -> None:
    targets = [
        DOCS_DIR / "SPEECH_PERSONA_1.md",
        DOCS_DIR / "SPEECH_PERSONA_2.md",
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        for md_file in targets:
            docx_file = tmp_path / f"{md_file.stem}.docx"
            markdown_to_docx(md_file, docx_file)
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(DOCS_DIR),
                    str(docx_file),
                ],
                check=True,
            )
            pdf_out = DOCS_DIR / f"{md_file.stem}.pdf"
            print(f"Generado: {pdf_out} ({pdf_out.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build_pdfs()
