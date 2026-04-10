"""
Clean and normalize VinPolicys markdown files (pass 3 - aggressive).

Handles the specific pattern from PDF conversion:
  - Each text line has a blank line after it (PDF paragraph spacing)
  - Lines that are continuations of the same sentence (no ending punctuation)
"""

import re
from pathlib import Path


def is_structural_line(line: str) -> bool:
    """Check if a line is a structural markdown element (not plain text)."""
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if stripped.startswith("|"):
        return True
    if stripped.startswith(">"):
        return True
    if stripped.startswith("```"):
        return True
    if stripped == "---" or stripped == "***":
        return True
    if re.match(r"^[-*+]\s", stripped):
        return True
    if re.match(r"^\d+\.\s", stripped):
        return True
    if re.match(r"^[a-z]\)\s", stripped):
        return True
    if re.match(r"^[a-z]\.\s", stripped):
        return True
    # Bold-only label lines
    if re.match(r"^\*\*[^*]+\*\*\s*$", stripped):
        return True
    return False


def looks_like_continuation(prev_line: str, next_line: str) -> bool:
    """Check if next_line is a continuation of prev_line (broken by PDF layout)."""
    prev = prev_line.rstrip()
    nxt = next_line.strip()

    if not prev or not nxt:
        return False

    # If previous line ends with certain punctuation, it's likely complete
    if prev[-1] in ".!?;:":
        return False

    # If previous line ends with a comma or conjunction, definitely a continuation
    if prev[-1] in ",":
        return True

    # If next line starts with lowercase, it's a continuation
    if nxt[0].islower():
        return True

    # If next line starts with common continuation patterns
    if nxt.startswith("of ") or nxt.startswith("in ") or nxt.startswith("and "):
        return True
    if nxt.startswith("the ") or nxt.startswith("to ") or nxt.startswith("for "):
        return True
    if nxt.startswith("or ") or nxt.startswith("at ") or nxt.startswith("with "):
        return True
    if nxt.startswith("that ") or nxt.startswith("which ") or nxt.startswith("who "):
        return True

    return False


def clean_markdown(text: str) -> str:
    """Clean a single markdown file's content."""

    # 1. Remove form feed
    text = text.replace("\f", "")

    # 2. Remove page footers, dates, and standalone page numbers
    text = re.sub(r"\n\s*VinUniversity\s*-\s*All Rights Reserved\s*\n", "\n", text)
    text = re.sub(r"\n\s*\d{4}-\d{2}-\d{2}\s*\n", "\n", text)
    text = re.sub(r"\n\s*\d{1,3}\s*\n", "\n", text)

    # 3. Strip trailing whitespace
    lines = [line.rstrip() for line in text.split("\n")]

    # 4. AGGRESSIVE paragraph merging:
    #    Pattern from PDF: text line -> blank line -> continuation text line -> blank line
    #    Strategy: collect text lines, skip blank lines between them if they're continuations
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip empty lines (we'll re-add them properly)
        if not line.strip():
            merged.append("")
            i += 1
            continue

        # If structural, keep as-is
        if is_structural_line(line):
            merged.append(line)
            i += 1
            continue

        # Plain text line - accumulate paragraph
        paragraph_parts = [line.strip()]
        j = i + 1

        while j < len(lines):
            # Skip blank lines between text continuations
            k = j
            while k < len(lines) and not lines[k].strip():
                k += 1

            if k >= len(lines):
                break

            next_line = lines[k]

            # Stop if structural
            if is_structural_line(next_line):
                break

            # Check if it's a continuation of the current paragraph
            current_text = " ".join(paragraph_parts)
            if looks_like_continuation(current_text, next_line):
                paragraph_parts.append(next_line.strip())
                j = k + 1
            else:
                break

        # Join paragraph and clean
        paragraph = " ".join(paragraph_parts)
        paragraph = re.sub(r"  +", " ", paragraph)
        merged.append(paragraph)
        i = j if j > i + 1 else i + 1

    # 5. Collapse excessive blank lines (max 1)
    result = []
    blank_count = 0
    for line in merged:
        if not line.strip():
            blank_count += 1
            if blank_count <= 1:
                result.append("")
        else:
            blank_count = 0
            result.append(line)

    text = "\n".join(result).strip() + "\n"
    return text


def main():
    data_dir = Path(__file__).parent.parent / "data" / "VinPolicys"

    if not data_dir.exists():
        print(f"Directory not found: {data_dir}")
        return

    files = sorted(data_dir.glob("*.md"))
    print(f"Found {len(files)} markdown files in {data_dir}\n")

    for filepath in files:
        original = filepath.read_text(encoding="utf-8")
        original_lines = original.count("\n")
        original_size = len(original)

        cleaned = clean_markdown(original)
        cleaned_lines = cleaned.count("\n")
        cleaned_size = len(cleaned)

        filepath.write_text(cleaned, encoding="utf-8")

        reduction = (1 - cleaned_size / original_size) * 100 if original_size > 0 else 0
        print(
            f"  {filepath.name:<50s} "
            f"{original_lines:>4d} -> {cleaned_lines:>4d} lines  "
            f"({original_size:>6d} -> {cleaned_size:>6d} bytes, "
            f"-{reduction:.1f}%)"
        )

    print(f"\nDone! Cleaned {len(files)} files.")


if __name__ == "__main__":
    main()
