#!/usr/bin/env python3
"""Phase 1: Multi-engine extraction of all course materials."""
import os
import sys

ENGINES = {
    ".pptx": "markitdown", ".docx": "markitdown",
    ".pdf": "liteparse", ".png": "liteparse", ".jpg": "liteparse",
    ".txt": "direct", ".md": "direct",
}

def extract_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    engine = ENGINES.get(ext, "direct")
    if engine == "markitdown":
        from markitdown import MarkItDown
        md = MarkItDown()
        return md.convert(filepath).text_content
    elif engine == "liteparse":
        import liteparse
        doc = liteparse.PDFDocument(filepath) if ext == ".pdf" else liteparse.ImageDocument(filepath)
        return doc.get_markdown()
    elif engine == "direct":
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(filepath, "r", encoding="gbk") as f:
                return f.read()
    return ""

def extract_all(course_dir):
    output_dir = os.path.join(course_dir, "__extracted__")
    os.makedirs(output_dir, exist_ok=True)
    extracted_count = 0
    for fname in sorted(os.listdir(course_dir)):
        filepath = os.path.join(course_dir, fname)
        ext = os.path.splitext(fname)[1].lower()
        if ext not in ENGINES or "_clean" in fname or "extracted" in fname:
            continue
        print(f"Extracting: {fname} ...")
        try:
            text = extract_file(filepath)
            base = os.path.splitext(fname)[0]
            out_path = os.path.join(output_dir, f"{base}.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"  -> {out_path} ({len(text)} chars)")
            extracted_count += 1
        except Exception as e:
            print(f"  [ERROR] {fname}: {e}")
    print(f"\nExtracted {extracted_count} files to {output_dir}/")
    return output_dir

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_all.py <course_directory>")
        sys.exit(1)
    extract_all(sys.argv[1])
