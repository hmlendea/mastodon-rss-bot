# Testing

## Overview

This document describes the current testing state and defines the target testing architecture for the mastodon-rss-bot application.

## Current State

| Property | Value |
|----------|-------|
| Test framework | None |
| Test files | None |
| Test coverage | 0% |
| CI/CD | None |
| Test dependencies | None |
| Test data | None |

**No tests exist** — The repository contains no test files, no test configuration, no CI pipeline.

## Target Architecture

### Test Framework

**Framework**: `pytest` (industry standard, minimal boilerplate)

**Structure**:
```
tests/
├── unit/
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_utils.py
│   └── test_main.py
├── integration/
│   ├── test_pipeline.py
│   └── test_mastodon_api.py
├── fixtures/
│   ├── sample_feed.xml
│   ├── sample_page.html
│   └── sample_config.json
├── conftest.py
└── requirements.txt
```

### Test Categories

#### 1. Unit Tests

**Scope**: Individual functions in isolation
**Speed**: Milliseconds per test
**Dependencies**: Mocked (no network, no DB, no Mastodon)

| Module | Functions to Test | Test Count (est.) |
|--------|-------------------|-------------------|
| `config.py` | `load_config()` | 5 |
| `database.py` | `init_db()`, `get_last_entry_posted()`, `save_posted_entry()` | 8 |
| `utils.py` | `detect_language()`, `try_import()` | 10 |
| `main.py` | `parse_args()`, hashing, date parsing, title extraction, ad filter, link processing, truncation | 25 |

#### 2. Integration Tests

**Scope**: Module interactions, external service contracts
**Speed**: Seconds per test
**Dependencies**: Local SQLite, mocked HTTP (responses library)

| Scenario | Description |
|----------|-------------|
| Full pipeline (mocked) | Feed → entries → toots (all external mocked) |
| Database round-trip | Insert → query → verify |
| Config loading | Sample config → constants |
| Media upload flow | Mock Mastodon API |

#### 3. End-to-End Tests (Manual)

**Scope**: Full system with real external services
**Frequency**: Before releases
**Dependencies**: Real Mastodon instance, real RSS feed

| Scenario | Description |
|----------|-------------|
| Happy path | Valid feed → toots posted → cache updated |
| Deduplication | Run twice → second run posts nothing |
| Age filter | Old entries skipped |
| Media posting | Entry with images → media uploaded |

## Unit Test Specifications

### `test_config.py`

```python
class TestLoadConfig:
    def test_creates_config_from_sample_when_missing(self, tmp_path):
        """When config.json absent, copies sample.config.json."""
        # Arrange: tmp_path with sample.config.json, no config.json
        # Act: load_config()
        # Assert: config.json exists, constants set to defaults

    def test_loads_existing_config(self, tmp_path):
        """When config.json present, loads values."""
        # Arrange: tmp_path with config.json (custom values)
        # Act: load_config()
        # Assert: constants match custom values

    def test_raises_on_malformed_json(self, tmp_path):
        """Malformed config.json raises JSONDecodeError."""
        # Arrange: config.json with invalid JSON
        # Act/Assert: pytest.raises(json.JSONDecodeError)

    def test_raises_on_missing_keys(self, tmp_path):
        """Missing required keys raise KeyError."""
        # Arrange: config.json with {} (empty)
        # Act/Assert: pytest.raises(KeyError)

    def test_monetise_links_defaults_true(self, tmp_path):
        """monetise_links missing defaults to True."""
        # Arrange: config.json without monetise_links key
        # Act: load_config()
        # Assert: MONETISE_LINKS is True
```

### `test_database.py`

```python
class TestInitDb:
    def test_creates_entries_table(self, tmp_path):
        """init_db creates entries table with correct schema."""
        # Arrange: tmp_path/cache.db
        # Act: init_db()
        # Assert: table exists with 5 TEXT columns

    def test_idempotent(self, tmp_path):
        """Calling init_db twice does not error."""
        # Arrange: init_db() already called
        # Act: init_db() again
        # Assert: no exception

class TestGetLastEntryPosted:
    def test_returns_none_for_unknown_hash(self, db):
        """Unknown hash returns None."""
        # Act: get_last_entry_posted(db, "unknown")
        # Assert: result is None

    def test_returns_row_for_known_hash(self, db, entry):
        """Known hash returns row."""
        # Arrange: save_posted_entry(db, entry)
        # Act: get_last_entry_posted(db, entry.hash)
        # Assert: row matches entry

class TestSavePostedEntry:
    def test_inserts_row(self, db, entry):
        """save_posted_entry inserts row."""
        # Act: save_posted_entry(db, entry)
        # Assert: get_last_entry_posted returns row

    def test_raises_on_duplicate_hash(self, db, entry):
        """Duplicate hash raises IntegrityError."""
        # Arrange: save_posted_entry(db, entry)
        # Act/Assert: pytest.raises(sqlite3.IntegrityError)
```

### `test_utils.py`

```python
class TestDetectLanguage:
    def test_detects_romanian_diacritics(self):
        """Text with diacritics returns 'ro'."""
        # Act: detect_language("Și eu am fost acolo")
        # Assert: result == 'ro'

    def test_detects_romanian_keywords(self):
        """Text with RO keywords returns 'ro'."""
        # Act: detect_language("pentru cu și în")
        # Assert: result == 'ro'

    def test_detects_english(self):
        """English text returns 'en'."""
        # Act: detect_language("the and for with")
        # Assert: result == 'en'

    def test_defaults_english_on_empty(self):
        """Empty text returns 'en'."""
        # Act: detect_language("")
        # Assert: result == 'en'

class TestTryImport:
    def test_returns_module_when_exists(self):
        """Existing module returns module object."""
        # Act: try_import('json')
        # Assert: result is json module

    def test_returns_none_when_missing(self):
        """Missing module returns None."""
        # Act: try_import('nonexistent_module_xyz')
        # Assert: result is None
```

### `test_main.py`

```python
class TestParseArgs:
    def test_required_args_parsed(self):
        """All required args parsed correctly."""
        # Arrange: sys.argv with all required args
        # Act: parse_args()
        # Assert: namespace attributes match

    def test_missing_required_arg_exits(self):
        """Missing required arg exits with error."""
        # Arrange: sys.argv without --rss
        # Act/Assert: pytest.raises(SystemExit)

class TestIdentityHashing:
    def test_same_input_same_hash(self):
        """Same title+link+published produces same hash."""
        # Act: hash twice
        # Assert: hashes equal

    def test_different_input_different_hash(self):
        """Different input produces different hash."""
        # Act: hash two different entries
        # Assert: hashes differ

class TestDateParsing:
    def test_parses_rfc2822_with_timezone(self):
        """RFC 2822 with %z parses."""
        # Act: parse("Mon, 15 Jan 2024 10:30:00 +0000")
        # Assert: datetime object

    def test_parses_iso8601(self):
        """ISO 8601 parses."""
        # Act: parse("2024-01-15T10:30:00+00:00")
        # Assert: datetime object

    def test_returns_none_on_unparseable(self):
        """Unparseable date returns None."""
        # Act: parse("not a date")
        # Assert: None

class TestTitleExtraction:
    def test_prefers_og_title(self):
        """og:title preferred over <title>."""
        # Arrange: HTML with both
        # Act: extract_title(soup, feed_title)
        # Assert: og:title returned

    def test_falls_back_to_title_tag(self):
        """<title> used when no og:title."""
        # Arrange: HTML with <title> only
        # Act: extract_title(soup, feed_title)
        # Assert: <title> returned

    def test_falls_back_to_feed_title(self):
        """Feed title used when no HTML title."""
        # Arrange: empty HTML
        # Act: extract_title(soup, feed_title)
        # Assert: feed_title returned

class TestAdFilter:
    def test_filters_ad_in_title(self):
        """Title containing 'ad' is filtered."""
        # Act: is_ad("Special Ad Offer")
        # Assert: True

    def test_passes_clean_title(self):
        """Clean title passes."""
        # Act: is_ad("News Article")
        # Assert: False

class TestLinkProcessing:
    def test_shortlink_calls_is_gd(self, requests_mock):
        """USE_SHORTLINK triggers is.gd request."""
        # Arrange: requests_mock with is.gd response
        # Act: process_link(url, use_shortlink=True)
        # Assert: shortened URL returned

    def test_privacy_frontends_rewrite_domains(self):
        """USE_PRIVACY_FRONTENDS rewrites domains."""
        # Act: process_link("https://reddit.com/r/test", privacy=True)
        # Assert: "libreddit.kavin.rocks" in result

    def test_monetisation_wraps_link(self):
        """MONETISE_LINKS wraps with ShrinkMe."""
        # Act: process_link(url, monetise=True)
        # Assert: "shrinkme.io" in result

class TestTruncation:
    def test_truncates_to_500_chars(self):
        """Status >500 chars truncated to 500."""
        # Act: truncate(status_600_chars)
        # Assert: len(result) == 500

    def test_preserves_short_status(self):
        """Status <=500 chars unchanged."""
        # Act: truncate(status_100_chars)
        # Assert: result == original
```

## Integration Test Specifications

### `test_pipeline.py`

```python
class TestFullPipeline:
    def test_posts_new_entries(self, mock_feed, mock_mastodon, tmp_path):
        """New entries are posted and cached."""
        # Arrange: mock feed with 3 entries, empty cache
        # Act: run pipeline
        # Assert: 3 status_post calls, 3 cache inserts

    def test_skips_cached_entries(self, mock_feed, mock_mastodon, db_with_entries):
        """Cached entries are skipped."""
        # Arrange: mock feed, cache with all entry hashes
        # Act: run pipeline
        # Assert: 0 status_post calls

    def test_skips_old_entries(self, mock_feed_old, mock_mastodon, db):
        """Entries older than days_to_check skipped."""
        # Arrange: feed with old entries, days_to_check=1
        # Act: run pipeline
        # Assert: 0 status_post calls

    def test_respects_maximum_toots_count(self, mock_feed_large, mock_mastodon, db):
        """Pipeline stops after MAXIMUM_TOOTS_COUNT."""
        # Arrange: feed with 20 entries, MAXIMUM_TOOTS_COUNT=5
        # Act: run pipeline
        # Assert: 5 status_post calls

    def test_failed_post_not_cached(self, mock_feed, mock_mastodon_error, db):
        """Failed posts are not cached (retry next run)."""
        # Arrange: mock Mastodon raising on status_post
        # Act: run pipeline
        # Assert: 0 cache inserts
```

## Test Fixtures

### `fixtures/sample_feed.xml`

RSS 2.0 feed with 5 entries:
- 1 with og:image
- 1 with enclosure
- 1 with Twitter link
- 1 with Reddit link
- 1 with ad in title

### `fixtures/sample_page.html`

HTML page with:
- `<meta property="og:title">`
- `<meta property="og:image">`
- `<title>` tag
- Tracking parameters in links

### `fixtures/sample_config.json`

Valid config with all 7 keys set to non-default values.

### `conftest.py`

```python
import pytest
import sqlite3
import tempfile
import os

@pytest.fixture
def db():
    """In-memory SQLite database with entries table."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE entries (
            entry_hash TEXT PRIMARY KEY,
            entry_title TEXT,
            entry_link TEXT,
            entry_published TEXT,
            entry_author TEXT
        )
    """)
    conn.commit()
    yield conn, cursor
    conn.close()

@pytest.fixture
def tmp_working_dir(tmp_path, monkeypatch):
    """Temporary working directory with sample config."""
    monkeypatch.chdir(tmp_path)
    # Copy sample.config.json
    shutil.copy("sample.config.json", "config.json")
    return tmp_path

@pytest.fixture
def mock_mastodon(mocker):
    """Mock Mastodon client."""
    client = mocker.MagicMock()
    client.media_post.return_value = {'id': '123'}
    client.status_post.return_value = {'id': '456'}
    return client
```

## Test Data

### Standard Test Values

Per the project's test-value standards:

| Category | Value |
|----------|-------|
| Feed URL | `https://example.com/feed.xml` |
| Mastodon instance | `mastodon.social` |
| Username | `IlarionPintilie` |
| Access token | `test_token_abc123` (never real) |
| Entry title | `Test News Article` |
| Entry link | `https://example.com/article/123` |
| Entry hash | `d41d8cd98f00b204e9800998ecf8427e` (MD5 of empty) |
| Published date | `Mon, 15 Jan 2024 10:30:00 +0000` |
| Author | `Ilarion Pintilie` |
| Tags | `news,tech` |
| Days to check | `7` |

### Personal Names (from test-values standards)

- `Ilarion Pintilie` — Primary test author
- `John Doe` — Alternative test author
- `Ionuț Karr` — Romanian test author
- `Robert Blitz` — Alternative test author

### Usernames (from test-values standards)

- `IlarionPintilie` — Primary test username
- `solaire_of_astora` — Alternative test username
- `Angetenar` — Alternative test username

### Integers (from test-values standards)

- `7` — Days to check
- `10` — Maximum toots count
- `42` — Generic test integer
- `256` — Generic test integer

## Coverage Targets

| Module | Target Coverage |
|--------|----------------|
| `config.py` | 90% |
| `database.py` | 90% |
| `utils.py` | 90% |
| `main.py` | 70% (hard to test external calls) |
| **Overall** | **80%** |

## CI/CD Integration (Future)

### GitHub Actions Workflow

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov pytest-mock responses
      - run: pytest tests/ --cov=. --cov-report=xml
      - run: coverage report --fail-under=80
```

### Pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

## Test Execution

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=. --cov-report=html

# Verbose
pytest -v

# Specific test
pytest tests/unit/test_utils.py::TestDetectLanguage::test_detects_romanian_diacritics
```

### Test Dependencies

```
# tests/requirements.txt
pytest>=7.0
pytest-cov>=4.0
pytest-mock>=3.11
responses>=0.23
```

## Migration Checklist

- [ ] Create `tests/` directory structure
- [ ] Add `tests/requirements.txt`
- [ ] Create `conftest.py` with fixtures
- [ ] Create test fixtures (feed XML, HTML, config)
- [ ] Write unit tests for `config.py`
- [ ] Write unit tests for `database.py`
- [ ] Write unit tests for `utils.py`
- [ ] Write unit tests for `main.py` (pure functions)
- [ ] Write integration tests for pipeline
- [ ] Add coverage reporting
- [ ] Add CI workflow
- [ ] Add pre-commit hooks
- [ ] Document test execution in CONTRIBUTING.md

## Related Documentation

- [Error Handling](../error-handling.md) — Error paths to test
- [Logging](../logging.md) — Log assertions in tests
- [Build and Deployment](../build-and-deployment.md) — CI integration
- [Contributing](../CONTRIBUTING.md) — Developer workflow