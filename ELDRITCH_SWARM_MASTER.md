# Eldritch Swarm: Master Orchestration Plan

**Palmer Eldritch sees all realities at once.**
**This plan covers every pending request, organized into parallel workstreams.**

---

## SITUATION: The Request Queue

| # | Request | Type | Status |
|---|---------|------|--------|
| 1 | Collection routes + templates | Code | DONE |
| 2 | SUMMARYTEMPLATE.md | Writing | DONE |
| 3 | Summary improvement swarm (Janitor, Messenger, Curator, Copywriter) | Code+Data | DONE (Phase 1) |
| 4 | Game ideas index with text links + filters | Code | DONE |
| 5 | Scholarly-to-games collection | Data | DONE |
| 6 | RPG-style ingestion guide | Writing | DONE |
| 7 | Building Dreams collection (Dev/OldDevProjects scan) | Data+Code | DONE |
| 8 | Project visualization page with Tufte-style display | Code | PENDING |
| 9 | RAW/Freemasonry/CS/Golden Dawn essay (~20 pages) | Writing | IN PROGRESS (background) |
| 10 | Historian showcase pages | Data+Code | IN PROGRESS (research phase) |
| 11 | ChatGPT batch summary workflow (110 files) | Manual grind | PENDING (Ted does this) |
| 12 | Curator/Copywriter review + apply | Manual review | PENDING (Ted reviews improvements/) |
| 13 | Claude artifacts extraction | Code | DEFERRED (feasible but parked) |
| 14 | Browse ideas by genre (platformer, autobattler, etc.) | Code | PENDING |
| 15 | Regenerate DREAMBASE_FULL_CONTEXT.md | Script | PENDING |

---

## SWARM ARCHITECTURE

### Workstream A: "The Builder" (Code Agents)

Things that produce routes, templates, and UI.

| Agent | Task | Inputs | Outputs | Dependencies |
|-------|------|--------|---------|--------------|
| **A1: Cartographer** | Create /projects route + visualization page | Dev scan data, style.css | projects.html with Tufte-style project map | None |
| **A2: Taxonomist** | Add genre sub-categories to ideas (platformer, autobattler, board_game, roguelike, etc.) | ideas table, conversation content | New `ideas.genre` column or tag-based genre filtering | None |
| **A3: Historian-Builder** | Create historian showcase pages | Historian research results | New SHOWCASES entries + route for /scholars | Workstream C research |
| **A4: Context-Regenerator** | Update concat_context.py FILE_ORDER, regenerate full context | All new files | Updated DREAMBASE_FULL_CONTEXT.md | After all code changes |

### Workstream B: "The Writer" (Content Agents)

Things that produce .md files, essays, and improved copy.

| Agent | Task | Inputs | Outputs | Dependencies |
|-------|------|--------|---------|--------------|
| **B1: RAW-Essayist** | Write RAW/Freemasonry/CS/Golden Dawn essay | Project data, alchemy conversations | RAW_FREEMASONRY_CS.md | None (IN PROGRESS) |
| **B2: Curator-Reviewer** | Improve 124 featured conversation summaries | improvements/featured_summaries.md | Reviewed + applied summaries in DB | Ted reviews proposals |
| **B3: Copy-Reviewer** | Improve collection descriptions + showcase hooks | improvements/copy_improvements.md | Updated app.py COLLECTIONS/SHOWCASES | Ted reviews proposals |
| **B4: Batch-Exporter** | Generate 110 ChatGPT batch files for remaining summaries | megabase.db | chunks/summaries/batch_*.md | After Janitor + Messenger (DONE) |

### Workstream C: "The Miner" (Research Agents)

Things that dig through data to find patterns.

| Agent | Task | Inputs | Outputs | Dependencies |
|-------|------|--------|---------|--------------|
| **C1: Historian-Miner** | Find all historian/scholar conversations + page counts | megabase.db | Structured report of scholars by engagement | None (IN PROGRESS) |
| **C2: Genre-Miner** | Classify game ideas by genre from conversation content | ideas table + first messages | Genre tags per idea | None |
| **C3: Project-Linker** | Match Dev/ project folders to megabase conversations | Dev scan + conversation titles | Project-to-conversation mapping | None |

---

## COMMUNICATION FLOW

```
WORKSTREAM C (Research)              WORKSTREAM B (Writing)
┌─────────────────────┐              ┌─────────────────────┐
│ C1: Historian-Miner  │──────────►  │ B1: RAW Essay        │
│ C2: Genre-Miner      │──┐          │ B2: Curator Review    │
│ C3: Project-Linker   │──┤          │ B3: Copy Review       │
└─────────────────────┘  │          │ B4: Batch Export      │
                         │          └─────────────────────┘
                         │                    │
                         ▼                    ▼
              WORKSTREAM A (Build)      TED (Human Gate)
              ┌─────────────────────┐   ┌─────────────────┐
              │ A1: Cartographer     │   │ Reviews proposals │
              │ A2: Taxonomist       │   │ Pastes batches    │
              │ A3: Historian-Builder│◄──│ Approves copy     │
              │ A4: Context-Regen    │   └─────────────────┘
              └─────────────────────┘
```

### Orchestration: Three-phase parallel with human gates

**Phase 1 — Research + Independent Writing (parallel, no human needed)**
- C1 mines historians (IN PROGRESS)
- C2 classifies game genres
- C3 links projects to conversations
- B1 writes RAW essay (IN PROGRESS)
- A1 builds /projects page
- A2 adds genre filtering to ideas

**Phase 2 — Human Review Gate**
- Ted reviews improvements/featured_summaries.md (B2)
- Ted reviews improvements/copy_improvements.md (B3)
- Ted approves historian showcase selections (from C1)

**Phase 3 — Build from reviewed inputs (parallel)**
- A3 builds historian showcases (after Ted approves C1 selections)
- B4 exports remaining batch files (after Phase 1 Janitor/Messenger done ✓)
- A4 regenerates full context (after all code changes)

**Phase 4 — Manual Batch Grind (Ted + ChatGPT, multi-day)**
- Ted pastes 110 batch files into ChatGPT
- Runs `improve_summaries.py batch-import` on each response

---

## AGENT SPECIFICATIONS

### A1: Cartographer (Project Visualization Page)

**Route:** `/projects`
**Template:** `projects.html`
**Data source:** Hardcoded project catalog (from Dev scan) in app.py

**Visualization design (Tufte-inspired):**
- **Timeline strip:** Projects arranged by last-modified date, width proportional to file count
- **Cluster grouping:** Color-coded by domain (games, scholarship, business, mobile, tools)
- **Size encoding:** Box area = source file count
- **Git indicator:** Filled vs outline = has git history vs no git
- **Linked conversations:** Count of megabase conversations connected to each project
- **Click to drill:** Each project links to its matching collection or filtered conversation view

**Project data structure:**
```python
PROJECTS = [
    {"name": "MarxistTradition", "domain": "scholarship", "framework": "Node.js",
     "files": 621, "commits": 33, "last_modified": "2026-03-13",
     "description": "Marxist intellectual tradition with multi-tendency perspectives",
     "conversation_ids": [702, 157, 2646, 809]},
    # ... 32 more
]
```

### A2: Taxonomist (Genre Classification)

**Approach:** Deterministic keyword matching on idea names and linked conversation titles.

**Genre tags for games:**
- `platformer` — bubble, jump, side-scroll, movement
- `autobattler` — auto, draft, army, battle, watch
- `board_game` — board, card, tabletop, transmutation chain
- `roguelike` — procedural, dungeon, permadeath, run
- `puzzle` — puzzle, match, minesweeper, maze
- `rpg` — quest, character, level, stats, skill tree
- `simulation` — sim, tycoon, management, ecosystem
- `educational` — learn, teach, tutorial, curriculum
- `card_game` — deck, draw, hand, mtg, tarot
- `adventure` — story, narrative, explore, text

**Implementation:** Add genre pills to ideas page, new filter option.

### A3: Historian-Builder (Showcase Pages for Scholars)

**Depends on:** C1 (Historian-Miner) results

**For each scholar with 3+ conversations:**
1. Create a collection entry in COLLECTIONS dict
2. If the scholar has 5+ conversations and 200+ total pages, consider a full SHOWCASE entry

**Anticipated scholars (from database patterns):**
- Lawrence Principe (alchemy/chemistry historian)
- Frances Yates (Renaissance magic/memory)
- Wouter Hanegraaff (Western esotericism)
- Antoine Faivre (esotericism methodology)
- Giordano Bruno (Renaissance philosopher)
- Pico della Mirandola (Renaissance syncretist)
- Paracelsus (physician-alchemist)
- Philip K. Dick (already has collection)
- Fredric Jameson (Marxist literary theory)

**Output:** Updated SHOWCASES/COLLECTIONS dicts + any new templates needed.

### C2: Genre-Miner (Game Idea Classification)

**Logic:**
```python
GENRE_KEYWORDS = {
    "platformer": ["platform", "jump", "bubble", "bog witch", "movement", "side-scroll"],
    "autobattler": ["autobattl", "auto battl", "draft army", "watch chaos"],
    "board_game": ["board game", "transmut", "card game", "tabletop"],
    "roguelike": ["procedural", "dungeon", "permadeath", "roguelike", "run-based"],
    "puzzle": ["puzzle", "minesweeper", "maze", "match"],
    "card_game": ["deck", "mtg", "tarot", "commander", "scryfall"],
    "adventure": ["text adventure", "narrative", "story", "tree of life"],
    "educational": ["learn", "teach", "curriculum", "pedagogy"],
}
# Match against idea.name + idea.description + conversation.title
```

### C3: Project-Linker

**Logic:** Match Dev/ folder names to conversation titles using fuzzy string matching.

**Known mappings (from scan):**
| Project | Likely Conversations |
|---------|---------------------|
| MarxistPortal / MarxistTradition | 702, 157, 2646, 809, 814 |
| capital_interpreter | 702, 476, 283 |
| MTGDraftOverlay / Overlay | 382, 2947, 2693, 570 |
| TreeTapper | 843, 778, 2652 |
| AlchemyDB | 712, 670, 726, 673 |
| alchemy_scryfall | 9, 5 |
| VoxFugiens / voicenotes | coding-tagged |
| draft-academy | educational-tagged |
| esoteric-beat-site | esoteric-tagged |
| megabase | meta — the project IS the database |

---

## FLAGGED ISSUES

| Issue | Severity | Resolution |
|-------|----------|------------|
| A3 depends on C1 which is still running | LOW | A3 waits for C1; other agents run in parallel |
| Genre classification is heuristic | LOW | Acceptable for v1 — can refine with ChatGPT batch later |
| 33 projects is a lot for one visualization | MEDIUM | Cluster by domain, use small multiples, allow filter |
| Historian showcases may overlap with existing collections (PKD, alchemy-scholarship) | MEDIUM | Historians get their own scholar-focused pages; existing collections keep thematic focus |
| RAW essay is creative writing, hard to validate | LOW | It's for Ted's enjoyment, not production code |
| 110 batch files = multi-day manual effort | MEDIUM | Acceptable per constraints. Ted can do 10-20 per day. |

---

## EXECUTION TIMELINE

### This Session (now)
- [x] A1: Cartographer — build /projects route + visualization
- [x] C2: Genre-Miner — classify game ideas by genre
- [ ] Wait for background agents (B1: RAW essay, C1: Historian mining)
- [x] B4: Batch export (run improve_summaries.py batch-export)
- [x] A4: Regenerate DREAMBASE_FULL_CONTEXT.md

### Next Session (Ted reviews)
- [ ] B2: Ted reviews improvements/featured_summaries.md
- [ ] B3: Ted reviews improvements/copy_improvements.md
- [ ] A3: Build historian showcases from C1 results

### Ongoing (multi-day)
- [ ] Ted pastes batch files into ChatGPT (Phase 4)
- [ ] Imports responses with batch-import

---

## WHAT "DONE" LOOKS LIKE

When all agents complete:

- **9 collections** in the Collections tab (alchemy-scholarship, philosophy, PKD, marxism, music-engineering, dark-horses, scholarly-deep-reads, scholarly-to-games, building-dreams) + historian collections from C1
- **3 showcase dream pages** for games (bubble-bog-witch, dungeon-autobattler, alchemy-board-game)
- **Scholar showcase pages** for Ted's favorite historians
- **Ideas page** with grid/list views, category + maturity + genre filters
- **Projects page** with Tufte visualization of 33 built projects linked to conversations
- **Values page** with evidence-based scholarly values
- **~3,600 improved summaries** (400 janitor + 1,592 messenger + ~110x20 batch)
- **SUMMARYTEMPLATE.md** for ongoing quality control
- **RAW_FREEMASONRY_CS.md** essay (~20 pages)
- **INGESTION_GUIDE_RPG.md** for onboarding
- **DREAMBASE_FULL_CONTEXT.md** regenerated with all new files
- **improvements/** folder with curator + copywriter proposals for review
