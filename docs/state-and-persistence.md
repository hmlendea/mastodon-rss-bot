# State and Persistence

## Overview

This document describes the state management, persistence mechanisms, and data lifecycle of the mastodon-rss-bot application.

## State Model

### State Categories

| Category | Storage | Lifetime | Scope |
|----------|---------|----------|-------|
| **Configuration** | `config.json` | Persistent | Application |
| **Credentials** | `app_<instance>.secret` | Persistent | Application |
| **Posted entries cache** | `cache.db` (SQLite) | Persistent | Feed + Instance |
| **Runtime state** | In-memory variables | Single run | Process |
| **Secrets** | CLI args / env | Process | Run |

### State Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION STATE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  config.json │    │ app_*.secret │    │   cache.db   │      │
│  │  (settings)  │    │ (credentials)│    │  (dedup)     │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    RUNTIME STATE                         │   │
│  │  • config dict (loaded)                                  │   │
│  │  • Mastodon client (authenticated)                       │   │
│  │  • DB connection (open)                                  │   │
│  │  • Feed entries (parsed)                                 │   │
│  │  • Current entry (processing)                            │   │
│  │  • Media files (temp, deleted after upload)              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Persistent State

### 1. Configuration File (`config.json`)

**Purpose**: Runtime configuration
**Created by**: `load_config()` in `config.py`
**Format**: JSON
**Schema**: See [Configuration](./configuration.md)

**Lifecycle**:
1. First run: copied from `sample.config.json`
2. Subsequent runs: loaded as-is
3. Updates: manual edit only (no auto-update)

**State Transitions**:
```
[Missing] --first run--> [Copied from sample] --user edit--> [Custom]
```

### 2. Mastodon App Credentials (`app_<instance>.secret`)

**Purpose**: OAuth app credentials (client_id, client_secret)
**Created by**: `Mastodon.create_app()` in `main.py`
**Format**: JSON
**Naming**: `app_<instance_domain>.secret`

**Lifecycle**:
1. First run: created via Mastodon API
2. Subsequent runs: loaded from file
3. Updates: never (delete to re-create)

**State Transitions**:
```
[Missing] --create_app()--> [Created] --[never updated]--> [Stale if revoked]
```

**Security**: Contains sensitive credentials — restrict file permissions.

### 3. Cache Database (`cache.db`)

**Purpose**: Deduplication — track posted entries
**Created by**: `init_db()` in `database.py`
**Format**: SQLite
**Schema**: See [Data Model](./data-model.md)

**Lifecycle**:
1. First run: created with `entries` table
2. Each run: read (dedup check) + write (new posts)
3. Updates: INSERT only (no UPDATE/DELETE)
4. Growth: unbounded (no cleanup)

**State Transitions**:
```
[Missing] --init_db()--> [Empty] --save_posted_entry()--> [Growing]
                                                      │
                                                      ▼
                                              [No cleanup → unbounded growth]
```

**Size Estimation**:
- Per row: ~200 bytes (5 TEXT columns)
- 10 entries/run × 365 days = 3,650 rows/year ≈ 730 KB/year
- Growth is slow; not a concern for years

## Runtime State

### In-Memory Variables

| Variable | Type | Scope | Lifetime |
|----------|------|-------|----------|
| `config` | dict | `main()` | Single run |
| `mastodon` | Mastodon client | `main()` | Single run |
| `feed` | feedparser object | `main()` | Single run |
| `db` | sqlite3.Connection | `main()` | Single run |
| `entry` | feedparser entry | Loop iteration | Single entry |
| `entry_id` | str (MD5 hash) | Loop iteration | Single entry |
| `entry_text` | str | Loop iteration | Single entry |
| `media_ids` | list | Loop iteration | Single entry |
| `media_files` | list | Loop iteration | Single entry |

### State Flow Within a Run

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Load Config │────▶│  Init DB     │────▶│  Auth        │
│  (dict)      │     │  (conn)      │     │  (client)    │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Post Status │◀────│  Assemble    │◀────│  Fetch Feed  │
│  (API call)  │     │  Text/Media  │     │  (entries)   │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  Save Cache  │────▶│  Next Entry  │
│  (INSERT)    │     │  or Exit     │
└──────────────┘     └──────────────┘
```

### State Mutations

| Mutation | Location | Trigger | Persistence |
|----------|----------|---------|-------------|
| Config load | `main()` | Run start | Memory only |
| DB connection | `main()` | Run start | Memory only |
| Mastodon auth | `main()` | Run start | Memory only |
| Feed parse | `main()` | Run start | Memory only |
| Entry processing | Loop body | Per entry | Memory only |
| Cache INSERT | `save_posted_entry()` | Per posted entry | Persistent (SQLite) |
| Media file write | `main.py` | Per media item | Temp file, deleted |
| Media file delete | `main.py` | After upload | File system |

## Data Lifecycle

### Entry Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Fetched │───▶│  Parsed  │───▶│  Filtered│───▶│  Enriched│
│  (feed)  │    │  (entry) │    │  (dedup) │    │  (page)  │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                     │
                                                     ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Cached  │◀───│  Posted  │◀───│  Assembled│◀───│  Media   │
│  (INSERT)│    │  (API)   │    │  (text)  │    │  (files) │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

**States**:
1. **Fetched** — Raw feed XML downloaded
2. **Parsed** — feedparser entry object
3. **Filtered** — Dedup check passed, age check passed
4. **Enriched** — Linked page fetched, title extracted
5. **Media collected** — Images/videos downloaded
6. **Assembled** — Final text + media IDs ready
7. **Posted** — Mastodon API returned status ID
8. **Cached** — INSERT into `entries` table

**Terminal State**: Cached (entry will never be re-processed)

### Media File Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  URL     │───▶│  Download│───▶│  Upload  │───▶│  Delete  │
│  (remote)│    │  (local) │    │  (API)   │    │  (local) │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

**States**:
1. **URL** — Remote media URL discovered
2. **Downloaded** — Saved to local temp file
3. **Uploaded** — Mastodon media ID obtained
4. **Deleted** — Local file removed

**Terminal State**: Deleted (no local persistence)

### Cache Entry Lifecycle

```
┌──────────┐
│  INSERT  │  (once, never modified)
└──────────┘
```

**States**:
1. **Inserted** — Row created with composite key
2. **Queried** — Read by `get_last_entry_posted()` for dedup

**Terminal State**: Inserted (immutable, never updated or deleted)

## Persistence Guarantees

### Write Semantics

| Operation | Atomicity | Durability | Consistency |
|-----------|-----------|------------|-------------|
| `save_posted_entry()` | SQLite transaction | WAL journal | Immediate |
| `init_db()` | DDL transaction | File system | Immediate |
| Config write | File write | File system | Immediate |
| App secret write | File write | File system | Immediate |

### Failure Scenarios

| Failure Point | State After | Recovery |
|---------------|-------------|----------|
| Before cache INSERT | Entry not cached | Re-run will re-post (duplicate) |
| After cache INSERT, before exit | Entry cached, posted | Normal — next run skips |
| During cache INSERT | SQLite transaction rollback | Entry not cached, re-posted |
| During media upload | Temp file remains | Orphaned temp file (cleanup needed) |
| During page fetch | No state change | Re-run retries |

### Duplicate Post Risk

**Window**: Between Mastodon post success and cache INSERT.

```
Post to Mastodon ──▶ [CRASH HERE] ──▶ Cache INSERT
       │                                    │
       ▼                                    ▼
  Status exists                    Entry not cached
  on Mastodon                      in cache.db
       │                                    │
       └────────── Next run ────────────────┘
                    │
                    ▼
            Entry re-processed
            → Duplicate post!
```

**Mitigation**: None currently. Recommendations:
1. Insert cache row BEFORE posting (with status_id placeholder)
2. Or: Use Mastodon status ID as dedup key
3. Or: Accept risk (low probability, manual cleanup)

## Cache Management

### Current: No Management

- No cleanup of old entries
- No size limits
- No vacuum
- No archive

### Recommended: Periodic Cleanup

```python
def cleanup_old_entries(db, days=90):
    """Delete entries older than N days."""
    cursor = db.cursor()
    cursor.execute("""
        DELETE FROM entries
        WHERE entry_published < date('now', ?)
    """, (f'-{days} days',))
    db.commit()
```

**Schedule**: Run monthly via separate maintenance script or timer.

### Recommended: Size Monitoring

```bash
# Check cache size
ls -lh cache.db

# Check row count
sqlite3 cache.db "SELECT COUNT(*) FROM entries;"

# Check oldest entry
sqlite3 cache.db "SELECT MIN(entry_published) FROM entries;"
```

## Configuration State

### Loading

```python
# config.py
config = json.load(open("config.json"))
INCLUDE_AUTHOR = config.get("include_author", False)
# ... etc
```

**Behavior**:
- Loaded once at import time
- Module-level constants
- No reload mechanism
- No validation

### Validation Gaps

| Gap | Risk | Recommendation |
|-----|------|----------------|
| No type checking | Wrong type → runtime error | Add schema validation |
| No range checking | Invalid values → unexpected behavior | Add bounds checking |
| No required key check | Missing key → default used silently | Add required key validation |
| No URL validation | Malformed URL → fetch failure | Add URL format validation |

## Related Documentation

- [Data Model](./data-model.md) — Cache schema details
- [Configuration](./configuration.md) — Configuration file details
- [Architecture](./architecture.md) — State in system context
- [Error Handling](./error-handling.md) — Failure scenarios
- [Concurrency and Scheduling](./concurrency-and-scheduling.md) — State access patterns
- [Troubleshooting](./troubleshooting.md) — State corruption recovery