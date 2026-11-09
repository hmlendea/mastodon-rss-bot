# Frequently Asked Questions

## General

### What is mastodon-rss-bot?

A Python command-line application that fetches RSS/Atom feed entries, enriches them with linked page content, and posts them as statuses to a Mastodon instance.

### Who is it for?

Self-hosters who want to automatically share feed content (blogs, news sites, YouTube channels, podcasts) to their Mastodon account.

### Is it a hosted service?

No. It is a self-hosted CLI application. You run it on your own server or machine.

### Is it free?

Yes. It is open source under GPL v3 license.

---

## Installation

### What are the requirements?

- Python 3.x
- pip (for installing dependencies)
- Network access to RSS feeds, linked pages, and Mastodon instance
- Write access to working directory (for cache.db, config.json, app secrets)

### How do I install it?

```bash
git clone <repository-url>
cd mastodon-rss-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Do I need a database server?

No. It uses SQLite (file-based, included in Python stdlib). No external database required.

### Do I need to create a Mastodon app?

The bot creates the app automatically on first run. It stores credentials in `app_<instance>.secret`.

---

## Configuration

### Where do I configure the bot?

Two places:
1. **CLI arguments** — Feed URL, instance, credentials, options (per run)
2. **config.json** — Feature toggles (created from sample.config.json on first run)

### How do I get a Mastodon access token?

1. Go to your Mastodon instance → Settings → Development → New Application
2. Set name, redirect URI (can be `urn:ietf:wg:oauth:2.0:oob`)
3. Set scopes (read, write, follow)
4. Create and copy the access token

### What does each config option do?

See [Configuration](./configuration.md) for detailed documentation of all 7 options.

### Can I use environment variables for secrets?

Not currently. The access token is passed via CLI argument. This is a known security concern — see [Security](./security.md).

---

## Usage

### How do I run it?

```bash
python main.py \
  --rss https://example.com/feed.xml \
  --instance mastodon.social \
  --username user@example.com \
  --access-token "$MASTODON_ACCESS_TOKEN" \
  --tags-to-add "news,tech" \
  --days-to-check 7
```

### How do I schedule it?

Use an external scheduler:
- **systemd timer** (recommended on Linux)
- **cron**
- **Kubernetes CronJob**
- **GitHub Actions** (with limitations)

See [Build and Deployment](./build-and-deployment.md) for systemd timer configuration.

### How often should I run it?

Depends on feed update frequency:
- News feeds: every 15-30 minutes
- Blogs: every 1-6 hours
- Low-activity feeds: daily

Balance freshness against Mastodon rate limits.

### Can I run multiple feeds?

Yes, but each feed requires a separate run (separate process). Run multiple instances with different `--rss` arguments. Each should have its own working directory to avoid cache conflicts.

### Can I post to multiple Mastodon instances?

Yes, but each instance requires a separate run with different `--instance` and `--access-token`. App credentials are per-instance (`app_<instance>.secret`).

---

## Behavior

### How does it avoid duplicate posts?

It maintains a SQLite cache (`cache.db`) of posted entries. Each entry is identified by an MD5 hash of title + link + published date. Before posting, it checks the cache.

### What happens if the same article appears in two feeds?

If the link is identical, the cache key matches and it's posted once. If links differ (e.g., different tracking parameters), it may post twice.

### How does it handle entries older than `--days-to-check`?

They are skipped. The age filter prevents posting old content on first run or after downtime.

### What happens to images in the feed?

Images are collected from multiple sources (Twitter/X → Nitter, Reddit, OpenGraph, enclosures), downloaded, uploaded to Mastodon as media, and attached to the status.

### How does it handle links?

Links are processed through a pipeline:
1. Shortening (ShrinkMe, if enabled)
2. Privacy frontends (Nitter, Redlib, etc., if enabled)
3. Tracking parameter removal
4. Monetisation (affiliate tags, if enabled)

See [Link Processing Pipeline](./flows/startup-and-rendering.md) for details.

### What happens if the linked page is down?

The page fetch fails, title extraction falls back to feed title, and the post proceeds without enriched content. If the fetch raises an unhandled exception, the run crashes (see [Error Handling](./error-handling.md)).

### What happens if the feed is down?

feedparser may return empty entries or raise. If it raises, the run crashes. If empty, the run exits normally with no posts.

### What happens if Mastodon rate limits me?

The Mastodon.py library may raise an exception. The run crashes. The scheduler retries on next interval. No rate limit awareness or backoff is implemented.

### What happens if the text exceeds 500 characters?

It is truncated to 500 characters. The truncation may cut mid-word or mid-link.

### What happens if there are more than 4 media items?

Behavior is undefined (see [Ambiguities](./ambiguities-and-open-questions.md#amb-003-media-limit-enforcement)). Mastodon API may reject the post.

---

## Troubleshooting

### The bot posts duplicates

Possible causes:
- `cache.db` was deleted or corrupted
- Entry title/link/date changed in feed (different hash)
- Running from different working directory (different cache.db)

See [Troubleshooting](./troubleshooting.md).

### The bot crashes on every run

Check logs for the exception. Common causes:
- Invalid access token
- Network unreachable
- Malformed feed
- Missing dependencies

See [Troubleshooting](./troubleshooting.md).

### The bot posts nothing

Possible causes:
- No new entries in feed
- All entries already in cache
- All entries older than `--days-to-check`
- Feed fetch failed silently

Check stdout output for entry counts.

### The bot posts old entries on first run

Set `--days-to-check` to a small value (e.g., 1) to limit initial posting to recent entries only.

### Media is not attached

Possible causes:
- No media found in entry
- Media download failed
- Media upload failed
- More than 4 media items (excess dropped or error)

Check stdout for media collection logs.

### Links are not shortened

Check:
- `USE_SHORTLINK` is true in config.json
- ShrinkMe API is reachable
- Hard-coded API key is valid

### Privacy frontends not applied

Check:
- `USE_PRIVACY_FRONTENDS` is true in config.json
- The link domain matches a known frontend mapping
- Frontend is reachable

---

## Security

### Is my access token safe?

The access token is passed as a CLI argument, which is visible in `ps` output to other users on the same machine. This is a known security concern. Recommendation: use environment variable or file-based secrets (not yet implemented).

### What data is stored?

- `cache.db`: Entry IDs, links, titles, publication dates, status URLs
- `app_<instance>.secret`: Mastodon app credentials
- `config.json`: Configuration (no secrets)

No feed content is stored persistently.

### Does it phone home?

No telemetry. It only connects to:
- RSS feed URLs (user-specified)
- Linked page URLs (from feed entries)
- Mastodon API (user-specified instance)
- ShrinkMe API (if shortlinks enabled)
- Privacy frontends (if enabled)

### Is the ShrinkMe API key safe?

The key is hard-coded in source code. If the repository is public, the key is exposed. This is a known security concern.

---

## Development

### Can I contribute?

Yes. See [CONTRIBUTING.md](../CONTRIBUTING.md) and [Change Guide](./change-guide.md).

### How do I add a new feature?

See [Change Guide](./change-guide.md) for the change process and [Design Decisions](./design-decisions.md) for architectural context.

### Can I write extensions?

Yes. Two extension points exist:
- `dynamic_tags.py` — Generate tags dynamically
- `text_replacements.py` — Transform text before posting

See [API Reference: Extensions](./api-reference/extensions.md).

### Why no tests?

The project ships without automated tests (see [Design Decisions](./design-decisions.md#dr-008-no-test-suite)). Contributions adding tests are welcome.

---

## Licensing

### What license is it?

GPL v3. See [LICENSE](../LICENSE).

### Can I use it commercially?

GPL v3 allows commercial use, but derivative works must also be GPL v3. Consult legal counsel for specific use cases.

### Can I host it as a service?

GPL v3 requires that users of a hosted service can access the source code (AGPL-like requirements may apply if modified). Consult legal counsel.

---

## Related Documentation

- [Quick Start](./quick-start.md) — Get running in 5 minutes
- [Troubleshooting](./troubleshooting.md) — Detailed issue resolution
- [Configuration](./configuration.md) — All configuration options
- [Architecture](./architecture.md) — System design
- [Design Decisions](./design-decisions.md) — Why things work this way