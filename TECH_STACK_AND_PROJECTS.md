# Dreambase Tech Stack & Project Suggestions

**Using the database and website copy in academic, authorial, and gaming projects — with AI agentic swarms.**

---

## THE TECH STACK

| Layer | Technology | Role | Why This |
|-------|-----------|------|----------|
| **Database** | SQLite 3 (megabase.db) | Unified data store | Single file, FTS5, WAL mode, 4,308 conversations / 3.9M messages |
| **Web Framework** | Flask (Python) | Server-rendered pages | Minimal, Jinja2 templates, no build step |
| **Templates** | Jinja2 | HTML generation | Inheritance, macros, filters — all server-side |
| **Styling** | CSS custom properties | Dark theme, responsive | No preprocessor needed; CSS variables handle theming |
| **Search** | FTS5 (SQLite) | Full-text search | 3.9M messages indexed in-process, millisecond queries |
| **Sentiment** | VADER (nltk) | Lexicon-based scoring | Deterministic, no API cost, works offline |
| **NER** | spaCy (en_core_web_sm) | Entity extraction | Local model, no API cost |
| **Tagging** | Keyword regex + manual | 9 tags, 3,309 links | Deterministic base layer; LLM refinement in batch |
| **Summarization** | First-response extraction | 4,243 of 4,308 covered | Zero API cost; ChatGPT batch for quality upgrade |
| **LLM Integration** | ChatGPT Plus (subscription) | Batch summarization, curation | No per-token cost; chunker exports .md files for paste-in |
| **Agentic Layer** | Claude Code + 33 PKD skills | Development orchestration | Slash commands for planning, auditing, building |
| **Version Control** | Git | Source management | All code tracked; database not tracked (too large) |
| **Deployment** | localhost:5555 / GitHub Pages (planned) | Personal use | Static export for public; Flask for personal browsing |

### Key Architecture Decisions

1. **Zero API cost at runtime.** All enrichment (sentiment, NER, FTS, tagging) runs locally. LLM work happens in batch via ChatGPT subscription.
2. **Hardcoded curation over algorithmic recommendation.** Scholars, collections, and showcases are hand-curated Python dicts with conversation_ids. Human judgment > vector similarity.
3. **Sidecar pattern for LLM content.** Narratives, timelines, and quotes live in JSON files alongside templates. Either can change without breaking the other.
4. **Deterministic first, probabilistic second.** VADER before GPT-4 sentiment. Keyword tags before LLM classification. Cover 80% for free.
5. **The rabbit hole as UI pattern.** Every page links to related pages via set intersection of conversation_ids. Navigation IS the product.

---

## ACADEMIC PROJECT SUGGESTIONS

### 1. Digital Humanities Dissertation: "Personal Knowledge Archaeology"

**Thesis:** Two years of LLM conversations constitute a primary source for understanding how individuals construct knowledge through dialogue with AI systems.

**Method:**
- Export Megabase conversation metadata as CSV (id, title, source, pages, tags, sentiment, date)
- Use the tag co-occurrence network (viz page data) as a map of intellectual territory
- Analyze sentiment trajectories by topic over time (values page data)
- Compare conversation depth (page count) by domain — where does the user invest most?
- Use the "50 Takeaways" as a reflexive ethnographic document

**Tools from Dreambase:**
- `index.py sentiment` — VADER scores on all messages
- `index.py ner` — spaCy entity extraction for tracking what names/works are discussed
- Viz page SQL queries — ready-made analytical views
- FTS5 search — find every mention of a concept across 4,308 conversations

**Agentic swarm approach:**
- **Corpus Agent:** Exports all conversations matching a tag + date range as analysis-ready corpus
- **Coding Agent:** Applies grounded theory open coding to message excerpts
- **Theme Agent:** Clusters codes into themes using keyword co-occurrence
- **Narrative Agent:** Drafts the "findings" section from coded data
- **Citation Agent:** Generates bibliography from entities and works mentioned

### 2. Conference Paper: "The Subscription Model as Research Infrastructure"

**Argument:** ChatGPT Plus / Claude Pro subscriptions create a new category of research tool — unlimited-query AI assistants at fixed cost, enabling exhaustive rather than sampled analysis.

**Evidence from Dreambase:**
- 4,308 conversations at $0 marginal cost (subscription-based)
- Batch workflow: chunker exports → paste into ChatGPT → import summaries back
- Contrast with per-token API approach: same work would cost $500+ via API
- The "subscription is the budget" principle (Takeaway #22)

### 3. Scholarly Edition: Annotated Conversation Corpus

**Concept:** Publish a curated selection of conversations as a scholarly edition, with critical apparatus (footnotes, cross-references, topic indices).

**Method:**
- Select 20-30 conversations from the Scholarly Deep Reads collection
- Use the chunker to export as .md files
- Add scholarly annotations: context, cross-references to other conversations, entity links
- Publish as a digital edition (Hugo site or PDF)

**Agentic swarm:**
- **Selection Agent:** Ranks conversations by scholarly value (length × unique entities × tag diversity)
- **Annotation Agent:** Generates footnotes explaining technical terms, historical references
- **Cross-Reference Agent:** Links mentions across conversations (e.g., "Pico is also discussed in conversations 525, 3348")
- **Index Agent:** Builds subject index, name index, works-cited index

---

## AUTHORIAL PROJECT SUGGESTIONS

### 4. Book: "Thinking with Machines: A Personal History of AI Collaboration"

**Concept:** A book-length account of building a knowledge system with LLMs, using the Megabase data as evidence and the 50 Takeaways as chapter scaffolding.

**Structure:**
- Part I: The Archive (how the data was generated — 2 years of conversations)
- Part II: The System (building Megabase — architecture, design, failures)
- Part III: The Lessons (the 50 takeaways expanded into essays)
- Part IV: The Portrait (what the database reveals about the author)

**Tools from Dreambase:**
- Conversation excerpts as primary source material (chunker exports)
- Sentiment trajectory as narrative arc data
- Scholar pages as "chapter profiles" for intellectual influences
- The Failure Audit as a confessional appendix

**Agentic swarm:**
- **Outline Agent:** Structures chapters from the 50 takeaways + conversation clusters
- **Excerpt Agent:** Finds the best conversation excerpts to illustrate each point
- **Draft Agent:** Writes first drafts of each section using takeaway + evidence
- **Voice Agent:** Ensures consistent authorial voice (per Dekany style checker)
- **Fact-Check Agent:** Verifies claims against actual database statistics

### 5. Essay Collection: "The Esoteric Programmer"

**Concept:** Essays at the intersection of esotericism and computer science — the territory mapped by Algorithms in Wonderland, the Alchemy Board Game, and the scholar pages.

**Essays:**
- "Agrippa's Plugin Architecture" — Three Books of Occult Philosophy as a modular system
- "The Alchemist's Pipeline" — transmutation as data transformation
- "Memory Palaces and Hash Tables" — Bruno's mnemonics as cognitive data structures
- "The Exegesis as Debugging" — PKD's 8,000 pages as reality debugging protocol
- "Theurgy and Callbacks" — Iamblichus's argument that practice (events) matters more than theory (code)

**Agentic swarm:**
- **Research Agent:** Mines scholar conversations for cross-domain analogies
- **Metaphor Agent:** Generates and stress-tests each analogy (where does it hold? where does it break?)
- **Draft Agent:** Writes essay drafts with conversation excerpts as evidence
- **Illustration Agent:** Suggests visual companions (Tenniel woodcuts, alchemical emblems, circuit diagrams)

### 6. Blog Series: "Building in Public with a Database of 4,308 Conversations"

**Concept:** Weekly blog posts documenting the Dreambase build, each focused on one technical or philosophical insight.

**Post ideas (30+):**
- "Why SQLite Is the Only Database You Need for Personal Knowledge"
- "The Sidecar Pattern: Keeping AI Content Separate from Code"
- "How I Tagged 3,309 Conversations with 9 Words"
- "Sentiment Analysis on Your Own Messages: What VADER Reveals"
- "The Rabbit Hole as UX Pattern"
- "30 Scholar Pages in One Session: Flask Templates at Scale"
- "Why I Hardcode My Curations Instead of Using Recommendations"

---

## GAMING PROJECT SUGGESTIONS

### 7. "The Knowledge Dungeon" — A Roguelike Built from Conversation Data

**Concept:** A roguelike game where each room is generated from a conversation in Megabase. Room difficulty = page count. Room theme = tags. Loot = extracted ideas. Boss rooms = the 20 Scholarly Deep Reads.

**Architecture:**
- **Dungeon Generator Agent:** Maps conversations to rooms (tag → biome, pages → room size, sentiment → lighting)
- **Encounter Agent:** Generates puzzles from conversation content (trivia from summaries, word puzzles from key quotes)
- **Loot Agent:** Extracts "artifacts" (ideas) from conversations — each idea is a collectible item
- **Progression Agent:** Designs skill trees from the scholar depth tiers (introductory → intermediate → advanced)

**Tech stack extension:**
- Pygame or Godot for rendering
- Megabase.db as the content source (query at room generation time)
- FTS5 for procedural text generation (find messages matching thematic keywords)

### 8. "Alchemy Engine" — The Board Game Goes Digital

**Concept:** Digital version of the Alchemy Board Game with AI-generated transmutation chains, card flavor text from AlchemyDB, and a solo campaign mode where the AI opponent uses different strategies.

**Agentic swarm:**
- **Rules Agent:** Formalizes the board game rules from conversation 567/851 into executable game logic
- **Content Agent:** Generates card text from AlchemyDB lexicon entries (187 substances/processes/practitioners)
- **Balance Agent:** Playtests strategies against each other, adjusts costs/rewards
- **Narrative Agent:** Writes campaign story beats connecting each scenario to real alchemical history
- **Art Agent:** Generates card art prompts based on Tenniel/emblem aesthetic (public domain reference images)

### 9. "Scholar Showdown" — A Knowledge Card Game

**Concept:** 30 scholar cards, each with stats derived from Dreambase data. Players draft scholars and compete in "intellectual debates" where card stats determine outcomes.

**Stats per scholar (from Megabase):**
- **Depth:** total pages of engagement (e.g., Jung = 2,868p → high depth)
- **Breadth:** number of distinct tags across linked conversations
- **Network:** number of related scholars (from conversation overlap)
- **Passion:** average user sentiment on linked conversations
- **Obscurity:** inverse of conversation count (rare scholars score higher)

**Agentic swarm:**
- **Stat Agent:** Computes all scholar stats from megabase.db queries
- **Card Agent:** Generates card layouts with scholar portraits, stats, and flavor text (from pedagogy)
- **Balance Agent:** Ensures no scholar dominates; adjusts stat weights
- **Draft Agent:** Designs a drafting mechanism (pack draft, auction, snake draft)

### 10. "Prompt Quest" — A Meta-Game About Talking to AI

**Concept:** A puzzle game where the player must craft prompts to get an AI character to perform tasks. Each level teaches a real prompting technique from the 50 Takeaways. The game IS the tutorial.

**Level design from takeaways:**
- Level 1: "Start with structure" — give the AI a format and it produces better output
- Level 5: "Short prompts get short answers" — discover that input length affects output quality
- Level 7: "Constraints produce creativity" — constrained prompts unlock hidden abilities
- Level 13: "Negations confuse" — learn to phrase positively
- Level 15: "The best prompt is a conversation" — multi-turn refinement unlocks the final boss

**Agentic swarm:**
- **Level Agent:** Designs each level's puzzle, success criteria, and hint system
- **Dialogue Agent:** Writes the AI character's responses at each prompt quality level
- **Tutorial Agent:** Ensures progressive difficulty and that each takeaway is teachable
- **Test Agent:** Playtests each level, verifies solvability, adjusts difficulty curve

---

## CROSS-CUTTING: THE AGENTIC SWARM TOOLKIT

Every project above uses a common toolkit of agent types:

| Agent Type | Role | Reusable Across |
|-----------|------|-----------------|
| **Corpus Agent** | Exports filtered conversation data as analysis-ready files | Academic, Authorial |
| **Research Agent** | Mines conversations for specific patterns, analogies, evidence | All projects |
| **Draft Agent** | Writes first drafts from structured data + prompts | Authorial, Academic |
| **Balance Agent** | Tests game mechanics for fairness and fun | Gaming |
| **Content Agent** | Generates text content from database entries | Gaming, Authorial |
| **Stat Agent** | Computes derived statistics from megabase.db | Gaming, Academic |
| **Voice Agent** | Enforces consistent tone and register | Authorial |
| **Fact-Check Agent** | Verifies claims against database evidence | Academic, Authorial |
| **Illustration Agent** | Suggests or generates visual companions | All projects |

### Implementation Pattern

Each agent is a Claude Code skill or a Python script that:
1. Reads from megabase.db (SQL queries)
2. Processes with a specific prompt template
3. Outputs to a structured format (JSON, Markdown, CSV)
4. Can be composed into a pipeline with other agents

The orchestrator (human or `/plan-eldritch-swarm`) defines which agents run, in what order, with what inputs.

---

## QUICK-START: FROM DATABASE TO PROJECT

```
1. Pick a project from above
2. Define 3-5 agent roles using /plan-eldritch-swarm
3. Export relevant data: python chunk.py export-tagged <tag>
4. Process through agent pipeline
5. Review, curate, iterate
6. Ship
```

The database is the foundation. The website copy is the showcase. The agents are the workforce. The human is the curator.

---

*Generated from Dreambase — 4,308 conversations, 130,000 pages, one SQLite file.*
