#!/usr/bin/env python3
"""Check all dependencies for final-exam-review skill."""
import shutil
import subprocess
import sys

deps = {
    "markitdown": ("markitdown", "pip install 'markitdown[all]'"),
    "liteparse": ("liteparse", "pip install liteparse"),
    "fitz": ("PyMuPDF", "pip install pymupdf"),
    "docx": ("python-docx", "pip install python-docx"),
    "yaml": ("PyYAML", "pip install pyyaml"),
    "PIL": ("Pillow", "pip install Pillow"),
}

binaries = {
    "pandoc": "winget install JohnMacFarlane.Pandoc",
    "xelatex": "winget install MiKTeX.MiKTeX",
    "mmdc": "npm install -g @mermaid-js/mermaid-cli",
}

print("=== Python Packages ===")
all_ok = True
for mod, (name, inst) in deps.items():
    try:
        __import__(mod)
        print(f"  [OK] {name}")
    except ImportError:
        print(f"  [MISSING] {name} → run: {inst}")
        all_ok = False

print("\n=== System Binaries ===")
for bin_name, inst in binaries.items():
    found = shutil.which(bin_name)
    if found:
        print(f"  [OK] {bin_name}: {found}")
    else:
        print(f"  [MISSING] {bin_name} → run: {inst}")
        all_ok = False

print("\n=== Fonts ===")
import os
fonts = ["simhei.ttf", "simsun.ttc", "msyh.ttc"]
font_dir = "C:/Windows/Fonts"
for f in fonts:
    path = os.path.join(font_dir, f)
    if os.path.exists(path):
        print(f"  [OK] {f}")
    else:
        print(f"  [MISSING] {f}")

if all_ok:
    print("\nAll dependencies satisfied.")
else:
    print("\nSome dependencies missing. Install them and re-run.", file=sys.stderr)
    sys.exit(1)
