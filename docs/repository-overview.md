# Repository Overview

## Purpose

Mastodon RSS Bot is a self-hosted Python command-line application that syndicates RSS feed entries to a Mastodon account. It fetches a configured RSS feed, identifies new entries within a configurable age window, enriches each entry with linked-page metadata and media, applies language-aware text transformations, and posts the result through the Mastodon API while preventing duplicates.

## Scope

**In scope:**
- RSS feed retrieval and parsing (RSS/Atom via feedparser)
- Entry deduplication using SQLite cache
- Linked-page HTML fetching and metadata extraction (title, Open Graph image, shortlink)
- Media collection from Twitter, Reddit, feed enclosures, and Open Graph images
- Language detection (English/Romanian heuristics)
- Text transformations via optional `text_replacements.py` module
- Dynamic hashtag generation via optional `dynamic_tags.py` module
- Link rewriting through privacy frontends (Libreddit, Nitter, Invidious)
- Link monetisation via ShrinkMe.io
- Mastodon media upload and status posting
- Character limit management (500 chars) with language-specific contractions

**Out of scope:**
- Daemon or background service operation
- Inbound HTTP endpoints or web UI
- Multi-account or multi-feed processing in a single run
- Automated scheduling (external scheduler required)
- Retry logic or exponential backoff
- Structured logging, metrics, or tracing
- Configuration UI or validation beyond JSON parsing
- Database migrations (schema is create-only)

## Entry Points

### Primary: `main.py`

```bash
python main.py --rss <URL> --instance <INSTANCE> --username <USER> --access-token <TOKEN> [--tags-to-add <TAGS>] [--days-to-check <DAYS>]
```

**Required arguments:**
- `--rss` — RSS feed URL
- `--instance` — Mastodon instance domain (e.g., `mastodon.social`)
- `--username` — Mastodon username
- `--access-token` — Mastodon OAuth access token

**Optional arguments:**
- `--tags-to-add` — Comma-separated hashtags to append
- `--days-to-check` — Age window in days (entries older than this are skipped)

### Configuration: `config.json`

Loaded by `config.py` at module import. Seeded from `sample.config.json` if missing.

### Optional Extensions

- `dynamic_tags.py` — Must export `get(toot_body, toot_language) → str`
- `text_replacements.py` — Must export `apply(text, language) → str`

Both loaded once at startup via `utils.try_import()` when present in working directory.

## High-Level Capabilities

| Capability | Implementation | Configuration |
|------------|----------------|---------------|
| Feed fetching | `feedparser.parse()` in `main.py` | `--rss` CLI argument |
| Deduplication | SQLite `cache.db` via `database.py` | Automatic |
| Age filtering | `datetime.now() - entry_date < timedelta(days=days_to_check)` | `--days-to-check` CLI argument |
| Title extraction | Priority: Twitter description → entry title → linked page title/og:title | Automatic |
| Media collection | Regex extraction + feed enclosures + OG image | `INCLUDE_LINK_THUMBNAIL` in config |
| Language detection | Heuristic keyword matching in `utils.py` | Automatic |
| Text replacements | `text_replacements.apply()` if module present | Optional module |
| Dynamic tags | `dynamic_tags.get()` if module present | Optional module |
| Link rewriting | Domain replacement in `main.py` | `USE_PRIVACY_FRONTENDS`, `USE_SHORTLINK` in config |
| Link monetisation | ShrinkMe.io URL wrapping in `main.py` | `MONETISE_LINKS` in config |
| Character limiting | Language-specific contractions + truncation in `main.py` | Automatic at 500 chars |
| Mastodon posting | `Mastodon.py` media_upload + status_post | `--access-token`, `--instance`, `--username` CLI |

## Runtime Characteristics

- **Process model**: Single short-lived CLI process per invocation
- **Concurrency**: Strictly sequential, single-threaded
- **Memory**: Bounded by largest linked page + media response per entry
- **Network**: Outbound HTTPS only (feed, linked pages, Mastodon instance)
- **State**: SQLite `cache.db` (persistent), `app_<instance>.secret` (persistent), `config.json` (persistent)
- **Exit codes**: 0 on success, 1 on fatal error
- **Scheduling**: External (systemd timer recommended in README)

## Operator Responsibilities

- Provide and secure Mastodon access token
- Maintain `config.json` and optional extension modules
- Schedule execution (cron, systemd timer, etc.)
- Manage `cache.db`, `app_<instance>.secret`, `config.json` backups
- Monitor stdout logs for failures
- Rotate access tokens and regenerate app credentials when needed