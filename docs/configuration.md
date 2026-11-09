# Configuration

## Schema

The application uses a single JSON configuration file: `config.json`. On first run, `config.py` copies `sample.config.json` to `config.json` if the latter is missing.

### `sample.config.json` (source of truth)

```json
{
  "include_author": false,
  "include_link": true,
  "include_link_thumbnail": true,
  "use_privacy_frontends": true,
  "use_shortlink": true,
  "monetise_links": true,
  "maximum_toots_count": 1
}
```

### Key Definitions

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `include_author` | boolean | `false` | Append feed entry author name to toot body |
| `include_link` | boolean | `true` | Append feed entry link to toot body |
| `include_link_thumbnail` | boolean | `true` | Include Open Graph image from linked page as media |
| `use_privacy_frontends` | boolean | `true` | Rewrite links through privacy frontends (Libreddit, Nitter, Invidious) |
| `use_shortlink` | boolean | `true` | Use page shortlink (`<link rel="shortlink">`) when available |
| `monetise_links` | boolean | `true` | Wrap links with ShrinkMe.io monetisation service |
| `maximum_toots_count` | integer | `1` | Maximum toots to post per run |

### `MONETISE_LINKS` Default Behaviour

In `config.py`, `MONETISE_LINKS` is loaded with `.get("monetise_links", True)`, so it defaults to `true` when the key is absent from `config.json`.

## Sources and Precedence

| Configuration Area | Source | Precedence | Notes |
|--------------------|--------|------------|-------|
| Feed URL | `--rss` CLI argument | Highest | Required; no config file equivalent |
| Mastodon instance | `--instance` CLI argument | Highest | Required; no config file equivalent |
| Mastodon username | `--username` CLI argument | Highest | Required; no config file equivalent |
| Access token | `--access-token` CLI argument | Highest | Required; never written to config |
| Age window (days) | `--days-to-check` CLI argument | Highest | Required; no config default |
| Additional tags | `--tags-to-add` CLI argument | Highest | Optional; comma-separated |
| Posting behaviour | `config.json` | Lower | 7 keys; seeded from sample |
| App credentials | `app_<instance>.secret` | Runtime | Created by `Mastodon.create_app()` |

**No environment variables** are used for configuration.

## Runtime Behaviour

### Loading Sequence

1. `config.py` module import triggers `load_config()`
2. If `config.json` missing → copy `sample.config.json` → `config.json`
3. Parse `config.json` as JSON
4. Extract 7 keys as module-level constants
5. `MONETISE_LINKS` uses `.get()` with default `True`

### Module Constants Exposed

```python
INCLUDE_AUTHOR           # bool
INCLUDE_LINK             # bool
INCLUDE_LINK_THUMBNAIL   # bool
USE_PRIVACY_FRONTENDS    # bool
USE_SHORTLINK            # bool
MONETISE_LINKS           # bool (defaults to True)
MAXIMUM_TOOTS_COUNT      # int
```

These are imported directly by `main.py`:
```python
from config import (
    INCLUDE_AUTHOR,
    INCLUDE_LINK,
    INCLUDE_LINK_THUMBNAIL,
    USE_PRIVACY_FRONTENDS,
    USE_SHORTLINK,
    MONETISE_LINKS,
    MAXIMUM_TOOTS_COUNT,
)
```

### Modification at Runtime

- Configuration is **read once at module import**
- Changes to `config.json` require process restart
- No hot-reload or SIGHUP handling

## Validation

**No schema validation** is performed beyond JSON parsing. Malformed JSON causes immediate exit with error. Missing keys cause `KeyError` at module import (except `monetise_links` which uses `.get()`).

## Security Considerations

- **Access token** is never written to `config.json`; only supplied via CLI
- **App credentials** (`app_<instance>.secret`) are separate from `config.json`
- **Monetisation API key** is hard-coded in `main.py` (not configurable)
- **Privacy frontend domains** are hard-coded in `main.py` (not configurable)

## Extension Points

### Adding New Configuration Keys

1. Add key to `sample.config.json` with default value
2. Add extraction in `config.py` `load_config()`:
   ```python
   NEW_KEY = cfg["new_key"]  # or cfg.get("new_key", default)
   ```
3. Add to `main.py` import list
4. Use in `main.py` logic
5. Document in `sample.config.json` comments (if any)

### Making Keys Optional

Use `.get("key", default)` pattern as done for `MONETISE_LINKS`.

## Known Issues

1. **No validation** — Typos in `config.json` keys cause `KeyError` at import
2. **No type coercion** — Values used as-is; boolean strings `"true"` would be truthy
3. **Hard-coded secrets** — ShrinkMe.io API key embedded in `main.py`
4. **Hard-coded frontends** — Privacy frontend mappings embedded in `main.py`
5. **Drift** — `requirements.txt` lists `argparse` (stdlib) and `regex` (unused)