# Swarm Prompt Evaluation: The PKD Skill System

**37 skills assessed across 7 dimensions. Honest verdict on what works, what's redundant, and what's missing.**

---

## Evaluation Methodology

Each skill scored 1-5 on seven dimensions:

| Dimension | What It Measures |
|-----------|-----------------|
| **Clarity** | Can the AI execute this unambiguously on first read? |
| **Specificity** | Does it prescribe concrete output format vs. vague goals? |
| **Scope Control** | Does it stay in its lane, or invite drift? |
| **Reusability** | How often would you realistically invoke this? |
| **Complementarity** | Does it play well with other skills in the system? |
| **Actionability** | Does it produce something immediately useful? |
| **Uniqueness** | Could another skill already do this? |

**Score key:** 5 = excellent, 4 = strong, 3 = adequate, 2 = weak, 1 = broken or redundant

---

## Tier 1: The Essential Core (Score 28+/35)

These are the load-bearing walls of your system. Every project benefits from them.

### 1. plan-joe-chip-scope — **32/35**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity | 5 | Crystal-clear steps: decompose, classify, freeze |
| Specificity | 5 | Mandatory non-goals list, version tiers, dependency order |
| Scope Control | 5 | *This IS scope control.* Self-referential excellence |
| Reusability | 5 | Every project, every time |
| Complementarity | 5 | Feeds directly into runciter-slice, abendsen-parking, steiner-gate |
| Actionability | 4 | Diagnostic only — correct choice, but means a second skill is needed to start |
| Uniqueness | 3 | Some overlap with bohlen-constraint (constraint articulation vs. scope freezing) |

**Verdict:** The single most important skill in the system. The "boring foundational work comes first" rule alone has probably saved you dozens of hours. The rule that "non-goals must be non-empty" is genuinely clever — it forces the uncomfortable conversation early.

**One improvement:** Add a "SCOPE SIZE" estimate (tiny/small/medium/large) to the output format so downstream skills can calibrate effort.

---

### 2. plan-runciter-slice — **31/35**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity | 5 | "Each slice goes from raw input to visible output" — impossible to misunderstand |
| Specificity | 5 | PASS-when criteria, dependency chains, effort estimates |
| Scope Control | 5 | The gate behavior is genuine scope enforcement |
| Reusability | 4 | Every multi-session project. Less useful for quick fixes |
| Complementarity | 5 | Perfect handoff from joe-chip-scope, feeds steiner-gate |
| Actionability | 4 | "Ready to start Slice 1?" is a strong call to action |
| Uniqueness | 3 | Some overlap with buckman-execute (both produce ordered task lists) |

**Verdict:** The vertical slice philosophy directly addresses your documented failure mode of building horizontally. "Slice 1 proves the boring foundational pipeline works" is the single most important sentence in any planning prompt. This skill has probably prevented more failures than any other.

**One improvement:** Add a "PROOF ARTIFACT" field to each slice — what file or screenshot proves the slice works. Makes gate verification concrete.

---

### 3. plan-runciter-audit — **30/35**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity | 5 | Six named anti-patterns with specific detection criteria |
| Specificity | 5 | "Tight polling loops (< 500ms)" — concrete thresholds, not vibes |
| Scope Control | 4 | Stays diagnostic. Minor risk: the failure mode list could grow unbounded |
| Reusability | 4 | Every project milestone. The /failure-audit shortcut makes it even more accessible |
| Complementarity | 4 | Feeds into arctor-retro (audit findings become retrospective inputs) |
| Actionability | 4 | Table format with severity + suggested fix is immediately useful |
| Uniqueness | 4 | Distinct from bulero-refactor (audit vs. refactor) though they share DNA |

**Verdict:** This skill is personalized to YOUR failure modes — scope tangle, UI-before-data, over-instrumentation, resource spirals. That makes it more effective than a generic code quality checker. The anti-pattern list reads like a post-mortem of real projects.

**One improvement:** Add a "DECAY RATE" dimension — how quickly does this system accumulate technical debt? Some architectures rot faster than others.

---

### 4. plan-buckman-critic — **30/35**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity | 5 | 8 scoring dimensions, all with specific questions |
| Specificity | 5 | "Lines that could be cut," "scope tangles," "vague adjectives" — actionable |
| Scope Control | 5 | Explicitly does NOT execute the prompt |
| Reusability | 5 | Every significant prompt benefits from review |
| Complementarity | 4 | Pairs with isidore-tokens (critic reviews quality, isidore reviews efficiency) |
| Actionability | 3 | Produces a revised prompt but requires user decision on which to use |
| Uniqueness | 3 | Overlaps with isidore-tokens on "conciseness" dimension |

**Verdict:** The 8-dimension scoring rubric is well-chosen. "Scope clarity" and "exit criteria" are the two dimensions most prompts fail on, and putting them first is correct prioritization. The rewrite-then-ask pattern is respectful of user agency.

**One improvement:** Add a "PROMPT TYPE" classification (instruction, persona, few-shot, chain-of-thought, system prompt) to tailor the critique. Different prompt types have different failure modes.

---

### 5. plan-eldritch-swarm — **29/35**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity | 4 | Clear agent table format, but "orchestration pattern" section is underspecified |
| Specificity | 5 | Agent table with 6 columns. Communication artifact format. Flag criteria |
| Scope Control | 3 | The swarm concept inherently invites scope expansion — "one more agent" |
| Reusability | 4 | Any multi-component project. The Dreambase swarm plans prove it works |
| Complementarity | 4 | Consumes joe-chip-scope output, produces buckman-execute input |
| Actionability | 5 | Output is directly implementable as parallel work streams |
| Uniqueness | 4 | Nothing else in the system does multi-agent design |

**Verdict:** The most ambitious skill in the system and the one that produced the V2/V3 swarm documents. The flag criteria ("vague responsibility," "overlapping scope," "bottleneck risk," "no completion signal") are excellent defensive checks. The risk is that swarm plans grow without bound — the V3 document is 277 lines and still growing.

**One improvement:** Add a "SWARM SIZE LIMIT" rule — e.g., "If more than 6 agents, split into sub-swarms with a coordinator." Also add a "COST PER AGENT" estimate to prevent over-engineering.

---

## Tier 2: Strong Supporting Skills (Score 23-27/35)

These are situationally excellent. Not every project needs them, but when you do, they're sharp.

### 6. plan-deckard-boundary — **27/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 4 | 4 | 4 | 3 | 4 |

**Verdict:** The deterministic/probabilistic boundary map is the right abstraction for LLM-augmented systems. The "WASTE" and "DANGER" flags are appropriately alarming. Directly relevant to Dreambase where VADER (deterministic) and LLM summaries (probabilistic) coexist.

**Weakness:** The classification examples are generic. Adding project-specific examples (e.g., "FTS5 keyword search = deterministic, topic extraction from conversation text = probabilistic") would make it more immediately useful.

---

### 7. plan-abendsen-parking — **27/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 5 | 4 | 5 | 4 | 5 | 2 | 2 |

**Verdict:** Conceptually perfect — it exists to PREVENT scope creep, which is your #1 failure mode. The "SCOPE WARNING" trigger is well-designed. The weakness is that it's essentially a formatted append to a text file, which feels over-engineered for what `echo >> PARKING_LOT.md` could do.

**Weakness:** Low actionability — parking an idea doesn't move any project forward. But that's by design, and it's the right design.

---

### 8. plan-steiner-gate — **27/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 5 | 3 | 5 | 3 | 3 |

**Verdict:** The gate check mechanism is the enforcement arm of runciter-slice. Without it, slices are aspirational; with it, they're contractual. "Firm but overridable" is the right policy — rigid gates cause workarounds, flexible gates cause drift.

**Weakness:** Overlaps with runciter-slice's own gate behavior. These could be merged: have runciter-slice include a `GATE CHECK` section in its output rather than needing a separate skill.

---

### 9. plan-isidore-tokens — **26/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 5 | 4 | 3 | 4 | 3 | 3 |

**Verdict:** The waste taxonomy (redundant instructions, inline context, verbose explanations, overflow risks) is well-organized. The "SAVINGS: ~X% reduction" output format is satisfying and motivating. Good pairing with buckman-critic.

**Weakness:** Token counting is approximate at best in a skill prompt. The real value is the compression heuristics, not the numbers. Also overlaps with buckman-critic's "conciseness" dimension.

---

### 10. plan-kevin-pipeline — **26/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 5 | 4 | 3 | 3 | 4 | 3 |

**Verdict:** The stage decomposition format (input/prompt template/output format/validation/failure mode) is excellent engineering. "Each stage does ONE transformation" is a powerful constraint. The checkpoint concept prevents wasted work.

**Weakness:** Somewhat redundant with runciter-slice for multi-step workflows. The distinction is thin: runciter-slice is for code projects, kevin-pipeline is for prompt workflows. This distinction could be made more explicit.

---

### 11. plan-bohlen-constraint — **26/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 5 | 4 | 3 | 3 | 4 | 3 |

**Verdict:** The AVAILABLE/UNAVAILABLE/CONSTRAINTS/THEREFORE framework is clean and forces reality-checking. "FIRST PROOF" is a great addition — it connects constraint analysis directly to action.

**Weakness:** Overlaps significantly with joe-chip-scope. Both decompose features and identify constraints. Bohlen is more granular (single feature), Joe Chip is more strategic (whole project). The boundary between them needs sharpening.

---

### 12. plan-buckman-execute — **26/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 3 | 4 | 4 | 4 | 3 |

**Verdict:** The task decomposition rules are practical: one session per task, verifiable results, specific file references. "Ready to start Task 1?" bridges planning to doing.

**Weakness:** Significant overlap with runciter-slice. Both produce ordered task lists with dependencies. Buckman-execute is more granular (file-level), runciter-slice is more strategic (slice-level). Consider: buckman-execute could be the INSIDE of a slice, not an alternative to slices.

---

### 13. plan-lampton-corpus — **25/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 3 | 3 | 4 | 3 | 4 |

**Verdict:** Well-suited to your research corpus work (PKD, alchemy texts, Marxism). The entity/topic/relation extraction framework is standard but well-structured. COVERAGE GAPS detection is valuable.

**Weakness:** The "RECOMMENDED PIPELINE" output tries to be both analytical and prescriptive. Pick one: either analyze the corpus, or design the processing pipeline. Trying to do both makes the output unfocused.

---

### 14. plan-mercer-reframe — **25/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 5 | 4 | 4 | 3 | 3 | 3 | 3 |

**Verdict:** The "WHAT YOU SAID / WHAT THAT IMPLIES / WHAT'S ACTUALLY HAPPENING / THE GAP" structure is genuinely elegant. Forces the AI to articulate the mental model before correcting it. "Respectful and curious, not corrective" is the right tone guidance.

**Weakness:** Hard to invoke proactively — you usually don't know your mental model is wrong until something breaks. This is more useful as a diagnostic after confusion than a preventive tool.

---

### 15. plan-pris-pedagogy — **25/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 3 | 3 | 3 | 4 | 4 |

**Verdict:** The concept→game mechanic mapping table is clever and well-curated (MTG draft for risk assessment, roguelikes for decision trees). The difficulty progression format is immediately usable for Draft Academy content.

**Weakness:** The "if no game mechanic fits, say so" escape valve is good, but the mechanic table is narrow. Real pedagogical game design often uses mechanics not in this list (negotiation, hidden information, asymmetric powers).

---

## Tier 3: Situational / Niche (Score 19-22/35)

Useful for specific project types but not daily drivers.

### 16. plan-tagomi-briefing — **24/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 4 | 3 | 3 | 3 | 3 |

**Verdict:** Solves a real problem (context handoff between conversations). The output format is good. But in practice, CLAUDE.md + memory files do most of this automatically now.

**Weakness:** Partially obsoleted by Claude Code's built-in memory system. The "MY LEVEL" field is the most unique part — consider keeping only that as a standalone prompt.

---

### 17. plan-arctor-retro — **23/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 4 | 2 | 3 | 3 | 3 |

**Verdict:** The root cause distinction ("skipped to UI" is a symptom; "excitement-driven prioritization" is a root cause) is sharp and insightful. The cross-project pattern detection is the most valuable part.

**Weakness:** Retrospectives are hard to invoke — you need to be in the right mood, and by the time a project is done, you've moved on. Consider: auto-trigger this skill when closing a project, not as an on-demand tool.

---

### 18. plan-bulero-refactor — **23/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 4 | 3 | 3 | 3 | 2 |

**Verdict:** Good complexity smell catalog (premature abstraction, imaginary problems, missed simplification, instrumentation bloat). "LINES SAVED" estimate is motivating.

**Weakness:** Significant overlap with plan-regan-simplify and plan-runciter-audit. All three look at code quality from slightly different angles. Consider merging bulero-refactor into runciter-audit as a "refactoring recommendations" section.

---

### 19. plan-fat-compress — **23/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 3 | 3 | 3 | 3 | 3 |

**Verdict:** The CONCEPT→DEFINITION→EXAMPLE→ARTIFACT→TEACHING HOOK pipeline is well-structured. "COMPRESSION RATIO" output is satisfying. Good for converting your research notes into Dreambase content.

**Weakness:** The line between "compressing concepts" and "writing summaries" is fuzzy. The TEACHING HOOK field tries to make it pedagogical, but that's plan-pris-pedagogy's job.

---

### 20. plan-rosen-artifact — **22/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 3 | 4 | 3 | 3 | 3 | 3 | 3 |

**Verdict:** The principle "every design element must produce a machine-readable artifact" is sound. The format list (JSON schemas, TypeScript interfaces, config files) is practical.

**Weakness:** This skill is a philosophy statement dressed as a tool. "Generate artifacts from designs" is what every implementation session does already. The unique value is the UNSTRUCTURED flag, which could be a single check in runciter-audit instead of a standalone skill.

---

### 21. plan-mayerson-prereq — **22/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 5 | 2 | 3 | 2 | 2 |

**Verdict:** The prerequisites checklist is thorough (runtimes, tools, services, env vars, files). The PASS/FAIL table is clean.

**Weakness:** This is largely automated by package managers and CI systems. Running `pip install -r requirements.txt` and checking for errors does 90% of this. The unique value is catching missing .env files and API keys, which could be a pre-flight check in joe-chip-scope instead.

---

### 22. plan-freck-narrative — **22/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 4 | 2 | 2 | 3 | 3 |

**Verdict:** The four output types (STORY, ANALOGY, LESSON, PITCH) are well-differentiated. "The analogy must hold at least 3 structural points" is a good quality bar.

**Weakness:** Low reusability for daily coding work. This is a content creation tool, not a planning tool. It belongs in the write-* namespace, not plan-*.

---

### 23. plan-fatmode-growth — **21/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 3 | 3 | 2 | 2 | 3 | 4 |

**Verdict:** The learning vs. real project distinction is genuinely valuable: "Learning projects can be ugly, incomplete, and throwaway." The COMFORT ZONE flag is a nice touch.

**Weakness:** Very personal and introspective — hard for an AI to evaluate accurately without deep knowledge of your skills. Works better as a self-reflection template than an AI-driven analysis.

---

### 24. plan-taverner-curriculum — **21/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 3 | 2 | 3 | 3 | 2 |

**Verdict:** Well-structured curriculum template. Useful for Draft Academy and educational product design.

**Weakness:** The module format is standard instructional design — nothing proprietary here. Low reusability unless you're actively building courses.

---

### 25. plan-brady-graph — **21/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 3 | 4 | 3 | 2 | 3 | 3 | 3 |

**Verdict:** Good quality checks (orphan nodes, overly dense clusters, ungrounded edges, merge candidates). Multi-format output (JSON, Markdown, DOT) is practical.

**Weakness:** Knowledge graph construction is a complex task that this prompt oversimplifies. Real graphs need entity resolution, relationship extraction from text, and iterative refinement — none of which can happen in a single skill invocation.

---

## Tier 4: Writing Skills (Score varies)

These serve a different function — they're evaluation/critique tools, not planning tools.

### 26. write-runciter-ux — **26/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 4 | 3 | 3 | 4 | 4 |

**Verdict:** The PAIRED dimension concept (FUNCTION + DESIGN for each area) is excellent. Forces evaluation of both whether it works AND whether it communicates well. The TOP 3 UX WINS / TOP 3 UX PROBLEMS format is actionable.

**Best in class for:** Dreambase page auditing.

---

### 27. write-rachael-aesthetic — **25/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 4 | 3 | 3 | 3 | 4 |

**Verdict:** "Not just appearance, but communication" is the right framing. The INTENT/REALITY/GAP structure for each design dimension is clean. Dark patterns check is a nice touch.

**Weakness:** CSS auditing requires seeing the rendered page. Without preview access, this skill operates on code alone, which misses visual issues.

---

### 28. write-archer-evaluate — **24/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 4 | 3 | 3 | 3 | 3 |

**Verdict:** Solid 8-dimension rubric. "WEAKEST PARAGRAPH (revised)" forces concrete improvement. Good general-purpose writing evaluator.

**Weakness:** Overlaps with write-isidore-critique (both evaluate writing quality). Archer is quantitative (scores), Isidore is qualitative (argument analysis). The distinction could be made clearer.

---

### 29. write-chip-copy — **24/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 5 | 4 | 3 | 3 | 3 | 2 |

**Verdict:** The microcopy inventory (button labels, error messages, tooltips, empty states) is thorough. The INCONSISTENCIES and MISSING TEXT sections are especially useful.

**Weakness:** This is a standard UX writing audit — the PKD framing adds character but not functionality.

---

### 30. write-isidore-critique — **23/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 4 | 2 | 3 | 3 | 3 |

**Verdict:** The critique categories (unsupported claims, logical gaps, buried lede, redundancies, weak transitions) are well-chosen. "Honest but constructive" tone guidance is important.

**Weakness:** Overlaps with write-archer-evaluate. Together they provide quantitative + qualitative review, but the user needs to know which to invoke when.

---

### 31. write-dekany-style — **22/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 4 | 2 | 2 | 3 | 3 |

**Verdict:** The 8 consistency dimensions (tense, voice, terminology, formality, formatting, citation, person, capitalization) are comprehensive. The "inferred style guide" output is useful for multi-author projects.

**Weakness:** Low reusability for solo projects where style is naturally consistent. More useful for documentation than code.

---

### 32. write-dominic-template — **22/35**

| Clarity | Specificity | Scope | Reuse | Complement | Action | Unique |
|---------|-------------|-------|-------|------------|--------|--------|
| 4 | 4 | 3 | 2 | 2 | 4 | 3 |

**Verdict:** The fill-in-the-blank template with REQUIRED/OPTIONAL/ANTI-PATTERNS is practical. "Copy it, fill in the brackets, done" is the right goal.

**Weakness:** Template generation is something any LLM does naturally. The unique value is the anti-patterns and format-specific guidance, which could be a few-shot examples rather than a full skill.

---

## Tier 5: Specialist / Project-Specific (Score varies)

### 33. github-pages-deploy — **24/35**

Practical, well-structured, immediately actionable. The troubleshooting 404 checklist is the most valuable part. Not really a "swarm prompt" — it's a deployment runbook.

### 34. pdf-catalog — **26/35**

Hard-won operational knowledge baked into a skill. The "background agents CANNOT get user approval" warning is the kind of lesson you learn by burning tokens. The batch-and-merge workflow is solid engineering.

### 35. pkdbiostyle — **24/35**

Highly specific to the Exegesis Analysis project. The 23-category controlled vocabulary and JSON schema are well-designed. Low portability to other projects.

### 36. pkdquerypataudit — **25/35**

A comprehensive audit template for one specific project. The 6 audit domains and known issues registry make this a living document. Useful as a pattern for other project-specific audit skills.

### 37. plan-regan-simplify — **22/35**

Overlaps heavily with plan-bulero-refactor. Both look for unnecessary complexity. Regan focuses on recent changes (git diff), Bulero on overall architecture. Could be merged.

---

## System-Level Analysis

### What the System Gets Right

1. **Scope control is the dominant theme.** Joe Chip, Abendsen, Steiner, and Runciter-Slice form a four-skill scope defense system. This directly addresses your documented #1 failure mode (scope creep). Grade: **A+**

2. **Diagnostic-first philosophy.** Most skills explicitly state "this skill is diagnostic" and don't modify code. This prevents the common AI trap of making changes before understanding the problem. Grade: **A**

3. **Structured output formats.** Every skill prescribes a specific output table or template. This makes outputs comparable across invocations and projects. Grade: **A**

4. **Cross-references between skills.** Joe-chip → runciter-slice → steiner-gate → arctor-retro is a natural workflow. The skills know about each other. Grade: **A-**

5. **Personalized anti-patterns.** Runciter-audit checks for YOUR failure modes (scope tangle, UI-before-data, over-instrumentation), not generic code smells. Grade: **A+**

### What the System Gets Wrong

1. **Too many overlapping skills.** There are 3-4 clusters of near-duplicates:
   - **Scope/Constraint cluster:** joe-chip-scope + bohlen-constraint + abendsen-parking (all manage scope)
   - **Task decomposition cluster:** runciter-slice + buckman-execute + kevin-pipeline (all produce ordered task lists)
   - **Code quality cluster:** runciter-audit + bulero-refactor + regan-simplify (all find code problems)
   - **Writing evaluation cluster:** archer-evaluate + isidore-critique + dekany-style (all review writing)

   **Recommendation:** Merge each cluster into a single skill with modes, or make the invocation triggers sharper so you know which to use when.

2. **The PKD naming is charming but creates a lookup tax.** When you're in the middle of coding and want a scope check, you need to remember "Joe Chip" = scope. The codenames add personality but reduce discoverability. The `/plan-*` prefix helps, but `plan-scope`, `plan-slice`, `plan-audit` would be faster to recall.

3. **No skill for the most common operation: reading and understanding existing code.** There's no "orient me in this codebase" skill. Plan-tagomi-briefing is close, but it generates output FOR other conversations rather than FOR the current conversation. A "plan-orientation" skill that produces a quick map of the current codebase would be the most-used skill of all.

4. **The write-* namespace is underused.** 7 writing skills vs. 26 planning skills is lopsided. Writing evaluation is important for Dreambase's showcase pages, but most of these skills would be invoked once per project, not regularly. Consider: do you need 4 separate writing evaluators, or one with modes?

5. **No "done" skill.** There's arctor-retro for looking back, but no "ship it" skill that validates the final artifact against the original scope (from joe-chip), checks all gates (from steiner), runs a final audit (from runciter), and produces a release checklist.

### Redundancy Map

```
MERGE CANDIDATES:
┌─────────────────────────────┐
│ joe-chip-scope              │ ← Keep as primary
│ + bohlen-constraint         │ ← Fold into scope as "deep constraint analysis" mode
│ + abendsen-parking          │ ← Keep separate (different purpose: defer vs. define)
└─────────────────────────────┘

┌─────────────────────────────┐
│ runciter-slice              │ ← Keep as primary
│ + buckman-execute           │ ← Fold into slice as "task-level breakdown" mode
│ + steiner-gate              │ ← Fold into slice as "gate check" mode
└─────────────────────────────┘

┌─────────────────────────────┐
│ runciter-audit              │ ← Keep as primary
│ + bulero-refactor           │ ← Fold into audit as "refactoring recommendations" mode
│ + regan-simplify            │ ← Fold into audit as "recent changes review" mode
└─────────────────────────────┘

┌─────────────────────────────┐
│ buckman-critic              │ ← Keep as primary
│ + isidore-tokens            │ ← Fold into critic as "token efficiency" dimension
└─────────────────────────────┘

┌─────────────────────────────┐
│ write-archer-evaluate       │ ← Keep as primary writing evaluator
│ + write-isidore-critique    │ ← Fold into evaluate as "deep logic critique" mode
│ + write-dekany-style        │ ← Fold into evaluate as "consistency check" mode
└─────────────────────────────┘

KEEP SEPARATE (distinct enough):
• plan-eldritch-swarm (unique: multi-agent design)
• plan-deckard-boundary (unique: deterministic vs probabilistic)
• plan-pris-pedagogy (unique: game-based teaching)
• plan-mercer-reframe (unique: mental model correction)
• plan-kevin-pipeline (unique: prompt pipeline design)
• plan-lampton-corpus (unique: research corpus analysis)
• write-runciter-ux (unique: paired function+design audit)
• write-rachael-aesthetic (unique: visual design logic)
• write-chip-copy (unique: microcopy inventory)
```

### Missing Skills

| Gap | What It Would Do | Why It's Missing |
|-----|-----------------|-----------------|
| **Codebase Orientation** | "Here's what this project does, where the important files are, and what state it's in" for the CURRENT conversation | plan-tagomi-briefing is close but generates for OTHER conversations |
| **Ship It / Release** | Final validation against original scope + gate check + audit + release checklist | No "closing" skill exists |
| **Data Pipeline Verification** | Specifically for megabase-style ETL: verify ingestor output, check row counts, validate schema compliance | Covered ad-hoc by runciter-audit but not specifically |
| **Cost/Budget Tracker** | Track token spend, API costs, time investment across a project | plan-isidore-tokens is per-prompt, not per-project |
| **Conversation Memory** | "What did we decide in the last 3 conversations about X?" | Partially handled by Claude Code memory, but no structured review skill |

---

## Final Scorecard

| Rank | Skill | Score | Tier | Verdict |
|------|-------|-------|------|---------|
| 1 | plan-joe-chip-scope | 32/35 | Essential | Your best skill. Keep as-is. |
| 2 | plan-runciter-slice | 31/35 | Essential | Close second. The vertical slice philosophy works. |
| 3 | plan-runciter-audit | 30/35 | Essential | Personalized failure detection. Highly effective. |
| 4 | plan-buckman-critic | 30/35 | Essential | Strong prompt review framework. |
| 5 | plan-eldritch-swarm | 29/35 | Essential | Ambitious but delivers. Watch for scope inflation. |
| 6 | plan-deckard-boundary | 27/35 | Strong | Right tool for LLM-augmented systems. |
| 7 | plan-abendsen-parking | 27/35 | Strong | Scope creep defense. Simple but necessary. |
| 8 | plan-steiner-gate | 27/35 | Strong | Consider merging into runciter-slice. |
| 9 | pdf-catalog | 26/35 | Strong | Hard-won operational knowledge. |
| 10 | plan-isidore-tokens | 26/35 | Strong | Consider merging into buckman-critic. |
| 11 | plan-kevin-pipeline | 26/35 | Strong | Good for prompt workflows specifically. |
| 12 | plan-bohlen-constraint | 26/35 | Strong | Consider merging into joe-chip-scope. |
| 13 | plan-buckman-execute | 26/35 | Strong | Consider merging into runciter-slice. |
| 14 | write-runciter-ux | 26/35 | Strong | Best writing skill. Paired audit concept is excellent. |
| 15 | write-rachael-aesthetic | 25/35 | Situational | Good when you have preview access. |
| 16 | plan-lampton-corpus | 25/35 | Situational | Good for research projects. |
| 17 | plan-mercer-reframe | 25/35 | Situational | Elegant structure, hard to invoke proactively. |
| 18 | plan-pris-pedagogy | 25/35 | Situational | Good for Draft Academy / educational work. |
| 19 | pkdquerypataudit | 25/35 | Specialist | Project-specific but well-designed. |
| 20 | plan-tagomi-briefing | 24/35 | Situational | Partially obsoleted by Claude Code memory. |
| 21 | write-archer-evaluate | 24/35 | Situational | Good general writing evaluator. |
| 22 | write-chip-copy | 24/35 | Situational | Standard UX writing audit. |
| 23 | github-pages-deploy | 24/35 | Specialist | Deployment runbook, not a swarm prompt. |
| 24 | pkdbiostyle | 24/35 | Specialist | Project-specific. |
| 25 | plan-arctor-retro | 23/35 | Situational | Hard to remember to invoke. |
| 26 | plan-bulero-refactor | 23/35 | Redundant | Merge into runciter-audit. |
| 27 | plan-fat-compress | 23/35 | Situational | Niche but useful for research notes. |
| 28 | write-isidore-critique | 23/35 | Redundant | Merge into write-archer-evaluate. |
| 29 | plan-rosen-artifact | 22/35 | Redundant | Philosophy, not a tool. Merge into buckman-execute. |
| 30 | plan-freck-narrative | 22/35 | Misplaced | Should be write-*, not plan-*. |
| 31 | plan-regan-simplify | 22/35 | Redundant | Merge into runciter-audit. |
| 32 | plan-mayerson-prereq | 22/35 | Redundant | Package managers do 90% of this. |
| 33 | write-dekany-style | 22/35 | Redundant | Merge into write-archer-evaluate. |
| 34 | write-dominic-template | 22/35 | Low-value | Any LLM does this naturally. |
| 35 | plan-fatmode-growth | 21/35 | Niche | Better as self-reflection than AI tool. |
| 36 | plan-taverner-curriculum | 21/35 | Niche | Standard instructional design. |
| 37 | plan-brady-graph | 21/35 | Niche | Oversimplifies knowledge graph construction. |

---

## Recommended Consolidation: From 37 to 20

If you consolidated the redundant skills, you'd have a tighter, faster-to-navigate system:

| # | Consolidated Skill | Absorbs | Modes |
|---|-------------------|---------|-------|
| 1 | plan-scope | joe-chip-scope + bohlen-constraint | `freeze` / `constrain` |
| 2 | plan-slice | runciter-slice + buckman-execute + steiner-gate | `design` / `decompose` / `gate-check` |
| 3 | plan-audit | runciter-audit + bulero-refactor + regan-simplify | `anti-patterns` / `refactor` / `recent-changes` |
| 4 | plan-critic | buckman-critic + isidore-tokens | `quality` / `efficiency` |
| 5 | plan-swarm | eldritch-swarm | (standalone) |
| 6 | plan-boundary | deckard-boundary | (standalone) |
| 7 | plan-park | abendsen-parking | (standalone) |
| 8 | plan-pipeline | kevin-pipeline | (standalone) |
| 9 | plan-corpus | lampton-corpus | (standalone) |
| 10 | plan-reframe | mercer-reframe | (standalone) |
| 11 | plan-pedagogy | pris-pedagogy + taverner-curriculum | `game-map` / `curriculum` |
| 12 | plan-compress | fat-compress | (standalone) |
| 13 | plan-narrative | freck-narrative + fatmode-growth | `explain` / `growth-check` |
| 14 | plan-briefing | tagomi-briefing + rosen-artifact | `briefing` / `artifacts` |
| 15 | plan-retro | arctor-retro | (standalone) |
| 16 | write-evaluate | archer-evaluate + isidore-critique + dekany-style | `score` / `critique` / `consistency` |
| 17 | write-ux | runciter-ux | (standalone) |
| 18 | write-visual | rachael-aesthetic | (standalone) |
| 19 | write-copy | chip-copy + dominic-template | `audit` / `template` |
| 20 | deploy | github-pages-deploy | (standalone) |

Plus the 3 project-specific skills (pdf-catalog, pkdbiostyle, pkdquerypataudit) kept as-is.

**Net result:** 37 → 23 skills. Same capability, half the lookup tax.

---

*Evaluated by Palmer Eldritch's quality assurance division. No skills were harmed in this analysis.*
