# Cost, Efficiency, and Mistakes Analysis

**Where your tokens went, what took too long, what bugs you introduced, and what patterns to break.**

---

## Token Expenditure Map (This Session)

Your session consumed roughly 200K+ output tokens. Here's an estimated breakdown of where they went:

| Activity | Est. Tokens | Produced | Value |
|----------|-------------|----------|-------|
| FAILURE_AUDIT.md | ~3,000 | 12 real findings, 1 real bug | **HIGH** — found the sidecar JSON bug |
| custom_logic.html | ~8,000 | Working showcase page | **MEDIUM** — built from AI assumptions, not data |
| ELDRITCH_SWARM_V2.md | ~5,000 | Plan document | **LOW** — superseded 30 min later by V3 |
| takeaways.html | ~10,000 | 50 takeaways page + JS | **MEDIUM** — content is AI-generated, not mined |
| Pris cross-pollination | ~3,000 | Cross-pollination matrix | **LOW** — good analysis, no execution |
| ELDRITCH_SWARM_V3.md | ~6,000 | Bigger plan document | **LOW** — superseded V2 but also never executed |
| AUDIT_DIMENSIONS.md | ~4,000 | 20 audit dimensions | **LOW** — you had unfixed findings already |
| NARRATIVE_COVERAGE_AUDIT.md | ~3,000 | Coverage gaps identified | **MEDIUM** — real gaps found |
| LLM reading cost analysis | ~3,000 | 4 strategies compared | **MEDIUM** — led to Strategy 2 decision |
| action_map.html | ~8,000 | Interactive website | **VERY LOW** — a todo list as a website |
| ELDRITCH_SWARM_V3 (again) | ~2,000 | Duplicate plan request | **ZERO** — third invocation of same skill |
| TECH_STACK_AND_PROJECTS.md | ~3,000 | Tech stack doc | **LOW** — describes what already exists |
| export_top20.py | ~2,000 | Working export script | **HIGH** — directly enables deep reading |
| SWARM_PROMPT_EVALUATION.md | ~8,000 | Evaluation V1 | **LOW** — too flattering, you rejected it |
| SWARM_PROMPT_EVALUATION_V2.md | ~10,000 | Evaluation V2 | **HIGH** — honest, you accepted it |
| PROMPT_PERFORMANCE_REVIEW.md | ~6,000 | Performance review | **HIGH** — directly requested |
| Subagent research (DB queries, file reads) | ~15,000 | Data for decisions | **MEDIUM** — necessary but some was redundant |

### Token Value Summary

| Category | Tokens | % of Session |
|----------|--------|-------------|
| **High value** (bugs found, working code, honest analysis) | ~30,000 | ~15% |
| **Medium value** (useful analysis, data queries) | ~20,000 | ~10% |
| **Low value** (plans that weren't executed, superseded docs) | ~30,000 | ~15% |
| **Zero/negative value** (duplicate swarm plans, action map website, V1 eval) | ~20,000 | ~10% |
| **Infrastructure** (file reads, subagents, tool overhead) | ~100,000 | ~50% |

**~25% of your productive tokens produced high-value output.** The rest was analysis that didn't lead to action, or plans that were immediately superseded.

---

## Time Waste Analysis

### Waste Pattern 1: The Supersession Trap

You asked for a swarm plan. Then you asked for more features. Then you asked for a new swarm plan incorporating the new features. Then more features. Then another swarm plan.

**Time burned:** The V2 swarm plan took ~5 minutes of AI time. It was obsolete within 10 minutes of conversation when you added the cross-pollination and quality upgrade requests. Then V3 was built. Then you asked for V3 again.

**Three swarm plans were generated. Zero were executed.** Each plan was larger than the last. The V3 plan describes 4 workstreams, 15+ agents, and 3 phases of work. At the rate of one feature per session, this plan represents months of work — but it was generated in a session where the goal was building features, not planning months ahead.

**Fix:** One plan per session. If new requests come in, AMEND the plan (add a row), don't regenerate it. And don't plan more than you can execute in 2-3 sessions.

### Waste Pattern 2: Analysis Stacking

The session generated 7 .md analysis documents:
1. FAILURE_AUDIT.md
2. ELDRITCH_SWARM_V2.md (then V3)
3. AUDIT_DIMENSIONS.md
4. NARRATIVE_COVERAGE_AUDIT.md
5. TECH_STACK_AND_PROJECTS.md
6. SWARM_PROMPT_EVALUATION.md (then V2)
7. PROMPT_PERFORMANCE_REVIEW.md (this document's parent)

These documents describe problems. None of them fix problems. The sidecar JSON bug identified in document #1 is STILL unfixed as of this writing.

**Rule of thumb:** After generating an analysis document, the next prompt should be "Fix the top finding" — not "Generate another analysis document."

### Waste Pattern 3: Building Meta-Tools Instead of Features

Time spent on action_map.html: ~15 minutes of AI time (template creation, CSS, JavaScript, route addition, preview verification).

What action_map.html does: Displays 13 cards in 4 swimlanes with expandable detail panes.

What a text file does: The same thing in 30 seconds.

**The action map is a tool for looking at your todo list. Your todo list is for tracking work on your actual tool (Dreambase). You built a tool to look at the plan to build the tool.** This is three levels of indirection from shipping a feature.

### Waste Pattern 4: Big Numbers Feel Productive

"Give me 50 takeaways" — why 50? Because 50 sounds comprehensive. But 50 AI-generated takeaways are less valuable than 10 takeaways extracted from your actual conversations with evidence links. The number creates an illusion of depth.

"Give me 20 audit dimensions" — why 20? Because 20 sounds thorough. But addressing 3 audit findings is more valuable than identifying 20.

"Read the 20 most important conversations" — the export produced 20 skim files. Will you actually paste all 5 batches into Claude desktop and process the responses? Or will you do 2-3 and move on?

**Fix:** Default to small numbers. 5 takeaways, 3 audit fixes, 5 conversations. You can always ask for more. But smaller batches get completed; larger batches get abandoned.

---

## Bug and Error Analysis

### Bugs Introduced This Session

1. **custom_logic.html conversation IDs are unverified.** The template hardcodes conversation IDs (570, 636, 631, etc.) that were suggested by AI mining, not verified by reading the actual conversations. If any of those IDs don't contain custom logic patterns, the showcase page links to irrelevant content.

   **Status:** Not checked. Not fixed.

2. **takeaways.html takeaways are AI-generated, not evidence-linked.** The 50 takeaways have no conversation_ids linking them to actual evidence. They're plausible but ungrounded. The showcase page claims "What 4,308 conversations taught me" but the content wasn't derived from those conversations.

   **Status:** Not checked. Not fixed. Would require deep-reading specific conversations to verify/rewrite.

3. **action_map.html has no route protection.** The `/action-map` route was added to app.py but there's no navigation link to it from the main site. It's an orphan page accessible only by direct URL. It's also a development planning tool embedded in a public-facing app — conceptually misplaced.

   **Status:** Not fixed.

4. **Sidecar JSON missing try/except (from failure audit).** The failure audit identified that sidecar JSON loading in showcase routes has no error handling. If a `.json` file is missing or malformed, the page crashes with a 500 error.

   **Status:** Identified in the first 10 minutes of the session. Still not fixed after 14 prompts and 7 analysis documents.

5. **FTS5 input not sanitized (from failure audit).** User search input is passed directly to FTS5, which has its own query syntax. A user typing `"` or `NEAR/` could cause query errors.

   **Status:** Identified early. Still not fixed.

### Bugs NOT Introduced (Good Instincts)

- The `IN (?)` parameterization pattern is used correctly everywhere — no SQL injection.
- The new SPECIAL_SHOWCASES entries use the correct dict format matching existing entries.
- The chunk export script handles missing conversations gracefully.
- The export batching respects Claude desktop context limits (48K chars per batch).

### Error During Session

- **"File has not been read yet" error** when editing app.py for the action-map route. The AI tried to edit a file it hadn't recently read. This is a Claude Code tool constraint, not your fault, but it cost one round-trip.

---

## Mistakes Pattern Analysis

### Mistake 1: You treat analysis as progress.

Each analysis document FEELS like you accomplished something. You now know 12 failure modes, 20 audit dimensions, 9 coverage gaps, 4 cost strategies, 50 takeaways, and 37 skill evaluations. But your database has the same bugs it had at the start of the session.

**The test for real progress:** Did the number of known unfixed bugs go DOWN during the session? No — it went UP. You discovered bugs and didn't fix them. The session made your technical debt visible, which is useful, but visibility without action is just anxiety.

### Mistake 2: You escalate scope when you should be narrowing.

Session trajectory:
- Start: "audit the failure modes" (focused)
- 10 min later: "build a showcase page" (new feature)
- 20 min later: "plan a swarm for ALL pending requests" (explosion)
- 30 min later: "build ANOTHER showcase page" (more new features)
- 40 min later: "cross-pollinate ALL pages" (meta-feature)
- 50 min later: "audit 20 MORE dimensions" (more analysis)
- 60 min later: "build an ACTION MAP WEBSITE" (meta-meta-feature)

Each prompt was individually reasonable. The trajectory is a textbook scope explosion. By the end, you're building tools to plan tools to audit the plan for building tools.

**Fix:** Before any new prompt, ask yourself: "Is the previous thing done?" If not, finish it first.

### Mistake 3: You don't distinguish between "interesting" and "important."

The narrative coverage audit is interesting — you might be missing Kabbalah and Shakespeare content. But is it important? Your existing showcases work. Your existing scholars render. The interesting gap (undiscovered content) is less urgent than the important gap (sidecar JSON crashes with 500 errors on missing files).

**Fix:** Rank by consequence, not curiosity. "What breaks if I don't fix this?" A missing sidecar JSON crashes the page. An undiscovered Kabbalah theme... doesn't break anything.

### Mistake 4: You ask the AI to make creative decisions you should make.

The 50 takeaways were written by the AI, not by you. The showcase page designs were chosen by the AI. The action map priorities were set by the AI.

These are YOUR creative decisions:
- What did YOU actually learn from working with LLMs? (not what the AI thinks you learned)
- What should YOUR showcase pages look like? (not what templates the AI defaults to)
- What is YOUR next priority? (not what the AI organizes into swimlanes)

**Fix:** Use the AI for execution, not for creative direction. Tell it WHAT to build; don't ask it to decide what to build.

### Mistake 5: You don't verify AI output against real data.

The custom_logic.html lists 9 extensibility patterns (Hooks, Middleware, Plugins, etc.) — but were these patterns actually verified in the conversation data? The AI generated plausible patterns for software engineering, not patterns confirmed in YOUR conversations.

The takeaways page claims lessons from "4,308 conversations" — but the content was generated from the AI's training data, not extracted from those 4,308 conversations.

**Fix:** Every claim in a showcase page should be traceable to a specific conversation ID and quote. If it can't be, it's an assertion, not evidence.

---

## Your 5 Most Expensive Habits (Token + Time Cost)

| Habit | Cost Per Occurrence | Frequency | Fix |
|-------|-------------------|-----------|-----|
| Requesting duplicate plans (V2→V3→V3 again) | ~10K tokens, 10 min | 2-3x per session | One plan, amend it |
| Building meta-tools (action map, skill registry) | ~15K tokens, 15 min | 1x per session | Use a text file |
| Requesting large number lists (50, 20, 20) | ~8K tokens, 5 min each | 3x per session | Default to 5-7 items |
| Analysis before fixing previous findings | ~5K tokens, 5 min | After every audit | Fix top finding first |
| Not verifying AI content against DB data | ~0 tokens but causes bugs | Every showcase page | Query DB before building |

**Total estimated waste per session: ~40K tokens and ~40 minutes.** That's roughly 20% of a productive session spent on work that doesn't move the project forward.

---

## What a More Efficient Session Looks Like

**Your session (14 prompts, ~2 hours):**
1. Audit → 2. Build page → 3. Plan swarm → 4. Build page → 5. Cross-pollinate → 6. Plan bigger swarm → 7. More audits → 8. Coverage analysis → 9. Cost analysis → 10. Build meta-tool → 11. Set constraint → 12. Plan again → 13. Export data → 14. Evaluate skills

**Optimized session (8 prompts, ~1 hour):**
1. `/audit` → finds sidecar JSON bug + FTS5 issue
2. "Fix the sidecar JSON try/except" → bug fixed
3. "Fix the FTS5 input sanitization" → bug fixed
4. "Build the Custom Logic showcase page. First query the DB for conversations matching these patterns: hooks, middleware, plugins, parsers, pipelines" → data-verified page
5. "Export the 5 largest untagged conversations for deep skim reading" → manageable batch
6. "What are the 3 most impactful features I should build next?" → focused priority list
7. Build feature #1 from that list
8. Verify it works

**Result:** 3 bugs fixed, 1 data-verified showcase page, 5 skims exported, 1 feature built. vs. your session's result: 0 bugs fixed, 2 unverified showcase pages, 7 analysis documents, 1 meta-tool, 20 skims exported (probably too many to process).

---

## The Uncomfortable Summary

You're using Claude Code like a research assistant when you need to use it like a mechanic. Research assistants produce documents. Mechanics fix things. Your Dreambase needs a mechanic right now — the sidecar JSON bug, the FTS5 sanitization, the untagged giants, the unverified showcase content. These are specific, fixable, valuable problems.

The skill system, the swarm plans, the evaluation documents, the action map — these are all ways of thinking about the work instead of doing the work. They're sophisticated and well-structured, which makes them feel more productive than they are.

**Your best prompts are short, specific, and demand action:**
- "STRATEGY 2 remember no API I am on 100/mo mode" — 11 words, set a real constraint
- "Fix the sidecar JSON bug" — would be 6 words that improve your app

**Your worst prompts are long, open-ended, and demand analysis:**
- "give me 20 other ways to audit the functionality and user experience dimensions of every aspect of our web engineering" — produces a document, not a fix

The gap between your analytical capability and your execution rate is the one thing worth fixing.
