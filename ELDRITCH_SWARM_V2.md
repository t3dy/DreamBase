# Eldritch Swarm V2: The Request Avalanche

**Palmer Eldritch sees all realities at once.**
**This plan captures every pending request from the brainstorm cascade.**

---

## SITUATION: The Request Queue (Post-Scholar-Build)

| # | Request | Type | Status |
|---|---------|------|--------|
| 1 | 30 scholar showcase pages | Code | DONE |
| 2 | Projects visualization page | Code | DONE |
| 3 | Fix cramped scholar cards | CSS | DONE |
| 4 | AlchemyDB integration (hyperlinked alchemy terms) | Code+Data | PLANNED |
| 5 | Reader pane (click "1438 pages" to read inline) | Code | PLANNED |
| 6 | Short prompts database + behavioral action map | Data+Viz | PLANNED |
| 7 | Content creation showcase | Data+Code | PLANNED |
| 8 | Document processing showcase | Data+Code | QUESTIONABLE (thin data) |
| 9 | CS rabbit holes showcase | Data+Code | PLANNED |
| 10 | Algorithms in Wonderland lavish showcase (Carroll illustrations) | Code+Design | PLANNED |
| 11 | Consistent index-card style across all card views | CSS | PLANNED |
| 12 | Showcase ideas + 20 clarifying questions | Planning | THIS DOCUMENT |

---

## SWARM ARCHITECTURE

### Workstream A: "The Alchemist" (AlchemyDB Integration)

Ingest AlchemyDB's 187 lexicon entries and wire them into the browsing experience.

| Agent | Task | Inputs | Outputs | Completion Signal |
|-------|------|--------|---------|-------------------|
| **A1: Lexicon-Ingestor** | Import AlchemyDB lexicon into megabase (new `alchemy_lexicon` table) | `C:\OldDevProjects\AlchemyDB\alchemydb.db` | 187 entries in megabase.db | Row count matches |
| **A2: Term-Linker** | Scan conversation summaries + scholar pedagogy for alchemy terms, build term-to-page index | alchemy_lexicon + conversations | `alchemy_mentions` table linking terms to conversations | Mentions table populated |
| **A3: Lexicon-Browser** | Create `/alchemy` index route + `/alchemy/<term>` detail route with definition, linked conversations, related terms | alchemy_lexicon + mentions | Routes + templates | Pages render |
| **A4: Auto-Hyperlinker** | Add JS/template logic to detect alchemy terms in any page text and auto-link to `/alchemy/<term>` | Term list + existing templates | Updated templates with auto-linking | Terms clickable on scholar/showcase pages |

**Communication:**
```
A1 (ingest) -> [alchemy_lexicon table] -> A2 (link terms to conversations)
A2 -> [alchemy_mentions table] -> A3 (browse routes)
A3 -> [working routes] -> A4 (auto-hyperlink across site)
```

**AlchemyDB Data Quality Issues to Fix During Ingestion:**
- 135 entries categorized as "Practitioner" include substances, processes, and texts (mislabeled)
- `theoretical_lineage` column contains duplicate of `definition` (ingestion bug)
- 0 of 187 entries marked `is_verified` (all AI-generated)
- Recommended: re-categorize into Practitioner, Substance, Process, Text, Apparatus, Concept during import

### Workstream B: "The Reader" (Inline Reading Pane)

| Agent | Task | Inputs | Outputs | Completion Signal |
|-------|------|--------|---------|-------------------|
| **B1: Reader-Route** | Create `/read/<context>/<id>` route that serves concatenated messages from linked conversations | conversation_ids from SCHOLARS/SHOWCASES/COLLECTIONS | JSON endpoint or rendered HTML | Route returns messages |
| **B2: Reader-UI** | Add AJAX-loaded reader panel to scholar/showcase/collection detail pages | Click handler on "X pages" stat | Scrollable reader pane with message-level view | Panel opens on click |
| **B3: Reader-Nav** | Add keyboard nav (j/k scroll, n/p next/prev conversation) and reading progress indicator | Reader pane | Enhanced reading experience | Keys work |

**Design Decision Needed:** Full-page reader vs. side panel vs. expandable section?

### Workstream C: "The Curator" (New Showcases & Collections)

| Agent | Task | Inputs | Outputs | Completion Signal |
|-------|------|--------|---------|-------------------|
| **C1: Content-Creator-Miner** | Find content creation conversations (game design, course design, creative tools, writing) | megabase.db | Curated conversation_ids list | List reviewed |
| **C2: CS-Miner** | Find CS rabbit hole conversations (algorithms, data structures, programming theory) | megabase.db | Curated conversation_ids list | List reviewed |
| **C3: Showcase-Builder** | Create new COLLECTIONS/SHOWCASES entries + update app.py | Mined IDs | New routes working | Pages render |
| **C4: Wonderland-Artisan** | Build lavish Algorithms in Wonderland showcase with Carroll illustrations (Tenniel public domain), novel excerpts as section headers, CS concepts mapped to Wonderland metaphors | Conversation 585 + public domain images | Special showcase template | Visual showcase live |

**Algorithms in Wonderland Showcase Concept:**
- Hero: Tenniel's Alice falling down the rabbit hole (public domain, 1865)
- Section headers: Carroll quotes mapping to CS concepts
  - "Begin at the beginning" -> Algorithms 101
  - "We're all mad here" -> NP-completeness and computational complexity
  - "Curiouser and curiouser" -> Recursion and self-reference
  - "Off with their heads!" -> Stack operations and LIFO
  - "Who are YOU?" -> Identity, hashing, and type systems
- Gallery tab: Tenniel illustrations with CS captions
- This is a SHOWCASE (5-tab treatment), not a collection

### Workstream D: "The Cartographer" (Behavioral Action Map)

| Agent | Task | Inputs | Outputs | Completion Signal |
|-------|------|--------|---------|-------------------|
| **D1: Prompt-Extractor** | Extract all user messages under 100 words from chatgpt+claude sources | megabase.db messages table | `short_prompts` table or CSV | Count matches expectation (~500K from src 1,4) |
| **D2: Prompt-Classifier** | Classify prompts by behavioral intent using keyword patterns | short_prompts | Classified prompts with labels: reading, building, learning, creating, directing, debugging, exploring, socializing | Classification coverage > 80% |
| **D3: Action-Visualizer** | Create `/actions` page with Tufte-style behavioral visualizations | Classified prompts | Sankey diagram or treemap of behaviors over time | Page renders |

**Behavioral Categories (proposed):**
- **Reading:** "summarize...", "what does X say about...", "give me a table of...", "continue with the book..."
- **Building:** "build the game", "make a script that...", "create a database...", "fix the bug in..."
- **Learning:** "explain...", "how does X work...", "what is the difference between...", "teach me..."
- **Creating:** "write an essay...", "design a...", "make a mockup of...", "give me ideas for..."
- **Directing:** "now do...", "proceed with...", "continue...", "next..."
- **Debugging:** "it's not working", "I get an error...", "fix...", "why does..."
- **Exploring:** "what if...", "could we...", "is it possible to...", "show me..."

### Workstream E: "The Stylist" (Card Consistency)

| Agent | Task | Inputs | Outputs | Completion Signal |
|-------|------|--------|---------|-------------------|
| **E1: Card-Auditor** | Audit all card layouts across pages (index, ideas, collections, scholars, showcases, projects) | All templates | Report of inconsistencies | Report produced |
| **E2: Card-Unifier** | Create shared `.dreambase-card` CSS class in style.css, apply to all card views | Audit report | Unified card styling | All pages use same card pattern |

---

## COMMUNICATION FLOW

```
WORKSTREAM A (Alchemy)          WORKSTREAM B (Reader)
+-----------------------+       +-----------------------+
| A1: Ingest Lexicon    |       | B1: Reader Route      |
| A2: Link Terms        |       | B2: Reader UI Panel   |
| A3: Browse Routes     |       | B3: Keyboard Nav      |
| A4: Auto-Hyperlink    |       +-----------------------+
+-----------------------+               |
        |                               |
        +--------> SHARED: scholar + showcase templates <--------+
                                                                  |
WORKSTREAM C (Showcases)        WORKSTREAM D (Action Map)        |
+-----------------------+       +-----------------------+        |
| C1: Content Miner     |       | D1: Extract Prompts   |        |
| C2: CS Miner          |       | D2: Classify Behavior |        |
| C3: Showcase Builder   |       | D3: Visualize Actions |        |
| C4: Wonderland Artisan|       +-----------------------+        |
+-----------------------+                                        |
                                WORKSTREAM E (Style)             |
                                +-----------------------+        |
                                | E1: Card Audit        |--------+
                                | E2: Card Unify        |
                                +-----------------------+
```

### Orchestration: Three phases

**Phase 1 — Independent work (all parallel, no dependencies)**
- A1: Ingest AlchemyDB lexicon
- B1: Build reader route
- C1+C2: Mine conversations for new showcases
- D1: Extract short prompts
- E1: Audit card styles

**Phase 2 — Build from Phase 1 outputs (parallel where possible)**
- A2: Link terms to conversations (needs A1)
- A3: Build alchemy browse routes (needs A2)
- B2: Build reader UI (needs B1)
- C3: Build showcase entries (needs C1+C2)
- C4: Build Wonderland showcase (needs C2)
- D2: Classify prompts (needs D1)
- E2: Unify card styles (needs E1)

**Phase 3 — Integration (sequential)**
- A4: Auto-hyperlink alchemy terms across all pages (needs A3 + all templates stable)
- B3: Reader keyboard nav (needs B2)
- D3: Action visualization page (needs D2)

---

## SHOWCASE IDEAS (beyond what's been requested)

### Tier 1: Strong data, clear theme
1. **Algorithms in Wonderland** — lavish Carroll-illustrated CS showcase (conversation 585, 148p)
2. **The Alchemy Lab** — powered by AlchemyDB lexicon, 442 alchemy-tagged conversations, 30,574 pages
3. **Game Design Workshop** — 628 game_idea conversations, from sketches to prototypes
4. **MTG Analytics** — 261 mtg-tagged conversations, draft overlay, Scryfall tools
5. **The Esoteric Library** — 566 esoteric conversations spanning Golden Dawn to chaos magic

### Tier 2: Interesting angle, needs curation
6. **Personal Archaeology** — the SMS/Facebook/email conversations as a time capsule
7. **The Teaching Machine** — 337 educational conversations, pedagogy theory meets game design
8. **Music Engineering Lab** — synth design, DAW automation, harmonic analysis (already a collection, could upgrade)
9. **The Divorce Papers** — if Ted wants to: personal conversations during a difficult period, sentiment-mapped
10. **Cross-Pollination** — conversations that bridge two unrelated domains (alchemy + CS, PKD + game design)

### Tier 3: Experimental / meta
11. **The Prompt Museum** — a showcase OF the action map (how Ted talks to AI, behavioral patterns)
12. **The Rabbit Hole Map** — a meta-visualization of how pages connect to each other across Dreambase
13. **Speed vs. Depth** — short prompt conversations (100-word exchanges) vs. marathon reads (500+ pages)
14. **The Unfinished** — ideas that never left sketch stage, with analysis of why

### Rabbit Hole Feature Ideas
- **Alchemy term auto-linking** — any alchemy word on any page becomes clickable
- **"Go deeper" cards** — at the bottom of every conversation, suggest related conversations by tag overlap
- **Scholar network graph** — interactive D3 visualization of which scholars appear in which conversations together
- **Reading trail** — track which conversations Ted has read deeply vs. skimmed, create a "you haven't explored..." section
- **Flashcard mode** — turn AlchemyDB definitions into Anki-style flashcards
- **Timeline scrubber** — slide through Ted's intellectual history month by month, seeing what he was reading/building

### Template Ideas
- **Gallery showcase** — image-heavy template for visual projects (MTG cards, alchemical emblems, sigils)
- **Reading list template** — ordered book/PDF list with progress indicators and linked conversations
- **Debate template** — side-by-side comparison of opposing views found across conversations
- **Evolution template** — how Ted's understanding of a topic changed over time (early vs. late conversations)

---

## 20 QUESTIONS FOR CLARITY

### Architecture Questions

**1.** The AlchemyDB lexicon has 187 entries, but the categories are messy (substances labeled as "Practitioner"). Should I clean up the categories during import, or preserve them as-is and let you curate later?

**2.** For the alchemy auto-hyperlinking — should EVERY alchemy term on every page be clickable (could be noisy), or only terms within specific sections (summaries, pedagogy boxes, narrative text)?

**3.** The reader pane: when you click "1438 pages" on Pico's page, do you want to read all 6 conversations concatenated into one scroll, or a conversation-picker where you choose which one to read?

**4.** Reader pane design: full-page takeover (like a book reader), a right-side panel (like Gmail), or an expandable section below the stats (accordion-style)?

### Content Questions

**5.** "Algorithms in Wonderland" with Carroll illustrations — should this be a one-off special showcase with a unique template, or should I build a reusable "illustrated showcase" template that other pages could use too (e.g., an alchemy showcase with alchemical emblem illustrations)?

**6.** For the CS rabbit holes showcase — should it include ALL coding conversations (248 tagged), or only the theoretical/conceptual ones (algorithms, data structures, design patterns) excluding bug-fix sessions?

**7.** The content creation showcase — your strongest content creation conversations are actually game design and course design. Should "content creation" mean "things Ted made" (creative output) or "conversations ABOUT content/media creation" (theory)?

**8.** You mentioned "document processing showcase" but the data is thin (12 conversations). Should I fold this into the "Building Dreams" collection instead, or broaden the search to include all data-pipeline conversations?

**9.** The behavioral action map found 77% of your messages are under 100 chars. Many are just "continue" or "proceed." Should the action map filter these out and only classify substantive prompts (>20 words), or include everything?

**10.** You asked for showcase pages for "content creation projects" — does this mean conversations about your projects, or a page listing the actual built projects (which is what /projects already does)?

### Design Questions

**11.** The Algorithms in Wonderland showcase wants "public domain Lewis Carroll illustrations" — should I embed actual Tenniel woodcut images from Wikimedia Commons, or use them as design inspiration for the page layout/typography without embedding?

**12.** You want consistent index-card style across all card views. The current card sizes vary: collection cards are compact, scholar cards are now spacious, idea cards have grid/list toggle. Should ALL cards be the same size, or should each page type have appropriate density?

**13.** For the alchemy lexicon browser — should it feel like a dictionary (A-Z list, click for definition) or like a knowledge graph (visual network of connected terms, click to explore)?

**14.** The behavioral action map visualization — do you want a Tufte-style static chart (like the existing viz page), an interactive explorer (filter by behavior type, time range), or both?

### Scope Questions

**15.** You now have: Browse, Viz, Ideas, Showcases, Collections, Scholars, Projects, Values — that's 8 nav tabs. Adding Alchemy and Actions would make 10. At what point does the nav get too wide? Should some items go into a dropdown or second row?

**16.** The AlchemyDB has 217 PDFs that were never ingested into its relational tables. Do you want to run the PDF ingestion pipeline as part of this work, or just use the 187 lexicon entries that already exist?

**17.** Should the reader pane work everywhere (collections, showcases, scholars, browse page) or just on scholar pages for now?

**18.** How many of these requests do you want built THIS session vs. planned for future sessions? We could do 2-3 more features now and queue the rest.

### Meta Questions

**19.** You're generating ideas faster than they can be built. Should I maintain a living "parking lot" document (per /plan-abendsen-parking) where new ideas get logged with priority, or do you prefer the current rapid-fire approach where we build as we go?

**20.** The end state of Dreambase is getting big — 30 scholars, 9 collections, 3 game showcases, projects page, viz page, values page, ideas page, plus all the new requests. Is this meant to be a personal knowledge tool (just for you), a portfolio/public site, or a framework that other people could adapt for their own data?

---

## FLAGGED ISSUES

| Issue | Severity | Resolution |
|-------|----------|------------|
| A4 (auto-hyperlink) touches ALL templates — high blast radius | MEDIUM | Run after all other template changes are stable |
| Nav has 8+ items, approaching overflow on mobile | MEDIUM | Consider grouped nav or hamburger menu |
| AlchemyDB category data quality needs manual curation | LOW | Auto-reclassify during import, flag for review |
| Wonderland showcase needs external image hosting or local assets | LOW | Use Wikimedia Commons URLs (public domain, stable) |
| D1 will produce ~500K classified prompts — could be slow | LOW | Sample or batch process |
| Reader pane loading all messages for 1438 pages could be very slow | HIGH | Paginate or lazy-load messages |

---

## RECOMMENDED EXECUTION ORDER

If we build right now (this session):
1. **A1: AlchemyDB lexicon import** — 30 minutes, unblocks everything alchemy
2. **B1+B2: Reader pane** — 45 minutes, highest user-visible impact
3. **C4: Algorithms in Wonderland** — 60 minutes, the showpiece

Everything else queued for next session after the 20 questions are answered.
