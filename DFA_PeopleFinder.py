
"""
DFA Name Scanner
Name List:
- Steve Jobs
- Mr Jobs
- Mr Obama
- Barack Obama
- Tim Cook
- Cory Moll
- Jin Yi

It works by scanning a full paragraph, thennstarting DFA simulation at every character index.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List

START_STATE = "q0"
TRAP_STATE = "trap"

# Deterministic transition table:
# transitions[state][character] -> next_state
TRANSITIONS: Dict[str, Dict[str, str]] = {
    "q0": {"S": "q1", "M": "q20", "B": "q40", "T": "q60", "C": "q80", "J": "q100"},
    # Branch 1: Steve Jobs
    "q1": {"t": "q2"},
    "q2": {"e": "q3"},
    "q3": {"v": "q4"},
    "q4": {"e": "q5"},
    "q5": {" ": "q6"},
    "q6": {"J": "q7"},
    "q7": {"o": "q8"},
    "q8": {"b": "q9"},
    "q9": {"s": "q10"},
    # Branch 2: Mr Jobs / Mr Obama
    "q20": {"r": "q21"},
    "q21": {" ": "q22"},
    "q22": {"J": "q23", "O": "q30"},
    "q23": {"o": "q24"},
    "q24": {"b": "q25"},
    "q25": {"s": "q26"},
    "q30": {"b": "q31"},
    "q31": {"a": "q32"},
    "q32": {"m": "q33"},
    "q33": {"a": "q34"},
    # Branch 3: Barack Obama
    "q40": {"a": "q41"},
    "q41": {"r": "q42"},
    "q42": {"a": "q43"},
    "q43": {"c": "q44"},
    "q44": {"k": "q45"},
    "q45": {" ": "q46"},
    "q46": {"O": "q47"},
    "q47": {"b": "q48"},
    "q48": {"a": "q49"},
    "q49": {"m": "q50"},
    "q50": {"a": "q51"},
    # Branch 4: Tim Cook
    "q60": {"i": "q61"},
    "q61": {"m": "q62"},
    "q62": {" ": "q63"},
    "q63": {"C": "q64"},
    "q64": {"o": "q65"},
    "q65": {"o": "q66"},
    "q66": {"k": "q67"},
    # Branch 5: Cory Moll
    "q80": {"o": "q81"},
    "q81": {"r": "q82"},
    "q82": {"y": "q83"},
    "q83": {" ": "q84"},
    "q84": {"M": "q85"},
    "q85": {"o": "q86"},
    "q86": {"l": "q87"},
    "q87": {"l": "q88"},
    # Branch 6: Jin Yi
    "q100": {"i": "q101"},
    "q101": {"n": "q102"},
    "q102": {" ": "q103"},
    "q103": {"Y": "q104"},
    "q104": {"i": "q105"},
}

ACCEPT_STATES: Dict[str, str] = {
    "q10": "Steve Jobs",
    "q26": "Mr Jobs",
    "q34": "Mr Obama",
    "q51": "Barack Obama",
    "q67": "Tim Cook",
    "q88": "Cory Moll",
    "q105": "Jin Yi",
}

PATTERN_SET = [
    "Steve Jobs",
    "Mr Jobs",
    "Barack Obama",
    "Mr Obama",
    "Tim Cook",
    "Cory Moll",
    "Jin Yi",
]


@dataclass
class Match:
    pattern: str
    start: int
    end: int
    text: str


def dfa_step(state: str, ch: str) -> str:
    """Return next DFA state for one input character."""
    if state == TRAP_STATE:
        return TRAP_STATE
    return TRANSITIONS.get(state, {}).get(ch, TRAP_STATE)


def scan_text(text: str) -> List[Match]:
    """Scan text and return all DFA matches with index positions.

    The scanner starts from every character position and simulates
    DFA transitions one character at a time until accept or trap.
    """
    matches: List[Match] = []

    for start_idx in range(len(text)):
        state = START_STATE

        for pos in range(start_idx, len(text)):
            state = dfa_step(state, text[pos])

            if state == TRAP_STATE:
                break

            if state in ACCEPT_STATES:
                matches.append(
                    Match(
                        pattern=ACCEPT_STATES[state],
                        start=start_idx,
                        end=pos,
                        text=text[start_idx : pos + 1],
                    )
                )
                break

    return matches


def build_highlighted_snippets(text: str, matches: List[Match], radius: int = 18) -> List[str]:
    snippets: List[str] = []
    for m in matches:
        left = max(0, m.start - radius)
        right = min(len(text), m.end + radius + 1)
        chunk = text[left:right]
        if left > 0:
            chunk = "... " + chunk
        if right < len(text):
            chunk = chunk + " ..."
        snippets.append(chunk)
    return snippets


def build_boldface_text(text: str, matches: List[Match]) -> str:
    """Return text with each matched pattern wrapped in **...** for demo visualization."""
    if not matches:
        return text

    sorted_matches = sorted(matches, key=lambda m: m.start)
    pieces: List[str] = []
    cursor = 0

    for m in sorted_matches:
        if m.start < cursor:
            continue
        pieces.append(text[cursor:m.start])
        pieces.append("**" + text[m.start : m.end + 1] + "**")
        cursor = m.end + 1

    pieces.append(text[cursor:])
    return "".join(pieces)


def print_demo_output(text: str, matches: List[Match]) -> None:
    status = "ACCEPT" if matches else "REJECT"
    counts = Counter(m.pattern for m in matches)

    print("<DFA-DEMO-OUTPUT>")
    print(f"- <PATTERN-SET(INPUT-STRINGS)>: {', '.join(PATTERN_SET)}")
    print(f"- <TEXT-USED-FOR-DEMO>: {text}")
    print(f"- <STATUS>: {status}")
    print("- <ADDITIONAL-INFORMATION>:")

    if matches:
        print("  - <POSITION-OF-PATTERN-FOUND>:")
        for m in matches:
            print(f"    - <{m.pattern}> found at <position {m.start}> (end {m.end})")

        print("  - <OCCURRENCES-OF-PATTERNS>:")
        for pattern in PATTERN_SET:
            print(f"    - <{pattern}>: {counts.get(pattern, 0)}")
        print(f"    - <TOTAL-OCCURRENCES>: {len(matches)}")

        print("  - <BOLDFACE-IN-TEXT>:")
        print("    - " + "\n    - ".join(build_boldface_text(text, matches).split("\n")))
        print("  - <HIGHLIGHTED-SNIPPETS>:")
        for snippet in build_highlighted_snippets(text, matches):
            print("    - " + snippet)
    else:
        print("  - <POSITION-OF-PATTERN-FOUND>: none")
        print("  - <OCCURRENCES-OF-PATTERNS>: 0")
        print("  - <VISUALIZATION-BOLDFACE-IN-TEXT>: no pattern occurrence")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan a paragraph using a character-level DFA for target names."
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="Paragraph text to scan. If omitted, the script will prompt for input.",
    )
    args = parser.parse_args()

    paragraph = " ".join(args.text).strip() if args.text else ""
    if not paragraph:
        paragraph = input("Enter paragraph to scan: ").rstrip("\n")

    matches = scan_text(paragraph)
    print_demo_output(paragraph, matches)


if __name__ == "__main__":
    main()
