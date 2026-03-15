# Dreambase Build: Prompting Methodology Evaluation

## Overview

Ted used a structured "PKD Planning Protocol" — a system of 33 named slash
commands organized by role (scope, slice, boundary, tokens, audit, etc.) — to
plan and build a personal knowledge archaeology system across 8+ sessions.
This is notably more methodical than typical conversational prompting.

**Overall assessment: 8.5/10** — The planning discipline prevented scope creep
and produced a working system with 15 scripts, 4,308 conversations ingested,
and 7 data visualizations. The main cost was token overhead from planning
prompts that sometimes overlapped or triggered unnecessary ceremony.

---

## Prompt-by-Prompt Narrative

### Prompt 1: "Find everything database on my computer"
**Score: 9/10**

The opening move was excellent — an open-ended exploration request that let
Claude discover the actual data landscape rather than Ted guessing what
existed. This produced the crucial inventory of 10+ data sources across
Desktop, Downloads, and Dev.

**What worked:** Gave Claude permission to search broadly. Didn't
pre-constrain the scope.
**Minor issue:** The phrase "everything database" was slightly ambiguous
(databases? or everything + data?), but context made it clear enough.

---

### Prompt 2: "I've also got pdf and html file collections..."
**Score: 8/10**

Good follow-up that expanded the discovery to non-database formats. This
surfaced the LLM logs HTML/PDF collection (1,703 files) that became a
major data source.

**What worked:** Explicitly named the formats Ted remembered.
**Could improve:** Could have said "check these specific directories" to
speed up the search.

---

### Prompt 3: `/plan-joe-chip-scope` — "how feasible is a megafile + idea catalog"
**Score: 9/10**

This was the key disciplined moment. Instead of saying "build it," Ted invoked
the scope-freeze skill FIRST. This forced explicit feasibility analysis and
prevented the classic "just start coding" trap.

**What worked:** The skill invocation made Claude produce a structured scope
document rather than diving into code. Established the 8-session plan, the
agent roles, and the unified schema before a single line was written.
**Result:** The plan survived nearly intact across all sessions.

---

### Prompt 4: `/plan-isidore-tokens` — "plan for doing this without running out of tokens"
**Score: 9/10**

Brilliant meta-prompt. Ted recognized that the project's biggest risk wasn't
technical — it was running out of context window. Isidore produced the
token budget analysis that shaped the entire build strategy: scripts write
to DB not stdout, errors go to log files, test with samples then bulk-run
in background.

**What worked:** Addressed the real constraint (context window, not
computation). Produced actionable rules that were followed throughout.
**Result:** The project completed without context exhaustion until the
very end (session 8+), which is remarkable for a project of this scope.

---

### Prompt 5: "the gmail data exists in some converted form"
**Score: 7/10**

A good intuition-based redirect that saved time — Ted suspected he'd already
processed Gmail elsewhere and flagged it. This prevented wasting a session
on 14GB mbox parsing that might have been redundant.

**Problem:** The memory was vague. "I might have used Antigravity" — this
turned out to be a false lead. The actual Gmail processing was `mbox_to_csv.py`
in Downloads. More precision would have helped: "search for any gmail or
mbox scripts I already wrote."

---

### Prompt 6: "card with the topic sketched in three sentences..."
**Score: 10/10**

The highest-scoring prompt. Ted articulated the EXACT user experience he
wanted: cards with 3-sentence summaries, click to expand, rabbit hole
navigation, distant reading for 1000-page conversations. This became the
north star for the entire Flask UI.

**What worked:** Specific enough to implement, abstract enough to leave
room for design. The "distant reading" framing showed Claude the
intellectual context. "Some conversations are a thousand pages" — this
single detail shaped the chunker's 60K-char design and the page-count
sorting.

---

### Prompt 7: `/plan-pris-pedagogy` — "what I want to learn from reviewing"
**Score: 7/10**

Invoked the pedagogy skill to reflect on learning goals. This was
intellectually valuable but didn't translate directly into code artifacts.
The sentiment analysis and personal message mining features came from this
prompt, but they would have emerged anyway from the scope document.

**Token cost concern:** This was the first prompt where skill ceremony
consumed context without proportional output. The pedagogy skill produced
a thoughtful analysis, but the actionable items (VADER sentiment,
emotional arc prompts) were already in the plan.

---

### Prompt 8: `/plan-deckard-boundary` — "deterministic and probabilistic hybrid"
**Score: 8/10**

Smart architectural prompt. Deckard's deterministic/probabilistic boundary
analysis produced the core design decision: keyword tagging + VADER + FTS5
first (free, instant), then targeted LLM for summaries/classification.
This directly shaped the token-budget tiers.

**What worked:** The "help me think about" framing was collaborative, not
prescriptive. Produced the tiered approach that let Ted control costs.
**Could improve:** Some overlap with Isidore's token analysis. Could have
been combined.

---

### Prompt 9: "8 sessions is not too much"
**Score: 8/10**

A simple but crucial approval prompt. Ted confirmed the scope was acceptable,
which locked in the session plan. Short, decisive, no wasted tokens.

---

### Prompt 10: `/plan-eldritch-swarm` — "break down into different roles"
**Score: 8/10**

The Eldritch Swarm skill produced the 6-agent architecture (Architect,
Ingestors, Indexer, Summarizer, Chunker, Browser) with a clear dependency
graph. This was genuinely useful — the parallel ingestor design and the
phase-gated pipeline came from this.

**What worked:** The agent decomposition prevented monolithic script design.
**Slight excess:** The swarm metaphor added flavor but the actual output was
a standard pipeline diagram. A simpler "break this into scripts" might have
produced the same architecture.

---

### Prompt 11: "I don't want to use the API I'm on the 100/mo plan"
**Score: 10/10**

A critical constraint injection at exactly the right time. This single
sentence rewrote the entire summarization strategy from "call Haiku API"
to "ChatGPT batch workflow." It also prevented any future API-cost
assumptions.

**What worked:** Short, clear, constraint-first. Didn't ask for permission
or hedge — just stated the boundary.

---

### Prompt 12: "125 paste-and-copy interactions is too much work"
**Score: 9/10**

Excellent pushback on a proposed workflow. Ted identified that the batch
summarization plan (125 ChatGPT paste sessions) was impractical and demanded
optimization. This led to bigger batches (50 per file instead of 20),
prioritized by tags, reducing the workload to ~24 focused sessions.

**What worked:** Quantified the complaint. "125 is too much" is more
actionable than "this seems like a lot of work."

---

### Prompt 13: "bigger batches, prioritized and I'll tell you what to have claude do"
**Score: 8/10**

Good follow-up that established the human-in-the-loop pattern: Ted decides
WHAT gets deep-read, Claude generates the batch files, Ted pastes into
ChatGPT. Clean division of labor.

---

### Prompt 14: "100 creative dreams as a website of cards..."
**Score: 7/10**

This was the first scope-expansion prompt. Ted described the dream catalog
website with theme buttons and rabbit holes. It was a great vision but
violated the Joe Chip scope freeze.

**Problem:** This should have triggered `/plan-abendsen-parking` (parking
lot) immediately, but Ted described it in enough detail that it became a
de facto commitment. The discipline would have been: state the vision in
one sentence, park it, continue building.

**What helped:** Ted self-corrected: "Let's be careful to plan before building."

---

### Prompt 15: `/plan-buckman-critic` — evaluate process for flaws
**Score: 8/10**

Good meta-reflection. Using the critic skill mid-build caught several
potential issues and validated the approach. This is the kind of
checkpoint prompt that most users skip.

---

### Prompt 16: `/failure-audit` — "concerned about stuff getting wiped"
**Score: 9/10**

This was triggered by a REAL incident — the PKD ingestor accidentally
deleted all 982 HTML conversations by importing from the wrong module.
Ted's response was exactly right: pause, audit for failure modes, tighten
before continuing.

**What worked:** Reacted to a concrete problem rather than abstract anxiety.
Led to the backup strategy (`cp megabase.db megabase_label.db`) and the
rule against importing ingest functions across scripts.
**Problem in the prompt:** "don't want to hear about wasted effort" was
slightly defensive. The wasted effort had already happened — what mattered
was preventing recurrence.

---

### Prompt 17: "hold off on gmail"
**Score: 8/10**

Correct prioritization call. Gmail was the biggest and riskiest ingestor
(14GB mbox), and Ted's instinct that he'd already processed it elsewhere
was partly right (the CSV existed). Deferring it saved a session.

---

### Prompt 18: "go"
**Score: 10/10**

The most efficient prompt in the entire project. One word. Meaning: "I've
reviewed everything, the plan is good, continue building." Maximum signal,
minimum tokens.

---

### Prompt 19: "change the name from Megabase to Dreambase"
**Score: 9/10**

Good rebranding prompt with context: "the concept is to haunt my records
to learn about what I want and eventually sell this workflow as a product."
This wasn't just a rename — it reframed the entire project from a personal
tool to a potential product.

**What worked:** Gave the WHY alongside the WHAT.

---

### Prompt 20: "let's try all the visualizations"
**Score: 8/10**

Ambitious scope expansion but well-timed — the core was built, the UI was
working, and visualizations are high-impact/low-risk. The "separate panes,
easily hideable" specification was perfect for implementation.

**Could improve:** Didn't specify which visualizations mattered most. "All 7"
is a lot — prioritizing 3 would have been more Tufte.

---

### Prompt 21: "xkcd comic meets infographic sense of humor"
**Score: 9/10**

Excellent creative direction delivered as a single sentence. This immediately
shaped the subtitle copy on every visualization pane ("the days you couldn't
stop talking to computers") and will guide the entire Dreambase tone.

---

### Prompt 22: Images from ChatGPT + historical sources
**Score: 7/10**

Good vision but came at the wrong time — mid-build of visualizations. This
is a classic Abendsen Parking moment. The question was worth asking, but
should have been flagged as "v2" rather than explored immediately.

---

### Prompt 23: "rabbit hole web design template + 20 questions"
**Score: 8/10**

Smart meta-prompt: instead of making all the design decisions himself, Ted
asked Claude to generate the decision space as questions. This is a good
"diverge before converge" strategy.

**What worked:** "20 questions" forced comprehensive coverage of visual,
UX, content, and product dimensions.
**Could improve:** 20 is a lot of questions to answer at once. Grouping
into "answer these 5 first" would make it more actionable.

---

### Prompt 24: This evaluation prompt
**Score: 9/10**

Asking for a retrospective evaluation of your own prompting methodology is
unusually self-aware. Most users never reflect on HOW they prompted, only
on WHAT they got. This kind of meta-analysis is how you improve the skill.

---

## PATTERNS OBSERVED

### What Ted Does Well
1. **Constraint injection** — "no API," "8 sessions is fine," "hold off on gmail."
   These short boundary statements saved more tokens than any planning skill.
2. **Skill-first planning** — Using Joe Chip scope freeze before coding prevented
   the most common failure mode: building the wrong thing.
3. **Quantified pushback** — "125 interactions is too much" is more useful than
   "this seems hard." Numbers enable optimization.
4. **The one-word prompt** — "go" is underrated. It communicates trust + approval
   + urgency in minimum tokens.
5. **Mid-build audits** — The failure-audit and Buckman-critic calls caught real
   issues before they compounded.

### What Could Improve
1. **Skill overlap** — Isidore (tokens) + Deckard (boundary) + Pris (pedagogy)
   all ran in the planning phase and produced partially overlapping outputs.
   Cost: ~3000-5000 tokens of redundant analysis. Fix: combine related skills
   into a single planning pass.
2. **Scope creep via enthusiasm** — The dream catalog, images, rabbit holes,
   and product vision all entered mid-build. Each was individually reasonable
   but collectively they expanded the project from "unified database + browser"
   to "productizable dream visualization platform." The parking lot skill
   existed but wasn't used aggressively enough.
3. **Vague memory references** — "I could have sworn I already did work on
   gmail in some kind of converted form or llm reading it" — this cost a
   search and a deferred task. More precise: "search Downloads for any
   gmail or mbox python scripts."
4. **All-at-once vs. prioritized** — "try all the visualizations" and
   "20 questions" are comprehensive but produce a lot of output to process.
   Batching in groups of 3-5 would make each round more actionable.

### The PKD Skill System's Value
The named skills (Joe Chip, Isidore, Deckard, Eldritch Swarm, Buckman,
Abendsen) provided genuine value as COGNITIVE TRIGGERS — they forced
Ted to think about scope, tokens, boundaries, and failure modes at the
right moments. The actual skill instructions were secondary to the ACT
of invoking them, which created deliberate pause points in what would
otherwise be a continuous stream of "build build build."

**Estimated token savings from planning discipline: 30-50%** compared to
an unplanned approach that would have required more backtracking,
re-ingestion, and architectural rework.

---

## SCORE SUMMARY

| # | Prompt | Score | Key Strength |
|---|--------|-------|-------------|
| 1 | "find everything database" | 9 | Open exploration |
| 2 | "pdf and html collections" | 8 | Format awareness |
| 3 | /plan-joe-chip-scope | 9 | Scope discipline |
| 4 | /plan-isidore-tokens | 9 | Meta-constraint |
| 5 | "gmail in converted form" | 7 | Intuition (vague) |
| 6 | "card with 3 sentences" | 10 | Perfect UX spec |
| 7 | /plan-pris-pedagogy | 7 | Intellectually rich, low ROI |
| 8 | /plan-deckard-boundary | 8 | Architecture |
| 9 | "8 sessions is fine" | 8 | Decisive approval |
| 10 | /plan-eldritch-swarm | 8 | Agent decomposition |
| 11 | "no API, 100/mo plan" | 10 | Critical constraint |
| 12 | "125 is too much work" | 9 | Quantified pushback |
| 13 | "bigger batches, I'll direct" | 8 | Human-in-the-loop |
| 14 | "100 creative dreams website" | 7 | Vision (scope creep) |
| 15 | /plan-buckman-critic | 8 | Mid-build checkpoint |
| 16 | /failure-audit | 9 | Incident response |
| 17 | "hold off on gmail" | 8 | Correct deferral |
| 18 | "go" | 10 | Maximum efficiency |
| 19 | "rename to Dreambase" | 9 | Vision + context |
| 20 | "all 7 visualizations" | 8 | Ambitious (unprioritized) |
| 21 | "xkcd humor" | 9 | Creative direction |
| 22 | "images + historical sources" | 7 | Wrong timing |
| 23 | "template + 20 questions" | 8 | Diverge-before-converge |
| 24 | "evaluate my prompting" | 9 | Meta-reflection |

**Average: 8.4/10**
**Weighted by impact: 8.7/10** (the high-scoring constraint prompts
mattered more than the lower-scoring exploratory ones)
