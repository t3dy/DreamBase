# Dreambase: Terminology & Prompting Audit

**Inspector Buckman examines the language.**
**Purpose:** Clarify every term of art in the project so builder and user mean the same thing.

---

## CURRENT VOCABULARY MAP

Every term used in the project, what it currently means, and where ambiguity lives.

### Core Architecture Terms

| Term | Current Usage | Where Used | Ambiguity Risk |
|------|-------------|------------|----------------|
| **Dreambase** | The project name (UI-facing) | All templates, docs | LOW — clear |
| **Megabase** | The project name (code-facing, historical) | Directory name, database filename | MEDIUM — newcomers confused |
| **Dream** | A curated showcase page for a game idea | URL `/dream/<slug>`, some UI copy | HIGH — also means "any creative idea" in casual use |
| **Showcase** | The implementation of a dream page (5-tab deep dive) | Nav link, `SHOWCASES` dict, template names | HIGH — overlaps with "dream" |
| **Collection** | A curated thematic grouping of conversations | Nav link, `COLLECTIONS` dict, templates | LOW — clear |
| **Rabbit Hole** | A themed navigation path that goes deeper | Design template, collection copy, button labels | MEDIUM — metaphor, not a code object |
| **Idea** | A database record in the `ideas` table | Ideas page, database | LOW — clear |
| **Conversation** | A database record in the `conversations` table | Browse page, all detail pages | LOW — clear |
| **Tag** | A keyword category applied to conversations | Filters, pills, database | LOW — clear |
| **Source** | Where data came from (chatgpt, claude, sms, etc.) | Badges, filters | LOW — clear |
| **Batch file** | A .md file meant to be pasted into ChatGPT | summarize.py, improve_summaries.py, chunks/ | MEDIUM — two scripts use different formats |
| **Chunk** | A GPT-ready export of a conversation | chunk.py, chunks/ dir | LOW — clear |
| **Sidecar** | A JSON file that overrides showcase defaults | `showcases/<slug>.json` | LOW — developers only |

### Voice & Style Terms

| Term | Current Usage | Where Defined |
|------|-------------|---------------|
| **Curator voice** | Third person present, museum placard tone | DREAMBASE_TEMPLATES.md |
| **xkcd voice** | Self-deprecating humor, microcopy | DREAMBASE_TEMPLATES.md |
| **Data voice** | Tufte-inspired, numbers-speak | DREAMBASE_TEMPLATES.md |
| **Hook** | 1-sentence curiosity-gap opener | SHOWCASES dict, SUMMARYTEMPLATE.md |
| **Summary** | 2-3 sentence description stored in DB | conversations.summary, SUMMARYTEMPLATE.md |
| **Narrative** | Multi-paragraph showcase overview | Sidecar JSON, showcase template |
| **Pedagogy** | What a game teaches through mechanics | SHOWCASES dict, showcase template |

### Process Terms

| Term | Current Usage | Ambiguity Risk |
|------|-------------|----------------|
| **Eldritch Swarm** | Multi-agent parallel work decomposition | LOW — PKD naming convention |
| **Janitor** | Agent that fixes bot-voice summaries | LOW — clear |
| **Curator** | Agent that proposes improved featured summaries | MEDIUM — also a voice register name |
| **Copywriter** | Agent that proposes improved app.py copy | LOW — clear |
| **Batch workflow** | The paste-into-ChatGPT manual grind | MEDIUM — two scripts compete |

---

## AMBIGUITY HOTSPOTS

### 1. "Dream" vs "Showcase"
The URL says `/dream/alchemy-board-game` but the nav says "Showcases." The design template says "Dream Wall" and "Dream Card." The code uses `SHOWCASES` dict and `showcase.html` template.

**Current state:** "Dream" is the user-facing poetic name. "Showcase" is the developer-facing implementation name. Both refer to the same thing: a curated 5-tab deep-dive page for a game idea.

**Risk:** When Ted says "give me a showcase page for historians" — does he mean a 5-tab SHOWCASE (with pedagogy, quotes, timeline) or a COLLECTION (lighter, just description + conversation list)?

### 2. "Showcase" vs "Collection"
Both are curated pages of conversation groupings. The distinction:
- **Showcase** = 5 tabs, pedagogy box, difficulty tiers, quotes, timeline. Currently only for 3 game ideas.
- **Collection** = hero description, ranked conversation list, adjacent themes. For thematic groupings.

**Risk:** As more showcase-like pages are requested (historians, projects), the boundary blurs. Is a historian page a showcase or a collection?

### 3. "Rabbit Hole"
Used metaphorically throughout the design template and collection pages. Not a code object. "Go deeper" buttons, "this rabbit hole also touches on..." copy.

**Risk:** When Ted says "each with its own rabbit hole" — he means each collection should have depth and links, not that there's a separate /rabbit-hole/ route.

### 4. "Index Page"
Ted asked for "index pages" and "an index of all game ideas as text links." This could mean:
- A literal text-link list (what was built: ideas page with list view)
- A table of contents for each section
- A site map / navigation page

### 5. "Visualization"
Ted asked for "beautiful visualizations of all projects." This could mean:
- A Tufte-style data visualization (chart/graph)
- A styled HTML page displaying project info
- An SVG/canvas interactive diagram

---

## 20 QUESTIONS FOR TERMINOLOGY CLARITY

### Architecture Questions

**1.** When you say "showcase page for historians" — do you want the full 5-tab treatment (pedagogy, quotes, timeline, gallery, source conversations) or the lighter collection format (description + ranked conversation list + adjacent themes)?

**2.** Should "Dream" be the official user-facing term for ALL curated pages (games, scholars, themes), or only for game ideas? Right now `/dream/` is only for games. Would `/dream/pico-della-mirandola` make sense, or should scholars live at `/scholar/` or `/collection/`?

**3.** Are "Showcases" and "Collections" genuinely different things in your mind, or are they the same concept at different levels of completeness? Could collections graduate to showcases once they have enough content (quotes, timeline, pedagogy)?

**4.** You've asked for showcase pages for: games (3), historians, favorite projects, scholarly PDF mining, PKD, philosophy, marxism, music engineering. Should these ALL be the same page type, or should games stay as showcases while everything else is a collection?

### Content Questions

**5.** When you say "rabbit hole" — are you describing the visual/UX pattern (depth, links, "go deeper"), or do you want a specific /rabbit-hole/ route that works differently from collections?

**6.** "Index page" — do you want a single master index listing EVERYTHING (ideas, collections, showcases, projects) as text links? Or separate indexes per section?

**7.** The "building dreams" collection maps your Dev/ projects to conversations. Should each project get its own detail page, or is the collection list with links to conversations sufficient?

**8.** For historian showcase pages — how many historians do you expect? 5 favorites? 15? All scholars mentioned in any conversation? This determines whether they're individual showcases or one "Scholars" collection.

### Voice & Writing Questions

**9.** The "Curator voice" is third person present ("Ted traces..."). When YOU are reading your own Dreambase, does third person feel right? Or would you prefer first person ("I traced...") for personal use, saving third person for a public/product version?

**10.** The xkcd voice (self-deprecating humor in subtitles) — how much is too much? Should EVERY page have a witty subtitle, or just the viz and values pages where it already exists?

**11.** When you say "flesh out our writing in the rich summaries" — do you mean you want ME to write improved summaries directly into the database, or produce proposals that you review first? (Currently the Curator agent produces proposals.)

### Data Questions

**12.** Game ideas are currently classified by category (game/app/educational/other) and maturity (sketch/design/prototype/built). You asked about genre (platformer, autobattler, board game). Should genre be a new database column, a tag, or just a filter derived from keywords?

**13.** The "scholarly values" on the Values page were derived from sentiment analysis and topic prevalence. Do you consider these stable findings, or are they hypotheses you want to test and revise as more conversations get better summaries?

**14.** SMS, Facebook, and Google Chat conversations now have auto-generated summaries ("Group chat with Sarah — 'hey are we...' 47 messages"). These are functional but generic. Do you care about improving them, or are non-LLM conversations background data?

### Scope Questions

**15.** You've requested a lot of .md output documents (RPG guide, RAW essay, audit, templates, swarm plans). Are these for your own reference, for loading into ChatGPT for future sessions, for a potential product/portfolio, or all three?

**16.** The "project visualization" — do you want an interactive web page on the Flask app (like the viz page), or a static document/image?

**17.** When you say "make it like 20 pages" for the RAW/Freemasonry essay — is that a literal length target, or more of a "go deep, don't hold back" signal?

### Process Questions

**18.** The batch workflow (paste into ChatGPT, import responses) requires ~110 manual paste operations. Is this something you plan to do over days/weeks, or should I prioritize automating it further?

**19.** You've invoked multiple PKD skills (/plan-eldritch-swarm, /plan-runciter-audit, /write-dominic-template, etc.). When you invoke a skill, do you want the full formal output in its prescribed format, or is it OK to integrate the skill's thinking into the natural flow of work?

**20.** Several requests are building on each other (showcases → collections → historian showcases → project showcases → genre filtering). Is the end state a single comprehensive website with 10+ nav tabs, or do you see some of these as separate projects/experiments?

---

## RECOMMENDED TERMINOLOGY DECISIONS

Based on usage patterns, here's what I think you mean. Correct me where I'm wrong:

| Decision | My Best Guess |
|----------|---------------|
| "Dream" = | Any curated deep-dive page (games, scholars, themes) |
| "Showcase" = | The 5-tab format specifically (pedagogy, quotes, timeline) |
| "Collection" = | The lighter format (description + conversation list) |
| "Rabbit hole" = | The UX pattern of depth and cross-linking, not a route |
| "Index page" = | A compact text-link view of items in a category |
| "Visualization" = | An interactive web page with Tufte-style data graphics |
| "Showcase page for X" = | You want the collection format unless X is a game idea |
| "20 pages" = | Go deep, quality over brevity |
| "Batch files" = | The ChatGPT paste workflow, not automation |
