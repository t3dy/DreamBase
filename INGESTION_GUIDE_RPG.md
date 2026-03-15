# Dreambase: The Data Ingestion Questline

**How to feed the database everything you've ever said, written for someone who's cleared every RPG side quest since age 12.**

---

## THE SETUP: Your Party Composition

You've got **6 agent scripts** (think of them as party members) and **1 dungeon** (the SQLite database). Each agent specializes in parsing a different data format. They don't share cooldowns. You can run them all in parallel — they write to different tables and don't step on each other.

```
┌──────────────────────────────────────────────┐
│              MEGABASE.DB (the dungeon)        │
│                                              │
│  conversations ←── messages ←── tags         │
│       ↑                ↑         ↑           │
│    sources          sentiment   ideas        │
└──────────────────────────────────────────────┘
         ↑↑↑↑↑↑↑↑↑↑
    7 INGESTORS FEEDING IN
```

---

## PHASE 1: THE ARCHITECT (creates the dungeon)

**Script:** `schema.py`
**What it does:** Creates all the empty tables in `megabase.db`
**Analogy:** Building the dungeon before spawning any mobs
**Run once:** `python schema.py`
**Completion signal:** "Created megabase.db with 8 tables"

Think of this like procedurally generating the map before anything lives in it.

---

## PHASE 2: THE INGESTORS (7 parallel grind sessions)

Each ingestor reads a different data source and dumps it into the same database. They're independent — run them in any order, even simultaneously. Like running 7 different fetch quests at the same time because none of them block each other.

### Ingestor 1: ChatGPT JSON
**Script:** `ingest_chatgpt_json.py`
**Source:** `Desktop/GPT Data/conversations.json`
**Difficulty:** Easy — it's already structured JSON
**Boss mechanic:** ChatGPT stores conversation trees, not flat lists. Messages branch. The script walks the tree depth-first to reconstruct the actual conversation order.
**Loot:** ~857 conversations, thousands of messages
**XP earned:** Your entire ChatGPT history in one searchable place

### Ingestor 2: HTML Chat Logs
**Script:** `ingest_html_chats.py`
**Source:** `Downloads/LLM logs/*.html` (1,050 files)
**Difficulty:** Easy — BeautifulSoup parses the HTML
**Boss mechanic:** Each file is a self-contained chat. Parse the `.msg.user` and `.msg.assistant` divs.
**Loot:** ~1,050 conversations
**XP earned:** Every AI conversation you saved as HTML

### Ingestor 3: PDF Chat Logs
**Script:** `ingest_pdf_chats.py`
**Source:** `Downloads/LLM logs/*.pdf` (653 files)
**Difficulty:** Medium — PDFs are the dark souls of data formats
**Boss mechanic:** PyMuPDF extracts text, but you lose formatting. The script guesses speaker turns from patterns like "User:" and "Assistant:" or from alternating text blocks.
**Loot:** ~653 conversations
**XP earned:** Even your printed-to-PDF conversations are now searchable

### Ingestor 4: Claude Database
**Script:** `ingest_claude_db.py`
**Source:** `Dev/Claude Data/*.db`
**Difficulty:** Easy — it's already SQLite, just a different schema
**Boss mechanic:** Map Claude's schema to megabase's schema. Different column names, same idea.
**Loot:** ~212 conversations
**XP earned:** Your Claude conversations alongside your ChatGPT ones

### Ingestor 5: Facebook Messages
**Script:** `ingest_facebook_json.py`
**Source:** `Downloads/your_facebook_activity/messages/inbox/*/message_1.json`
**Difficulty:** Easy — Takeout JSON, well-structured
**Boss mechanic:** 3,967 inbox folders, one JSON per thread. Iterate all of them.
**Loot:** ~767 conversation threads
**XP earned:** Every Facebook DM and group chat

### Ingestor 6: Gmail (the raid boss)
**Script:** `ingest_gmail_mbox.py`
**Source:** `Downloads/All mail...mbox` (14 GB!)
**Difficulty:** Medium — it's huge and streaming is required
**Boss mechanic:** The mbox format is one giant text file. You can't load it all into memory. The script uses Python's `mailbox` module to stream-parse it, extracting headers first, then going back for bodies of personal emails only. Skip automated/marketing emails.
**Loot:** Thousands of email threads
**XP earned:** Your email conversations mined for intellectual content
**Pro tip:** This is the longest grind. Let it run in background.

### Ingestor 7: Google Chat + SMS + Twitter + PKD
**Script:** `ingest_google_chat.py`, `ingest_sms_twitter.py`, `ingest_pkd_chats.py`
**Source:** Various Takeout/backup files
**Difficulty:** Easy — small datasets, known formats
**Boss mechanic:** SMS already has a rich SQLite schema. Twitter has a pre-built archive DB. Just map and import.
**Loot:** ~837 conversations across 4 sources
**XP earned:** The personal communication layer

---

## PHASE 3: THE ENRICHMENT PASS (buff your data)

After all ingestors finish, you have raw conversations. Now you buff them.

### The Indexer — `index.py`
Think of this as enchanting all your gear after you've collected it.

- **`python index.py fts`** — Builds a full-text search index. Now you can search across 3.9M messages instantly. Like adding "detect hidden" to your whole inventory.
- **`python index.py sentiment`** — VADER sentiment scoring on every message. Each message gets a mood label: positive, negative, neutral. Like adding a "sense motive" check to every conversation.
- **`python index.py keywords`** — Tag conversations by topic using keyword patterns. "game_idea", "alchemy", "esoteric", etc. Like auto-sorting your loot into categories.
- **`python index.py stats`** — Calculate message counts, character counts, estimated pages per conversation. The "appraise item" pass.

### The Summarizer — `summarize.py`
- **`python summarize.py auto`** — Deterministic: grabs the first assistant response as a provisional summary. Free, instant, covers everything. Like auto-naming items in your inventory.
- **`python summarize.py batch-export`** — Generates batch files you paste into ChatGPT for better summaries. The manual grind, but it produces gold-tier descriptions.

### The Janitor — `improve_summaries.py janitor`
Fixes the ~400 summaries where the "summary" was actually the AI saying "Here is a summary of..." instead of, you know, the actual summary. Like cleaning up your inventory after a messy dungeon run.

### The Messenger — `improve_summaries.py messenger`
Auto-generates basic summaries for SMS/Facebook/Google Chat from message content. Tier 4 quality but better than nothing. Like auto-identifying unidentified items.

---

## PHASE 4: THE BROWSER (explore your loot)

**Script:** `app.py`
**Command:** `python app.py` then open `localhost:5555`
**What you get:**
- **Browse** — Card grid of all 4,308 conversations. Search, filter, sort.
- **Ideas** — 397 extracted ideas with grid/list view, category + maturity filters.
- **Viz** — 7 data visualizations (timeline, topic constellation, heatmap, sentiment river, treemap, etc.)
- **Showcases** — Deep 5-tab pages for 3 game dreams.
- **Collections** — 8 curated thematic rabbit holes.
- **Values** — Scholarly and engineering values with database evidence.

---

## PHASE 5: THE DEEP READING GRIND (endgame)

Once you have the database and browser running, the real game begins:

1. **Find conversations that matter** — Browse by tag, sort by pages, filter by sentiment
2. **Export for deep reading** — `python chunk.py export <conversation_id>` produces ChatGPT-ready .md files
3. **Paste into ChatGPT** with analysis prompts (idea extraction, theme analysis, evolution tracking)
4. **Import notes back** — ChatGPT's analysis goes back into the database
5. **Repeat** — Each deep read surfaces more ideas, connections, patterns

This is the endgame loop. There's no level cap. The more you read, the more the database reveals.

---

## THE FULL QUESTLINE (run order)

```
1. python schema.py                           # Create dungeon
2. python ingest_chatgpt_json.py              # (parallel)
3. python ingest_html_chats.py                # (parallel)
4. python ingest_pdf_chats.py                 # (parallel)
5. python ingest_claude_db.py                 # (parallel)
6. python ingest_facebook_json.py             # (parallel)
7. python ingest_gmail_mbox.py                # (parallel, long grind)
8. python ingest_google_chat.py               # (parallel)
9. python ingest_sms_twitter.py               # (parallel)
10. python ingest_pkd_chats.py                # (parallel)
11. python index.py fts                       # After all ingestors done
12. python index.py sentiment                 # (parallel with fts)
13. python index.py keywords                  # (parallel)
14. python index.py stats                     # (parallel)
15. python summarize.py auto                  # After indexer done
16. python improve_summaries.py janitor       # Fix bot summaries
17. python improve_summaries.py messenger     # Generate SMS/FB summaries
18. python app.py                             # Launch browser, explore
```

Steps 2-10 can all run in parallel (separate terminal windows).
Steps 11-14 can all run in parallel.
Steps 15-17 are sequential (each improves on the previous).

**Total estimated runtime:** ~30 minutes for everything except Gmail (which could take an hour).
**Total API cost:** $0. Everything is local or uses your existing ChatGPT subscription.
**Total disk space:** ~1.3 GB for the database.

---

## ACHIEVEMENT UNLOCKED

When you finish:
- 4,308 conversations searchable in under a second
- 3.9M messages with sentiment analysis
- 397 ideas cataloged by category and maturity
- 7 data visualizations of your intellectual evolution
- 8 curated collections for rabbit-hole browsing
- 3 showcase dream pages for your best game ideas
- Batch export pipeline for unlimited ChatGPT deep reading

You've basically built a personal Library of Alexandria, except it only contains things you actually said.
