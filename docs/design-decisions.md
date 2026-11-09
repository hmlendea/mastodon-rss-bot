# Design Decisions

## Overview

This document records the key design decisions in the mastodon-rss-bot codebase, their rationale, alternatives considered, and consequences.

## Decision Records

### DR-001: Single-Process, Sequential Architecture

**Decision**: The application runs as a single process with sequential, blocking execution.

**Context**: The bot processes RSS feed entries and posts them to Mastodon. Feeds typically contain few new entries per run (1-10).

**Rationale**:
- Simplicity: No concurrency bugs, no locking, no race conditions
- Debuggability: Linear execution, easy to trace
- Resource efficiency: Low CPU/memory footprint
- Mastodon rate limits: Sequential posting avoids hitting limits
- Feed size: Most feeds have few new entries per interval

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Multi-threading | Complexity, GIL limitations, no benefit for I/O-bound small workload |
| Asyncio | Library compatibility (feedparser, Mastodon.py are sync), complexity |
| Multiprocessing | Overhead, no benefit for sequential pipeline |
| Queue + workers | Over-engineering for current scale |

**Consequences**:
- ✅ Simple, reliable, easy to maintain
- ✅ No concurrency bugs possible
- ❌ Limited throughput (sequential network I/O)
- ❌ Slow for large feeds (many entries)
- ❌ One slow entry blocks all subsequent entries

**Revisit When**: Feed has >50 new entries per run, or run duration exceeds scheduler interval.

---

### DR-002: SQLite for Deduplication Cache

**Decision**: Use SQLite (`cache.db`) with a simple `entries` table for deduplication.

**Context**: Need to track which feed entries have been posted to avoid duplicates across runs.

**Rationale**:
- Zero configuration: No external database server required
- stdlib: `sqlite3` included in Python, no dependency
- ACID: Transactional guarantees for INSERT
- Portable: Single file, easy to backup/copy
- Sufficient: Simple key-value lookup pattern

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| JSON file | No atomic writes, corruption risk on crash |
| Redis | External dependency, overkill for single-process |
| PostgreSQL | External dependency, overkill |
| In-memory only | No persistence across runs |
| File per entry | File system overhead, no indexing |

**Consequences**:
- ✅ No external dependencies
- ✅ Atomic writes
- ✅ Easy backup (single file)
- ❌ No cleanup mechanism (unbounded growth)
- ❌ No migration framework
- ❌ No concurrent write support (single process only)
- ❌ Composite key includes `entry_link` (long TEXT, inefficient index)

**Revisit When**: Multiple processes need concurrent access, or cache exceeds 100MB.

---

### DR-003: MD5 for Entry Identity Hashing

**Decision**: Use MD5 hash of `entry.title + entry.link + entry.published` as entry identity.

**Context**: Need a stable, unique identifier for each feed entry to detect duplicates.

**Rationale**:
- Deterministic: Same input → same hash
- Stable: Doesn't change between runs
- Compact: 32-char hex string
- Available: `hashlib.md5` in stdlib
- Sufficient: Collision risk negligible for dedup use case

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| SHA-256 | Longer hash, no benefit for dedup |
| UUID | Not deterministic, changes each run |
| Raw concatenation | Variable length, indexing issues |
| Feed-provided GUID | Not always present, not always stable |

**Consequences**:
- ✅ Simple, deterministic
- ✅ No external dependency
- ❌ MD5 is cryptographically broken (irrelevant for dedup)
- ❌ Hash collision → missed duplicate (extremely unlikely)
- ❌ Title change → different hash → re-post (by design)

**Revisit When**: Security audit requires SHA-256, or feed GUIDs become reliable.

---

### DR-004: CLI Arguments for Runtime Configuration

**Decision**: Use `argparse` CLI arguments for feed URL, instance, credentials, and options.

**Context**: Need to configure the bot per run without code changes.

**Rationale**:
- Explicit: All parameters visible in command line
- Flexible: Different feeds/instances per invocation
- Scriptable: Easy to wrap in shell scripts
- Standard: argparse is stdlib, well-understood

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Environment variables | Less visible, harder to debug |
| Config file only | Less flexible for per-run variation |
| Interactive prompts | Not scriptable, breaks automation |
| YAML/TOML config | Additional dependency, more complex |

**Consequences**:
- ✅ Explicit, visible configuration
- ✅ Easy to script and automate
- ❌ Access token visible in `ps` output (security risk)
- ❌ Long command lines for many options
- ❌ No validation of argument values
- ❌ No secrets management

**Revisit When**: Security requirements mandate env vars or secret files.

---

### DR-005: Three-Tier Title Extraction

**Decision**: Extract page title with priority: OpenGraph `og:title` → first `<h1>` → `<title>`.

**Context**: Linked pages have varying HTML structures; need reliable title extraction.

**Rationale**:
- `og:title`: Explicitly designed for sharing, usually clean
- `<h1>`: Main heading, semantic meaning
- `<title>`: Browser title, may include site name or branding
- Priority order: Most specific → most general

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| `<title>` only | Often includes site name, too long |
| `<h1>` only | Not always present, may be empty |
| Meta `description` | Not a title, too long |
| ML-based extraction | Overkill, dependency |

**Consequences**:
- ✅ Robust across different page structures
- ✅ Clean titles for most pages
- ❌ Three HTTP parsing passes (BeautifulSoup)
- ❌ No fallback if all three fail (empty title)
- ❌ No title length limit (may exceed char budget)

**Revisit When**: Title extraction fails frequently, or pages use non-standard markup.

---

### DR-006: Hard-Coded Privacy Frontends

**Decision**: Hard-code privacy frontend URLs (Nitter, Redlib, etc.) in source code.

**Context**: Need to replace tracking links with privacy-respecting alternatives.

**Rationale**:
- Simple: No configuration needed
- Predictable: Known frontends, known behavior
- Maintainable: Easy to update in code review

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Config file | More flexible but adds config burden |
| Frontend discovery API | No standard API exists |
| User-provided list | More complex, error-prone |

**Consequences**:
- ✅ Simple, no configuration
- ✅ Works out of the box
- ❌ Frontends change URLs or go offline
- ❌ No fallback if frontend unavailable
- ❌ Requires code change to update frontends
- ❌ Single point of failure (one frontend per service)

**Revisit When**: Frontends frequently change, or users need custom frontends.

---

### DR-007: Hard-Coded ShrinkMe API Key

**Decision**: Embed ShrinkMe API key directly in `main.py` source code.

**Context**: Link shortening service requires API key for authentication.

**Rationale**:
- Simple: No configuration needed
- Works immediately: No setup step
- Low risk: Key has limited scope (link shortening only)

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Config file | Key exposed in plaintext file |
| Environment variable | Requires env setup, not documented |
| CLI argument | Visible in `ps` output |
| Secret manager | Overkill for this scale |

**Consequences**:
- ✅ Zero configuration
- ✅ Works out of the box
- ❌ Key exposed in source code (public repository)
- ❌ Key rotation requires code change
- ❌ Cannot use per-user keys
- ❌ Security anti-pattern

**Revisit When**: Key compromised, or security policy prohibits embedded secrets.

---

### DR-008: No Test Suite

**Decision**: Ship without automated tests.

**Context**: Small project, single developer, rapid iteration.

**Rationale**:
- Speed: No test maintenance overhead
- Simplicity: No test framework dependency
- Manual testing sufficient for current scale

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Unit tests | Maintenance burden, mocking complexity |
| Integration tests | Requires Mastodon test instance |
| E2E tests | Requires real feed, real instance |
| Property-based tests | Overkill for current complexity |

**Consequences**:
- ✅ Fast development cycle
- ✅ No test dependencies
- ❌ Regressions undetected
- ❌ Refactoring risky
- ❌ No safety net for contributors
- ❌ Documentation of expected behavior missing

**Revisit When**: Contributor onboarding needed, or regression reported.

---

### DR-009: Stdout Logging Only

**Decision**: Use `print()` to stdout for all logging.

**Context**: Need visibility into pipeline execution for debugging.

**Rationale**:
- Simple: No logging framework setup
- Visible: Immediate output in terminal
- Capturable: systemd/journald captures stdout
- Sufficient: Current debugging needs met

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| `logging` module | More setup, no current need for levels |
| Log files | File management, rotation needed |
| Structured logging | Overkill for current scale |
| Remote logging | External dependency |

**Consequences**:
- ✅ Simple, no dependencies
- ✅ Works with systemd journal
- ❌ No log levels (all same priority)
- ❌ No timestamps (systemd adds them)
- ❌ No structured format
- ❌ No log rotation
- ❌ No remote aggregation

**Revisit When**: Debugging requires log levels, or multiple instances need aggregation.

---

### DR-010: No Error Handling for Network Operations

**Decision**: Let network exceptions propagate and crash the process.

**Context**: Network failures (feed fetch, page fetch, Mastodon API) are possible.

**Rationale**:
- Simple: No try/except blocks cluttering code
- Fail-fast: Crash signals problem immediately
- Scheduler retry: External scheduler re-runs on next interval
- Transparency: Error visible in logs

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Try/except per operation | Hides failures, complex error recovery |
| Retry with backoff | Complexity, may mask persistent failures |
| Circuit breaker | Overkill for batch job |
| Dead letter queue | Overkill for current scale |

**Consequences**:
- ✅ Simple code
- ✅ Failures visible
- ✅ Scheduler handles retry
- ❌ One failure aborts entire run
- ❌ Remaining entries not processed
- ❌ No partial success
- ❌ No error categorization

**Revisit When**: Feeds frequently fail, or partial processing needed.

---

### DR-011: Reverse Iteration of Feed Entries

**Decision**: Iterate feed entries in reverse order (oldest first).

**Context**: RSS feeds typically list newest entries first. The bot should post oldest unposted entries first to maintain chronological order.

**Rationale**:
- Chronological: Posts appear in original publication order
- Natural: Readers expect oldest-first in timeline
- Dedup-friendly: Process all old entries before new ones

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Forward iteration (newest first) | Reverses chronological order in timeline |
| Sort by date | Redundant (feed already sorted) |
| Random order | Confusing timeline |

**Consequences**:
- ✅ Chronological timeline order
- ✅ Predictable behavior
- ❌ Assumes feed is newest-first (not always true)
- ❌ No explicit date sorting (relies on feed order)

**Revisit When**: Feeds with non-standard ordering encountered.

---

### DR-012: Character Limit Enforcement via Truncation

**Decision**: Truncate text to 500 characters when exceeding Mastodon limit.

**Context**: Mastodon has a 500-character status limit. Assembled text may exceed it.

**Rationale**:
- Simple: One-line truncation
- Guaranteed post: Never fails due to length
- Acceptable loss: Truncated text still conveys main content

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Skip entry | Loses content entirely |
| Split into thread | Complex, changes semantics |
| Shorten link | Already shortened |
| Remove tags | Loses discoverability |
| Error and abort | Stops pipeline |

**Consequences**:
- ✅ Always posts (no failure)
- ✅ Simple implementation
- ❌ Truncated text may be incomplete
- ❌ No indication of truncation to reader
- ❌ Hard-coded limit (not configurable)
- ❌ May cut mid-word or mid-emoji

**Revisit When**: Truncation causes significant content loss, or thread support added.

---

### DR-013: Dynamic Module Import for Extensions

**Decision**: Use `try_import()` in `utils.py` for optional modules (`dynamic_tags`, `text_replacements`).

**Context**: Extensions may or may not be present; core should work without them.

**Rationale**:
- Graceful degradation: Core works without extensions
- Optional features: Users add extensions as needed
- No hard dependency: Extensions not in requirements.txt

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Hard import | Breaks if extension missing |
| Plugin registry | Over-engineering for current scale |
| Entry points | Packaging complexity |

**Consequences**:
- ✅ Core works without extensions
- ✅ Extensions are optional
- ❌ Silent failure if extension has import error
- ❌ No version checking
- ❌ No extension discovery mechanism

**Revisit When**: Multiple extensions need management, or version compatibility matters.

---

### DR-014: Language Detection via Keyword Matching

**Decision**: Detect Romanian/English via diacritics and keyword lists in `utils.py`.

**Context**: Need to detect entry language for Mastodon language field.

**Rationale**:
- Simple: No ML dependency
- Fast: String matching only
- Targeted: Optimized for Romanian/English (project's languages)
- Zero dependency: No langdetect library needed

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| `langdetect` library | Additional dependency, slower |
| `langid` library | Additional dependency |
| FastText | Heavy, model download |
| CLD3 | Native dependency, complex |

**Consequences**:
- ✅ No dependencies
- ✅ Fast
- ✅ Good for RO/EN
- ❌ Limited to RO/EN (other languages → "und")
- ❌ Keyword lists may be incomplete
- ❌ Short text may be misclassified
- ❌ No confidence score

**Revisit When**: Multi-language feeds common, or accuracy insufficient.

---

### DR-015: No Configuration Validation

**Decision**: Load configuration with `.get(key, default)` and no validation.

**Context**: Configuration loaded from `config.json` at import time.

**Rationale**:
- Simple: No validation code
- Forgiving: Defaults prevent crashes on missing keys
- Fast: No startup validation overhead

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| JSON Schema validation | Additional dependency, complexity |
| Pydantic model | Additional dependency |
| Manual validation | Maintenance burden |

**Consequences**:
- ✅ Simple, no validation code
- ✅ Defaults prevent crashes
- ❌ Invalid values accepted silently
- ❌ Type errors surface at runtime
- ❌ No early error detection
- ❌ Misconfiguration discovered late

**Revisit When**: Configuration errors cause production incidents.

---

## Decision Index

| ID | Decision | Status |
|----|----------|--------|
| DR-001 | Single-process sequential architecture | Active |
| DR-002 | SQLite for dedup cache | Active |
| DR-003 | MD5 for entry identity | Active |
| DR-004 | CLI arguments for configuration | Active |
| DR-005 | Three-tier title extraction | Active |
| DR-006 | Hard-coded privacy frontends | Active |
| DR-007 | Hard-coded ShrinkMe API key | Active (security concern) |
| DR-008 | No test suite | Active (risk) |
| DR-009 | Stdout logging only | Active |
| DR-010 | No error handling for network ops | Active (risk) |
| DR-011 | Reverse iteration of entries | Active |
| DR-012 | Truncation for char limit | Active |
| DR-013 | Dynamic module import for extensions | Active |
| DR-014 | Keyword-based language detection | Active |
| DR-015 | No configuration validation | Active |

## Related Documentation

- [Architecture](./architecture.md) — System context
- [Design Constraints](./design-decisions.md#constraints) — Technical constraints
- [Change Guide](./change-guide.md) — How to propose new decisions
- [Security](./security.md) — Security implications of decisions
- [Ambiguities and Open Questions](./ambiguities-and-open-questions.md) — Unresolved decisions