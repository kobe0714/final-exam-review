#!/usr/bin/env python3
"""Phase 4: Generate mock exam skeleton matching exam structure.

Strategy: Script generates the correct structure (section headers, chapter tags,
question numbers matching the outline distribution). AI fills in question content.
Never overwrites existing files.
"""
import os
import sys

EXAM_STRUCTURE = {
    "single_choice": {"title": "Part I: Single Choice", "count": 15, "score": 2,
        "chapters": {"Ch1": 2, "Ch2": 3, "Ch3": 3, "Ch4": 1, "Ch5": 2, "Ch6": 2, "Ch7": 2}},
    "multiple_choice": {"title": "Part II: Multiple Choice", "count": 10, "score": 2,
        "chapters": {"Ch1": 3, "Ch2": 3, "Ch3": 1, "Ch4": 2, "Ch7": 1}},
    "true_false": {"title": "Part III: True or False", "count": 10, "score": 1,
        "chapters": {"Ch1": 2, "Ch2": 2, "Ch3": 2, "Ch4": 2, "Ch5": 2}},
    "short_answer": {"title": "Part IV: Short Answer", "count": 2, "score": 5,
        "chapters": {"Ch1": 1, "Ch4": 1}},
    "calculation": {"title": "Part V: Calculation", "count": 6, "score": "3-4",
        "chapters": {"Ch2": 5, "Ch3": 1}},
    "current_affairs": {"title": "Part VI: Current Affairs", "count": 2, "score": 5,
        "chapters": {"时政": 2}},
}


def generate(course_dir, output_name="mock_exam"):
    """Generate mock exam + answer skeleton files. Skip if already exist."""

    exam_path = os.path.join(course_dir, f"{output_name}.md")
    answer_path = os.path.join(course_dir, f"{output_name}_answers.md")

    if os.path.exists(exam_path):
        print(f"  [SKIP] {exam_path} already exists, not overwriting")
        return exam_path, answer_path

    qnum = 1
    exam_lines = [
        "# International Finance Mock Exam",
        "",
        "> Total: 100 points | 33 questions | 120 minutes",
        "",
    ]
    answer_lines = [
        "# Mock Exam Answer Key",
        "",
    ]

    for qtype, cfg in EXAM_STRUCTURE.items():
        title = cfg["title"]
        count = cfg["count"]
        score = cfg["score"]
        chapters = cfg["chapters"]

        exam_lines.append(f"## {title} ({count} x {score} pts)")
        exam_lines.append("")
        answer_lines.append(f"## {title}")
        answer_lines.append("")

        for ch, ch_count in chapters.items():
            for _ in range(ch_count):
                exam_lines.append(f"**{qnum}.** ({ch}) ")
                exam_lines.append("")
                answer_lines.append(f"**{qnum}.** ({ch}) ")
                answer_lines.append("")
                qnum += 1

        exam_lines.append("")

    # Write exam
    with open(exam_path, "w", encoding="utf-8") as f:
        f.write("\n".join(exam_lines))

    # Write answers
    with open(answer_path, "w", encoding="utf-8") as f:
        f.write("\n".join(answer_lines))

    print(f"  [OK] Mock exam skeleton: {exam_path}")
    print(f"  [OK] Answer skeleton: {answer_path}")
    print(f"  Next: fill in questions manually or via AI")

    return exam_path, answer_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_mock.py <course_dir> [output_name]")
        sys.exit(1)

    course_dir = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else "mock_exam"

    if not os.path.isdir(course_dir):
        print(f"Error: directory not found: {course_dir}")
        sys.exit(1)

    generate(course_dir, output_name)
