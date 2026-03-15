# Eldritch Swarm V3: The Showcase Renaissance

**Palmer Eldritch orchestrates the upgrade of every showcase page to Wonderland-tier quality.**

---

## SITUATION: What's Changed Since V2

The Algorithms in Wonderland flagship page raised the bar. It has:
- 1200+ word illustrated essay with inline Tenniel images
- 7 tabs (not 5) including Texts & Allusions and Concept Map
- Split-panel "allusion cards" mapping literary scenes to CS concepts
- Cross-reference matrix linking topics to related Dreambase pages
- Dedicated rabbit hole cards pointing to scholars, collections, showcases

Now every showcase and scholar page should aspire to this level. Not identical — each page has its own genre — but with the same density of thought, interconnection, and delight.

---

## THE REQUEST QUEUE (V3 additions in bold)

| # | Request | Status |
|---|---------|--------|
| 1-3 | Scholar pages, projects, card fixes | DONE |
| 4 | AlchemyDB integration | PLANNED (V2) |
| 5 | Reader pane | PLANNED (V2) |
| 6 | Short prompts + action map | PLANNED (V2) |
| 7 | Content creation showcase | PLANNED (V2) |
| 8 | CS rabbit holes showcase | PLANNED (V2) |
| 9 | Algorithms in Wonderland | DONE |
| 10 | Consistent card style | PLANNED (V2) |
| **11** | **"Injecting Custom Logic" showcase** | **NEW** |
| **12** | **"50 Takeaways from LLM Work" showcase with rabbit holes** | **NEW** |
| **13** | **Cross-pollination audit (Pris Pedagogy): each page learns from others** | **NEW** |
| **14** | **Showcase quality upgrade swarm: bring all pages to Wonderland standard** | **NEW** |
| **15** | **Tech stack + academic/authorial/gaming .md output** | **NEW** |
| **16** | **Reader pane design essay (10 paragraphs)** | **NEW** |
| **17** | **50 takeaways from showcase page study + genre templates** | **NEW** |

---

## SWARM ARCHITECTURE: THE SHOWCASE RENAISSANCE

### Workstream F: "The Pedagogue" (Cross-Pollination Engine)

**Goal:** Each showcase page reads the others for design cues, borrows what works, and evolves a shared vocabulary of components.

| Agent | Task | Inputs | Outputs |
|-------|------|--------|---------|
| **F1: Component Inventory** | Catalog every reusable component across all templates: tabs, cards, stat bars, pedagogy boxes, allusion panels, matrices, rabbit holes, timelines, quote blocks, illustration layouts | All 13 templates | Component registry with source template, CSS, and use count |
| **F2: Gap Analysis** | For each showcase/scholar page, list which Wonderland-level components are missing. E.g., "Pico's page has no concept matrix. Bruno's page has no allusion cards." | Component registry + all page types | Per-page gap report |
| **F3: Template Library** | Extract the best version of each component into reusable Jinja2 macros: `{% macro allusion_card(literary, technical, connector) %}`, `{% macro concept_matrix(rows) %}`, etc. | Best-of-breed components | `templates/macros/components.html` |
| **F4: Page Upgrader** | Apply missing components to each page using the macro library + sidecar JSON for content | Gap report + macros | Upgraded templates |

**Cross-pollination matrix — what each page type can learn from the others:**

| Source Page | Learnable Component | Target Pages |
|-------------|-------------------|--------------|
| Wonderland | Allusion cards (split-panel literary↔technical) | Scholar pages (e.g., Pico's 900 Theses ↔ database normalization) |
| Wonderland | Concept matrix with rabbit hole links | All showcase + scholar pages |
| Wonderland | Inline illustrated essay | Alchemy Board Game (alchemical emblem illustrations) |
| Scholar pages | Depth tiers (introductory/intermediate/advanced) | Game showcases (replace easy/med/hard) |
| Scholar pages | Related scholars + related collections | Showcases (add "related showcases") |
| Collection pages | Adjacent collections (set overlap) | Scholars (already done), Showcases (not done) |
| Values page | Evidence-backed claims with data links | Scholar pedagogy boxes |
| Viz page | Sparkline trends | Scholar pages (engagement over time mini-chart) |

---

### Workstream G: "The Custom Logic Artisan"

**New showcase page: "Injecting Custom Logic"**

**Concept:** A showcase exploring every pattern in Ted's projects where custom logic needs to be injected — hooks, middleware, plugin architectures, parsers, pipeline steps, event systems, strategy patterns, configuration overrides.

**Conversation IDs (from mining):**
- Coding tag top: 570, 636, 631, 270, 500, 703, 710, 32, 711, 578, 679, 75, 14
- Parser/pipeline specific: 28, 1858, 3014
- Direct hits: 2562, 2521, 252

**Tab structure (6 tabs):**
1. **Overview** — essay: "Every non-trivial system has a seam where users need to inject their own logic. This showcase maps every pattern Ted used."
2. **Pattern Catalog** — matrix of injection patterns: Hooks, Middleware, Plugins, Callbacks, Parsers, Pipelines, Strategy, Decorator, Event Bus — with project examples for each
3. **Project Examples** — linked conversations grouped by which injection pattern they use
4. **Design Evolution** — timeline of how Ted's approach to extensibility evolved
5. **Source Conversations** — ranked by pages
6. **Rabbit Holes** — links to related scholars (Agrippa's classification system as "extensibility"), projects, collections

---

### Workstream H: "The Metacognitive Cartographer"

**New showcase page: "50 Takeaways from Working with LLMs"**

**Concept:** A lavish showcase that presents 50 hard-won lessons from 2 years and 4,308 conversations of LLM work. Each takeaway is a card with: the lesson, the evidence (linked conversation), and a rabbit hole.

**Conversation IDs (from mining):**
- Meta-learning: 570, 559, 636, 632, 571, 565, 3268, 339, 523
- Workflow: 3259, 3268, 571, 523
- Prompt engineering: 559, 636, 653, 565

**Tab structure (7 tabs — Wonderland-tier):**
1. **Overview** — illustrated essay: "What 4,308 conversations taught me about thinking with machines"
2. **The 50 Takeaways** — scrollable card grid, each takeaway numbered, categorized (Prompting, Workflow, Architecture, Mindset, Failure Modes), and linked to evidence conversations
3. **By Category** — grouped view: Prompting (15), Workflow (10), Architecture (10), Mindset (10), Failure Modes (5)
4. **Key Quotes** — most striking quotes from conversations where insights crystallized
5. **Design Evolution** — timeline of how Ted's LLM usage evolved (early: simple Q&A → middle: chain-of-thought → late: agentic swarms)
6. **Source Conversations** — ranked by pages
7. **Rabbit Holes** — links to related: Action Map page, Projects page, scholars who influenced the approach

---

### Workstream I: "The Quality Enforcer"

**Goal:** Upgrade existing showcase pages (3 game showcases, 9 collections) to the new standard.

| Page Type | Current State | Upgrade Needed |
|-----------|--------------|----------------|
| Game Showcases (3) | 5 tabs, pedagogy boxes, difficulty tiers | Add: concept matrix, allusion cards where relevant, rabbit holes tab, related showcases |
| Collections (9) | Basic: description, conversation list, adjacent collections, sentiment | Add: narrative essay, key quotes, rabbit holes, related scholars |
| Scholar pages (30) | 5 tabs with depth tiers, related scholars/collections | Add: concept matrix, engagement sparklines, deeper pedagogy boxes |

**Phase plan:**
1. Build the component macro library (F3)
2. Create sidecar JSON files with enriched content for each page
3. Update templates to use macros
4. Verify each page renders correctly

---

## COMMUNICATION FLOW (V3)

```
WORKSTREAM F (Cross-Pollination)
+---------------------------+
| F1: Component Inventory   |
| F2: Gap Analysis          |
| F3: Template Library      |---→ SHARED MACROS
| F4: Page Upgrader         |
+---------------------------+
        |
        +---→ feeds into ALL other workstreams
        |
WORKSTREAM G (Custom Logic)     WORKSTREAM H (50 Takeaways)
+---------------------------+   +---------------------------+
| New showcase page         |   | New showcase page         |
| 6 tabs, pattern catalog   |   | 7 tabs, 50 lesson cards   |
+---------------------------+   +---------------------------+

WORKSTREAM I (Quality Upgrade)
+---------------------------+
| Upgrade 3 game showcases  |
| Upgrade 9 collections     |
| Upgrade 30 scholar pages  |
+---------------------------+

        PLUS V2 WORKSTREAMS STILL PENDING:
        A: AlchemyDB Integration
        B: Reader Pane
        C: New Showcases (content creation, CS rabbit holes)
        D: Short Prompts + Action Map
        E: Card Consistency
```

---

## ORCHESTRATION

### Phase 1 — Foundation (parallel, no dependencies)
- **F1:** Inventory all components across templates
- **G data:** Mine conversations for custom logic patterns
- **H data:** Mine conversations for LLM meta-learning
- **A1:** Ingest AlchemyDB lexicon (from V2)
- **D1:** Extract short prompts (from V2)
- **E1:** Audit card styles (from V2)

### Phase 2 — Build (parallel where possible)
- **F2+F3:** Gap analysis → macro library (needs F1)
- **G page:** Build "Injecting Custom Logic" showcase (needs G data)
- **H page:** Build "50 Takeaways" showcase (needs H data)
- **B1+B2:** Reader pane route + UI (from V2)
- **A2+A3:** AlchemyDB linking + browse routes (from V2)
- **D2:** Classify short prompts (from V2)

### Phase 3 — Upgrade (needs Phase 2 macros)
- **F4+I:** Upgrade all existing pages using macro library
- **A4:** Auto-hyperlink alchemy terms (from V2)
- **D3:** Action visualization page (from V2)
- **B3:** Reader keyboard nav (from V2)
- **E2:** Unify card styles (from V2)

---

## THE 50 TAKEAWAYS (Draft)

### Prompting (1-15)
1. **Start with structure, not content.** Give the LLM a format before you give it a task.
2. **The first response is a draft, not an answer.** Always iterate.
3. **Chain of thought works because it forces sequencing.** The model thinks better when you make it show its work.
4. **Personas are cognitive primes, not roleplay.** "You are a senior engineer" changes reasoning quality.
5. **Short prompts get short answers.** Length of input correlates with depth of output.
6. **"Give me 20 ideas" beats "give me an idea" 20 times.** Batch requests produce more varied output.
7. **Constraints produce creativity.** "Write a poem in exactly 14 lines" gets better results than "write a poem."
8. **The prompt is a UI.** Treat it like interface design: what does the model need to see, in what order?
9. **Examples are worth a thousand words of instruction.** One good example beats three paragraphs of description.
10. **Temperature is a collaboration dial.** Low for precision, high for exploration, medium for drafting.
11. **System prompts are persistent context.** Use them for persona + constraints, not instructions.
12. **The model can't see what you didn't paste.** If it's not in the context, it doesn't exist.
13. **Negations confuse.** "Don't use jargon" works worse than "Use plain language."
14. **Markdown structure improves reasoning.** Headers and lists in prompts produce structured output.
15. **The best prompt is often a conversation.** Multi-turn refinement beats a single perfect prompt.

### Workflow (16-25)
16. **Use the LLM for the 80%, then do the 20% yourself.** The last mile of quality is human.
17. **Batch similar tasks.** Don't prompt one conversation at a time — export 20 and process them together.
18. **Version your prompts like code.** Keep the working version, archive the old ones.
19. **LLMs are force multipliers, not replacements.** They amplify expertise; they don't substitute for it.
20. **Context switching kills LLM productivity too.** Keep focused sessions on one topic.
21. **Export early, export often.** Don't let good output live only in chat history.
22. **The subscription is the budget.** Design workflows that use existing subscriptions, not per-token API.
23. **Build tools to talk to the LLM, not tools that ARE the LLM.** The interface layer matters.
24. **Read the output critically.** Fluent text ≠ correct text. LLMs are confident about everything.
25. **Keep a research journal.** Your conversations are data about your own thinking.

### Architecture (26-35)
26. **Chunking is the fundamental operation.** If you can chunk it, you can process it.
27. **SQLite is the universal interchange format.** Put everything in a database first, ask questions later.
28. **Deterministic first, probabilistic second.** Keyword matching before LLM classification.
29. **The sidecar pattern works.** Keep LLM-generated content in separate files from code.
30. **Curated IDs are the simplest recommendation engine.** A human-curated list of 20 IDs beats a vector similarity search.
31. **FTS5 is a superpower.** Full-text search on 4M messages in milliseconds, no external service needed.
32. **Flask + SQLite + Jinja2 is a complete stack.** You don't need React for a personal knowledge tool.
33. **Hardcoded data is fine for small scale.** 30 scholars in a Python dict is simpler than a CMS.
34. **The rabbit hole is the UI pattern.** Every page should link to related pages. That's the whole UX.
35. **Build the database before the interface.** Prove the data works in SQL before touching HTML.

### Mindset (36-45)
36. **You are the curator, the model is the librarian.** You decide what matters; it finds and organizes.
37. **Intellectual archaeology is a real discipline.** Your old conversations are primary sources.
38. **Cross-domain connections are the highest-value output.** Alchemy → game design is more interesting than either alone.
39. **The process IS the product.** Building Dreambase taught more than reading any book about knowledge management.
40. **Obsessive documentation pays compound interest.** Today's notes are tomorrow's database entries.
41. **Personal tools don't need to be products.** Build for yourself first. Generalize only if needed.
42. **The conversation is the unit of thought.** Not the message, not the session — the full conversation arc.
43. **Sentiment analysis reveals what you can't self-report.** Your excitement about alchemy is measurable.
44. **Tags are a lossy compression of meaning.** But they're the best compression we have.
45. **Two years of LLM conversations is a portrait.** The database is autobiographical.

### Failure Modes (46-50)
46. **Scope creep is the default.** You will always want one more feature. Use a parking lot.
47. **Premature abstraction wastes time.** Build three concrete things before abstracting.
48. **Re-ingestion destroys IDs.** If you rebuild the database, every hardcoded link breaks.
49. **LLMs hallucinate confidence.** The more certain the output sounds, the more you should verify.
50. **The rabbit hole has no bottom.** Set a timer. Ship something. Come back tomorrow.

---

## PRIS PEDAGOGY: CROSS-POLLINATION MAP

Each page type has something to teach and something to learn:

| Page Type | Teaches | Learns From |
|-----------|---------|-------------|
| **Wonderland** | Illustrated essay, allusion cards, concept matrix, 7-tab structure | Scholar depth tiers (could add difficulty ratings to CS concepts) |
| **Game Showcases** | Pedagogy boxes, difficulty tiers, game-design-as-teaching framing | Wonderland's illustrated essay (games deserve illustrated design docs) |
| **Scholar Pages** | Depth tiers, cross-scholar relationships, adapted pedagogy | Wonderland's concept matrix (scholars need cross-reference tables) |
| **Collections** | Adjacent collections discovery, sentiment overlays | Scholar pages' related-entity section, Wonderland's rabbit holes tab |
| **Values Page** | Evidence-backed claims, data-as-argument | Scholar pedagogy format (values could have "depth tiers" of engagement) |
| **Viz Page** | Data density, Tufte aesthetics, sparklines | Collections' narrative framing (viz needs contextual text, not just charts) |
| **Projects Page** | Domain clustering, build-status metadata | Collections' conversation links (projects should link to their source conversations) |
| **50 Takeaways** | Meta-cognitive framing, lesson-as-card format | Values page's evidence linking (each takeaway should link to proof) |
| **Custom Logic** | Pattern catalog as knowledge format | Game showcases' difficulty tiers (injection patterns have complexity tiers) |

---

*Palmer Eldritch sees every page simultaneously. The Showcase Renaissance begins.*
