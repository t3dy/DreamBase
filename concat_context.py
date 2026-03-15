"""
Generate DREAMBASE_FULL_CONTEXT.md — a single document containing all code,
templates, and design documents for loading into ChatGPT.
"""
import os

FILE_ORDER = [
    ("schema.py", "Database Schema"),
    ("app.py", "Flask Web Application"),
    ("index.py", "Indexer (FTS5, VADER, Keywords)"),
    ("summarize.py", "Summarizer (Batch Export/Import)"),
    ("chunk.py", "Chunker (GPT-ready exports)"),
    ("showcase_chunks.py", "Showcase Batch Chunk Generator"),
    ("verify.py", "Verification Queries"),
    ("ingest_chatgpt_json.py", "ChatGPT JSON Ingestor"),
    ("ingest_html_chats.py", "HTML Chat Ingestor"),
    ("ingest_pdf_chats.py", "PDF Chat Ingestor"),
    ("ingest_claude_db.py", "Claude DB Ingestor"),
    ("ingest_facebook_json.py", "Facebook JSON Ingestor"),
    ("ingest_google_chat.py", "Google Chat Ingestor"),
    ("ingest_gmail_mbox.py", "Gmail Mbox Ingestor"),
    ("ingest_pkd_chats.py", "PKD Chats Ingestor"),
    ("ingest_sms_twitter.py", "SMS + Twitter Ingestor"),
    ("templates/index.html", "Browse Page Template"),
    ("templates/conversation.html", "Conversation View Template"),
    ("templates/ideas.html", "Ideas Page Template"),
    ("templates/viz.html", "Visualizations Dashboard Template"),
    ("templates/showcase.html", "Showcase Page Template (Tabbed)"),
    ("templates/showcases.html", "Showcases Index Template"),
    ("templates/collections.html", "Collections Index Template"),
    ("templates/collection.html", "Collection Detail Template"),
    ("templates/values.html", "Values Page Template"),
    ("improve_summaries.py", "Summary Improvement Agents"),
    ("static/style.css", "CSS Stylesheet"),
    ("DREAMBASE_DESIGN_TEMPLATE.md", "Rabbit Hole Web Design Template"),
    ("DREAMBASE_TEMPLATES.md", "Writing Templates and Style Guides"),
    ("SUMMARYTEMPLATE.md", "Summary Writing Templates"),
    ("PROMPTING_EVALUATION.md", "Prompting Methodology Evaluation"),
]

PREAMBLE = """# Dreambase: Full Project Context Document
**Generated: 2026-03-14**
**Purpose:** Complete context for ChatGPT deep analysis sessions.
Contains all code, templates, design documents, and data analysis.

## Project Summary
Dreambase (formerly Megabase) is a Personal Knowledge Archaeology System that unifies
2+ years of LLM conversations, social media, texts, and emails into one searchable
SQLite database with a Flask web UI. Built across 8+ Claude Code sessions.

**Stats:** 4,308 conversations | 3.9M messages | 1.3 GB database | 15 Python scripts |
7 data visualizations | 3 showcase dream pages | 397 extracted ideas

---

## DESIGN INSTINCTS ANALYSIS (from database mining)

### Topic Prevalence (conversations tagged)
| Tag | Conversations | Total Pages | Avg Pages | User Sentiment |
|-----|--------------|-------------|-----------|----------------|
| game_idea | 628 | 25,724 | 41.0 | +0.193 |
| esoteric | 566 | 30,398 | 53.7 | +0.160 |
| personal | 549 | 20,132 | 36.7 | +0.161 |
| alchemy | 442 | 30,574 | 69.2 | +0.152 |
| educational | 337 | 15,425 | 45.8 | +0.233 |
| mtg | 261 | 11,690 | 44.8 | +0.183 |
| coding | 248 | 8,336 | 33.6 | +0.199 |
| app_project | 166 | 5,935 | 35.8 | +0.218 |
| pkd | 112 | 3,938 | 35.2 | +0.158 |

### Sentiment Patterns (what the data reveals about scholarly style)

**Most Positive Topics (by user message sentiment):**
1. Educational (+0.233) - Ted is most enthusiastic when designing things that teach
2. App Projects (+0.218) - Building functional tools generates positive energy
3. Coding (+0.199) - Technical problem-solving is satisfying

**Most Complex/Serious Topics (lower but still positive sentiment):**
1. Alchemy (+0.152) - Deepest engagement (69.2 avg pages) but most wrestling
2. PKD (+0.158) - Literary/philosophical work carries more tension
3. Esoteric (+0.160) - Intellectual depth correlates with seriousness

**Key Insight:** Ted writes most positively about EDUCATIONAL topics and most
extensively about ALCHEMY topics. The sweet spot - where passion meets depth -
is where these two overlap: games that teach through alchemical mechanics.
The Alchemy Board Game sits exactly at this intersection.

### Idea Maturity Distribution
| Category | Sketch | Design | Prototype | Built |
|----------|--------|--------|-----------|-------|
| Game | 230 | 34 | 19 | 1 |
| App | 32 | 2 | 6 | 0 |
| Educational | 0 | 5 | 3 | 2 |
| Other | 3 | 35 | 18 | 7 |

### Design Values (evidence-based)
1. **Implicit Pedagogy** - Games should teach through mechanics, not tutorials
2. **Discovery Over Instruction** - Hidden complexity reveals itself through play
3. **Data Density** - Tufte-inspired information design, no chartjunk
4. **Systems Thinking** - Everything connects; ideas cross-pollinate across domains
5. **Honest Self-Reflection** - Willing to confront what the data shows

---

"""


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with open("DREAMBASE_FULL_CONTEXT.md", "w", encoding="utf-8") as out:
        out.write(PREAMBLE)

        for filepath, label in FILE_ORDER:
            if not os.path.exists(filepath):
                continue

            ext = filepath.rsplit(".", 1)[-1]
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            out.write(f"## {label}\n")
            out.write(f"**File:** `{filepath}` ({len(content):,} chars)\n\n")
            out.write(f"```{ext}\n")
            out.write(content)
            if not content.endswith("\n"):
                out.write("\n")
            out.write("```\n\n---\n\n")

    sz = os.path.getsize("DREAMBASE_FULL_CONTEXT.md")
    print(f"Generated: DREAMBASE_FULL_CONTEXT.md")
    print(f"Size: {sz:,} bytes = ~{sz // 4:,} tokens")


if __name__ == "__main__":
    main()
