#!/usr/bin/env python3
"""Fix markdown formatting before PDF generation. Handles exercise spacing, table spacing, fenced div removal, and Unicode sanitization for SimHei font compatibility."""
import re
import sys
import os

def fix_exercise_spacing(lines):
    result = []
    in_exercise = False
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n").rstrip("\r")
        if re.match(r'^(###\s+第[0-9]+章\s+(学习通|PPT))|(####\s+(单选题|多选题|判断题))', stripped):
            in_exercise = True
            result.append(line)
            continue
        if in_exercise and (stripped.startswith("## ") or stripped == "---" or re.match(r'^###\s+第[0-9]+章\s+PPT', stripped)):
            in_exercise = False
            result.append(line)
            continue
        if in_exercise:
            is_numbered = bool(re.match(r'^\d+\.\s', stripped))
            is_dash_bullet = bool(re.match(r'^-\s.*[\(（][√×✓✗]{1,2}[\)）]', stripped))
            is_q_bullet = bool(re.match(r'^\*\*Q\d+\*\*', stripped))
            if (is_numbered or is_dash_bullet or is_q_bullet) and i > 0:
                prev = lines[i-1].rstrip("\n").rstrip("\r")
                if prev.strip():
                    result.append("\n")
            result.append(line)
        else:
            result.append(line)
    return result

def fix_table_spacing(lines):
    result = []
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n").rstrip("\r")
        if stripped.startswith("|") and i > 0:
            prev = lines[i-1].rstrip("\n").rstrip("\r")
            if prev.strip() and not prev.startswith("|"):
                result.append("\n")
        result.append(line)
    return result

def remove_fenced_divs(lines):
    result = []
    in_div = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(":::") and "{" in stripped:
            in_div = True
            continue
        if in_div and stripped == ":::":
            in_div = False
            continue
        result.append(line)
    return result

UNICODE_REPLACEMENTS = [
    ("★★★", "【重中之重】"), ("★★", "【重点】"),
    ("⚠️", "【易错】"), ("⚠", "【易错】"),
    ("✓", "(Y)"), ("✗", "(N)"),
    ("≠", "!="), ("≤", "<="), ("≥", ">="), ("≈", "~="),
    ("①", "(1)"), ("②", "(2)"), ("③", "(3)"), ("④", "(4)"), ("⑤", "(5)"),
    ("ηx", "eta_x"), ("ηm", "eta_m"), ("η", "eta"),
]

def sanitize_unicode(lines):
    result = []
    replaced_count = 0
    for line in lines:
        for pattern, replacement in UNICODE_REPLACEMENTS:
            if pattern in line:
                line = line.replace(pattern, replacement)
                replaced_count += 1
        result.append(line)
    if replaced_count > 0:
        print(f"  [OK] Unicode sanitized: {replaced_count} replacements")
    return result

def apply_all(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = remove_fenced_divs(lines)
    lines = sanitize_unicode(lines)
    lines = fix_exercise_spacing(lines)
    lines = fix_table_spacing(lines)
    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"  [OK] All formatting fixes applied: {md_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix_formatting.py <markdown_file>")
        sys.exit(1)
    md_path = sys.argv[1]
    if not os.path.isfile(md_path):
        print(f"Error: file not found: {md_path}")
        sys.exit(1)
    apply_all(md_path)
