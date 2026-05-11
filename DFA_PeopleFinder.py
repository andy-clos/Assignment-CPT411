
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


"""DFA Processes"""

def scan_text_with_log(text: str):
    log = []
    matches = []

    for start_idx in range(len(text)):
        state = START_STATE
        buffer = ""

        for pos in range(start_idx, len(text)):
            ch = text[pos]
            prev_state = state

            state = dfa_step(state, ch)

            buffer += ch

            # Action description
            if prev_state == START_STATE:
                action = f"Start with '{ch}'"
            elif state == TRAP_STATE:
                action = f"Invalid transition with '{ch}'"
            elif state in ACCEPT_STATES:
                action = f"Accept pattern: {ACCEPT_STATES[state]}"
            else:
                action = f"Continue with '{buffer}'"

            log.append({
                "Character": ch,
                "Previous State": prev_state,
                "Action/Details": action,
                "New State": state,
                "Current Buffer": buffer
            })

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

    return matches, log