# Eldritch Swarm: Summary Improvement System

**Palmer Eldritch Orchestration Plan**
**Purpose:** Improve all Dreambase summaries and website copy using SUMMARYTEMPLATE.md
**Constraint:** NO API. All work is either deterministic (Python scripts) or ChatGPT batch workflow.

---

## SITUATION REPORT

| Metric | Count | Notes |
|--------|-------|-------|
| Total conversations | 4,308 | |
| Have summary (>10 chars) | 2,650 | 61% coverage |
| Bad/missing summaries | 1,944 | includes SMS, Facebook, Google Chat (no summaries) |
| LLM conversations with "bot voice" summaries | ~200 | "Here is a summary...", "Would you like...", "It seems..." |
| Featured conversations (showcases + collections) | 116 unique | **priority targets** |
| Featured with bad/missing summaries | 15 | must fix first |

### Priority Tiers

1. **Tier 1 — Featured (116 convos):** Showcases + Collections. Visible on curated pages. Must be excellent.
2. **Tier 2 — Bot Voice Fix (~200 convos):** LLM conversations where the "summary" is actually the assistant's first response preamble. Fix deterministically.
3. **Tier 3 — LLM Bulk (2,450 convos):** All other LLM conversations. Improve via ChatGPT batch workflow.
4. **Tier 4 — Non-LLM (1,592 convos):** SMS, Facebook, Google Chat, Twitter. Generate basic summaries deterministically from message content.

---

## AGENT ROLES

| Agent | Script | Responsibility | Inputs | Outputs | Completion Signal |
|-------|--------|---------------|--------|---------|-------------------|
| **Curator** | `improve_summaries.py curator` | Write rich summaries for 116 featured conversations by reading first 10 messages + title + tags | megabase.db, SUMMARYTEMPLATE.md Template A | `improvements/featured_summaries.md` (structured output) | All 116 entries written |
| **Janitor** | `improve_summaries.py janitor` | Fix ~200 bot-voice summaries deterministically — strip "Here is...", "Would you like...", extract actual content from assistant response | megabase.db | Direct DB updates to `conversations.summary` | UPDATE count logged |
| **Batcher** | `improve_summaries.py batch-export` | Export remaining LLM conversation excerpts as ChatGPT batch files (20 per file, ~125 files) using SUMMARYTEMPLATE.md Template A as the prompt | megabase.db, SUMMARYTEMPLATE.md | `chunks/summaries/batch_NNN.md` files | File count logged |
| **Importer** | `improve_summaries.py batch-import <file>` | Parse ChatGPT's structured summary responses back into DB | Pasted ChatGPT output files | DB updates to `conversations.summary` | Row count logged |
| **Messenger** | `improve_summaries.py messenger` | Generate deterministic summaries for SMS/Facebook/Google Chat from message content (first+last message, participant names, message count) | megabase.db | Direct DB updates | UPDATE count logged |
| **Copywriter** | `improve_summaries.py copywriter` | Output improved collection descriptions, showcase hooks, and pedagogy text for app.py | megabase.db, current app.py SHOWCASES/COLLECTIONS dicts, SUMMARYTEMPLATE.md Templates B-E | `improvements/copy_improvements.md` | File written |

---

## COMMUNICATION FLOW

```
                    ┌─── Janitor (deterministic, bot-voice fix)
                    │         │
                    │         ▼ [direct DB update]
                    │
Curator ───────────►│─── Batcher (export for ChatGPT)
  (featured 116)    │         │
  │                 │         ▼ [batch files on disk]
  ▼                 │    Ted pastes into ChatGPT
  [improvements/    │         │
   featured.md]     │         ▼
  │                 │    Importer (parse ChatGPT responses)
  ▼                 │         │
  Ted reviews,      │         ▼ [DB updates]
  approves,         │
  runs import       │─── Messenger (SMS/Facebook deterministic)
                    │         │
                    │         ▼ [direct DB update]
                    │
                    └─── Copywriter (app.py copy improvements)
                              │
                              ▼ [improvements/copy.md]
                              │
                              Ted reviews, pastes into app.py
```

### Orchestration Pattern: **Parallel with human gate**

- **Phase 1 (parallel):** Janitor + Messenger + Curator + Copywriter run simultaneously. No dependencies.
- **Phase 2 (human gate):** Ted reviews Curator and Copywriter output, applies to DB/app.py.
- **Phase 3 (sequential):** Batcher runs after Phase 1 (skips conversations already fixed).
- **Phase 4 (human loop):** Ted pastes batch files into ChatGPT, runs Importer on responses.

---

## AGENT SPECIFICATIONS

### Agent: Janitor (deterministic, no LLM needed)

**Logic:**
```python
# For each conversation where summary starts with bot preamble:
# 1. Find the first SUBSTANTIVE assistant message (skip greetings)
# 2. Extract first 2 sentences that aren't meta-commentary
# 3. If the summary contains a markdown table, extract the table title as summary
# 4. Prefix with conversation title context

BAD_PREFIXES = [
    "Would you like", "It seems", "Here is", "Sure", "Certainly",
    "I'd be happy", "The file", "The document", "Of course",
    "Let me", "I'll", "Based on"
]

# Strip prefix, take first substantive sentence from remaining text
# If nothing salvageable, generate from: title + first user message (truncated)
```

**Completion signal:** Prints `"Janitor: fixed N summaries"`

### Agent: Messenger (deterministic, no LLM needed)

**Logic:**
```python
# For SMS/Facebook/Google Chat conversations with no summary:
# Generate: "[Participant(s)] — [first message preview]. [N messages] over [date range]."
# Example: "Group chat with Sarah, Mike — 'hey are we still on for saturday'. 47 messages, Jan-Mar 2025."
```

**Completion signal:** Prints `"Messenger: generated N summaries"`

### Agent: Curator (deterministic + manual review)

**Logic:**
```python
# For each of 116 featured conversations:
# 1. Read title, tags, first 5 user messages, first 3 assistant messages
# 2. Apply SUMMARYTEMPLATE.md Template A structure
# 3. Output as structured markdown for Ted to review/edit

# Output format per conversation:
# CONVERSATION_ID: 712
# TITLE: Medieval Magic Summary Request
# CURRENT_SUMMARY: Here is a partial summary of...
# PROPOSED_SUMMARY: [improved 3-sentence summary]
# SOURCE_EVIDENCE: [key phrases from first messages that inform the summary]
# ---
```

**Note:** This agent outputs a PROPOSAL file, not direct DB writes. Ted reviews.

### Agent: Copywriter (deterministic + manual review)

**Logic:**
```python
# For each collection in COLLECTIONS dict:
# 1. Read all linked conversations' titles, summaries, tags
# 2. Apply SUMMARYTEMPLATE.md Template B
# 3. Output improved description

# For each showcase in SHOWCASES dict:
# 1. Read linked conversations
# 2. Apply Templates C (hook) and D (narrative)
# 3. Output improved hooks and pedagogy text

# Output format:
# COLLECTION: alchemy-scholarship
# CURRENT_DESCRIPTION: Renaissance alchemy as a system...
# PROPOSED_DESCRIPTION: [improved text]
# ---
```

### Agent: Batcher (deterministic)

**Logic:** Same as existing `summarize.py batch-export` but:
1. Skips conversations already fixed by Janitor/Messenger
2. Uses SUMMARYTEMPLATE.md Template A as the ChatGPT prompt header
3. Groups 20 conversations per batch file
4. Targets ~2,200 remaining LLM conversations = ~110 batch files

### Agent: Importer (deterministic)

**Logic:** Same as existing `summarize.py batch-import` — parses structured ChatGPT output.

---

## FLAGGED ISSUES

| Issue | Severity | Resolution |
|-------|----------|------------|
| Curator has vague responsibility ("write rich summaries") | MEDIUM | Bounded: reads first 10 messages only, applies Template A mechanically, outputs proposal not direct writes |
| Batcher and existing summarize.py overlap | LOW | Batcher IS summarize.py with updated skip logic and new prompt template |
| Copywriter output requires manual paste into app.py | LOW | By design — app.py edits should be human-reviewed |
| SMS/Facebook summaries will be generic | LOW | Acceptable for Tier 4 — these aren't featured content |
| 110 batch files for ChatGPT = multi-day manual effort | MEDIUM | Acceptable per project constraints (no API, $100/mo plan) |

---

## EXECUTION ORDER

```
Session N (this session):
  1. Build improve_summaries.py with all 6 agent subcommands
  2. Run Janitor (immediate, deterministic)
  3. Run Messenger (immediate, deterministic)
  4. Run Curator (generates proposal file for review)
  5. Run Copywriter (generates proposal file for review)

Session N+1 (Ted reviews):
  6. Ted reviews improvements/featured_summaries.md, edits, approves
  7. Run import of approved featured summaries
  8. Ted reviews improvements/copy_improvements.md, pastes into app.py

Session N+2+ (batch workflow):
  9. Run Batcher (generates ~110 batch files)
  10. Ted pastes batches into ChatGPT over several days
  11. Run Importer on each response file
```
