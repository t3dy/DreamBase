# Dreambase: Writing Templates, Style Guides & Narrative Design Patterns

**Mary Anne Dominic Template System** — structured templates for every content type
in the Dreambase ecosystem, plus a narrative designer's guide to using the database
as a storytelling engine.

---

## TEMPLATE 1: Dream Card (Compact)

**AUDIENCE:** Browser/visitor scanning the Dream Wall
**TOTAL TARGET:** 50-80 words
**TONE:** Evocative, curious, inviting

### Required Elements
- **Title** (3-7 words, evocative not descriptive)
- **Hook** (1 sentence that makes someone want to click)
- **Summary** (3 sentences: what is it, why does it matter, where did it go)
- **Tags** (2-4 theme tags)
- **Maturity badge** (sketch / design / prototype / built)

### Template
```
TITLE: [verb-noun or mystery-phrase, e.g. "The Alchemy Board Game"]
HOOK: [question or provocative claim, e.g. "What if transmutation was a game mechanic?"]
SUMMARY:
  Sentence 1: [WHAT — describe the core idea in plain language]
  Sentence 2: [WHY — why this matters or what makes it interesting]
  Sentence 3: [WHERE — where did it go? Still a sketch? Built? Abandoned?]
TAGS: [tag1, tag2, tag3]
MATURITY: [sketch | design | prototype | built]
```

### Anti-Patterns
- "This conversation discusses..." (boring, passive — write like a curator, not an indexer)
- Tags that are too generic ("coding", "ideas") — be specific ("procedural_generation", "alchemy")
- Summaries that describe the conversation instead of the idea

### Example Opening
GOOD: "The Alchemy Board Game" / "What if transmutation was a game mechanic?"
BAD: "Conversation about making a board game with alchemy theme" / "This discusses alchemy-themed games."

---

## TEMPLATE 2: Showcase Page (Tabbed Deep Dive)

**AUDIENCE:** Someone who clicked a dream card and wants the full story
**TOTAL TARGET:** 1,500-3,000 words across all tabs
**TONE:** Intellectual but accessible, xkcd humor in margins, Tufte density in data

### Tab: Overview (500-800 words)

```
NARRATIVE:
  Paragraph 1: [THE HOOK — what is this dream and why should anyone care?
    Write in third person present. "Ted explores the idea of..." not
    "I wanted to build..."]

  Paragraph 2: [THE DESIGN — what makes the core mechanic interesting?
    Connect to game design principles. Reference specific conversations
    where key decisions were made.]

  Paragraph 3: [THE EVOLUTION — how did this idea change over time?
    What started as X became Y when Z happened. Show the intellectual
    journey, not just the endpoint.]

  Paragraph 4: [THE PEDAGOGY — what does this game teach? Not what it
    teaches ABOUT, but what cognitive skill the mechanic develops.
    "The player learns X by doing Y" not "The game is about X."]

  Paragraph 5 (optional): [THE VISION — where could this go? What would
    a finished version look like? What's the one-screenshot pitch?]

PEDAGOGY BOX:
  Concept: [what the game teaches]
  Mechanic: [which game mechanic maps to the concept]
  Difficulty Easy: [simplified version]
  Difficulty Medium: [standard version]
  Difficulty Hard: [full complexity]
```

**Required:** Paragraphs 1-3, Pedagogy Box
**Optional:** Paragraphs 4-5
**Anti-pattern:** Don't write a feature list. Write a story.

### Tab: Design Evolution (timeline entries)

```
For each significant conversation:

DATE: [YYYY-MM-DD]
TITLE: [conversation title]
DESCRIPTION: [1-2 sentences — what happened, what decision was made.
  Use active voice: "Introduced the transmutation chain mechanic" not
  "The transmutation chain mechanic was discussed."]
CONVERSATION_ID: [database ID for link]
```

**Anti-pattern:** Don't list every conversation. Pick the 5-8 that represent
genuine evolution points. Skip conversations that just refined existing ideas
without changing direction.

### Tab: Key Quotes (3-8 quotes)

```
QUOTE: "[exact text, max 50 words — pick moments of creative energy,
  surprising insight, or design breakthrough]"
ROLE: [user | assistant]
CONVERSATION: [title]
CONVERSATION_ID: [database ID]
```

**Selection criteria:**
- Moments where the design clicked ("what if we...")
- Surprising connections between domains
- Self-aware humor or meta-commentary
- Honest doubt or creative tension

**Anti-pattern:** Don't pick quotes that are just descriptions. Pick quotes
that show thinking-in-progress.

### Tab: Gallery

```
For each image:

URL: [path or external URL]
CAPTION: [1 sentence describing what this shows and why it matters]
SOURCE: [dall-e | wikimedia | concept-art | screenshot]
```

**Sources in priority order:**
1. DALL-E images extracted from ChatGPT conversations (already generated)
2. Public domain art from Wikimedia Commons (alchemical diagrams, medieval manuscripts)
3. Screenshots of any prototypes or mockups
4. AI-generated concept art (v2)

### Tab: Source Conversations

Auto-populated from database. No template needed.

---

## TEMPLATE 3: Theme Description (Rabbit Hole Header)

**AUDIENCE:** Someone navigating by theme (alchemy, games, esoteric, etc.)
**TOTAL TARGET:** 40-60 words
**TONE:** Intellectual but accessible, curious not pretentious

```
THEME: [theme name]
DESCRIPTION:
  Sentence 1: [What this theme covers — be specific, not generic]
  Sentence 2: [Why this matters to Ted / "why this matters to me" personal angle]
DREAM_COUNT: [auto-populated]
CONVERSATION_COUNT: [auto-populated]
```

### Examples

GOOD:
```
THEME: Alchemy
DESCRIPTION: The art of transformation — not just lead-into-gold, but
  the deeper question of how systems change state. Ted keeps returning
  to alchemy because it's the oldest framework for thinking about
  game mechanics, learning progressions, and creative process.
```

BAD:
```
THEME: Alchemy
DESCRIPTION: Conversations about alchemy topics. Various discussions
  related to alchemical themes.
```

---

## TEMPLATE 4: Database Entry Templates

### Idea Record

```sql
-- Template for manually adding an idea to the database
INSERT INTO ideas (conversation_id, name, category, description, maturity, method, created_at)
VALUES (
  [conversation_id],     -- Link to source conversation
  '[idea name]',         -- 3-7 words, evocative
  '[category]',          -- game | app | educational | product
  '[description]',       -- 1-2 sentences: what is it, what makes it interesting
  '[maturity]',          -- sketch | design | prototype | built
  'manual',              -- method: manual curation
  '[YYYY-MM-DD]'         -- when the idea first appeared
);
```

### Showcase JSON Sidecar

After ChatGPT batch reading, save responses as `showcases/<slug>.json`:

```json
{
  "narrative": "<p>Paragraph 1...</p><p>Paragraph 2...</p>",
  "timeline_entries": [
    {
      "date": "2025-01-03",
      "title": "First conversation title",
      "description": "What happened and what was decided.",
      "conversation_id": 40
    }
  ],
  "quotes": [
    {
      "text": "The exact quote from the conversation.",
      "role": "user",
      "conversation_title": "Conversation Title",
      "conversation_id": 40
    }
  ],
  "images": [
    {
      "url": "/static/images/showcase/bubble-bog-witch-01.png",
      "caption": "DALL-E concept art of the Bog Witch emerging from bubbles."
    }
  ]
}
```

### Tag Record

```sql
-- When tagging conversations manually or adding new themes
INSERT OR IGNORE INTO tags (name) VALUES ('[tag_name]');

INSERT OR REPLACE INTO conversation_tags (conversation_id, tag_id, confidence, method)
VALUES (
  [conv_id],
  (SELECT id FROM tags WHERE name='[tag_name]'),
  0.9,        -- confidence: 0.7 for keyword, 0.9 for manual/LLM
  'manual'    -- method: keyword | llm | folder_name | manual
);
```

---

## STYLE GUIDE: Dreambase Voice

### The Three Registers

**1. Curator Voice** (dream cards, theme descriptions, showcase narratives)
- Third person present: "Ted explores..." not "I wanted..."
- Intellectual but warm — a museum placard written by someone who cares
- Show the thinking, not just the result
- Never explain what a conversation "discusses" — describe what it DISCOVERS

**2. xkcd Voice** (subtitles, empty states, tooltips, UI microcopy)
- Self-deprecating humor about the absurdity of the data
- "397 ideas, 10 built. The graveyard of ambition."
- "No dreams here yet. You were probably touching grass that week."
- Every subtitle should make the reader smile without undermining the data
- Alt-text/tooltips with bonus commentary (xkcd's signature move)

**3. Data Voice** (visualizations, sparkline tables, statistics)
- Tufte discipline: every word encodes information
- Direct labeling, no legends floating off to the side
- Numbers speak for themselves — "662 pages" hits harder than "a very long conversation"
- Context makes numbers meaningful: "662 pages — longer than War and Peace"

### Rabbit Hole Navigation Copy

Per DREAMBASE_DESIGN_TEMPLATE.md:
- Button labels should be inviting: **"Go deeper"** not "View more"
- Theme transitions: **"This dream also touches on..."** not "Related tags:"
- Dead ends acknowledged: **"This rabbit hole loops back to [X]"**
- Connections between dreams: **"Born in the same conversation as..."**

### Words to Use
- discover, explore, haunt, unearth, trace, evolve, emerge, converge
- dream, vision, obsession, rabbit hole, constellation
- transmute, transform, iterate, prototype

### Words to Avoid
- discuss, conversation (too meta — the user knows they're reading conversations)
- interesting (show, don't tell)
- various, multiple, several (be specific: "7 conversations across 3 months")
- simple, just, basically (dismissive of the work)

---

## TEMPLATE 5: Narrative Designer's Guide to Dreambase

**How a narrative designer would use this database to build story-driven projects.**

### The Premise

You have 4,308 conversations, 397 ideas, 1,825 tagged threads, and 3.9 million
messages spanning 2+ years of one person's intellectual life. This isn't a
database — it's a primary source archive. Here's how a narrative designer
would mine it.

### Strategy 1: Character Arc Through Data

The database contains a protagonist (Ted) whose interests, skills, and
creative ambitions evolved over time. A narrative designer would:

1. **Pull the sentiment river** for emotional arc across months
2. **Track topic frequency** to see what obsessions wax and wane
3. **Find convergence points** — months where alchemy + games + coding
   all peak simultaneously = creative breakthroughs
4. **Identify "dark periods"** — gaps in activity, negative sentiment runs,
   abandoned ideas = tension in the narrative

**Query pattern:**
```sql
-- Find the month with the most diverse creative activity
SELECT substr(c.created_at,1,7) as month,
       count(DISTINCT t.name) as unique_tags,
       count(DISTINCT c.id) as conversations
FROM conversations c
JOIN conversation_tags ct ON ct.conversation_id=c.id
JOIN tags t ON t.id=ct.tag_id
WHERE c.created_at >= '2024-01-01'
GROUP BY month ORDER BY unique_tags DESC LIMIT 10;
```

### Strategy 2: Idea Genealogy

Every idea has ancestors. The Alchemy Board Game didn't appear from nothing —
it descended from conversations about:
- Alchemy as a system of transformation (esoteric interest)
- Game mechanics that teach through play (pedagogy interest)
- Board games as physical artifacts (craft interest)

A narrative designer traces these genealogies:

1. **Find the first mention** of each idea's key concepts
2. **Map the cross-pollination** — which conversations from different domains
   fed into the same idea?
3. **Build the "creative DNA"** — each idea is a recombination of 2-3 themes

**Query pattern:**
```sql
-- Find conversations that share tags with a specific idea's conversation
SELECT c2.title, c2.created_at, t.name as shared_tag
FROM conversation_tags ct1
JOIN conversation_tags ct2 ON ct1.tag_id=ct2.tag_id
  AND ct1.conversation_id != ct2.conversation_id
JOIN conversations c2 ON c2.id=ct2.conversation_id
JOIN tags t ON t.id=ct1.tag_id
WHERE ct1.conversation_id = [idea_conversation_id]
ORDER BY c2.created_at;
```

### Strategy 3: The Unreliable Narrator

Ted's memory of his own creative history is incomplete and sometimes wrong
(see: "I could have sworn I already did work on gmail"). A narrative designer
would exploit this:

1. **Compare what Ted says he worked on** vs **what the data shows**
2. **Find forgotten ideas** — things discussed passionately in 2024 that
   never appear again in 2025
3. **Find false memories** — ideas Ted attributes to one period that
   actually originated elsewhere
4. **Find the idea that won't die** — concepts that keep reappearing
   across different projects under different names

### Strategy 4: The Showcase as Narrative Structure

Each showcase page IS a short story:
- **Act 1 (Overview):** Meet the idea. What is it? Why does it matter?
- **Act 2 (Design Evolution):** Watch it struggle. Pivots, dead ends, breakthroughs.
- **Act 3 (Key Quotes):** Hear the protagonist's voice in the moment.
- **Epilogue (Gallery):** See what it looks like. Or what it COULD look like.
- **Appendix (Sources):** The primary sources, for the reader who wants to
  go deeper than the narrator went.

The tabbed structure isn't just UI convenience — it's narrative pacing.
The reader chooses their own depth. Some will skim the overview. Others
will read every source conversation. The showcase page accommodates both
without forcing either.

### Strategy 5: The Product Narrative

If Dreambase becomes a product ("help people mine their own social media data"),
the narrative designer's job is to answer: **what story does YOUR data tell?**

The template:
1. **Ingest** — "Here's everything you've said for 2 years"
2. **Discover** — "Here are the 10 ideas you kept coming back to"
3. **Confront** — "Here's how much time you spent on X vs Y"
4. **Decide** — "Here's which dreams are still alive and which you abandoned"

This is the emotional arc of the product: curiosity, discovery, honest
self-reflection, and then action. The database isn't the product.
The MIRROR is the product.

---

## TEMPLATE 6: Values Evidence Card

For the proposed Values tab — summarizing scholarly and engineering values
with evidence links that rabbit-hole into the database.

**AUDIENCE:** Ted (self-reflection) or potential collaborators/clients
**TOTAL TARGET:** 100-150 words per value
**TONE:** Curator voice, evidence-first

```
VALUE: [name, 3-5 words, e.g. "Games That Teach Themselves"]

CLAIM: [1 sentence — what Ted believes about this topic.
  Not "I value X" but "X works because Y."]

EVIDENCE: [2-3 specific database references]
  - [conversation title] ([pages]p, [date]) — [what it demonstrates]
  - [conversation title] ([pages]p, [date]) — [what it demonstrates]
  - [idea name] ([maturity]) — [what it demonstrates]

RABBIT HOLE: [which theme or tag to explore for more]

COUNTER-EVIDENCE (optional): [honest acknowledgment of tension
  or contradiction in the data — shows intellectual honesty]
```

### Example

```
VALUE: Implicit Pedagogy Over Explicit Tutorial

CLAIM: The best game mechanics teach through play, not through text boxes.
  If you need a tutorial popup to explain the mechanic, the level design failed.

EVIDENCE:
  - "Bubble Witch Platformer Ideas" (30p, 2025-01) — 122 messages designing
    bubble mechanics that communicate zone properties without text
  - "Games Learning Alchemy Board Game" (241p) — transmutation discovery
    as the core loop, deliberately hiding the complete transformation graph
  - "Snake Autobattler Concept" (29p, 2025-01) — post-battle replay as
    the teaching mechanism, not pre-battle instructions

RABBIT HOLE: game_idea + educational tags (47 conversations)

COUNTER-EVIDENCE: "Alchemy Game Tutorial Design" (137p) exists — sometimes
  even implicit-pedagogy advocates need to write a tutorial. The tension
  between these positions IS the design challenge.
```
