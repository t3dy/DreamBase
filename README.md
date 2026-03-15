# Dreambase

**[github.com/t3dy/DreamBase](https://github.com/t3dy/DreamBase)**

A personal knowledge archaeology system that unifies two years of LLM conversations, social media, email, and text messages into a single searchable SQLite database — then surfaces them through curated scholar profiles, thematic collections, game design showcases, and public domain art galleries.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-green) ![SQLite](https://img.shields.io/badge/SQLite-FTS5-orange) ![Conversations](https://img.shields.io/badge/Conversations-4%2C308-purple) ![Messages](https://img.shields.io/badge/Messages-3.9M-red)

---

## What This Is

Dreambase started as a question: *what happens when you treat two years of AI conversations as a primary source archive?*

The answer turned out to be a 1.3GB SQLite database containing 4,308 conversations and 3.9 million messages from 10 different platforms, browsable through a Flask app with full-text search, sentiment analysis, 30 scholar profiles, 10 thematic collections, and 3 game design deep-dives — all illustrated with public domain Renaissance and alchemical art.

The conversations span alchemy, Kabbalah, Philip K. Dick, game design, procedural content generation, digital humanities, Marxist economics, Magic: The Gathering analytics, and the history of Western esotericism.

## Tech Stack

### Core

| Layer | Technology | Role |
|-------|-----------|------|
| Database | **SQLite 3** with **FTS5** | Unified storage, full-text search |
| Web | **Flask 3.x** + **Jinja2** | Browsing UI with 16 templates |
| Sentiment | **VADER** (vaderSentiment) | Compound sentiment scoring on all messages |
| PDF parsing | **PyMuPDF** (fitz) | Text extraction from 653 PDF chat exports |
| Testing | **pytest** | Route and data integrity tests |
| Language | **Python 3.10+** | Everything is pure Python, stdlib where possible |

### No API Keys Required

A deliberate design constraint. Summaries are generated deterministically (first assistant response, truncated) or via a manual ChatGPT batch workflow where conversations are exported as `.md` chunk files, pasted into ChatGPT, and the structured responses are imported back. Zero API cost.

## Data Sources

Nine ingestor scripts parse conversations from 10 platforms into a unified schema:

| Source | Script | Volume | Format |
|--------|--------|--------|--------|
| ChatGPT | `ingest_chatgpt_json.py` | 857 conversations | JSON (tree-mapped messages) |
| LLM logs (HTML) | `ingest_html_chats.py` | 1,050 files | Self-contained HTML |
| LLM logs (PDF) | `ingest_pdf_chats.py` | 653 files | PDF via PyMuPDF |
| Claude | `ingest_claude_db.py` | 1 database | SQLite |
| Gmail | `ingest_gmail_mbox.py` | 14 GB archive | mbox (streaming parser) |
| Facebook Messenger | `ingest_facebook_json.py` | 3,967 threads | Takeout JSON |
| Google Chat | `ingest_google_chat.py` | 133 conversations | Takeout JSON |
| SMS | `ingest_sms_twitter.py` | 36 MB database | SQLite |
| Twitter | `ingest_sms_twitter.py` | 147 MB archive | SQLite |
| PKD research chats | `ingest_pkd_chats.py` | 13 files | Mixed HTML |

## Database Schema

Eight tables with full-text search and foreign key relationships:

```
sources ──→ conversations ──→ messages ──→ entities (NER)
                │                │
                ├──→ conversation_tags ──→ tags
                ├──→ ideas
                └──→ chunk_exports

+ messages_fts (FTS5 virtual table for full-text search)
```

**Key fields:**
- `conversations`: title, summary, created_at, message_count, char_count, estimated_pages
- `messages`: role (user/assistant/system), content, sentiment_vader, sentiment_label
- `ideas`: name, category (game/app/educational/product), maturity (sketch → built)
- `conversation_tags`: tag assignment with confidence scores and method tracking

## Flask App

### Routes

| Route | Page |
|-------|------|
| `/` | Card grid dashboard — search, filter by source/tag/date, click to expand |
| `/conversation/<id>` | Full message-level conversation view |
| `/scholars` | Index of 30 scholar profiles |
| `/scholar/<slug>` | 6-tab deep dive: Overview, Journey, Quotes, Connections, Gallery, Sources |
| `/showcases` | Index of curated game design showcases |
| `/dream/<slug>` | Showcase deep dive with narrative, timeline, pedagogy tiers |
| `/collections` | 10 thematic collections |
| `/collection/<slug>` | Collection page with conversation cards |
| `/ideas` | Extracted game/app/educational product ideas |
| `/projects` | Building projects tracker |
| `/viz` | Data visualization dashboard |
| `/values` | Values and metadata view |
| `/api/search` | Full-text search JSON endpoint |

### Scholar Pages

30 curated profiles spanning Renaissance philosophy, Western esotericism, game design theory, and digital humanities. Each scholar page includes:

- **Narrative portrait** — HTML essay on the intellectual thread
- **Intellectual journey** — Timeline entries linked to source conversations
- **Key quotes** — Extracted from the longest and most substantive conversations
- **Connections** — Cross-references to other scholars and collections
- **Gallery** — Public domain Renaissance and alchemical art (served locally from `static/art/`)
- **Source conversations** — Direct links to every conversation about that scholar

### Art Gallery

Nine public domain artworks downloaded from Wikimedia Commons and served locally:

- Giovanni Pico della Mirandola (Cristofano dell'Altissimo, Uffizi)
- Giordano Bruno statue at Campo de' Fiori
- Giordano Bruno portrait (19th century engraving)
- John Dee portrait (Ashmolean Museum)
- Paracelsus portrait (attributed to Quentin Matsys)
- Isaac Newton portrait (Godfrey Kneller, 1689)
- Thomas Aquinas (Carlo Crivelli, Demidoff Altarpiece, 1476)
- Khunrath's Alchemist's Laboratory (Amphitheatrum Sapientiae Aeternae, 1595)
- Kabbalistic Tree of Life (medieval manuscript)

## Analysis Pipeline

### Deterministic Enrichment (`index.py`)

- **FTS5 indexing** — Full-text search across all 3.9M messages
- **VADER sentiment** — Compound scores and positive/negative/neutral labels on every message
- **Keyword tagging** — 11 categories: game_idea, app_project, educational, alchemy, pkd, mtg, esoteric, coding, personal, etc.
- **Idea detection** — Automatic extraction with maturity classification (sketch/design/prototype/built)
- **Stats computation** — Message counts, character counts, estimated page lengths

### Summarization (`summarize.py`)

Two-phase approach with zero API cost:

1. **Auto mode** — Extracts first assistant response (truncated to 500 chars) as provisional summary for all 4,308 conversations. Instant and free.
2. **Batch mode** — Exports conversation excerpts as `.md` files sized for ChatGPT's context window (~60K chars per chunk). User pastes into ChatGPT, copies structured response, imports back via `batch-import`.

### Chunk Export (`chunk.py`)

The key differentiator — turns any conversation into GPT-ready reading material:

- Target chunk size: ~60,000 chars (~15K tokens)
- Splits on message boundaries (never mid-message)
- Includes header with title, source, date range, chunk number
- Ships with analysis prompt templates in `prompts/`:
  - `idea_extraction.md` — Catalog every game/app/product idea
  - `sentiment_deep.md` — Emotional arc analysis
  - `theme_summary.md` — Theme identification and connections
  - `evolution.md` — Track how thinking changed across the conversation

## The Learning Process

This project was built across eight sessions as a collaboration between a human (interdisciplinary researcher working across alchemy, game design, PKD studies, and digital humanities) and Claude Code. Here's what we learned:

### Session 1-3: Ingestion

The hardest part wasn't parsing — it was normalization. ChatGPT conversations are tree-structured (each message has a parent pointer, not a simple list). Facebook messages have mojibake encoding that needs repair. Gmail at 14GB requires streaming, not loading. Each source had its own idea of what a "conversation" is — a thread, a chat, an email chain, a PDF document.

**Key decision:** Use `external_id` to prevent duplicate ingestion across runs. Every ingestor is idempotent.

### Session 4: Indexing

VADER sentiment analysis on 3.9 million messages runs in minutes on SQLite. The keyword tagger uses regex patterns calibrated against known conversations — "game_idea" triggers on terms like "deck-building", "roguelike", "procedural generation" appearing near "idea", "concept", "design". Confidence scores distinguish keyword matches (0.7) from LLM-verified tags (0.9) from manual curation (1.0).

**Key decision:** Keep everything deterministic and local. No API calls in the indexing pipeline.

### Session 5-6: The ChatGPT Batch Workflow

Instead of paying for API summarization, we built a human-in-the-loop pipeline: export conversation excerpts as markdown chunks, paste into ChatGPT (which the user already has via subscription), get structured responses back, import them. This turned a potential $50+ API bill into $0 and produced better summaries because the human could course-correct in real time.

**Key decision:** The chunker respects message boundaries and includes enough context for the LLM to understand the conversation's arc without seeing all of it.

### Session 7-8: The Flask Browser

The browse UI went through several iterations. The initial card grid was functional but flat. Adding scholar profiles, thematic collections, and game showcases transformed it from a search tool into something closer to a digital humanities exhibit — you can trace how an interest in Pico della Mirandola connects to Kabbalah connects to game design through the actual conversation history.

**Key decision:** Curated pages (scholars, showcases, collections) are defined as Python dicts in `app.py`, not database tables. This keeps curation fast and version-controlled.

### What We'd Do Differently

1. **Start with `requirements.txt`** — Dependencies accumulated organically. Flask, PyMuPDF, and vaderSentiment are the only third-party packages, but they should have been pinned from day one.
2. **Separate curation from code** — The `SHOWCASES`, `SCHOLARS`, and `COLLECTIONS` dicts in `app.py` grew to hundreds of lines. They'd be better as YAML or JSON files loaded at startup.
3. **Build FTS5 triggers** — Currently the FTS index must be rebuilt manually after new ingestion. SQLite triggers could keep it in sync automatically.

## Project Structure

```
megabase/
├── app.py                          # Flask app (routes, showcase/scholar/collection data)
├── schema.py                       # Database creation and shared utilities
├── index.py                        # FTS5, VADER sentiment, keyword tagging, idea detection
├── summarize.py                    # Deterministic + batch summarization pipeline
├── chunk.py                        # GPT-ready conversation export
├── improve_summaries.py            # Summary quality improvement agents
│
├── ingest_chatgpt_json.py          # ChatGPT conversations.json parser
├── ingest_html_chats.py            # LLM logs HTML parser
├── ingest_pdf_chats.py             # LLM logs PDF parser (PyMuPDF)
├── ingest_claude_db.py             # Claude SQLite database importer
├── ingest_gmail_mbox.py            # Gmail mbox streaming parser
├── ingest_facebook_json.py         # Facebook Messenger JSON parser
├── ingest_google_chat.py           # Google Chat Takeout parser
├── ingest_pkd_chats.py             # PKD research chat parser
├── ingest_sms_twitter.py           # SMS + Twitter SQLite importer
│
├── generate_narratives.py          # Scholar/showcase narrative generation
├── generate_timelines.py           # Timeline + quote extraction
├── generate_images.py              # Wikimedia Commons image sourcing
├── download_art.py                 # Art downloader with API resolution
├── fix_image_paths.py              # Local path migration for images
│
├── prompts/                        # Analysis prompt templates for ChatGPT
│   ├── idea_extraction.md
│   ├── sentiment_deep.md
│   ├── theme_summary.md
│   └── evolution.md
│
├── templates/                      # Jinja2 templates (16 HTML files)
├── static/
│   ├── style.css                   # Dark theme CSS
│   └── art/                        # Public domain artwork (9 images)
│
├── test_app.py                     # pytest test suite
├── verify.py                       # Database integrity checks
└── narratives.json                 # Generated narrative content
```

## Running Locally

```bash
# Install dependencies
pip install flask vaderSentiment pymupdf pytest

# Build the database (requires source data files on disk)
python schema.py
python ingest_chatgpt_json.py
python ingest_html_chats.py
# ... (run each ingestor for your data sources)
python index.py

# Start the Flask app
python app.py
# Open http://localhost:5000
```

Note: The database (`megabase.db`, 1.3GB) is not included in the repository. The ingestor scripts expect source data files at specific paths on the original machine. The Flask app, templates, and all curation data are fully self-contained.

## License

The codebase is open source. Artwork in `static/art/` is public domain (pre-1900 works sourced from Wikimedia Commons).
