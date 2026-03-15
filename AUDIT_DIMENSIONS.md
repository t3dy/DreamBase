# 20 Ways to Audit Dreambase: Functionality & User Experience

**Beyond the failure audit — a comprehensive checklist for evaluating every dimension of the web engineering.**

---

## 1. LINK INTEGRITY AUDIT
Crawl every page and verify every `<a href>` resolves. Check internal links (`/scholar/`, `/collection/`, `/conversation/`), external links (Wikimedia, GitHub), and anchor links (`#tab-`). Report dead links, redirect chains, and links to 404s.

**Tool:** Write a script that walks all routes, renders them, and extracts/validates every href. Or use `linkchecker` CLI.

## 2. RESPONSIVE BREAKPOINT AUDIT
Render every page at 5 widths (375px mobile, 768px tablet, 1024px small desktop, 1440px desktop, 1920px widescreen). Screenshot each. Look for: horizontal overflow, truncated text, overlapping elements, touch target sizes (<44px), nav collapse behavior.

**Tool:** `preview_resize` at each breakpoint + `preview_screenshot`.

## 3. PERFORMANCE PROFILING AUDIT
Time every route's database queries. Log: query count per page, total DB time, template render time, total response time. Identify the slowest routes and the most expensive queries.

**Method:** Add timing middleware to Flask, or use `EXPLAIN QUERY PLAN` on each SQL statement to check for table scans vs. index usage.

## 4. ACCESSIBILITY (a11y) AUDIT
Check every page for: semantic HTML (headings hierarchy, landmarks), color contrast (WCAG AA 4.5:1 for text), keyboard navigation (all interactive elements reachable via Tab), screen reader compatibility (alt text on images, ARIA labels on tabs), focus indicators visible.

**Tool:** Lighthouse audit, axe-core browser extension, or manual keyboard walkthrough.

## 5. DATA FRESHNESS AUDIT
For every hardcoded data structure (SCHOLARS, COLLECTIONS, SHOWCASES, PROJECTS), verify that the data matches the current state of the database. Check: do all conversation_ids exist? Do page counts match? Are summaries populated for all linked conversations?

**Method:** Script that loads all Python dicts, queries DB for each conversation_id, reports mismatches.

## 6. NAVIGATION FLOW AUDIT
Map every page-to-page link in the app as a directed graph. Identify: dead-end pages (no outbound links), orphan pages (no inbound links), the longest path a user must take to reach any page, and whether "Back" behavior is consistent.

**Method:** Build an adjacency list from template link analysis. Visualize with D3 or Graphviz.

## 7. CONTENT DENSITY AUDIT
For every card/summary/overview, measure: character count, reading time, information-to-whitespace ratio. Are some cards overloaded while others are sparse? Is the 3-sentence summary format consistent? Do all pedagogy boxes have content?

**Method:** Extract text from rendered pages, compute per-element word counts.

## 8. VISUAL CONSISTENCY AUDIT
Compare CSS properties across all card types (scholar cards, collection cards, showcase cards, idea cards, project cards, conversation cards). Check: font sizes, padding, border styles, color usage, hover effects, transition timing. Document inconsistencies.

**Tool:** `preview_inspect` on each card type. Build a comparison table.

## 9. ERROR HANDLING AUDIT
Test every route with: invalid slugs, SQL injection attempts, missing query params, extremely long query strings, Unicode edge cases, empty database. Verify that errors produce friendly messages, not stack traces.

**Method:** Write a test harness that hits each route with malformed input.

## 10. SEARCH UX AUDIT
Test the search experience: Does it find what you expect? How does it handle typos, partial matches, quoted phrases, Boolean operators? What does "no results" look like? Is there a suggestion mechanism? How fast is the response?

**Method:** Create a test suite of 20 realistic search queries (scholar names, topics, specific phrases) and evaluate precision/recall.

## 11. RABBIT HOLE DEPTH AUDIT
Starting from the homepage, measure how many clicks it takes to reach: the deepest scholar detail, the longest conversation, every collection, every showcase. Map the "rabbit hole" experience — can users get lost? Can they always get back?

**Method:** Manual walkthrough + breadcrumb analysis.

## 12. DATA VISUALIZATION ACCURACY AUDIT
For every chart/viz on the viz page and values page: verify that the data displayed matches a direct SQL query. Check: are axes labeled? Are units clear? Do tooltips show correct values? Are there misleading scales (truncated Y-axis, log vs linear)?

**Method:** Cross-reference displayed numbers with raw SQL output.

## 13. CROSS-BROWSER RENDERING AUDIT
Test the app in Chrome, Firefox, Safari (if available), and Edge. Check: CSS custom properties support, flexbox/grid rendering, SVG rendering, JavaScript tab switching, font rendering differences.

**Tool:** BrowserStack or manual testing.

## 14. STATE PERSISTENCE AUDIT
When a user applies filters on the browse page (source, tag, sort, search), do those filters survive: page refresh? Browser back/forward? Bookmark? Share link? Check URL parameter handling for all filter combinations.

**Method:** Apply filters, copy URL, paste in new tab, verify identical state.

## 15. CONTENT QUALITY AUDIT
Read every summary, hook, pedagogy box, and description in the app. Grade each for: clarity (is it understandable?), accuracy (does it match the linked conversations?), voice consistency (same register throughout?), length appropriateness (too long? too terse?).

**Method:** Human review with a rubric, or LLM-assisted batch evaluation.

## 16. TEMPLATE DRY-NESS AUDIT
Analyze all 13 templates for duplicated HTML patterns. Check: is the nav bar copy-pasted or included? Are card layouts shared or re-implemented? Is CSS duplicated between templates or centralized in style.css? How many lines of CSS are in `<style>` blocks vs. the shared stylesheet?

**Method:** Diff template headers/navs, count inline `<style>` lines, identify candidates for `{% include %}` or `{% macro %}`.

## 17. SECURITY SURFACE AUDIT
Check for: XSS via user-generated content (search queries reflected in HTML, conversation titles with HTML), SQL injection (are all queries parameterized?), path traversal (slug-to-file-path conversions), CSRF on any POST routes, sensitive data exposure (DB path, internal file paths).

**Method:** Manual code review + automated scanner (OWASP ZAP or similar).

## 18. LOAD TESTING AUDIT
Simulate 10 concurrent users browsing the app. Measure: response times under load, SQLite connection contention (WAL mode helps but has limits), memory usage growth, whether any route becomes a bottleneck.

**Tool:** `wrk`, `ab`, or `locust` pointed at localhost:5555.

## 19. PRINT / EXPORT AUDIT
What happens when a user tries to print a page? Does the dark theme produce unreadable output? Are tab sections all visible or only the active one? Could a user export a scholar page as a PDF that looks reasonable?

**Method:** Print preview each page type, check for: white text on white background, missing content, broken layouts.

## 20. DELIGHT / POLISH AUDIT
The subjective dimension: Does the app feel good to use? Check: page load jank (layout shift during render), hover state feedback (do things respond to cursor?), empty state messaging (what does a new collection look like?), loading indicators (none exist — should they?), micro-interactions (tab switching, filter changes).

**Method:** Record a screen session of a 5-minute browsing session and review for friction points.

---

## PRIORITY MATRIX

| Audit | Effort | Impact | Do First? |
|-------|--------|--------|-----------|
| Link Integrity | LOW | HIGH | ✅ |
| Data Freshness | LOW | HIGH | ✅ |
| Error Handling | MEDIUM | HIGH | ✅ |
| Responsive Breakpoints | MEDIUM | HIGH | ✅ |
| Visual Consistency | MEDIUM | MEDIUM | ✅ |
| Template DRY-ness | MEDIUM | MEDIUM | Next |
| Search UX | LOW | MEDIUM | Next |
| Accessibility | HIGH | HIGH | Next |
| Performance Profiling | MEDIUM | LOW (personal use) | Later |
| Content Quality | HIGH | HIGH | Later (needs human review) |
| Security Surface | MEDIUM | LOW (localhost) | Later |
| Cross-Browser | HIGH | LOW (personal use) | Skip unless deploying |

---

*Each audit produces a .md report in the same format as FAILURE_AUDIT.md. Run them incrementally — don't try to do all 20 at once.*
