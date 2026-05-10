import streamlit as st
from collections import Counter
import json
import streamlit.components.v1 as components

# Import from backend
from DFA_PeopleFinder import scan_text_with_log, PATTERN_SET

st.set_page_config(
    page_title="DFA People Finder",
    layout="wide"
)

# -----------------------------
# Convert matches to dictionary
# -----------------------------
def convert_matches(matches):
    results = {pattern: [] for pattern in PATTERN_SET}
    for m in matches:
        results[m.pattern].append((m.start, m.end))
    return results


# -----------------------------
# Build summary table
# -----------------------------
def build_summary_table(results):
    rows = []
    for pattern in PATTERN_SET:
        positions = results.get(pattern, [])
        rows.append({
            "Pattern": pattern,
            "Status": "Accept" if positions else "Reject",
            "Found": len(positions),
            "Positions": ", ".join([f"({s}, {e})" for s, e in positions]) if positions else "-"
        })
    return rows


# -----------------------------
# Highlight text
# -----------------------------
def highlight_text_html(text, matches):
    if not matches:
        return text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

    colors = ["#fff59d", "#a5d6a7", "#90caf9", "#ffccbc", "#ce93d8", "#80deea"]

    pattern_colors = {p: colors[i % len(colors)] for i, p in enumerate(PATTERN_SET)}

    sorted_matches = sorted(matches, key=lambda m: m.start)

    parts = []
    cursor = 0

    for m in sorted_matches:
        if m.start < cursor:
            continue

        parts.append(text[cursor:m.start])

        parts.append(
            f"<mark style='background-color:{pattern_colors[m.pattern]}; "
            f"padding:2px 4px; border-radius:4px;'>"
            f"{text[m.start:m.end+1]}</mark>"
        )

        cursor = m.end + 1

    parts.append(text[cursor:])

    return "".join(parts).replace("\n", "<br>")


# -----------------------------
# Snippets
# -----------------------------
def build_snippets(text, matches, radius=25):
    snippets = []
    for m in matches:
        left = max(0, m.start - radius)
        right = min(len(text), m.end + radius + 1)

        chunk = text[left:right]

        if left > 0:
            chunk = "... " + chunk
        if right < len(text):
            chunk = chunk + " ..."

        snippets.append({
            "Pattern": m.pattern,
            "Position": f"{m.start} - {m.end}",
            "Snippet": chunk
        })

    return snippets


# -----------------------------
# UI
# -----------------------------
st.title("DFA People Finder")

st.write("Detect predefined people names using DFA (character-by-character scanning).")

with st.sidebar:
    st.header("Pattern Set")
    for p in PATTERN_SET:
        st.write(f"- {p}")


# -----------------------------
# Input Section
# -----------------------------
st.subheader("Input Text")

uploaded_file = st.file_uploader("Upload .txt file", type=["txt"])

default_text = """Steve Jobs, co-founder and former chief executive of US technology giant Apple, has died at the age of 56.

Apple said, external he had been "the source of countless innovations that enrich and improve all of our lives" and had made the world "immeasurably better".

Mr Jobs had announced he was suffering from pancreatic cancer in 2004.

Tributes have been made by technology company bosses and world leaders, with US President Barack Obama saying the world had "lost a visionary".

"Steve was among the greatest of American innovators - brave enough to think differently, bold enough to believe he could change the world, and talented enough to do it," said Mr Obama.

A statement from Mr Jobs's family said they were with him when he died peacefully on Wednesday.

"In his public life, Steve was known as a visionary; in his private life, he cherished his family," they said, requesting privacy and thanking those who had "shared their wishes and prayers" during his final year.

Apple said the company had "lost a visionary and creative genius, and the world has lost an amazing human being".

Tim Cook, who was made Apple's CEO after Mr Jobs stood down in August, said his predecessor had left behind "a company that only he could have built, and his spirit will forever be the foundation of Apple".

Flags are being flown at half mast outside the Apple headquarters in Cupertino, California, while fans of the company have left tributes outside Apple shops around the world.

"What he's done for us as a culture, it resonates uniquely in every person," said Cory Moll, an Apple employee in San Francisco.

"Even if they never use an Apple product, the impact they have had is so far-reaching."

At the company's Shanghai shop, customer Jin Yi said Mr Jobs had created gadgets which had "changed people's perceptions of machines".
"""

manual_text = st.text_area("Or paste text here", value=default_text, height=250)

if uploaded_file:
    st.info("Using uploaded file")
    text = uploaded_file.read().decode("utf-8")
else:
    st.info("Using pasted text")
    text = manual_text


# -----------------------------
# Buttons
# -----------------------------
run = st.button("Run DFA")


# -----------------------------
# RUN ANALYSIS
# -----------------------------
if run:

    matches, log = scan_text_with_log(text)
    results = convert_matches(matches)

    counts = Counter(m.pattern for m in matches)
    total_occurrences = sum(counts.values())

    status = "ACCEPT" if matches else "REJECT"

    # -----------------------------
    # TEXT DISPLAY
    # -----------------------------
    st.subheader("Text Used for Demo")
    st.text_area("", value=text, height=200, disabled=True)

    # -----------------------------
    # STATUS
    # -----------------------------
    st.subheader("Status")
    if matches:
        st.success(status)
    else:
        st.error(status)

    # -----------------------------
    # METRICS
    # -----------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Patterns", len(PATTERN_SET))
    col2.metric("Matched Patterns", sum(1 for p in PATTERN_SET if results[p]))
    col3.metric("Total Occurrences", total_occurrences)

    # -----------------------------
    # TABLE
    # -----------------------------
    st.subheader("Results Table")
    st.dataframe(build_summary_table(results), use_container_width=True)
    st.write(f"**Total Found:** {total_occurrences}")

    # -----------------------------
    # HIGHLIGHT
    # -----------------------------
    st.subheader("Visualization (Highlighted Text)")

    highlighted = highlight_text_html(text, matches)

    st.markdown(
        f"<div style='padding:10px;border:1px solid #ccc;border-radius:8px'>{highlighted}</div>",
        unsafe_allow_html=True
    )

    # -----------------------------
    # DFA Processing Log
    # -----------------------------

    st.subheader("DFA Processing Log")

    if log:
        log_json = json.dumps(log).replace("</", "<\\/")
        components.html(
            f"""
            <script>
                const dfaLog = {log_json};
                console.groupCollapsed("DFA Processing Log");
                for (const entry of dfaLog) {{
                    console.log(
                        `Run ${{entry.Run}} | Step ${{entry.Step}} | index ${{entry['Text Index']}} | ${{entry.Transition}} | ${{entry.Outcome}} | buffer: ${{entry['Current Buffer']}}`
                    );
                }}
                console.table(dfaLog);
                console.groupEnd();
            </script>
            """,
            height=0,
        )
        st.caption("Log details were sent to your browser console. Open DevTools (F12) and view the Console tab.")
    else:
        st.write("No processing log available")