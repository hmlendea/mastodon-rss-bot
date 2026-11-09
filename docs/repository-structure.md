# Repository Structure

## Source Tree Layout

```
mastodon-rss-bot/
├── main.py                 # Pipeline orchestrator, CLI entry point
├── config.py               # Configuration loader (config.json → module constants)
├── database.py             # SQLite persistence layer (cache.db)
├── utils.py                # Language detection, dynamic module import
├── config.json             # Runtime configuration (seeded from sample.config.json)
├── sample.config.json      # Configuration template
├── requirements.txt        # Python dependencies
├── README.md               # Usage, deployment, architecture overview
├── ARCHITECTURE.md         # Root architecture document
├── CONTRIBUTING.md         # Contribution guidelines
├── PRIVACY.md              # Privacy and data handling
├── SECURITY.md             # Security policy
├── CODE_OF_CONDUCT.md      # Community conduct standards
├── LICENSE                 # GNU GPL v3+
├── cache.db                # SQLite deduplication cache (created at runtime)
├── app_<instance>.secret   # Mastodon app credentials (created at runtime)
├── dynamic_tags.py         # Optional: dynamic hashtag generator (operator-provided)
├── text_replacements.py    # Optional: text transformation module (operator-provided)
└── run.sh                  # Referenced in systemd unit; NOT in repository (operator-provided)
```

## Module Organisation

### Core Modules (always present)

| File | Role | Public API |
|------|------|------------|
| `main.py` | Pipeline orchestrator, CLI entry point | Module-level execution; `parse_args()` |
| `config.py` | Configuration loader | `load_config()`, module constants: `INCLUDE_AUTHOR`, `INCLUDE_LINK`, `INCLUDE_LINK_THUMBNAIL`, `USE_PRIVACY_FRONTENDS`, `USE_SHORTLINK`, `MONETISE_LINKS`, `MAXIMUM_TOOTS_COUNT` |
| `database.py` | SQLite persistence | `init_db() → (connection, cursor)`, `get_last_entry_posted(cursor, entry_id, username, instance) → row`, `save_posted_entry(connection, cursor, feed_entry_id, toot_id, feed_url, username, instance)` |
| `utils.py` | Utilities | `determine_content_language(text) → 'en'|'ro'`, `try_import(filepath, module_name) → module|None` |

### Configuration Files

| File | Purpose | Lifecycle |
|------|---------|-----------|
| `sample.config.json` | Template with documented keys and defaults | Committed; source of truth for schema |
| `config.json` | Runtime configuration | Created from sample on first run; operator-edited |
| `cache.db` | Deduplication cache (SQLite) | Created by `database.init_db()`; one row per posted entry |
| `app_<instance>.secret` | Mastodon app credentials | Created by `Mastodon.create_app()` on first run |

### Optional Extension Modules (operator-provided)

| File | Required API | Loaded By |
|------|--------------|-----------|
| `dynamic_tags.py` | `get(toot_body: str, toot_language: str) → str` | `utils.try_import()` in `main.py` |
| `text_replacements.py` | `apply(text: str, language: str) → str` | `utils.try_import()` in `main.py` |

### Documentation Files (repository root)

| File | Purpose |
|------|---------|
| `README.md` | Usage, systemd deployment, configuration, privacy table, architecture summary |
| `ARCHITECTURE.md` | System context, architectural style, runtime process, components, data architecture, interfaces, toot construction, cross-cutting concerns, dependencies, deployment, compatibility, testing, constraints, extensions |
| `CONTRIBUTING.md` | Issue reporting, enhancements, code contributions, style, documentation |
| `PRIVACY.md` | Data handling, self-hosted deployments, data categories, processing, storage, integrations, protection |
| `SECURITY.md` | Supported versions, vulnerability reporting, scope, disclosure policy |
| `CODE_OF_CONDUCT.md` | Expected/unacceptable conduct, moderation, reporting, enforcement |
| `LICENSE` | GNU GPL v3+ |

### Generated Documentation (docs/)

```
docs/
├── INDEX.md                          # Master index and navigation
├── architecture.md                   # Detailed architecture (complements root ARCHITECTURE.md)
├── repository-overview.md            # Purpose, scope, entry points, capabilities
├── repository-structure.md           # This file
├── configuration.md                  # Configuration schema, sources, precedence
├── data-model.md                     # Domain entities, relationships, persistence
├── dependencies.md                   # External and internal dependencies
├── design-decisions.md               # Key architectural choices and rationale
├── error-handling.md                 # Error taxonomy, handling patterns, recovery
├── logging.md                        # Logging framework, levels, sinks, redaction
├── security.md                       # Security model, threats, mitigations
├── state-and-persistence.md          # State management, cache, migrations
├── testing.md                        # Test strategy, coverage gaps, verification
├── concurrency-and-scheduling.md     # Threading, async, schedulers, locks
├── build-and-deployment.md           # Build pipeline, deployment, environments
├── change-guide.md                   # Safe modification patterns
├── api-usage-examples.md             # CLI and API examples
├── ambiguities-and-open-questions.md # Unresolved items, TODOs, gaps
├── faq.md                            # Frequently asked questions
├── troubleshooting.md                # Common issues and solutions
├── documentation-maintenance.md      # Doc maintenance process
├── invariants.md                     # System-wide invariants and contracts
├── integrations.md                   # External integration details
├── quick-start.md                    # Getting started guide
├── api-reference/
│   ├── INDEX.md                      # API reference index
│   └── main-pipeline.md              # Main pipeline orchestration
├── components/
│   ├── presentation.md               # Main pipeline orchestration
│   ├── host-and-composition.md       # Process topology, scheduling
│   ├── application-services.md       # Config, database, utilities
│   ├── browser-state-and-localisation.md # Language, replacements, tags
│   └── integration-models.md         # RSS, pages, Mastodon, frontends
└── flows/
    ├── startup-and-rendering.md      # Startup, config, client init, feed retrieval
    ├── calendar-search.md            # Entry iteration, dedup, age filter, enrichment
    └── detail-mutation.md            # Media upload, toot assembly, posting, cache
```

## File Responsibilities Summary

### `main.py` — Pipeline Orchestrator

**Owns:**
- CLI argument parsing (`argparse`)
- Mastodon app credential creation (`Mastodon.create_app()`)
- Mastodon API client authentication
- Feed retrieval and parsing (`feedparser`)
- Entry iteration (reverse chronological order)
- Entry identity derivation (MD5 hash of id/link/title/date)
- Deduplication lookup (`database.get_last_entry_posted()`)
- Age window filtering (`--days-to-check`)
- Linked page fetching (`urllib` + rotating User-Agent)
- Title extraction (Twitter description → entry title → page title/og:title)
- Advertisement filter (`(P)` in title)
- Missing title detection (regex pattern)
- Media URL collection (Twitter→Nitter, Reddit, OG image, feed enclosures)
- Media upload (`requests.get()` → `mastodon.media_post()`)
- Link processing (shortlink, privacy frontends, cleanup, monetisation)
- Author inclusion (`INCLUDE_AUTHOR`)
- Tag aggregation (CLI + dynamic_tags)
- Tag filtering (exclude tags already in body)
- Language detection (`utils.determine_content_language()`)
- Text replacements (`text_replacements.apply()`)
- Character limit management (contractions + truncation)
- Status posting (`mastodon.status_post()`)
- Cache persistence (`database.save_posted_entry()`)
- Maximum toots limit (`MAXIMUM_TOOTS_COUNT`)
- Progress logging to stdout

### `config.py` — Configuration Loader

**Owns:**
- `config.json` loading with `sample.config.json` fallback
- Module-level constant exposure for all configuration keys
- `MONETISE_LINKS` default to `True` when absent

### `database.py` — Persistence Layer

**Owns:**
- SQLite connection to `cache.db`
- `entries` table schema creation (5 TEXT columns)
- Duplicate lookup by composite key (entry_id, username, instance)
- Posted entry insertion (never update/delete)

### `utils.py` — Utility Services

**Owns:**
- Language detection heuristics (Romanian diacritics, English/Romanian keywords)
- Safe dynamic module import (`importlib.util`)

## Runtime-Generated Files

| File | Created By | Purpose |
|------|------------|---------|
| `config.json` | `config.py` (first run) | Runtime configuration |
| `cache.db` | `database.init_db()` | Deduplication cache |
| `app_<instance>.secret` | `Mastodon.create_app()` | Mastodon app credentials |

## Missing from Repository (Operator-Provided)

| File | Referenced By | Purpose |
|------|---------------|---------|
| `run.sh` | README.md systemd unit | Wrapper script for systemd service |
| `dynamic_tags.py` | `main.py` via `utils.try_import()` | Optional dynamic hashtags |
| `text_replacements.py` | `main.py` via `utils.try_import()` | Optional text transformations |