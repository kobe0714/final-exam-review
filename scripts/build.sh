#!/bin/bash
# Phase 3: Build review document -> PDF + DOCX + HTML
# Usage: bash scripts/build.sh "<course_dir>" "<output_name>"
set -e

COURSE_DIR="${1:?Usage: build.sh <course_dir> <output_name>}"
OUTPUT_NAME="${2:-final_review}"

# ---- Detect pandoc ----
PANDOC=""
for candidate in \
    "$(which pandoc 2>/dev/null || true)" \
    "$(find "$HOME/AppData/Local/Microsoft/WinGet/Packages" -name pandoc.exe 2>/dev/null | head -1 || true)" \
    "/c/Program Files/Pandoc/pandoc.exe" \
    "$(where.exe pandoc 2>/dev/null | head -1 || true)"
do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        PANDOC="$candidate"
        break
    fi
done

if [ -z "$PANDOC" ]; then
    echo "[ERROR] pandoc not found. Install: winget install JohnMacFarlane.Pandoc"
    exit 1
fi

# ---- Detect xelatex ----
XELATEX=""
for candidate in \
    "$(which xelatex 2>/dev/null || true)" \
    "$(find "$HOME/AppData/Local/Programs/MiKTeX" -name xelatex.exe 2>/dev/null | head -1 || true)" \
    "/c/Program Files/MiKTeX/miktex/bin/x64/xelatex.exe" \
    "$(where.exe xelatex 2>/dev/null | head -1 || true)"
do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        XELATEX="$candidate"
        break
    fi
done

if [ -z "$XELATEX" ]; then
    echo "[ERROR] xelatex not found. Install: winget install MiKTeX.MiKTeX"
    exit 1
fi

# Ensure MiKTeX bin is in PATH (pdflatex, etc.)
XELATEX_DIR="$(dirname "$XELATEX")"
export PATH="$XELATEX_DIR:$PATH"

# Auto-install MiKTeX packages without popup
if [ -x "$XELATEX_DIR/initexmf" ]; then
    "$XELATEX_DIR/initexmf" --set-config-value "[MPM]AutoInstall=1" 2>/dev/null || true
fi

# ---- Skill directories ----
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="${SKILL_DIR}/templates"
CONTENT_STYLE="${TEMPLATE_DIR}/content-classes.tex"
FIX_FORMAT="${SKILL_DIR}/scripts/fix_formatting.py"

MD_FILE="${COURSE_DIR}/${OUTPUT_NAME}.md"
PDF_FILE="${COURSE_DIR}/${OUTPUT_NAME}.pdf"
DOCX_FILE="${COURSE_DIR}/${OUTPUT_NAME}.docx"
HTML_FILE="${COURSE_DIR}/${OUTPUT_NAME}.html"
PDF_MD_TEMP="${COURSE_DIR}/__pdf_temp_${OUTPUT_NAME}.md"

if [ ! -f "$MD_FILE" ]; then
    echo "[ERROR] Markdown not found: $MD_FILE"
    exit 1
fi

# ---- Fix markdown formatting (on temp copy for PDF) ----
echo "=== Fixing markdown formatting ==="
# DOCX uses original MD (keeps ★ ⚠ ✓ Unicode chars that render fine in Word)
# PDF uses temp sanitized copy (Unicode chars replaced for SimHei font compatibility)
cp "$MD_FILE" "$PDF_MD_TEMP"
python3 "$FIX_FORMAT" "$PDF_MD_TEMP" 2>&1
echo "=== Build starting ==="

# ---- Validate markdown tables (blank line check) ----
echo "  Checking table spacing..."
TABLE_ISSUES=$(python3 -c "
import sys
with open('$MD_FILE', 'r', encoding='utf-8') as f:
    lines = f.readlines()
issues = 0
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('|') and i > 0:
        prev = lines[i-1].rstrip('\n').rstrip('\r')
        if prev and not prev.startswith('|') and prev.strip():
            print(f'Line {i+1}: table needs blank line before it')
            issues += 1
if issues:
    print(f'Total: {issues} table formatting issues found')
    sys.exit(1)
" 2>&1)
if [ $? -ne 0 ]; then
    echo "  [WARN] Table blank-line issues found (tables may render as plain text):"
    echo "$TABLE_ISSUES"
fi
echo "  [OK] Validation complete"

echo "=== Building: $OUTPUT_NAME ==="

# Detect CJK font
CJK_FONT="SimHei"
if fc-list 2>/dev/null | grep -qi "Charter"; then
    CJK_FONT="Charter"
fi

# ---- PDF (from sanitized temp copy) ----
echo "[1/3] Generating PDF..."
if [ -f "$CONTENT_STYLE" ]; then
    "$PANDOC" "$PDF_MD_TEMP" \
        -o "$PDF_FILE" \
        --pdf-engine="$XELATEX" \
        -V CJKmainfont="$CJK_FONT" \
        -V monofont="$CJK_FONT" \
        -V geometry:margin=2cm \
        -V colorlinks=true \
        --toc --toc-depth=2 -N 2>&1 | grep -v "miktex.*major issue\|So far.*checked" || true
else
    "$PANDOC" "$PDF_MD_TEMP" \
        -o "$PDF_FILE" \
        --pdf-engine="$XELATEX" \
        -V CJKmainfont="$CJK_FONT" \
        -V monofont="$CJK_FONT" \
        -V geometry:margin=2cm \
        -V colorlinks=true \
        --toc --toc-depth=2 -N 2>&1 | grep -v "miktex.*major issue\|So far.*checked" || true
fi

# Clean up temp file
rm -f "$PDF_MD_TEMP"

if [ -f "$PDF_FILE" ]; then
    echo "  [OK] PDF: $PDF_FILE"
else
    echo "  [ERROR] PDF generation failed"
    exit 1
fi

# ---- DOCX ----
echo "[2/3] Generating DOCX..."
"$PANDOC" "$MD_FILE" -o "$DOCX_FILE" --toc --toc-depth=2 2>&1 | grep -v "^$" || true
echo "  [OK] DOCX: $DOCX_FILE"

# ---- HTML (self-contained) ----
echo "[3/3] Generating HTML..."
"$PANDOC" "$MD_FILE" -o "$HTML_FILE" --standalone --toc --toc-depth=2 \
    --metadata title="$OUTPUT_NAME" 2>&1 | grep -v "^$" || true
echo "  [OK] HTML: $HTML_FILE"

echo ""
echo "=== Done: 3 formats generated ==="
echo "  PDF:  $PDF_FILE"
echo "  DOCX: $DOCX_FILE"
echo "  HTML: $HTML_FILE"
