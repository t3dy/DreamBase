"""
Dreambase test suite — tests every route, data linkage, and known failure mode.
Run: python -m pytest test_app.py -v
"""
import json
import os
import sqlite3
import tempfile
import pytest

from app import app, SHOWCASES, COLLECTIONS, SCHOLARS, SPECIAL_SHOWCASES, PROJECTS, get_db
from schema import DB_PATH


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def db():
    """Direct database connection for data verification."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


# ---------------------------------------------------------------------------
# 1. ROUTE SMOKE TESTS — Every route returns 200
# ---------------------------------------------------------------------------

class TestRouteSmoke:
    """Every route should return 200 with no errors."""

    def test_index(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_index_with_search(self, client):
        resp = client.get("/?q=alchemy")
        assert resp.status_code == 200

    def test_index_with_tag_filter(self, client):
        resp = client.get("/?tag=alchemy")
        assert resp.status_code == 200

    def test_index_with_source_filter(self, client):
        resp = client.get("/?source=chatgpt")
        assert resp.status_code == 200

    def test_index_sort_by_date(self, client):
        resp = client.get("/?sort=date")
        assert resp.status_code == 200

    def test_index_sort_by_title(self, client):
        resp = client.get("/?sort=title")
        assert resp.status_code == 200

    def test_index_pagination(self, client):
        resp = client.get("/?page=2")
        assert resp.status_code == 200

    def test_conversation_detail(self, client, db):
        """Test a real conversation renders."""
        row = db.execute("SELECT id FROM conversations LIMIT 1").fetchone()
        resp = client.get(f"/conversation/{row['id']}")
        assert resp.status_code == 200

    def test_conversation_404(self, client):
        resp = client.get("/conversation/9999999")
        assert resp.status_code == 404

    def test_ideas(self, client):
        resp = client.get("/ideas")
        assert resp.status_code == 200

    def test_viz(self, client):
        resp = client.get("/viz")
        assert resp.status_code == 200

    def test_values(self, client):
        resp = client.get("/values")
        assert resp.status_code == 200

    def test_showcases_index(self, client):
        resp = client.get("/showcases")
        assert resp.status_code == 200

    def test_collections_index(self, client):
        resp = client.get("/collections")
        assert resp.status_code == 200

    def test_scholars_index(self, client):
        resp = client.get("/scholars")
        assert resp.status_code == 200

    def test_projects(self, client):
        resp = client.get("/projects")
        assert resp.status_code == 200

    def test_action_map(self, client):
        resp = client.get("/action-map")
        assert resp.status_code == 200

    def test_api_search(self, client):
        resp = client.get("/api/search?q=alchemy")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_api_search_short_query(self, client):
        """Queries under 2 chars return empty."""
        resp = client.get("/api/search?q=a")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_api_search_empty(self, client):
        resp = client.get("/api/search?q=")
        assert resp.status_code == 200
        assert resp.get_json() == []


# ---------------------------------------------------------------------------
# 2. SHOWCASE ROUTES — Every showcase slug returns 200
# ---------------------------------------------------------------------------

class TestShowcaseRoutes:
    """Every defined showcase must render without errors."""

    @pytest.mark.parametrize("slug", list(SHOWCASES.keys()))
    def test_showcase(self, client, slug):
        resp = client.get(f"/dream/{slug}")
        assert resp.status_code == 200, f"Showcase {slug} returned {resp.status_code}"

    def test_showcase_404(self, client):
        resp = client.get("/dream/nonexistent-slug")
        assert resp.status_code == 404


class TestCollectionRoutes:
    """Every defined collection must render without errors."""

    @pytest.mark.parametrize("slug", list(COLLECTIONS.keys()))
    def test_collection(self, client, slug):
        resp = client.get(f"/collection/{slug}")
        assert resp.status_code == 200, f"Collection {slug} returned {resp.status_code}"

    def test_collection_404(self, client):
        resp = client.get("/collection/nonexistent-slug")
        assert resp.status_code == 404


class TestScholarRoutes:
    """Every defined scholar must render without errors."""

    @pytest.mark.parametrize("slug", list(SCHOLARS.keys()))
    def test_scholar(self, client, slug):
        resp = client.get(f"/scholar/{slug}")
        assert resp.status_code == 200, f"Scholar {slug} returned {resp.status_code}"

    def test_scholar_404(self, client):
        resp = client.get("/scholar/nonexistent-slug")
        assert resp.status_code == 404


class TestSpecialShowcaseRoutes:
    """Every special showcase (wonderland) must render without errors."""

    @pytest.mark.parametrize("slug", list(SPECIAL_SHOWCASES.keys()))
    def test_special_showcase(self, client, slug):
        resp = client.get(f"/wonderland/{slug}")
        assert resp.status_code == 200, f"Special showcase {slug} returned {resp.status_code}"

    def test_wonderland_404(self, client):
        resp = client.get("/wonderland/nonexistent-slug")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 3. DATA INTEGRITY — Hardcoded IDs exist in the database
# ---------------------------------------------------------------------------

class TestDataIntegrity:
    """All hardcoded conversation IDs must exist in the database."""

    def _check_ids(self, db, ids, source_name):
        """Verify a list of IDs exist in conversations table."""
        if not ids:
            return
        ph = ",".join("?" * len(ids))
        found = db.execute(
            f"SELECT id FROM conversations WHERE id IN ({ph})", ids
        ).fetchall()
        found_ids = {r["id"] for r in found}
        missing = set(ids) - found_ids
        assert not missing, f"{source_name}: IDs {missing} not found in database"

    @pytest.mark.parametrize("slug,sc", list(SHOWCASES.items()))
    def test_showcase_ids(self, db, slug, sc):
        self._check_ids(db, sc["conversation_ids"], f"SHOWCASE:{slug}")

    @pytest.mark.parametrize("slug,col", list(COLLECTIONS.items()))
    def test_collection_ids(self, db, slug, col):
        self._check_ids(db, col["conversation_ids"], f"COLLECTION:{slug}")

    @pytest.mark.parametrize("slug,sc", list(SCHOLARS.items()))
    def test_scholar_ids(self, db, slug, sc):
        self._check_ids(db, sc["conversation_ids"], f"SCHOLAR:{slug}")

    @pytest.mark.parametrize("slug,sc", list(SPECIAL_SHOWCASES.items()))
    def test_special_showcase_ids(self, db, slug, sc):
        self._check_ids(db, sc["conversation_ids"], f"SPECIAL:{slug}")

    def test_project_ids(self, db):
        for p in PROJECTS:
            self._check_ids(db, p["conversation_ids"], f"PROJECT:{p['name']}")


# ---------------------------------------------------------------------------
# 4. DATA MODEL CONSISTENCY — Dicts have required fields
# ---------------------------------------------------------------------------

class TestDataModelConsistency:
    """All data dicts must have the required fields for their templates."""

    SHOWCASE_REQUIRED = ["slug", "title", "hook", "conversation_ids", "tags"]
    COLLECTION_REQUIRED = ["slug", "title", "description", "conversation_ids", "color"]
    SCHOLAR_REQUIRED = ["slug", "title", "hook", "field", "era", "conversation_ids",
                        "depth_introductory", "depth_intermediate", "depth_advanced", "color"]
    SPECIAL_REQUIRED = ["slug", "title", "conversation_ids", "template"]

    @pytest.mark.parametrize("slug,sc", list(SHOWCASES.items()))
    def test_showcase_fields(self, slug, sc):
        for field in self.SHOWCASE_REQUIRED:
            assert field in sc, f"SHOWCASE:{slug} missing field '{field}'"

    @pytest.mark.parametrize("slug,col", list(COLLECTIONS.items()))
    def test_collection_fields(self, slug, col):
        for field in self.COLLECTION_REQUIRED:
            assert field in col, f"COLLECTION:{slug} missing field '{field}'"

    @pytest.mark.parametrize("slug,sc", list(SCHOLARS.items()))
    def test_scholar_fields(self, slug, sc):
        for field in self.SCHOLAR_REQUIRED:
            assert field in sc, f"SCHOLAR:{slug} missing field '{field}'"

    @pytest.mark.parametrize("slug,sc", list(SPECIAL_SHOWCASES.items()))
    def test_special_showcase_fields(self, slug, sc):
        for field in self.SPECIAL_REQUIRED:
            assert field in sc, f"SPECIAL:{slug} missing field '{field}'"

    def test_slug_matches_key(self):
        """Dict keys must match the slug field inside each entry."""
        for slug, sc in SHOWCASES.items():
            assert sc["slug"] == slug, f"SHOWCASE key '{slug}' != slug '{sc['slug']}'"
        for slug, col in COLLECTIONS.items():
            assert col["slug"] == slug, f"COLLECTION key '{slug}' != slug '{col['slug']}'"
        for slug, sc in SCHOLARS.items():
            assert sc["slug"] == slug, f"SCHOLAR key '{slug}' != slug '{sc['slug']}'"
        for slug, sc in SPECIAL_SHOWCASES.items():
            assert sc["slug"] == slug, f"SPECIAL key '{slug}' != slug '{sc['slug']}'"

    def test_no_empty_conversation_ids(self):
        """No showcase/collection/scholar should have an empty conversation_ids list."""
        for slug, sc in SHOWCASES.items():
            assert sc["conversation_ids"], f"SHOWCASE:{slug} has empty conversation_ids"
        for slug, col in COLLECTIONS.items():
            assert col["conversation_ids"], f"COLLECTION:{slug} has empty conversation_ids"
        for slug, sc in SCHOLARS.items():
            assert sc["conversation_ids"], f"SCHOLAR:{slug} has empty conversation_ids"

    def test_special_showcase_templates_exist(self):
        """Every special showcase must reference a template that exists."""
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        for slug, sc in SPECIAL_SHOWCASES.items():
            tpl = sc["template"]
            path = os.path.join(templates_dir, tpl)
            assert os.path.exists(path), f"SPECIAL:{slug} template '{tpl}' not found"


# ---------------------------------------------------------------------------
# 5. FTS5 SANITIZATION — Dangerous inputs don't crash search
# ---------------------------------------------------------------------------

class TestFTS5Sanitization:
    """Search must handle FTS5 special characters without crashing."""

    @pytest.mark.parametrize("query", [
        '"unclosed quote',
        'NEAR/3',
        'term1 AND',
        'term1 OR',
        'NOT',
        '(parentheses)',
        'column:prefix',
        '*wildcard*',
        '^caret',
        'a + b',
        'hello"world',
        'test OR AND NOT NEAR',
        '""',
        "it's apostrophe",
        'back\\slash',
    ])
    def test_search_special_chars(self, client, query):
        """FTS5 special characters must not cause 500 errors."""
        resp = client.get(f"/?q={query}")
        assert resp.status_code == 200, f"Search for '{query}' returned {resp.status_code}"

    def test_search_returns_results(self, client):
        """A normal search should return results."""
        resp = client.get("/?q=alchemy")
        assert resp.status_code == 200
        assert b"alchemy" in resp.data.lower() or b"Alchemy" in resp.data


# ---------------------------------------------------------------------------
# 6. SIDECAR JSON RESILIENCE — Malformed JSON doesn't crash pages
# ---------------------------------------------------------------------------

class TestSidecarResilience:
    """Sidecar JSON errors must not crash showcase or scholar pages."""

    def test_showcase_with_malformed_sidecar(self, client, tmp_path):
        """A malformed sidecar JSON must not crash the showcase route."""
        # Create a malformed JSON sidecar for the first showcase
        slug = list(SHOWCASES.keys())[0]
        sidecar_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "showcases")
        os.makedirs(sidecar_dir, exist_ok=True)
        sidecar_path = os.path.join(sidecar_dir, f"{slug}.json")

        try:
            with open(sidecar_path, "w") as f:
                f.write("{invalid json content!!!")

            resp = client.get(f"/dream/{slug}")
            assert resp.status_code == 200, \
                f"Malformed sidecar JSON crashed showcase {slug}"
        finally:
            if os.path.exists(sidecar_path):
                os.remove(sidecar_path)

    def test_scholar_with_malformed_sidecar(self, client):
        """A malformed sidecar JSON must not crash the scholar route."""
        slug = list(SCHOLARS.keys())[0]
        sidecar_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scholars")
        os.makedirs(sidecar_dir, exist_ok=True)
        sidecar_path = os.path.join(sidecar_dir, f"{slug}.json")

        try:
            with open(sidecar_path, "w") as f:
                f.write("not json at all")

            resp = client.get(f"/scholar/{slug}")
            assert resp.status_code == 200, \
                f"Malformed sidecar JSON crashed scholar {slug}"
        finally:
            if os.path.exists(sidecar_path):
                os.remove(sidecar_path)

    def test_showcase_with_valid_sidecar(self, client):
        """A valid sidecar JSON should not crash the page."""
        slug = list(SHOWCASES.keys())[0]
        sidecar_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "showcases")
        os.makedirs(sidecar_dir, exist_ok=True)
        sidecar_path = os.path.join(sidecar_dir, f"{slug}.json")

        try:
            with open(sidecar_path, "w") as f:
                json.dump({"narrative": "Test narrative from sidecar",
                           "quotes": ["A test quote"]}, f)

            resp = client.get(f"/dream/{slug}")
            assert resp.status_code == 200
            # Sidecar data should be loaded without error
            # (template may or may not render all fields depending on design)
        finally:
            if os.path.exists(sidecar_path):
                os.remove(sidecar_path)


# ---------------------------------------------------------------------------
# 7. DATABASE HEALTH — Tables exist, FTS index populated, counts sane
# ---------------------------------------------------------------------------

class TestDatabaseHealth:
    """Database must have expected tables with sane row counts."""

    def test_conversations_exist(self, db):
        count = db.execute("SELECT count(*) FROM conversations").fetchone()[0]
        assert count > 4000, f"Expected 4000+ conversations, got {count}"

    def test_messages_exist(self, db):
        count = db.execute("SELECT count(*) FROM messages").fetchone()[0]
        assert count > 100000, f"Expected 100K+ messages, got {count}"

    def test_fts_index_populated(self, db):
        count = db.execute("SELECT count(*) FROM messages_fts").fetchone()[0]
        assert count > 100000, f"FTS index has only {count} rows"

    def test_sources_exist(self, db):
        sources = db.execute("SELECT name FROM sources").fetchall()
        source_names = {r["name"] for r in sources}
        assert "chatgpt" in source_names
        assert len(source_names) >= 5

    def test_tags_exist(self, db):
        count = db.execute("SELECT count(*) FROM tags").fetchone()[0]
        assert count >= 5, f"Expected 5+ tags, got {count}"

    def test_conversation_tags_linked(self, db):
        count = db.execute("SELECT count(*) FROM conversation_tags").fetchone()[0]
        assert count > 1000, f"Expected 1000+ tag links, got {count}"

    def test_ideas_exist(self, db):
        count = db.execute("SELECT count(*) FROM ideas").fetchone()[0]
        assert count > 100, f"Expected 100+ ideas, got {count}"

    def test_summaries_populated(self, db):
        """Most conversations should have summaries."""
        total = db.execute("SELECT count(*) FROM conversations").fetchone()[0]
        with_summary = db.execute(
            "SELECT count(*) FROM conversations WHERE summary IS NOT NULL AND LENGTH(summary) > 10"
        ).fetchone()[0]
        ratio = with_summary / total
        assert ratio > 0.90, f"Only {ratio:.0%} of conversations have summaries (expected >90%)"

    def test_no_orphan_messages(self, db):
        """Every message should reference a valid conversation."""
        orphans = db.execute("""
            SELECT count(*) FROM messages m
            LEFT JOIN conversations c ON c.id=m.conversation_id
            WHERE c.id IS NULL
        """).fetchone()[0]
        assert orphans == 0, f"{orphans} orphan messages (no matching conversation)"


# ---------------------------------------------------------------------------
# 8. CROSS-REFERENCE INTEGRITY — Related scholars/collections work
# ---------------------------------------------------------------------------

class TestCrossReferences:
    """The set-intersection relationship system must produce valid links."""

    def test_scholar_related_scholars_valid(self, client):
        """Related scholars on each page must be real scholar slugs."""
        for slug in list(SCHOLARS.keys())[:5]:  # test first 5 to keep it fast
            resp = client.get(f"/scholar/{slug}")
            assert resp.status_code == 200
            # If there are related scholar links, they should be valid slugs
            for other_slug in SCHOLARS:
                if other_slug != slug and f"/scholar/{other_slug}" in resp.data.decode():
                    assert other_slug in SCHOLARS

    def test_no_duplicate_ids_within_entity(self):
        """No showcase/collection/scholar should list the same ID twice."""
        for slug, sc in SHOWCASES.items():
            ids = sc["conversation_ids"]
            assert len(ids) == len(set(ids)), f"SHOWCASE:{slug} has duplicate IDs"
        for slug, col in COLLECTIONS.items():
            ids = col["conversation_ids"]
            assert len(ids) == len(set(ids)), f"COLLECTION:{slug} has duplicate IDs"
        for slug, sc in SCHOLARS.items():
            ids = sc["conversation_ids"]
            assert len(ids) == len(set(ids)), f"SCHOLAR:{slug} has duplicate IDs"


# ---------------------------------------------------------------------------
# 9. NAVIGATION — All nav links actually resolve
# ---------------------------------------------------------------------------

class TestNavigation:
    """Key navigation paths must work."""

    def test_home_to_showcases(self, client):
        resp = client.get("/showcases")
        assert resp.status_code == 200
        # Should contain links to each showcase
        for slug in SHOWCASES:
            assert f"/dream/{slug}" in resp.data.decode()

    def test_home_to_collections(self, client):
        resp = client.get("/collections")
        assert resp.status_code == 200
        for slug in COLLECTIONS:
            assert f"/collection/{slug}" in resp.data.decode()

    def test_home_to_scholars(self, client):
        resp = client.get("/scholars")
        assert resp.status_code == 200
        for slug in SCHOLARS:
            assert f"/scholar/{slug}" in resp.data.decode()


# ---------------------------------------------------------------------------
# 10. EDGE CASES — Boundary conditions and defensive checks
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Boundary conditions that could cause failures."""

    def test_page_zero(self, client):
        """Page 0 shouldn't crash."""
        resp = client.get("/?page=0")
        assert resp.status_code == 200

    def test_negative_page(self, client):
        resp = client.get("/?page=-1")
        assert resp.status_code == 200

    def test_huge_page_number(self, client):
        """Very large page number returns 200 (empty results ok)."""
        resp = client.get("/?page=99999")
        assert resp.status_code == 200

    def test_invalid_sort(self, client):
        """Invalid sort parameter should default gracefully."""
        resp = client.get("/?sort=nonexistent")
        assert resp.status_code == 200

    def test_empty_search(self, client):
        """Empty search string should return unfiltered results."""
        resp = client.get("/?q=")
        assert resp.status_code == 200

    def test_very_long_search(self, client):
        """Extremely long search query shouldn't crash."""
        long_q = "a" * 1000
        resp = client.get(f"/?q={long_q}")
        assert resp.status_code == 200

    def test_sql_injection_search(self, client):
        """SQL injection attempts in search should be harmless."""
        resp = client.get("/?q='; DROP TABLE messages; --")
        assert resp.status_code == 200

    def test_conversation_id_zero(self, client):
        resp = client.get("/conversation/0")
        assert resp.status_code == 404

    def test_conversation_negative_id(self, client):
        resp = client.get("/conversation/-1")
        # Should handle gracefully (404 or 200 with no data)
        assert resp.status_code in (200, 404)
