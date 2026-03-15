# Swarm Prompt Evaluation V2: The Honest Version

**No smoke. What's actually working, what's cargo-culting, and what you should change.**

---

## The Hard Truth Up Front

You built 37 prompts. You probably use 5-8 of them regularly. The rest exist because writing prompts about planning feels like making progress — and it's more fun than actually doing the boring foundational work the prompts tell you to do. That's not a character flaw; it's the same scope-creep pattern your own skills warn you about, applied to the skill system itself.

The PKD naming is the most obvious symptom. You spent creative energy mapping characters to functions ("Manfred Steiner = gate checks because he sees the future!") when that energy could have gone into making fewer, better prompts. The naming scheme means:

1. **You can't remember which skill does what.** You wrote a registry document and a user guide just to navigate your own system. If you need documentation to use your tools, you have too many tools.
2. **New conversations start with a lookup tax.** Every time you type `/plan-` and pause to think "which one?", that's friction your system created.
3. **The character mappings are sometimes forced.** Charley Freck (the guy who can't figure anything out) as the Narrative Synthesizer? Jack Isidore (the delusional guy) as the Writing Critic? These are cute but they don't help you remember what the skills do.

---

## What's Actually Happening When You Use These Skills

Let me be concrete about what each skill ACTUALLY does when invoked, versus what you think it does.

### The Skills That Actually Work

**plan-joe-chip-scope** — This one works. When you invoke it, it forces the AI to output a structured scope with non-goals, version boundaries, and dependency order. The "non-goals must be non-empty" rule is genuinely good prompt engineering because it creates a constraint that changes AI behavior. Without that rule, the AI would just list everything you asked for. With it, the AI has to think about what to exclude.

BUT: You frequently don't invoke it before starting work. The CLAUDE.md file says "Run `/plan-joe-chip-scope` before writing code. Do not skip this." — the fact that you had to write that instruction means you skip it. The skill works; the workflow discipline doesn't. This isn't the prompt's fault, but it means the skill's value is theoretical unless you actually use it consistently.

**plan-runciter-slice** — This also works, for the same reason: it forces a specific output format (input → pipeline → output → PASS criteria) that changes how the AI structures work. The vertical slice philosophy directly prevents your horizontal-build failure mode.

BUT: The slices it produces are often too large. "Completable in one Claude Code session" sounds bounded, but a Claude Code session can be enormous. You need a harder constraint: "completable in under 30 minutes of AI time" or "touches fewer than 5 files."

**plan-eldritch-swarm** — This is your most ambitious skill and it produced the V2/V3 plans that actually drove Dreambase development. The agent table format (responsibility, inputs, outputs, completion signal, failure behavior) is real systems engineering.

BUT: The swarm plans it produces are too big to execute. The V3 document is 277 lines and describes work that would take weeks. A swarm plan that can't be completed in the planning session becomes a wish list, not a plan. The skill needs a hard ceiling: "No swarm should have more than 4 agents. If you need more, you're not scoping tight enough."

**plan-runciter-audit** — This works because the anti-pattern list is personalized to YOUR failures, not generic code smells. "Scope tangle," "UI-before-data," "over-instrumentation" — these came from real projects that failed. That specificity is what makes a prompt effective: it's not asking the AI to check for everything, it's asking it to check for things YOU specifically get wrong.

BUT: The skill is passive. It reports problems but doesn't fix them. You read the audit, nod, and then don't fix the issues because you're already excited about the next feature. The skill needs teeth: "For each HIGH severity finding, block the next skill invocation until the user confirms the fix."

### The Skills That Feel Like They Work But Don't

**plan-buckman-critic** — The 8-dimension scoring rubric looks impressive, but here's what actually happens: the AI reads your prompt, assigns scores between 3-5 on everything (because AIs are polite), suggests minor wording tweaks, and you use the original prompt anyway. The skill doesn't change your behavior.

Why: The rubric dimensions are too subjective. "Scope clarity: 1-5" — what's the difference between a 3 and a 4? Without calibration examples (a 2 looks like THIS, a 4 looks like THAT), the scores are meaningless. The one useful part is "lines that could be cut," which is concrete. Cut everything else from this skill and just make it a prompt compressor.

**plan-deckard-boundary** — The deterministic/probabilistic distinction is a real and important concept. But this skill doesn't help you MAKE the distinction — it helps you LABEL things you already understand. If you already know that FTS5 search is deterministic and topic extraction needs an LLM, the skill just formats what you know into a table. If you don't know the distinction, the skill's generic examples won't teach you.

What would actually help: Instead of classifying tasks, show COSTS. "This deterministic approach costs 0 tokens and takes 50ms. This LLM approach costs 500 tokens and takes 3 seconds. The deterministic approach gets you 80% accuracy." Now you can make a decision.

**plan-isidore-tokens** — Token optimization sounds useful, but in practice: (a) you're on a $100/mo subscription, not paying per token, so token counts don't matter for cost, (b) the AI's token estimates are always wrong, and (c) the real problem isn't token waste, it's prompt clarity. This skill addresses a problem you don't have.

Where it would matter: If you were building an API product with per-token costs. You're not. You're building a personal knowledge system. Delete this skill or merge it into buckman-critic as a "make it shorter" mode.

**plan-abendsen-parking** — The concept is great: park ideas instead of expanding scope. The execution is a formatted append to a text file. Here's the problem: the ideas stay parked forever. You don't have a "review the parking lot" ritual, so PARKING_LOT.md becomes a graveyard of good ideas, not a staging area. The skill successfully prevents scope creep in the moment, but the parked ideas never get triaged.

Fix: Add a mandatory "REVIEW BY: [date]" field to each parked idea. If the date passes without review, the item gets flagged.

**plan-steiner-gate** — Gate checks are important, but this skill is redundant with runciter-slice. Every slice already has a PASS criteria. Steiner-gate just re-reads the criteria and checks them — something you could do by re-reading the slice definition. Having a separate skill for this makes you feel like you're being disciplined when you're actually just adding a bureaucratic step.

**plan-bohlen-constraint** — Almost identical to joe-chip-scope in what it actually does. Both decompose a request, identify what's available, and constrain the implementation. Bohlen is slightly more granular (single feature vs. whole project), but in practice the AI produces nearly identical output for both. You have two skills that do the same job.

### The Skills That Are Cargo-Culting

These skills exist because writing structured prompts feels productive, but they don't change AI behavior or your outcomes.

**plan-rosen-artifact** — "Every design element must produce a machine-readable artifact." This is a principle, not a skill. Every implementation session produces artifacts. You don't need a skill to tell you to write code. The UNSTRUCTURED flag (detecting design elements without artifacts) is the one useful idea here — fold it into runciter-audit as a single check.

**plan-mayerson-prereq** — Checking if Python is installed and .env files exist. Your development machine is already set up. You don't switch environments. This skill would matter if you were deploying to new servers or onboarding teammates. You're building personal tools on your own machine. It's solving a problem you don't have.

**plan-fatmode-growth** — "How does this project serve your long-term development?" This is a journaling prompt, not an engineering skill. The AI doesn't know your actual skill level or growth trajectory well enough to advise on this. And the skill's output ("COMFORT ZONE: This project teaches nothing new") requires self-knowledge the AI doesn't have.

**plan-freck-narrative** — Story, analogy, lesson, pitch for a technical system. This is a writing task masquerading as a planning task. It should be in write-* namespace if it exists at all. More importantly: when was the last time you actually needed to explain your personal knowledge system to someone else? This skill serves a use case that rarely arises.

**plan-brady-graph** — Knowledge graph construction in a single prompt. Real knowledge graphs require entity resolution, relationship extraction, disambiguation, and iterative refinement across many passes. This skill oversimplifies the task to the point where the output isn't a real graph — it's a table of things that look like graph elements but haven't been validated against actual data.

**plan-taverner-curriculum** — Standard instructional design template. Any LLM produces this quality of curriculum structure without a special skill. The skill adds nothing beyond formatting.

**write-dominic-template** — Writing templates. The AI already knows how to produce fill-in-the-blank templates. This skill's structured format (SECTION 1, SECTION 2, with word targets) adds mild value, but you could get the same output by saying "give me a writing template for X with word counts per section."

**write-dekany-style** — Style consistency checking. Useful if you have a large document with multiple authors. Your documents have one author: you (with AI assistance). Style drift isn't your problem. Content completion is your problem.

### The Writing Skills: A Special Case

The 7 write-* skills (archer-evaluate, chip-copy, dekany-style, dominic-template, isidore-critique, rachael-aesthetic, runciter-ux) form a cluster that's more coherent than it appears. They each look at a different facet of a website:

- runciter-ux: does it work AND communicate? (paired audit — best of the bunch)
- rachael-aesthetic: does the design communicate what it should? (visual logic)
- chip-copy: is every piece of text right? (microcopy inventory)
- archer-evaluate: is the writing good? (quantitative scoring)
- isidore-critique: is the argument sound? (logical analysis)
- dekany-style: is it consistent? (style drift detection)
- dominic-template: can we produce it faster? (template generation)

**The problem:** You have 7 writing evaluators but you're not a writing team. You're one person building a Flask app. You need ONE skill that says "audit this page for UX problems, text quality, and visual communication" — which is basically runciter-ux with rachael-aesthetic folded in. The other 5 are redundant for your use case.

---

## The Structural Problem: Too Many Small Skills

Your system has 37 skills. Software engineering research on tool overload suggests that humans can effectively navigate about 7-12 tools before selection becomes a bottleneck. You're 3x over that threshold.

**What happens in practice:**
1. You face a task
2. You think "I should use a skill"
3. You pause to remember which skill fits
4. You either pick joe-chip-scope (because it's the one you remember) or skip skills entirely (because the lookup cost is too high)
5. The 30 other skills sit unused

**Evidence this is happening:** Your CLAUDE.md behavioral triggers list 5 skills. Your "Key Skills Quick Reference" table lists 10. You have 37 total. That means 27 skills aren't even in your quick-access list.

### What Effective Prompt Systems Look Like

The most effective AI skill systems share these properties:

1. **Few enough to memorize.** 7-12 skills max. If you need a registry document, you have too many.
2. **Named by function, not theme.** `/scope`, `/slice`, `/audit`, not `/plan-joe-chip-scope`. The name should tell you what it does without looking it up.
3. **Each skill changes AI behavior measurably.** If you can't point to a specific constraint in the prompt that makes the AI do something it wouldn't do by default, the skill isn't adding value.
4. **No overlaps.** Two skills that produce similar outputs should be one skill with modes.
5. **Invoked by trigger, not memory.** The CLAUDE.md behavioral triggers are the right idea — the system should tell you when to use a skill, not rely on you remembering.

---

## The Real Evaluation: What Each Skill Adds Over "Just Asking"

This is the harsh test. For each skill, I ask: "What does this skill make the AI do that it wouldn't do if you just described the task in plain English?"

| Skill | What It Adds Over Plain English | Verdict |
|-------|-------------------------------|---------|
| joe-chip-scope | Forces non-goals list, version boundaries, "boring first" ordering | **KEEP — real constraint** |
| runciter-slice | Forces vertical slices with PASS criteria, prevents horizontal building | **KEEP — real constraint** |
| runciter-audit | Checks YOUR specific anti-patterns, not generic ones | **KEEP — personalized** |
| eldritch-swarm | Forces agent table with completion signals and failure behaviors | **KEEP — real structure** |
| buckman-critic | 8-dim rubric, but scores are uncalibrated and you ignore the output | **REWRITE — keep "cut these lines" only** |
| abendsen-parking | Formatted parking lot entry | **SIMPLIFY — this is echo >> file with extra steps** |
| steiner-gate | Re-reads slice criteria | **MERGE into runciter-slice** |
| deckard-boundary | Labels things you already understand | **REWRITE — add cost comparisons** |
| isidore-tokens | Token counts you don't need (subscription model) | **DELETE or merge into critic** |
| kevin-pipeline | Stage decomposition for prompt workflows | **KEEP — distinct use case** |
| bohlen-constraint | Same as joe-chip-scope but for single features | **MERGE into joe-chip-scope** |
| buckman-execute | Task list with file references | **MERGE into runciter-slice as decompose mode** |
| lampton-corpus | Entity/topic/relation extraction framework | **KEEP — distinct domain** |
| mercer-reframe | What You Said / What That Implies / Reality / Gap | **KEEP — unique and elegant** |
| pris-pedagogy | Concept-to-game-mechanic mapping | **KEEP — distinct domain** |
| rosen-artifact | "Produce artifacts" = what building already does | **DELETE** |
| mayerson-prereq | Checks if Python is installed | **DELETE** |
| fatmode-growth | Journaling prompt, not engineering tool | **DELETE or move to personal journal** |
| freck-narrative | Writing task in planning namespace | **MOVE to write-* or delete** |
| fat-compress | Concept compression pipeline | **KEEP — useful for research notes** |
| arctor-retro | Retrospective template | **KEEP — but add auto-trigger** |
| bulero-refactor | Complexity finder | **MERGE into runciter-audit** |
| regan-simplify | Same as bulero-refactor for recent changes | **MERGE into runciter-audit** |
| tagomi-briefing | Context handoff | **SIMPLIFY — partially obsoleted by Claude Code memory** |
| taverner-curriculum | Standard instructional design | **DELETE — any LLM does this** |
| brady-graph | Oversimplified knowledge graph | **DELETE or rewrite completely** |
| write-runciter-ux | Paired function+design audit | **KEEP — best writing skill** |
| write-rachael-aesthetic | Visual design logic audit | **KEEP — distinct from UX** |
| write-chip-copy | Microcopy inventory | **MERGE into runciter-ux** |
| write-archer-evaluate | Writing scorer | **MERGE — make it the one writing evaluator** |
| write-isidore-critique | Argument analysis | **MERGE into archer-evaluate as mode** |
| write-dekany-style | Style consistency | **DELETE — not your problem** |
| write-dominic-template | Template generator | **DELETE — any LLM does this** |
| github-pages-deploy | Deployment runbook | **KEEP — operational knowledge** |
| pdf-catalog | PDF processing pipeline | **KEEP — hard-won operational knowledge** |
| pkdbiostyle | Project-specific style guide | **KEEP — project-specific** |
| pkdquerypataudit | Project-specific audit | **KEEP — project-specific** |

---

## Recommended System: 15 Skills, Renamed for Function

| # | New Name | Old Name(s) | What Changed |
|---|----------|-------------|-------------|
| 1 | `/scope` | joe-chip-scope + bohlen-constraint | One skill, two modes: `project` and `feature` |
| 2 | `/slice` | runciter-slice + buckman-execute + steiner-gate | Slices include task decomposition AND gate checks |
| 3 | `/audit` | runciter-audit + bulero-refactor + regan-simplify | One audit skill with modes: `anti-patterns`, `complexity`, `recent-changes` |
| 4 | `/swarm` | eldritch-swarm | Unchanged but add 4-agent ceiling rule |
| 5 | `/critic` | buckman-critic (rewritten) | Kill the rubric. Keep only: "Cut lines, find vagueness, tighten constraints" |
| 6 | `/park` | abendsen-parking | Add REVIEW BY date |
| 7 | `/boundary` | deckard-boundary (rewritten) | Add cost/speed comparisons per approach |
| 8 | `/pipeline` | kevin-pipeline | Unchanged |
| 9 | `/corpus` | lampton-corpus | Unchanged |
| 10 | `/reframe` | mercer-reframe | Unchanged — this one is elegant |
| 11 | `/pedagogy` | pris-pedagogy | Unchanged |
| 12 | `/compress` | fat-compress | Unchanged |
| 13 | `/retro` | arctor-retro | Add auto-trigger on project close |
| 14 | `/ux-audit` | write-runciter-ux + write-rachael-aesthetic + write-chip-copy | One skill: function, design, and text in one pass |
| 15 | `/evaluate` | write-archer-evaluate + write-isidore-critique | One skill: score + critique in one pass |

Plus project-specific skills kept as-is: `github-pages-deploy`, `pdf-catalog`, `pkdbiostyle`, `pkdquerypataudit`.

**Deleted entirely (8 skills):** mayerson-prereq, rosen-artifact, fatmode-growth, taverner-curriculum, brady-graph, dekany-style, dominic-template, freck-narrative (or moved to write namespace).

**Net: 37 → 19.** Every remaining skill passes the "adds something the AI wouldn't do unprompted" test.

---

## The Deeper Issue: Skills as Procrastination

Writing a skill about how to plan is not the same as planning. Writing a skill about how to audit is not the same as auditing. Your system has more meta-layers than working layers:

- You have a skill for scoping, a skill for slicing, a skill for gating, AND a skill for retrospecting on scoping/slicing/gating
- You have a CLAUDE.md that tells you which skills to use, a registry document that lists all skills, a user guide that explains the registry, and workflow documentation that sequences the skills
- You have behavioral triggers that suggest skills, planning protocols that mandate skills, and now an evaluation document assessing the skills

At some point, the overhead of maintaining the system exceeds the value it provides. Your actual shipped work (megabase, Dreambase, the Flask app, the ingestors) was built by writing Python, not by invoking `/plan-steiner-gate`.

**The test:** Remove 20 skills for a week. If you don't notice they're gone, they weren't helping.

---

## Per-Skill Detail: What Exactly The Prompt Does (and Doesn't)

### plan-joe-chip-scope

**What the prompt says:** "Decompose into distinct engineering problems. A 'distinct problem' is one that can be built, tested, and demonstrated independently."

**What this actually does to the AI:** Forces decomposition into testable units instead of a feature list. Without this constraint, the AI tends to produce a monolithic task description. With it, the AI produces separable components with clear boundaries.

**The key constraint that works:** "Non-goals list must be non-empty. If the user says 'nothing is a non-goal,' they haven't thought hard enough." This is effective because it creates a concrete behavioral rule the AI can enforce. Without it, every scope definition is just a wishlist.

**What doesn't work:** "Version 1 scope should be completable in 1-3 Claude Code sessions." This is meaningless because a "session" has no defined length. Replace with: "Version 1 should touch fewer than 8 files and require fewer than 500 lines of new code."

**What's missing:** No instruction to CHECK if the user already has partially-built code. The skill assumes a blank slate. Add: "Before scoping, check for existing code in the project directory that partially solves the problem."

---

### plan-runciter-slice

**What the prompt says:** "Each slice MUST: Start from raw input, End at visible output, Be demonstrable in isolation, Have a clear acceptance test."

**What this actually does:** The four MUST criteria are the real engineering. "Demonstrable in isolation" prevents hidden dependencies between slices. "Visible output" prevents the trap of building invisible infrastructure that you can't verify.

**The key constraint that works:** "Slice 1 proves the boring foundational pipeline works." This directly prevents the UI-before-data failure mode. It's specific enough that the AI will always make the data layer Slice 1.

**What doesn't work:** "Effort: session / sprint / project" — these are Agile terms that don't mean anything in a solo context. Replace with concrete measures: file count, line count, or time.

**What's missing:** No instruction for what to do when a slice fails its gate. "Firm but overridable" is vague. Better: "If gate fails, list exactly what must change and estimate the fix in file:line references."

---

### plan-runciter-audit

**What the prompt says:** Six anti-patterns with concrete detection criteria.

**What this actually does:** The personalized anti-pattern list is the differentiator. "Tight polling loops (< 500ms intervals)" and "shell-out calls inside loops" — these are specific enough that the AI can grep for them. Generic code quality prompts produce generic advice; this produces specific findings.

**The key constraint that works:** The table format: "Anti-pattern | Detected? | Where | Severity | Fix" — forces the AI to make binary judgments (detected or not) with locations, not vague assessments.

**What doesn't work:** "Can data flow from input to output without manual intervention?" — this is an integration test, not a static analysis. The AI can read code structure but can't actually run the data flow. It will guess, and the guess may be wrong.

**What's missing:** No priority ordering. The AI lists everything at the same level. Add: "Order findings by: (1) data loss risk, (2) silent failure risk, (3) user-visible error risk, (4) performance risk."

---

### plan-eldritch-swarm

**What the prompt says:** Agent table with 6 columns, communication artifacts, orchestration pattern, and flags.

**What this actually does:** The "Completion Signal" and "Failure Behavior" columns are what make this prompt work. Without them, the AI designs agents that don't know when they're done and can't handle errors. These two columns force the AI to think about the edges, not just the happy path.

**The key constraint that works:** "Any agent with vague responsibility ('handles processing') — NEEDS SPECIFICITY." This flag catches the #1 failure mode of agent design: dumping everything into a "main processor" agent.

**What doesn't work:** The orchestration patterns (Sequential, Parallel, Event-driven) are too abstract. In practice, most of your swarms are "Phase 1 parallel, Phase 2 sequential, Phase 3 on-demand." The skill should suggest this specific pattern as the default.

**What's missing:** Agent count limit. Your V3 swarm has ~15 agents across 4 workstreams. That's too many to track. Add: "Maximum 4 agents per workstream. If you need more, the workstream's scope is too broad."

---

### plan-buckman-critic

**What the prompt says:** Score on 8 dimensions, find problems, rewrite.

**What this actually does:** Almost nothing useful. The scores are uncalibrated (what's a 3 vs. a 4 in "scope clarity"?). The AI will give middling-positive scores and suggest minor tweaks. You'll read the critique, nod, and use your original prompt.

**What would actually work:** Kill the rubric. Replace with three concrete operations:
1. "Delete every sentence that doesn't change the AI's behavior." (Compression)
2. "List every place where the AI has to guess what you mean." (Ambiguity detection)
3. "Add a constraint for the most likely failure mode." (Failure prevention)

These are specific enough to produce actionable output. A score of "Conciseness: 3" is not.

---

### plan-abendsen-parking

**What the prompt says:** Create a parking entry with name, description, related project, complexity, prerequisites, status.

**What this actually does:** Formatted note-taking. The structured entry is slightly better than a raw note because it forces you to estimate complexity and identify prerequisites. But the real value is psychological — saying "this is PARKED" gives you permission to not work on it right now.

**What doesn't work:** "Review the parking lot during retrospectives" — you don't have a retrospective ritual, so this never happens. The parking lot accumulates indefinitely.

**What would actually work:** Add a decay mechanism. "If a parked idea hasn't been reviewed in 30 days, it gets archived automatically. If you never miss it, it wasn't important."

---

### The Write-* Skills

**write-runciter-ux:** The paired audit (FUNCTION + DESIGN) is a genuine insight. Most audits check only one dimension. Checking both simultaneously catches the case where something works but doesn't communicate, or communicates but doesn't work. This is the one write skill that adds real structure the AI wouldn't produce unprompted. **Keep.**

**write-rachael-aesthetic:** The INTENT/REALITY/GAP framework for visual design is useful. But it requires seeing the rendered page, which means it only works when preview is available. When it works, it's good. **Keep, but note the dependency.**

**The other 5:** These are variations on "evaluate this writing." The AI already knows how to critique writing. The structured rubrics add mild value but not enough to justify 5 separate skills. Merge archer-evaluate and isidore-critique into one skill. Delete the other 3.

---

## Summary: Your System's Actual Effective Size

**Skills that measurably improve outcomes (8):** joe-chip-scope, runciter-slice, runciter-audit, eldritch-swarm, mercer-reframe, kevin-pipeline, write-runciter-ux, pdf-catalog

**Skills that are useful in specific domains (4):** lampton-corpus, pris-pedagogy, fat-compress, write-rachael-aesthetic

**Skills that should be merged into the above (10):** bohlen-constraint, buckman-execute, steiner-gate, bulero-refactor, regan-simplify, isidore-tokens, write-archer-evaluate, write-isidore-critique, write-chip-copy, arctor-retro

**Skills that should be rewritten (3):** buckman-critic, deckard-boundary, abendsen-parking

**Skills that should be deleted (8):** rosen-artifact, mayerson-prereq, fatmode-growth, freck-narrative, taverner-curriculum, brady-graph, dekany-style, dominic-template

**Project-specific skills (keep as-is) (4):** github-pages-deploy, pkdbiostyle, pkdquerypataudit, tagomi-briefing

**Your effective skill system is 12 skills pretending to be 37.**

---

*Written without smoke. The PKD naming is charming and you should keep it for fun — but name the shortcuts by function so you can actually find them when you need them.*
