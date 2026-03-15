# Dreambase: Summary Writing Templates

**Mary Anne Dominic Template System** — operational templates for every summary
type that appears in the Dreambase UI. Designed for batch processing: an agent
reads conversation data, applies the matching template, outputs structured text.

**Companion to:** DREAMBASE_TEMPLATES.md (design philosophy, narrative design)
**Purpose:** Machine-actionable templates for improving database copy at scale

---

## VOICE REGISTERS (quick reference)

| Register | Used Where | Key Rule | Example |
|----------|-----------|----------|---------|
| **Curator** | Summaries, descriptions, narratives | Third person present. Show thinking, not results. | "Ted traces transmutation chains through 12th-century manuscripts, building a vocabulary that resurfaces in his board game designs." |
| **xkcd** | Subtitles, empty states, tooltips | Self-deprecating. Every line earns a smile without undermining the data. | "397 ideas, 10 built. The graveyard of ambition." |
| **Data** | Stats, sparklines, badge labels | Every word encodes information. No decorative text. | "662 pages — longer than War and Peace" |

---

## TEMPLATE A: Conversation Summary

**Database field:** `conversations.summary`
**Displayed on:** Browse cards, collection entries, search results
**Voice:** Curator
**Target:** 2-3 sentences, 40-80 words

### Structure

```
Sentence 1: [WHAT — the core subject or idea, stated concretely.
  Name specific texts, concepts, mechanics, or frameworks discussed.
  Not "alchemy is discussed" but "a transmutation chain mechanic
  maps alchemical stages to engine-building phases."]

Sentence 2: [HOW — the method or approach. What did the user actually DO
  in this conversation? Design a system? Summarize a book? Debate a theory?
  Work through a technical problem?]

Sentence 3: [SO WHAT — what emerged. A design decision, a new question,
  an abandoned path, a working prototype. Give the reader a reason to click.]
```

### Required Elements
- At least one **specific noun** (name of a text, game mechanic, tool, philosopher)
- The **maturity signal** — did this produce something concrete or remain exploratory?
- A **hook** — something unexpected, a connection, a question still open

### Anti-Patterns
- "This conversation discusses..." (passive, meta — describe the idea, not the conversation)
- "Various topics are explored..." (vague — name them)
- "The user asks about..." (indexer voice — write like a curator)
- Starting with "In this conversation..." (redundant — the reader knows it's a conversation)
- Ending with "...and more" (lazy — pick the best detail instead)

### Examples

**GOOD:**
> Renaissance alchemical illustration as a form of materials science documentation — Principe's argument that alchemical images encode laboratory procedures, not mystical visions. Ted builds a lecture outline connecting Atalanta Fugiens emblem sequences to modern process diagrams.

**GOOD:**
> A bubble platformer where the swamp itself teaches the player through movement physics. Three difficulty tiers emerge: bubbles as traversal (easy), bubbles as limited resource (medium), bubbles as ecological indicator the player learns to read (hard).

**BAD:**
> This conversation discusses alchemy and game design. Various ideas are explored including a board game concept. The user asks about different mechanics.

**BAD:**
> Would you like a summary of this document, or do you want to search for something specific in it?

---

## TEMPLATE B: Collection Description

**Database field:** `COLLECTIONS[slug]["description"]` in app.py
**Displayed on:** Collection index cards, collection hero section
**Voice:** Curator with a personal angle
**Target:** 2-4 sentences, 40-80 words

### Structure

```
Sentence 1: [SCOPE — what this collection covers, stated with specificity.
  Name 2-3 concrete things (texts, thinkers, frameworks, tools)
  that anchor the theme.]

Sentence 2: [THREAD — what connects these conversations beyond the tag.
  What question or obsession runs through them?
  "The recurring question of..." or "The connection between X and Y
  that keeps appearing..."]

Sentence 3 (optional): [SURPRISE — something unexpected the data reveals.
  A cross-domain connection, an intensity signal, a convergence
  with another collection.]
```

### Required Elements
- **Specific anchors** — name texts, thinkers, tools, not just themes
- **A thread** — what makes this a collection rather than just "conversations tagged X"
- **Personal angle** — why this matters to the person behind the data

### Anti-Patterns
- "A collection of conversations about..." (tautological — the UI shows it's a collection)
- "Many interesting discussions..." (show, don't tell)
- Generic theme descriptions that could describe anyone's research

### Examples

**GOOD:**
> Renaissance alchemy as a system of transformation — not just lead-into-gold but the deeper question of how matter, mind, and symbol change state. These conversations span Atalanta Fugiens, Tilton, alchemical illustration, and the chemistry underneath the mysticism.

**GOOD:**
> PKD as philosopher, Gnostic, and inadvertent game designer. From the Exegesis to biopolitics to hermeticism — and the recurring question of what happens when reality itself is unreliable.

---

## TEMPLATE C: Dream Card Hook

**Database field:** `SHOWCASES[slug]["hook"]` in app.py
**Displayed on:** Showcase index cards, showcase hero
**Voice:** Curator, single sentence
**Target:** 1 sentence, 12-25 words

### Structure

```
[A question or provocative claim that creates curiosity.
  Format options:
  - "What if [unexpected combination]?"
  - "[Concrete thing] as [surprising reframe]."
  - "[Familiar concept], but [twist that makes it new]."
]
```

### Required Elements
- Must create **curiosity gap** — reader needs to click to resolve it
- Must be **specific** enough to distinguish this dream from others
- Must be **honest** — don't overpromise what the conversations contain

### Anti-Patterns
- "An exploration of..." (not a hook — it's a label)
- "A comprehensive guide to..." (product copy, not dream copy)
- Hooks that could apply to any project in the category

### Examples

**GOOD:** "What if transmutation was a platformer mechanic and the swamp was alive?"
**GOOD:** "The Great Work as engine-building: transmutation chains, hidden knowledge, and the joy of discovery."
**BAD:** "A game about alchemy with board game mechanics."
**BAD:** "Exploring the intersection of games and alchemy."

---

## TEMPLATE D: Showcase Narrative

**Database field:** JSON sidecar `showcases/<slug>.json` → `"narrative"`
**Displayed on:** Showcase page, Overview tab
**Voice:** Curator
**Target:** 3-5 paragraphs, 300-600 words

### Structure

```
Paragraph 1 — THE HOOK:
[What is this dream and why should anyone care? Write in third person
  present. Open with the most compelling aspect, not the chronological
  beginning. "Ted explores..." or "The core mechanic is..." not
  "In January 2025, Ted started thinking about..."]

Paragraph 2 — THE DESIGN:
[What makes the core mechanic/concept interesting? Reference specific
  conversations where key decisions were made. Connect to design
  principles (implicit pedagogy, systems thinking, etc.).]

Paragraph 3 — THE EVOLUTION:
[How did this idea change over time? "What started as X became Y
  when Z happened." Show the intellectual journey, not just the endpoint.
  This is where conversation dates and page counts add texture.]

Paragraph 4 (optional) — THE PEDAGOGY:
[What does this teach? Not what it teaches ABOUT, but what cognitive
  skill the mechanic develops. "The player learns X by doing Y."]

Paragraph 5 (optional) — THE VISION:
[Where could this go? What's unfinished? What question remains open?
  End on forward motion, not retrospection.]
```

### Required Elements
- At least one **conversation reference** (title, date, or page count)
- At least one **design decision** described concretely
- The **evolution arc** — the idea must move, not sit static

### Anti-Patterns
- Feature lists disguised as narrative
- Chronological recitation without synthesis
- "This game would..." (future speculation without grounding in actual conversations)

---

## TEMPLATE E: Values Evidence Card

**Displayed on:** Values tab, expandable evidence sections
**Voice:** Curator (claim), Data (evidence)
**Target:** 80-120 words per card

### Structure

```
VALUE NAME: [3-5 words, stated as a principle not a topic.
  "Games That Teach Themselves" not "Pedagogy"
  "Data Density Over Decoration" not "Visualization"]

CLAIM: [1 sentence — what the data shows Ted believes about this.
  Not "I value X" but "X works because Y." Falsifiable, grounded.]

EVIDENCE:
  - [conversation title] ([pages]p, [date]) — [what it demonstrates, 8-15 words]
  - [conversation title] ([pages]p, [date]) — [what it demonstrates]
  - [idea or tag pattern] — [what it demonstrates]

COUNTER-EVIDENCE (optional): [honest acknowledgment of tension.
  "But [title] exists, showing that even X sometimes requires Y."
  This is intellectual honesty, not weakness.]

RABBIT HOLE: [tag name or collection slug → "Go deeper"]
```

---

## TEMPLATE F: Collection Conversation Entry

**Displayed on:** Collection detail page, ranked conversation list
**Voice:** Curator (summary), Data (stats)
**Target:** The existing `conversations.summary` field, enhanced

### Enhancement Rules for Batch Processing

When an agent reads a conversation to improve its summary:

1. **Keep it to 3 sentences.** More is not better.
2. **Name the thing.** If there's a text being discussed, name it. If there's a game being designed, name it. If there's a philosopher being read, name them.
3. **State the scale.** "662 pages of close reading" or "a 30-page brainstorm" — the length tells the reader whether this is a deep dive or a sketch.
4. **Find the turn.** Every good conversation has a moment where the direction shifts — a new insight, a design pivot, a connection made. Put that in sentence 2 or 3.
5. **Cut the meta.** Remove any language that describes the conversation as a conversation. The reader knows.

### Batch Processing Format

For an agent improving summaries at scale, output as:

```
CONVERSATION_ID: [id]
TITLE: [title]
SUMMARY: [improved 2-3 sentence summary following Template A]
---
```

---

## BATCH WORKFLOW: How to Use These Templates

### For ChatGPT Manual Batch Processing

1. Export conversations using `showcase_chunks.py` or `summarize.py batch-export`
2. Paste into ChatGPT with the relevant template from this file
3. Copy structured output
4. Import using `summarize.py batch-import`

### For Eldritch Swarm Automated Processing

Each agent in the swarm:

1. **Reads** — pulls conversation data from megabase.db (title, first N messages, tags, sentiment, page count)
2. **Classifies** — determines which template applies (A for summaries, B for collection descriptions, etc.)
3. **Writes** — generates text following the template structure
4. **Validates** — checks against anti-patterns list
5. **Outputs** — structured format ready for database import or app.py insertion

### Quality Checklist (all templates)

Before accepting any generated summary:

- [ ] Contains at least one **specific noun** (not just abstract themes)
- [ ] Does NOT start with "This conversation..." or "In this conversation..."
- [ ] Does NOT contain "various", "interesting", "discusses", or "explores"
- [ ] Contains a **hook** or **turn** — something that creates curiosity
- [ ] Is **honest about scope** — doesn't overpromise what the conversation contains
- [ ] Matches the **voice register** for its display context
- [ ] Is **under the word target** — brevity over completeness

---

## VOCABULARY QUICK REFERENCE

### Use These Words
discover, trace, map, build, design, iterate, transmute, converge, emerge,
wrestle, prototype, mine, unearth, haunt, excavate

### Avoid These Words
discuss, explore (overused), interesting, various, several, multiple,
simple, just, basically, comprehensive, delve

### Dreambase-Specific Terms
- **dream** = a curated showcase (not "project" or "idea")
- **idea** = a database record in the ideas table
- **rabbit hole** = a themed navigation path through collections
- **collection** = a curated group of conversations by theme
- **haunt** = to revisit your own data (Dreambase's verb)
