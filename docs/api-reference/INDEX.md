# API Reference Index

## Overview

This section documents the programmatic interfaces of the mastodon-rss-bot application. Since this is a CLI application with no public API, the "API reference" covers:

1. **Internal module interfaces** — Functions and classes available for extension
2. **CLI interface** — Command-line arguments and invocation
3. **Configuration interface** — Configuration file schema
4. **Extension interfaces** — Optional modules (`dynamic_tags.py`, `text_replacements.py`)

## Document Map

| Document | Scope | Audience |
|----------|-------|----------|
| [Main Pipeline](./main-pipeline.md) | `main.py` functions, classes, constants | Developers extending the pipeline |
| [Configuration Interface](../configuration.md) | `config.py` module constants, `load_config()` | Operators, developers |
| [Database Interface](../data-model.md) | `database.py` functions, schema | Developers |
| [Utilities Interface](../utils.py) | `utils.py` functions | Developers |
| [Extension Interfaces](./extensions.md) | `dynamic_tags.py`, `text_replacements.py` | Developers creating extensions |

## Quick Reference

### Main Pipeline (`main.py`)

| Symbol | Type | Description |
|--------|------|-------------|
| `parse_args()` | Function | CLI argument parsing |
| `main()` | Function | Pipeline entry point |
| `MAXIMUM_TOOTS_COUNT` | Constant | From config (default 10) |
| `INCLUDE_AUTHOR` | Constant | From config (default true) |
| `INCLUDE_LINK` | Constant | From config (default true) |
| `INCLUDE_LINK_THUMBNAIL` | Constant | From config (default true) |
| `USE_PRIVACY_FRONTENDS` | Constant | From config (default true) |
| `USE_SHORTLINK` | Constant | From config (default true) |
| `MONETISE_LINKS` | Constant | From config (default true) |

### Configuration (`config.py`)

| Symbol | Type | Description |
|--------|------|-------------|
| `load_config()` | Function | Loads/creates config.json |
| `CONFIG_FILE` | Constant | `'config.json'` |
| `SAMPLE_FILE` | Constant | `'sample.config.json'` |

### Database (`database.py`)

| Symbol | Type | Description |
|--------|------|-------------|
| `init_db()` | Function | Returns (connection, cursor) |
| `get_last_entry_posted(db, hash)` | Function | Returns row or None |
| `save_posted_entry(db, hash, title, link, published, author)` | Function | Inserts row |

### Utilities (`utils.py`)

| Symbol | Type | Description |
|--------|------|-------------|
| `detect_language(text)` | Function | Returns 'ro' or 'en' |
| `try_import(module_name)` | Function | Dynamic import, returns module or None |

## Extension Points

### Dynamic Tags (`dynamic_tags.py`)

**Loading**: `utils.try_import('dynamic_tags')`
**Expected Interface**: Module-level function or variable (see [Extensions](./extensions.md))

### Text Replacements (`text_replacements.py`)

**Loading**: `utils.try_import('text_replacements')`
**Expected Interface**: Module-level dict or list of `(pattern, replacement)` tuples (see [Extensions](./extensions.md))

## Related Documentation

- [Architecture](../architecture.md) — System context
- [Components](../components/) — Service implementations
- [Flows](../flows/) — Execution sequences
- [Configuration](../configuration.md) — Config schema
- [Data Model](../data-model.md) — Database schema