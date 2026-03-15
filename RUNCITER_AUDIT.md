# Runciter Audit: Dreambase Consistency Report

**Glen Runciter checks reality for decay.**
**Generated: 2026-03-14**

---

## FAILURE MODE ANALYSIS

| Component | Failure Mode | Probability | Impact | Detection | Recovery |
|-----------|-------------|-------------|--------|-----------|----------|
| Showcase narrative rendering | Sidecar data silently ignored | HIGH (100% if sidecar exists) | HIGH — showcase content never displays | None — no error, just empty | **FIXED** — added `narrative=narrative` to render_template |
| improve_summaries.py IDs | Stale hardcoded IDs drift from app.py | HIGH (already drifted) | MEDIUM — wrong conversations get featured treatment | None — silent | **FIXED** — now imports from app.py |
| concat_context.py FILE_ORDER | Missing new files from full context | HIGH (already stale) | MEDIUM — ChatGPT sessions miss new code | Manual comparison | **FIXED** — added 5 missing files |
| Nav in conversation.html | "Back" vs "Browse" inconsistency | LOW | LOW — cosmetic only | Visual inspection | Rename to "Browse" |
| Nav in index.html | Ideas count shows conversation total | LOW | LOW — misleading but minor | Visual inspection | Remove count or fix to ideas count |
| /api/search orphaned | Unused route | LOW | LOW — dead code | Grep for usage | Remove or wire up autocomplete |
| Inline styles fragmentation | Global style changes require 7+ file edits | MEDIUM | MEDIUM — consistency drift over time | Manual audit | Consolidate to style.css (v2) |
| summarize.py vs improve_summaries.py | Parallel batch workflows, incompatible formats | MEDIUM | MEDIUM — confusion about which tool to use | Developer confusion | Document which to use when, or merge |

---

## ANTI-PATTERN SCAN

| Anti-pattern | Detected? | Where | Severity | Fix |
|-------------|-----------|-------|----------|-----|
| **Scope tangle** | MILD | app.py mixes data definitions (SHOWCASES, COLLECTIONS) with routing and DB queries | LOW | Acceptable for project size. Extract dicts to config.py if it grows |
| **UI-before-data** | NO | All UI references valid data | — | — |
| **Over-instrumentation** | NO | No logging/diagnostic code | — | — |
| **Resource spirals** | NO | No polling or loops | — | — |
| **Hardcoded magic values** | YES | Conversation IDs hardcoded in SHOWCASES/COLLECTIONS dicts in app.py, and were duplicated in improve_summaries.py | MEDIUM | **FIXED** — improve_summaries.py now imports from app.py. App.py hardcoding is intentional (curated selections). |
| **Missing integration layer** | MILD | improve_summaries.py curator/copywriter produce .md proposal files that require manual copy-paste into DB/app.py. No automated import path. | LOW | By design — human gate prevents bad data. |
| **Style fragmentation** | YES | Every template except index.html and conversation.html has its own `<style>` block | MEDIUM | Move shared patterns to style.css when design stabilizes |

---

## BUGS FOUND AND FIXED

### BUG 1: Showcase narrative never renders (CRITICAL)
**Location:** `app.py` line 575
**Symptom:** `narrative` variable computed from sidecar merge but never passed to template. Template reads `showcase.narrative` which is always `None`.
**Fix:** Added `narrative=narrative` to `render_template()` call.
**Status:** FIXED

### BUG 2: improve_summaries.py stale IDs (MEDIUM)
**Location:** `improve_summaries.py` lines 22-39
**Symptom:** Hardcoded SHOWCASE_IDS and COLLECTION_IDS missing conversation 157 (marxism) and entirely missing scholarly-to-games and building-dreams collections.
**Fix:** Replaced hardcoded lists with `_get_featured_ids()` that imports from app.py.
**Status:** FIXED

### BUG 3: concat_context.py missing files (MEDIUM)
**Location:** `concat_context.py` FILE_ORDER
**Symptom:** Missing collections.html, collection.html, values.html, improve_summaries.py, SUMMARYTEMPLATE.md from full context export.
**Fix:** Added 5 entries to FILE_ORDER.
**Status:** FIXED

---

## CONSISTENCY ISSUES (unfixed, low priority)

### 1. Nav inconsistency in conversation.html
- Says "← Back" instead of "Browse"
- Every other template says "Browse"
- **Recommendation:** Change to "Browse" for consistency, or keep "← Back" as intentional (it IS a child page)

### 2. Nav inconsistency in index.html
- Ideas link shows `Ideas ({{ total }})` where `total` is conversation count
- No other template appends a count to the Ideas link
- **Recommendation:** Either show the actual ideas count, or remove the count

### 3. /api/search route is orphaned
- Exists in app.py but no template calls it
- **Recommendation:** Either wire up autocomplete in the search input, or remove the route

### 4. Inline styles not in style.css
- 7 templates define their own `<style>` blocks
- Shared patterns duplicated: `.page-intro`/`.collections-intro`/`.values-intro` are the same component
- `.source-conv` in showcase.html ≈ `.conv-entry` in collection.html
- **Recommendation:** Consolidate when design stabilizes. Not urgent while layouts are still in flux.

### 5. "Megabase" vs "Dreambase" naming
- Directory: `megabase/`
- Database: `megabase.db`
- UI: "Dreambase" everywhere
- **Recommendation:** Cosmetic. Document in a rename tracking note if it matters.

---

## DATA MODEL COHERENCE

### Current architecture:

```
SHOWCASES (3 entries)          COLLECTIONS (9 entries)
├─ slug                        ├─ slug
├─ title                       ├─ title
├─ hook                        ├─ subtitle
├─ category                    ├─ description
├─ maturity                    ├─ conversation_ids[]
├─ conversation_ids[]          └─ color
├─ tags[]
├─ pedagogy
├─ difficulty_easy/med/hard
├─ narrative (None, from sidecar)
├─ timeline_entries[]
├─ quotes[]
└─ images[]
```

**Observation:** Showcases and Collections serve different purposes:
- **Showcases** = deep 5-tab pages for 3 game ideas (with pedagogy, quotes, timeline)
- **Collections** = lighter thematic groupings (description + conversation list + adjacent links)

This distinction is clear and intentional. No model confusion.

### Potential future model additions:
- **PROJECTS** dict (for /projects page) — maps Dev/ folders to conversations
- **SCHOLARS** dict (for historian showcases) — could be showcases or collections
- **Genre tags** on ideas — currently ideas have category + maturity but no genre

---

## OVERALL ASSESSMENT

**This project has good separation of concerns.** The main risks are:

1. **Style fragmentation** — inline styles will become painful if the design changes globally. This is the most likely source of future inconsistency.

2. **Data dict proliferation** — SHOWCASES, COLLECTIONS, and potentially PROJECTS/SCHOLARS are all hardcoded in app.py. If these grow beyond ~20 entries each, they should move to a config file or the database itself.

3. **Batch workflow confusion** — Two scripts (summarize.py, improve_summaries.py) both offer batch-export/import but with incompatible formats. Document which to use or merge them.

The 3 critical bugs found have all been fixed in this session.
