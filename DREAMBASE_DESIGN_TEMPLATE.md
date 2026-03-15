# Dreambase: Rabbit Hole Web Design Template

## Concept
A card-based "dream catalog" website where each card represents a creative dream,
idea, or intellectual obsession mined from 2+ years of personal data. Users navigate
by clicking theme buttons to descend deeper into interconnected rabbit holes.

Think: xkcd's visual wit meets Tufte's data density meets a Renaissance cabinet of curiosities.

---

## INFORMATION ARCHITECTURE

### Level 0: The Dream Wall
- All 100 (or N) dream cards visible at once as a mosaic
- Each card: illustration + title + 1-sentence hook
- Theme buttons along top or side for filtering (alchemy, games, esoteric, etc.)
- Cards resize/reflow based on active filters
- Subtle animation: cards not matching a filter fade rather than disappear

### Level 1: The Dream Card (expanded)
- Full card view with: title, 3-sentence summary, illustration, source badge
- "Down the rabbit hole" section with theme buttons specific to THIS dream
- Related dreams sidebar (connected by shared tags/topics)
- Key quotes or moments pulled from the original conversation
- Maturity badge: sketch / design / prototype / built
- Timeline: when this dream first appeared, how it evolved

### Level 2: The Rabbit Hole
- Filtered view showing ALL dreams connected by a theme
- Theme header with description and visual motif
- Dreams arranged by: chronological, maturity, or interconnection
- Visualization: mini constellation showing how dreams in this theme connect
- "Adjacent themes" links to other rabbit holes

### Level 3: The Conversation (existing /conversation/<id> view)
- Full original conversation with sentiment and message-level detail
- "Other dreams born in this conversation" links

---

## VISUAL DESIGN PRINCIPLES

### The xkcd Spirit
- Captions and labels should have personality, not be sterile
- Occasional self-deprecating humor in empty states
  ("No dreams here yet. You were probably touching grass that week.")
- Hand-drawn or sketch aesthetic for borders/arrows/annotations
- Stick-figure-style mascot or recurring visual character?
- Alt-text / tooltips with bonus commentary (xkcd's signature move)

### The Tufte Discipline
- No chartjunk: every visual element encodes data
- Small multiples over animation
- High information density per screen
- Direct labeling (no legends floating off to the side)
- Minimal chrome, maximum content

### The Cabinet of Curiosities
- Each dream card feels like a physical artifact
- Illustrations sourced from: ChatGPT DALL-E outputs, public domain
  historical art (Wikimedia, Met Open Access, British Library, Wellcome)
- Visual texture: parchment, manuscript margins, alchemical diagrams
- But not cosplay — modern typography, dark theme, clean grid

---

## CONTENT GUIDELINES

### Dream Card Copy
- Title: 3-7 words, evocative not descriptive
  GOOD: "The Alchemy Board Game"
  BAD: "Conversation about making a board game with alchemy theme"
- Hook: 1 sentence that makes someone want to click
  GOOD: "What if transmutation was a game mechanic?"
  BAD: "This conversation discusses alchemy-themed board games."
- Summary: 3 sentences — what is it, why does it matter, where did it go
- Tags: 2-4 theme tags for rabbit hole navigation

### Theme Descriptions
- Each theme (alchemy, games, esoteric, etc.) gets a 2-sentence description
- Tone: intellectual but accessible, curious not pretentious
- Include a "why this matters to me" personal angle

### Rabbit Hole Navigation Copy
- Button labels should be inviting: "Go deeper" not "View more"
- Theme transitions: "This dream also touches on..." not "Related tags:"
- Dead ends acknowledged: "This rabbit hole loops back to [X]"

---

## TECHNICAL ARCHITECTURE

### Data Source
- SQLite megabase.db (4,308 conversations, 397 ideas, 1,825 tagged)
- Ideas table: name, category, maturity, description, conversation_id
- Tags for theme routing
- Summaries for card copy
- Sentiment for emotional context

### Image Pipeline
- Tier 1: Extract DALL-E URLs from conversations.json (already on disk)
- Tier 2: Wikimedia Commons API for public domain historical art
  (search by: "alchemy engraving", "medieval manuscript illumination", etc.)
- Tier 3: AI-generated themed headers using conversation summary as prompt
- Store in static/images/ or serve from CDN
- Fallback: colored gradient with icon per theme

### Routing
- / — Dream Wall (card mosaic)
- /dream/<id> — Expanded dream card
- /theme/<tag> — Rabbit hole view
- /viz — Data visualizations (already built)
- /conversation/<id> — Full conversation (already built)

### Deployment Target
- Static export possible (for GitHub Pages / Netlify)
- Or keep as Flask app for dynamic queries
- Consider: pre-render dream cards as static HTML for speed

---

## PRODUCT VISION (for selling the workflow)

### What You're Selling
Not the website. The PROCESS:
1. Export your social media data (ChatGPT, Facebook, SMS, Gmail, etc.)
2. Run Dreambase ingestion pipeline
3. Get: searchable archive + idea catalog + sentiment analysis + visualizations
4. Browse your own intellectual history as a beautiful artifact

### Target Users
- Prolific LLM users who want to mine their chat history
- Digital humanities researchers
- People going through life transitions who want to understand their own patterns
- Creators who have 1000 ideas scattered across 10 apps

### Differentiator
- Not a backup tool (you already have the data)
- Not an AI wrapper (the value is in YOUR data, not another chatbot)
- It's a MIRROR — "here's what you've been thinking about for 2 years"

---

## 20 QUESTIONS FOR TED

### Visual Identity
1. **Color mood**: The current dark theme is functional. Do you want to keep it dark
   (night sky / observatory vibe), go warm dark (parchment-on-dark / manuscript vibe),
   or something else entirely?

2. **Typography character**: Should headings feel modern-clean (Inter, Helvetica),
   literary-bookish (Georgia, Garamond), or hand-drawn-playful (xkcd's font is
   actually a handwriting font called "xkcd Script")?

3. **Illustration style**: For dream cards, what's the mix?
   a) Mostly historical art (engravings, manuscripts, alchemical diagrams)
   b) Mostly AI-generated themed images
   c) Abstract/geometric (colored shapes encoding data)
   d) Hand-drawn sketch style (xkcd-adjacent)

4. **Mascot or no?** xkcd has stick figures. Do you want a recurring character
   (a little alchemist? a PKD android? a pixel sprite?) or keep it character-free?

### Navigation & UX
5. **Entry point**: When someone first arrives, do they see ALL dreams at once
   (wall of cards), a curated "top 10" highlights, or a single featured dream
   with navigation to browse?

6. **Theme navigation**: Buttons along the top (horizontal tabs), a sidebar tree,
   floating filter pills, or something more unusual (a constellation map you
   click into)?

7. **Depth model**: How deep should rabbit holes go?
   a) 2 levels (theme -> dream card -> conversation)
   b) 3 levels (theme -> sub-theme -> dream card -> conversation)
   c) Infinite (every dream links to related dreams, no fixed hierarchy)

8. **Search prominence**: Is full-text search a primary feature (big search bar)
   or secondary (hidden behind an icon, since browsing is the point)?

### Content Curation
9. **How many dream cards for v1?** Your database has 397 ideas. Do you want:
   a) All 397 as cards (comprehensive but possibly overwhelming)
   b) Top 100 hand-curated (your original vision)
   c) Start with 50, grow over time
   d) Let the user configure a threshold

10. **Curation method**: Will you hand-pick the top 100, or should the system
    auto-rank by some signal (most pages discussed, highest maturity, most
    tag connections)?

11. **Personal vs. public**: Some dreams involve personal topics (therapy, anxiety,
    relationships). Should the product version:
    a) Include everything (radical transparency)
    b) Auto-filter personal tags
    c) Let the user mark cards as private/public

12. **Conversation excerpts**: When showing the source conversation on a dream card,
    how much?
    a) Just the 3-sentence summary
    b) Key quotes (auto-extracted or hand-picked)
    c) Full conversation available behind a click
    d) Chunked deep reading (existing chunk.py output)

### Tone & Humor
13. **Humor density**: xkcd puts a joke in every panel. How much humor do you want?
    a) Witty subtitles on every section (like the viz pane subtitles)
    b) Occasional easter eggs and empty-state jokes
    c) Dedicated "commentary" layer (like xkcd alt-text)
    d) Keep it serious — let the data speak

14. **Voice**: Who's narrating the dream cards?
    a) First person ("I wanted to build a game where...")
    b) Third person observer ("Ted explored the idea of...")
    c) The dream itself speaks ("I am a game that never got built...")
    d) No narrator — just title, tags, summary, data

15. **Self-awareness level**: How much meta-commentary?
    a) "397 ideas, 10 built. The graveyard of ambition."
    b) "Here's what I was thinking about in October 2024."
    c) No meta — just the content
    d) Full xkcd: every section has a self-aware subtitle

### Data & Visualization
16. **Viz integration**: Should visualizations live on their own page (/viz)
    or be embedded within dream cards and theme pages?
    a) Separate page (current design)
    b) Mini-viz on each theme page (e.g., sentiment river for alchemy conversations)
    c) Both — full dashboard + contextual mini-viz
    d) Viz IS the navigation (click a node in the constellation to enter a theme)

17. **Sentiment display**: How prominent should emotional data be?
    a) Subtle (colored dots, background tints)
    b) Explicit (sentiment scores, emotional arc charts)
    c) Narrative ("this conversation started anxious and ended hopeful")
    d) Hidden by default, available on demand

18. **Temporal dimension**: Should the dream wall show WHEN dreams happened?
    a) Yes — arrange cards chronologically
    b) No — arrange by theme/category
    c) Toggle between both views
    d) Timeline as a separate visualization (current approach)

### Product & Distribution
19. **Target format for v1 of the sellable product**:
    a) Open-source Python toolkit (run locally, keep your data private)
    b) Hosted web app (upload your data, get a Dreambase)
    c) Desktop app (Electron/Tauri)
    d) Just the methodology + template (a guide, not software)

20. **What's the one screenshot that sells this?** If you could show ONE view
    to a potential user and have them say "I want that for MY data" — which
    visualization or page is it?
    a) The dream wall with beautiful card illustrations
    b) The topic constellation showing their brain's wiring
    c) The sentiment river showing their emotional arc over years
    d) The sparkline table showing all their themes at a glance
    e) Something else entirely
