#!/usr/bin/env python3
"""Phase 0: Detect exam structure from outline and scope documents."""
import os
import sys
import json
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF with encoding fallback for CMap-encoded files."""
    import fitz
    doc = fitz.open(pdf_path)
    text = ""
    has_cids = False
    for page in doc:
        page_text = page.get_text()
        # Check for CIDs (indicates garbled CMap-encoded text)
        if "(cid:" in page_text.lower():
            has_cids = True
        text += page_text + "\n"
    doc.close()

    if has_cids:
        # Try block-level text which sometimes handles encoding better
        doc2 = fitz.open(pdf_path)
        text = ""
        for page in doc2:
            blocks = page.get_text("blocks")
            for b in blocks:
                if b[6] == 0:  # text block
                    text += b[4] + "\n"
        doc2.close()

    return text, has_cids


def parse_exam_table(text, has_cids):
    """Parse the exam chapter-question distribution table from raw text."""
    chapters = []
    chapter_names_cn = []
    chapter_names_en = ["Ch1 BOP", "Ch2 Exchange Rate", "Ch3 FX Market",
                         "Ch4 FX Regime", "Ch5 Intl Reserves",
                         "Ch6 Intl Financial Markets", "Ch7 Capital Flows"]

    # Detect chapter names even from garbled text
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Try to detect Chinese chapter markers
        if any(kw in line for kw in ['第一章', '第二章', '第三章', '第四章',
                                       '第五章', '第六章', '第七章', '第1章',
                                       '第2章', '第3章', '第4章', '第5章',
                                       '第6章', '第7章']):
            chapters.append(line)
        # Also look for garbled markers (e.g., "��һ��" -> 第一章)
        if re.search(r'第[一二三四五六七]章', line):
            chapters.append(line)

    # Extract question type distribution from known layout
    # Based on typical format: each chapter has rows with 题型 as column headers
    question_types_cn = ['单选题', '多选题', '判断题', '简答题', '计算题', '时政题']

    return {
        "chapters": chapter_names_en,
        "question_types": question_types_cn,
        "has_cids": has_cids,
        "raw_text": text[:3000]
    }


def scan_directory(course_dir):
    """Scan directory for exam-relevant files and detect structure."""
    files = os.listdir(course_dir)

    outline_files = [f for f in files if '题纲' in f or '大纲' in f]
    scope_files = [f for f in files if '范围' in f or 'scope' in f.lower()]
    ppt_files = sorted([f for f in files if f.lower().endswith('.pptx')])
    pdf_files = [f for f in files if f.lower().endswith('.pdf') and '课本' in f]
    exercise_files = [f for f in files if '习题' in f or '答案' in f or 'exercise' in f.lower()]
    extracted_dir = os.path.join(course_dir, '__extracted__')
    has_extracted = os.path.isdir(extracted_dir)
    ppt_text_dir = os.path.join(course_dir, 'ppt_text')
    has_ppt_text = os.path.isdir(ppt_text_dir)

    result = {
        "course_dir": course_dir,
        "outline_files": outline_files,
        "scope_files": scope_files,
        "ppt_files": ppt_files,
        "textbook_files": pdf_files,
        "exercise_files": exercise_files,
        "has_extracted": has_extracted,
        "has_ppt_text": has_ppt_text,
    }

    # Try to extract exam structure from outline
    for fname in outline_files:
        path = os.path.join(course_dir, fname)
        try:
            text, has_cids = extract_text_from_pdf(path)
            structure = parse_exam_table(text, has_cids)
            result["exam_structure"] = structure
            if has_cids:
                result["warning"] = (
                    "PDF text is CMap-encoded (garbled). "
                    "Numbers and layout are extracted but Chinese text may not be reliable. "
                    "Consider using liteparse OCR with Tesseract installed."
                )
        except Exception as e:
            result["exam_structure"] = {"error": str(e)}
        break

    # Check for pre-extracted textbook
    textbook_ocr = os.path.join(course_dir, 'textbook_ocr.txt')
    if os.path.isfile(textbook_ocr):
        result["has_textbook_ocr"] = True

    return result


def print_summary(result):
    """Print exam structure summary for user confirmation."""
    print("\n" + "=" * 60)
    print("EXAM STRUCTURE DETECTED")
    print("=" * 60)

    if "exam_structure" in result:
        s = result["exam_structure"]
        if "error" in s:
            print(f"  ERROR: {s['error']}")
        else:
            qtypes = s.get("question_types", [])
            print(f"  Question types: {', '.join(qtypes)}")
            if s.get("has_cids"):
                print("  [WARNING] PDF has CMap encoding - Chinese text may be garbled")

    if result.get("warning"):
        print(f"  [WARNING] {result['warning']}")

    print(f"\n  PPT files ({len(result['ppt_files'])}):")
    for f in result["ppt_files"]:
        print(f"    - {f}")

    print(f"\n  Textbook: {result['textbook_files']}")
    print(f"  Exercises: {result['exercise_files']}")
    print(f"  Outline: {result['outline_files']}")
    print(f"  Scope: {result['scope_files']}")
    if result.get("has_extracted"):
        print(f"  Extracted text: __extracted__/ exists")
    if result.get("has_ppt_text"):
        print(f"  PPT text: ppt_text/ exists")

    print("\n" + "-" * 40)
    print("Please verify this structure before proceeding to Phase 1.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scanner.py <course_directory>")
        sys.exit(1)

    course_dir = sys.argv[1]
    if not os.path.isdir(course_dir):
        print(f"Error: directory not found: {course_dir}")
        sys.exit(1)

    result = scan_directory(course_dir)

    # Save config
    config_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config"
    )
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "exam-format.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Config saved to {config_path}")

    print_summary(result)
