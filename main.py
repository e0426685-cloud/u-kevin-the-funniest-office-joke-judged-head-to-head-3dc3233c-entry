#!/usr/bin/env python3
"""The Funniest Office Joke, Judged Head to Head — make.fun entry.

Writes a single-line joke about office life to /output/entry.txt.

Gate (from competition.yaml): the file must be UTF-8 text of 1 to 200
characters, not only whitespace, and a single line.
Standard library only; no network, no third-party packages.

Usage: python3 main.py [--check|--dry-run]
  --check / --dry-run validates the entry against the gate and exits
  without writing anything.
"""

import os
import sys

JOKE = (
    "I hit reply-all to say 'please stop replying all' and 400 "
    "colleagues agreed \u2014 in 400 separate reply-all emails."
)

OUTPUT_PATH = "/output/entry.txt"
MIN_CHARS = 1
MAX_CHARS = 200


def validate_entry(text):
    """Validate one candidate entry against the competition gate.

    The gate (competition.yaml) requires /output/entry.txt to be UTF-8
    text of 1 to 200 characters, not only whitespace, and a single line.
    This check mirrors that gate plus a stricter control-character rule:
    a printable one-line joke has no business carrying control codes,
    so any character below U+0020 (and DEL, U+007F) is also a problem.

    Returns a list of problem strings; an empty list means the text is
    valid and safe to write.
    """
    problems = []
    if not text:
        problems.append("entry is empty")
    if text != text.strip() or not text.strip():
        problems.append("entry is blank or has surrounding whitespace")
    if not (MIN_CHARS <= len(text) <= MAX_CHARS):
        problems.append(
            "entry is %d characters, outside the %d-%d gate"
            % (len(text), MIN_CHARS, MAX_CHARS)
        )
    if "\n" in text or "\r" in text:
        problems.append("entry is not a single line")
    bad_controls = sorted(
        {repr(ch) for ch in text if ord(ch) < 0x20 or ord(ch) == 0x7F}
    )
    if bad_controls:
        problems.append(
            "entry contains control characters: %s" % ", ".join(bad_controls)
        )
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append("entry is not valid UTF-8: %s" % exc)
    return problems


def write_entry(text):
    """Write the entry to /output/entry.txt and verify what landed.

    Uses plain open() + an explicit chmod 0644: the grader runs as a
    different user, so the file must be world-readable (never
    tempfile.mkstemp, which forces mode 0600 and breaks grader
    readability). Returns a list of problems; empty means the file on
    disk is byte-identical to the entry and mode 644.
    """
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    os.chmod(OUTPUT_PATH, 0o644)

    problems = []
    with open(OUTPUT_PATH, "r", encoding="utf-8") as handle:
        written = handle.read()
    if written != text:
        problems.append("file content differs from entry")
    if oct(os.stat(OUTPUT_PATH).st_mode & 0o777) != "0o644":
        problems.append("unexpected file permissions")
    return problems


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    check_only = False
    if "--check" in args or "--dry-run" in args:
        check_only = True
        args = [a for a in args if a not in ("--check", "--dry-run")]
    if args:
        print("usage: main.py [--check|--dry-run]", file=sys.stderr)
        return 2

    problems = validate_entry(JOKE)
    if problems:
        for problem in problems:
            print("self-check failed: %s" % problem, file=sys.stderr)
        return 1

    if check_only:
        # Validate without touching the filesystem: useful for a quick
        # gate check and for the grader's own dry runs.
        print("entry valid: %d characters, single line" % len(JOKE))
        return 0

    problems = write_entry(JOKE)
    if problems:
        for problem in problems:
            print("self-check failed: %s" % problem, file=sys.stderr)
        return 1

    print("wrote %d characters to %s" % (len(JOKE), OUTPUT_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
